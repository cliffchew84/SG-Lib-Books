import os
import requests
import pendulum
from typing import Dict, List

# Add os.environ for authentication
APPLICATION_ID = os.environ['nlb_rest_app_id']
API_KEY = os.environ['nlb_rest_api_key']


def authenticate_into_nlb_rest(app_id, api_key):
    return {'X-App-Code': app_id, 'X-API-KEY': api_key}


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
    item_list = set(
        ['ItemNo', 'BranchName', 'CallNumber', 'StatusDesc', 'DueDate'])
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


# 29th Nov latest GetTitles API used for Search
def get_rest_title(input_dict: Dict,
                   offset=None,
                   app_id: str = APPLICATION_ID,
                   api_key: str = API_KEY) -> Dict:
    """ Makes API call to GetTitles """
    headers = authenticate_into_nlb_rest(app_id, api_key)
    final_url = "https://openweb.nlb.gov.sg/api/v2/Catalogue/GetTitles"
    if offset:
        input_dict.update({"Offset": offset})

    return requests.get(final_url, headers=headers, params=input_dict).json()


def get_title_process(api_input) -> List[Dict]:
    """ Processes the GetTitles API data to fit my origin data structure"""
    main_list = []
    for i in api_input.get("titles"):
        tmp_dict = dict()
        tmp_dict['TitleName'] = i.get('title')
        tmp_dict['Author'] = i.get('author')
        tmp_dict['BID'] = i.get('brn')
        tmp_dict['PublishYear'] = i.get('publishDate')
        tmp_dict["type"] = i.get('format', None).get('name', None)

        main_list.append(tmp_dict)

    return main_list


def process_rest_single_lib_avail_v2(nlb_input: Dict):
    """ Process a single book availability from NLB rest API """
    output = dict()
    output['ItemNo'] = nlb_input.get('itemId')
    output['CallNumber'] = nlb_input.get('callNumber')
    output['BranchName'] = nlb_input.get('location').get("name")
    output['StatusDesc'] = nlb_input.get('transactionStatus').get("name")
    if output['StatusDesc'] == "On Loan":
        output['DueDate'] = nlb_input.get(
            'transactionStatus').get("date").split("T")[0]
    else:
        output['DueDate'] = None

    output.update({"InsertTime": pendulum.now().int_timestamp})
    output['BID'] = str(nlb_input.get('brn'))
    return output


def process_rest_all_lib_avail_v2(nlb_input: List[Dict]):
    return [process_rest_single_lib_avail_v2(i) for i in nlb_input.get(
        "items")]


def process_new_search(single_search_record: List[Dict]) -> List[Dict]:
    final_output = []

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
    all_page_search_books = []
    for book in all_search_record.get("titles"):
        single_title_result = process_new_search(book)
        all_page_search_books += single_title_result

    return all_page_search_books


def filter_for_author(books: List[Dict], author: str) -> List[Dict]:
    """ Temp filter for author name, as the new API doesn't
        allow direct author query
    """
    final_books = []
    author_lower = author.lower()
    for book in books:
        book_author = book.get("Author", None)
        if book_author is not None and author_lower in book_author.lower():
            final_books.append(book)

    return final_books


# eResource
def get_eresource_info(input_dict: Dict) -> List[Dict]:
    """ Get eResource book info, using dictionary
        with keys of either 'title', 'creator' or both

        Issue - There are books with missing isbns records from the DB
        Hence, I need keep more relevant data from this API call later on.
    """
    url = "https://openweb.nlb.gov.sg/api/v1/EResource/SearchResources"
    headers = authenticate_into_nlb_rest(APPLICATION_ID, API_KEY)
    input_dict.update({"contenttype": 'eBooks', 'limit': 100})

    return requests.get(url, headers=headers, params=input_dict).json()


def process_single_eresource_info(raw_bk: Dict) -> Dict:
    """ Process required eResource book data to get a list of isbns

    - isbns are needed to make extra API calls to get eResource availabilities
    - Need to keep other details as I found records with missing isbns
    """

    # Single book process
    single_bk = dict()
    single_bk['title'] = raw_bk['title'].replace(
        " [electronic resource] ", " ")
    single_bk['url'] = raw_bk['resourceUrlExt']
    single_bk['authors'] = " | ".join(raw_bk['authors'])
    single_bk['isbns'] = " | ".join(
        [''.join(filter(str.isdigit, i)) for i in raw_bk["isbns"]])

    # Combine all book results into a single list
    return single_bk


def get_eresource_avail(isbn: str):
    """ Get eResource availability by ISBN """
    url = "https://openweb.nlb.gov.sg/api/v1/EResource/GetAvailabilityInfo"
    headers = authenticate_into_nlb_rest(APPLICATION_ID, API_KEY)
    payload = {"idtype": 'ISBN', 'id': isbn}

    return requests.get(url, headers=headers, params=payload).json()


def process_single_eresource_avail(raw_bk: Dict) -> Dict:
    """ Additional eResource availability data to include into eResource info
    """

    output_bk = dict()
    output_bk['total'] = raw_bk.get('totalCopies')
    output_bk['available'] = raw_bk.get('available')
    output_bk['avail_copies'] = raw_bk.get('totalAvailableCopies')
    output_bk['reserved_copies'] = raw_bk.get('totalReservationCopies')

    return output_bk
