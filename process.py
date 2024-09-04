from datetime import timedelta, datetime
from typing import Dict, List
import pendulum
import re


def get_unique_bks(response):
    return set(i["TitleName"] for i in response)


def get_avail_bks(response):
    return set(i['TitleName'] for i in response if i["StatusDesc"] == "Available")


def get_unique_libs(response):
    output = sorted(set(i['BranchName'] for i in response))
    output = [i.split("Public Library", 1)[0].split("Library", 1)[0] for i in output]
    return output


def get_avail_bks_by_lib(response):
    """ Get available library books by library """
    avail_bks_by_lib = []
    for book in response:
        if book['StatusDesc'] == "Available":
            avail_bks_by_lib.append(book)

    unique_avail_bks_by_lib = list(
        dic for i, dic in enumerate(avail_bks_by_lib)
        if dic not in avail_bks_by_lib[i + 1:])
    return unique_avail_bks_by_lib


def get_lib_bk_summary(all_unique_lib, all_avail_bks_by_lib):
    # Creating book summary
    lib_bk_summary = []
    for lib in all_unique_lib:
        book_count = 0

        for book in all_avail_bks_by_lib:
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

        raw_status = a.get("StatusDesc")
        status = re.findall('Not Loan|Loan|Reference|Transit|$', raw_status)[0]
        status = "Available" if status == "Not Loan" else status
        status = raw_status if status == "" else status

        if due_date is not None:
            status = status + '[' + str(due_date) + ']'

        branch_name = a.get("BranchName")
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
            "BranchName": library,
            "CallNumber": call_no,
            "StatusDesc": status,
            "UpdateTime": update_time,
            "BID": a.get("BID", None)
        })

    return response


def process_title(api_input) -> List[Dict]:
    """ Processes GetTitles API data to fit my origin data structure"""
    main_list = []
    for i in api_input.get("titles"):
        tmp_dict = dict()
        tmp_dict['TitleName'] = i.get('title', None)
        tmp_dict['Author'] = i.get('author', None)
        tmp_dict['BID'] = i.get('brn', None)
        tmp_dict['DigitalID'] = i.get('digitalId', None)
        tmp_dict['PublishYear'] = i.get('publishDate', None)
        tmp_dict["type"] = i.get('format', None).get('name', None)
        main_list.append(tmp_dict)
    return main_list


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
    if output['StatusDesc'] == "On Loan":
        output.update({'DueDate': nlb_input.get(
            'transactionStatus', None).get("date", None).split("T", 1)[0]})
    return output

