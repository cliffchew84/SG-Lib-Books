def process_all_unique_books(response):
    return set([i["TitleName"] for i in response])


def process_all_avail_books(response):
    return set([i['TitleName'] for i in response if i["StatusDesc"] ==
                "Available"])


def process_all_unique_lib(response): 
    output = sorted(list(set([i['BranchName'] for i in response])))
    output = [i.split("Public Library")[0] for i in output]
    output = [i.split("Library")[0] for i in output]
    return output


def process_all_avail_bks_by_lib(response):
    all_avail_bks_by_lib = []
    for book in response:
        if book['StatusDesc'] == "Available":
            all_avail_bks_by_lib.append(book)
    
    return all_avail_bks_by_lib


def process_lib_book_summary(all_unique_lib, all_avail_bks_by_lib):
    # Creating book summary
    lib_book_summary = []
    for lib in all_unique_lib:
        lib_count = {"Library": lib}
        book_count = 0
        
        for book in all_avail_bks_by_lib:
            if lib == book["BranchName"]:
                book_count = book_count + 1

        lib_count["Count"] = book_count
            
        if lib_count['Count'] >= 1:
            lib_book_summary.append(lib_count)


    # Sorting to top 5 libraries (Need more data to check on this...)
    lib_book_summary = sorted(
            lib_book_summary, key=lambda d: d['Count'], reverse=True) 
    return lib_book_summary[:5]

