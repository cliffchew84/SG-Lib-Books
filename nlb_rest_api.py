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
