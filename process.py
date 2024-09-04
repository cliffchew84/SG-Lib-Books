from datetime import timedelta, datetime
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
        due_date = None
        if a.get("DueDate"):
            tmp_date = a.get("DueDate").split("T", 1)[0]
            input_date = datetime.strptime(tmp_date, "%Y-%m-%d")
            due_date = input_date.strftime("%d/%m")

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
            "TitleName": a.get("TitleName").split("/", 1)[0],
            "BranchName": library,
            "CallNumber": a.get("CallNumber").split(" -", 1)[0],
            "StatusDesc": status,
            "UpdateTime": update_time,
            "BID": a.get("BID", None)
        })

    return response
