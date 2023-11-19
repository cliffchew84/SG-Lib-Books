import os
import requests
import pendulum
from typing import Dict, List

# Add os.environ for authentication
APPLICATION_ID = os.environ['nlb_rest_app_id']
API_KEY = os.environ['nlb_rest_api_key']


def authenticate_into_nlb_rest(app_id, api_key):
    return {'X-App-Code': app_id, 'X-API-KEY': api_key}


def get_rest_nlb_api(extension_url: str,
                     input: str,
                     author=None,
                     setid=None,
                     lastirn=None,
                     app_id: str = APPLICATION_ID,
                     api_key: str = API_KEY) -> Dict:
    """ Using one function to call all REST API methods
        extension_url param: (1) SearchTitles (2) GetAvailabilityInfo
                             (3) GetTitleDetails
        search_on param: (1) Title (2) Subject (3) Author (4) BRN (5) ISBN
    """

    headers = authenticate_into_nlb_rest(app_id, api_key)
    final_url = "https://openweb.nlb.gov.sg/api/v1/Catalogue/" + extension_url

    if extension_url == "SearchTitles":
        payload = {'Limit': 100,
                   "Format": "BK",
                   "setID": setid,
                   "lastIrn": lastirn}

        if input:
            if input.isdigit() and len(input) in [10, 13]:
                payload.update({"ISBN": input})
            else:
                payload.update({"Title": input})

        if author:
            payload.update({"Author": author})

    else:
        payload = {'BRN': input}

    return requests.get(final_url, headers=headers, params=payload).json()


def process_rest_bk_search(nlb_input: Dict) -> List[Dict]:
    """ To process get_search_by_title_keyword
    To make my life easier, I am transform the new variable names to the
    # old variable names """

    output = list()
    nlb_info = nlb_input.get("titles")

    if nlb_info:
        for bk_info in nlb_info.get("titles"):
            tmp = dict()
            tmp['BID'] = bk_info.get('brn')
            tmp['TitleName'] = bk_info.get('title')
            tmp['Author'] = bk_info.get('author')
            tmp['PublishYear'] = bk_info.get('publishDate')

            output.append(tmp)
        return output
    else:
        return output


def process_rest_single_lib_avail(nlb_input: Dict):
    """ Process a single book availability from NLB rest API """
    output = dict()
    output['ItemNo'] = nlb_input.get('ItemNo')
    output['CallNumber'] = nlb_input.get('callNumber')

    location = nlb_input.get("location")
    if location:
        output['BranchName'] = location.get("name")

    status = nlb_input.get("transactionStatus")
    if status:
        output['StatusDesc'] = status.get("name")
        if output['StatusDesc'] == "On Loan":
            output['StatusDesc'] = 'Loan'
            output['DueDate'] = status.get("date").split("T")[0]
    else:
        output['DueDate'] = None

    return output


def process_rest_all_lib_avail(nlb_input: Dict):
    nlb_input_list = nlb_input.get("items")
    if nlb_input_list:
        return [process_rest_single_lib_avail(i) for i in nlb_input_list]
    else:
        return []


def process_rest_bk_info(nlb_input: Dict) -> Dict:
    """ Process book info output from NLB rest API """
    output = dict()
    output['BID'] = nlb_input.get('brn')
    output['TitleName'] = nlb_input.get('title')
    output['Author'] = nlb_input.get('author')
    output['PublishYear'] = nlb_input.get('publishDate')

    return output


def process_single_bk_avail(lib_record: List[Dict]) -> Dict:
    """ Process a single lib record to keep what I want"""
    output = dict()
    item_list = ['ItemNo', 'BranchName', 'CallNumber', 'StatusDesc', 'DueDate']
    for items in lib_record:
        if items in item_list:
            output.update({items: lib_record[items]})

    output.update({"InsertTime": pendulum.now().int_timestamp})

    return output


# 17th Nov new NLB API #########################
def get_rest_nlb_api_v2(extension_url: str,
                        input: str,
                        offset=None,
                        app_id: str = APPLICATION_ID,
                        api_key: str = API_KEY) -> Dict:
    """ Using one function to call all REST API methods
        extension_url param: (1) SearchTitles
                             (2) GetAvailabilityInfo
                             (3) GetTitleDetails
        search_on param: Just on Keywords
    """

    headers = authenticate_into_nlb_rest(app_id, api_key)
    final_url = "https://openweb.nlb.gov.sg/api/v2/Catalogue/" + extension_url

    if extension_url == "SearchTitles":
        payload = {'Keywords': input}

        if offset:
            payload.update({"Offset": offset})

    else:
        payload = {'BRN': input}

    return requests.get(final_url, headers=headers, params=payload).json()


def process_rest_single_lib_avail_v2(nlb_input: Dict):
    """ Process a single book availability from NLB rest API """
    output = dict()
    output['ItemNo'] = nlb_input['itemId']
    output['CallNumber'] = nlb_input['callNumber']
    output['BranchName'] = nlb_input.get('location').get("name")
    output['StatusDesc'] = nlb_input.get('transactionStatus').get("name")
    if output['StatusDesc'] == "On Loan":
        output['DueDate'] = nlb_input.get(
            'transactionStatus').get("date").split("T")[0]
    else:
        output['DueDate'] = None

    output.update({"InsertTime": pendulum.now().int_timestamp})
    output['BID'] = str(nlb_input['brn'])
    return output


def process_rest_all_lib_avail_v2(nlb_input: List[Dict]):
    return [process_rest_single_lib_avail_v2(i) for i in nlb_input.get(
        "items")]


def process_new_search(single_search_record: List[Dict]) -> List[Dict]:
    final_output = list()

    # Get title and author of book
    record_title = single_search_record.get("title").split(" | ")[0]
    record_author = single_search_record.get("author")

    for record in single_search_record.get('records'):
        if record.get("format").get("name") == 'Book':
            tmp_record = dict()
            tmp_record["BID"] = record.get("brn")
            tmp_record['TitleName'] = record_title
            tmp_record['Author'] = record_author
            tmp_record["PublishYear"] = record.get("publishDate")
            final_output.append(tmp_record)

    # Go through each record to get their BID, publishYear
    return final_output


def process_new_search_all(all_search_record: Dict) -> List[Dict]:
    all_page_search_books = list()
    for book in all_search_record.get("titles"):
        single_title_result = process_new_search(book)
        all_page_search_books += single_title_result

    return all_page_search_books


def filter_for_author(books: List[Dict], author: str) -> List[Dict]:
    """ Temp filter for author name, as the new API doesn't
        allow direct author query
    """
    final_books = list()
    for book in books:
        try:
            if author.lower() in book.get("Author").lower():
                final_books += [book]
        except Exception:
            pass

    return final_books


# eResource
def get_eresource_info(title=None, creator=None):
    """ Get eResource book info """
    eresource_url = "https://openweb.nlb.gov.sg/api/v1/EResource"
    headers = authenticate_into_nlb_rest(APPLICATION_ID, API_KEY)
    payload = {"contenttype": 'eBooks', 'limit': 100}

    if title:
        payload.update({"title": title})

    if creator:
        payload.update({"creator": creator})

    if title or creator:
        return requests.get(eresource_url + "/SearchResources",
                            headers=headers,
                            params=payload).json()

    else:
        return {"results": "Please provide a Title or Creator"}


def process_eresource_info(raw_bks: List[Dict]) -> List[Dict]:
    """ Get eResource book availability """

    all_books = []

    # Loop through all books
    for raw_bk in raw_bks:
        # Single book process
        single_bk = dict()
        for i in raw_bk:
            # Parameters needed for
            if i in ['title', 'authors', 'resourceUrlExt', 'isbns']:
                if i == 'authors':
                    to_include = " | ".join(raw_bk[i])
                elif i == "isbns":
                    to_include = " | ".join(
                        [''.join(filter(str.isdigit, i)) for i in raw_bk[i]])
                else:
                    to_include = raw_bk[i]
                # Combining needed book parameters into single dict
                single_bk.update({i: to_include})

        # Combine all book results into a single list
        all_books.append(single_bk)

    return all_books


def get_eresource_avail(isbn: str):
    """ Get book availability based on isbn """

    base_url = "https://openweb.nlb.gov.sg/api/v1/EResource"
    headers = authenticate_into_nlb_rest(APPLICATION_ID, API_KEY)
    payload = {"idtype": 'ISBN', 'id': isbn}

    return requests.get(base_url + "/GetAvailabilityInfo",
                        headers=headers,
                        params=payload).json()
