from datetime import timedelta, datetime
from typing import Dict, List
import pendulum
import re

# This script focuses purely on functions that processes my data. The good thing
# is this script doesn't require the nlb_api nor the m_db api, so everything
# happens on the Python programming level itself. In a way, this is also the
# transition layer between the raw data from NLB to the processed data that is
# to be ingested into MongoDB.


def get_unique_bks(response):
    return set(i["TitleName"] for i in response)


def get_avail_bks(response):
    return set(i['TitleName'] for i in response if i["StatusDesc"] == "Available")


def get_unique_libs(response):
    op = sorted(set(i['BranchName'] for i in response))
    return [i.split("Public Library", 1)[0].split("Library", 1)[0] for i in op]


def get_avail_bks_by_lib(response):
    """ Get avail bks at lib level """
    avail_bks_by_lib = []
    for book in response:
        if book.get('StatusDesc', None) == "Available":
            avail_bks_by_lib.append(book)

    unique_avail_bks_by_lib = list(
        dic for i, dic in enumerate(avail_bks_by_lib)
        if dic not in avail_bks_by_lib[i + 1:])
    return unique_avail_bks_by_lib


def get_lib_bk_summary(unique_libs, avail_bks_by_lib):
    """ Create summary of library and their respective bks"""
    lib_bk_summary = []
    for lib in unique_libs:
        book_count = 0

        for book in avail_bks_by_lib:
            if lib == book["BranchName"]:
                book_count += 1
        lib_bk_summary.append({lib: book_count})

    lib_bk_summary = sorted(
        lib_bk_summary, key=lambda x: list(x.values())[0], reverse=True)
    return lib_bk_summary


def pg_links(offset, total):
    """ Create pagination for the output of my NLB Search """
    items = 30
    previous = offset - items if offset != 0 else None
    current = offset
    next = offset + items if (offset + items < total) else None
    last = items * (total // items) if next is not None else None

    return {"previous": previous, "current": current, "next": next, "last": last}


def process_user_bks(query: str):
    """ Process db result for frontpage """
    response = []
    for a in query:
        title = a.get("TitleName", None)
        if title is not None:
            try:
                title = title.split("/", 1)[0]
            except:
                pass

        call_no = a.get("CallNumber", None)
        if call_no is not None:
            try:
                call_no = call_no.split(" -", 1)[0]
            except:
                pass

        due_date = a.get("DueDate", None)
        if due_date:
            due_date = datetime.strptime(
                due_date.split("T", 1)[0], "%Y-%m-%d").strftime("%d/%m")

        update_time = datetime.fromtimestamp(
            a.get("InsertTime"), pendulum.timezone("Asia/Singapore")
        ).strftime("%d/%m %H:%M")

        raw_status = a.get("StatusDesc", None)
        status = re.findall('Not Loan|Loan|Reference|Transit|$', raw_status)[0]
        status = "Available" if status == "Not Loan" else status
        status = raw_status if status == "" else status

        if due_date is not None:
            status = status + '[' + str(due_date) + ']'

        branch_name = a.get("BranchName", None)
        if "Lifelong Learning" in branch_name:
            library = "Lifelong Learning Institute"
        elif "Public Library" in branch_name:
            library = branch_name.split("Public Library", 1)[0]
        elif "Library" in branch_name:
            library = branch_name.split("Library", 1)[0]
        else:
            library = branch_name

        response.append({
            "TitleName": title,
            "Author": a.get("Author"),
            "BranchName": library,
            "CallNumber": call_no,
            "StatusDesc": status,
            "UpdateTime": update_time,
            "BID": a.get("BID", None)
        })
    return response


def process_title(json_input) -> List[Dict]:
    """ Processes GetTitles API data to fit my origin data structure"""
    output_list = []
    for i in json_input.get("titles"):
        output = dict()
        output['TitleName'] = i.get('title', None)
        output['Author'] = i.get('author', None)
        output['BID'] = i.get('brn', None)
        output['DigitalID'] = i.get('digitalId', None)
        output['PublishYear'] = i.get('publishDate', None)
        output["type"] = i.get('format', None).get('name', None)
        output_list.append(output)
    return output_list


def process_bk_avail(nlb_input: Dict):
    """ Process a single book availability from NLB rest API """
    output = {
        "ItemNo": nlb_input.get('itemId', None),
        "CallNumber": nlb_input.get('callNumber', None),
        "BranchName": nlb_input.get('location', None).get("name", None),
        "StatusDesc": nlb_input.get('transactionStatus', None).get("name", None),
        "DueDate": None,
        "InsertTime": pendulum.now().int_timestamp,
        "BID": str(nlb_input.get('brn'))
    }
    if output.get('StatusDesc', None) == "On Loan":
        output.update({'DueDate': nlb_input.get(
            'transactionStatus', None).get("date", None).split("T", 1)[0]})
    return output

