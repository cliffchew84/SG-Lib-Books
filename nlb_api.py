import os
import requests
import pendulum
from typing import Dict, List

# Add os.environ for authentication
APPLICATION_ID = os.environ['nlb_rest_app_id']
API_KEY = os.environ['nlb_rest_api_key']


def auth_nlb(app_id, api_key):
    return {'X-App-Code': app_id, 'X-API-KEY': api_key}


def process_bk_info(nlb_input: Dict) -> Dict:
    """ Process book info output from NLB rest API """
    output = dict()
    output['BID'] = nlb_input.get('brn')
    output['TitleName'] = nlb_input.get('title')
    output['Author'] = nlb_input.get('author')
    output['PublishYear'] = nlb_input.get('publishDate')
    return output


def get_bk_data(ext_url: str,
                input: str,
                offset=None,
                app_id: str = APPLICATION_ID,
                api_key: str = API_KEY) -> Dict:
    """ Using one function to call all REST API methods
        ext_url param: (1) SearchTitles (2) GetAvailabilityInfo (3) GetTitleDetails
        search_on param: Keyword Search
    """
    headers = auth_nlb(app_id, api_key)
    final_url = "https://openweb.nlb.gov.sg/api/v2/Catalogue/" + ext_url
    payload = {'BRN': input, "Limit": 100}
    if ext_url == "SearchTitles":
        payload = {'Keywords': input}
        if offset:
            payload.update({"Offset": offset})
    return requests.get(final_url, headers=headers, params=payload).json()


def get_title(input_dict: Dict,
              offset=None,
              app_id: str = APPLICATION_ID,
              api_key: str = API_KEY) -> Dict:
    """ Get GetTitles using APIs"""
    headers = auth_nlb(app_id, api_key)
    final_url = "https://openweb.nlb.gov.sg/api/v2/Catalogue/GetTitles"
    input_dict.update({"limit": 30})
    if offset:
        input_dict.update({"Offset": offset})

    return requests.get(final_url, headers=headers, params=input_dict).json()


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
    output = dict()
    output['ItemNo'] = nlb_input.get('itemId', None)
    output['CallNumber'] = nlb_input.get('callNumber', None)
    output['BranchName'] = nlb_input.get('location', None).get("name", None)
    output['StatusDesc'] = nlb_input.get('transactionStatus', None).get("name",
                                                                        None)
    if output['StatusDesc'] == "On Loan":
        output['DueDate'] = nlb_input.get(
            'transactionStatus', None).get("date", None).split("T", 1)[0]
    else:
        output['DueDate'] = None

    output.update({"InsertTime": pendulum.now().int_timestamp})
    output['BID'] = str(nlb_input.get('brn'))
    return output

# eResource
def get_eresource_info(input_dict: Dict) -> List[Dict]:
    """ Get eResource book info, using dictionary
        with keys of either 'title', 'creator' or both

        Issue - There are books with missing isbns records from the DB
        Hence, I need keep more relevant data from this API call later on.
    """
    url = "https://openweb.nlb.gov.sg/api/v1/EResource/SearchResources"
    headers = auth_nlb(APPLICATION_ID, API_KEY)
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
    headers = auth_nlb(APPLICATION_ID, API_KEY)
    payload = {"idtype": 'ISBN', 'id': isbn}
    return requests.get(url, headers=headers, params=payload).json()


def process_single_eresource_avail(raw_bk: Dict) -> Dict:
    " Additional eResource availability data to include into eResource info "
    output_bk = dict()
    output_bk['total'] = raw_bk.get('totalCopies')
    output_bk['available'] = raw_bk.get('available')
    output_bk['avail_copies'] = raw_bk.get('totalAvailableCopies')
    output_bk['reserved_copies'] = raw_bk.get('totalReservationCopies')
    return output_bk
