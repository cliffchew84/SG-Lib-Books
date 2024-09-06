import os
import time
import requests
import pendulum
from typing import Dict, List

# This script focuses on functions that interacts with the NLB API. I have added
# a bit more robust code by checking if the code hits any statusCode 429 issue,
# which is the rate limiting error from NLB. I also tried to make sure that all
# dictionary convrsions from NLB uses .get("var_name", None), to ensure
# that I at least always have that parameter as a None if it is missing.
# Hopefully this helps with reducing any error at the ingestion into MongoDB.

# Add os.environ for authentication
APPLICATION_ID = os.environ['nlb_rest_app_id']
API_KEY = os.environ['nlb_rest_api_key']


def auth_nlb(app_id, api_key):
    return {'X-App-Code': app_id, 'X-API-KEY': api_key}


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
    
    json_output = requests.get(final_url, headers=headers, params=payload).json() 

    while json_output.get('statusCode') == 429:
        print("Please wait for awhile. We are hitting NLB too hard!")
        time.sleep(2)
        json_output = requests.get(final_url, headers=headers, params=payload).json() 
    
    return json_output

def process_bk_info(nlb_input: Dict) -> Dict:
    """ Process book info output from NLB rest API """

    return {
        'BID' : nlb_input.get('brn', None),
        'TitleName': nlb_input.get('title', None),
        'Author': nlb_input.get('author', None), 
        'PublishYear' : nlb_input.get('publishDate', None)
    }


def get_process_bk_info(db, bid_no):
    """ Make API calls to book info and ingest into DB """
    raw_bk_title = get_bk_data("GetTitleDetails", input=bid_no)
    bk_title = process_bk_info(raw_bk_title) 
    bk_title.update({"BID": str(bid_no)})
    del bk_title['PublishYear']

    title = bk_title.get("TitleName", None)
    if title:
        bk_title['TitleName'] = title.split("/", 1)[0]
    return bk_title


def bk_search(input_dict: Dict,
              offset=None,
              app_id: str = APPLICATION_ID,
              api_key: str = API_KEY) -> Dict:
    """ Get GetTitles using APIs"""
    headers = auth_nlb(app_id, api_key)
    final_url = "https://openweb.nlb.gov.sg/api/v2/Catalogue/GetTitles"
    input_dict.update({"limit": 30})
    if offset:
        input_dict.update({"Offset": offset})

    json_output = requests.get(
        final_url, headers=headers, params=input_dict).json()

    while json_output.get('statusCode') == 429:
        print("Please wait for awhile. We are hitting NLB too hard!")
        time.sleep(2)
        json_output = requests.get(
            final_url, headers=headers, params=input_dict).json()

    return json_output


def check_bk_avail(bid_no: int):
    """ To check the availability of book by count 
        if bk.get('count') == 0, this means that this
        book isn't searchable on the actual NLB app!
    """
    bk = get_bk_data("GetAvailabilityInfo", input=bid_no)
    return bk.get("count")


# eResource
# None of these functions are used, because the API results from the original
# books already provide eBooks data as well that I am using
def get_ebk_info(input_dict: Dict) -> List[Dict]:
    """ Get eResource book info, using dictionary
        with keys of either 'title', 'creator' or both

        Issue - There are books with missing isbns records from the DB
        Hence, I need keep more relevant data from this API call later on.
    """
    url = "https://openweb.nlb.gov.sg/api/v1/EResource/SearchResources"
    headers = auth_nlb(APPLICATION_ID, API_KEY)
    input_dict.update({"contenttype": 'eBooks', 'limit': 100})
    return requests.get(url, headers=headers, params=input_dict).json()


def process_ebk_info(raw_bk: Dict) -> Dict:
    """ Process required eResource book data to get a list of isbns
    - isbns are needed to make extra API calls to get eResource availabilities
    - Need to keep other details as I found records with missing isbns
    """
    bk = dict()
    bk['title'] = raw_bk['title'].replace(" [electronic resource] ", " ")
    bk['url'] = raw_bk['resourceUrlExt']
    bk['authors'] = " | ".join(raw_bk['authors'])
    bk['isbns'] = " | ".join([''.join(filter(str.isdigit, i)) for i in raw_bk["isbns"]])
    return bk


def get_ebk_avail(isbn: str):
    """ Get eResource availability by ISBN """
    url = "https://openweb.nlb.gov.sg/api/v1/EResource/GetAvailabilityInfo"
    headers = auth_nlb(APPLICATION_ID, API_KEY)
    payload = {"idtype": 'ISBN', 'id': isbn}
    return requests.get(url, headers=headers, params=payload).json()


def process_ebk_avail(raw_bk: Dict) -> Dict:
    " Additional eResource availability data to include into eResource info "
    output_bk = dict()
    output_bk['total'] = raw_bk.get('totalCopies')
    output_bk['available'] = raw_bk.get('available')
    output_bk['avail_copies'] = raw_bk.get('totalAvailableCopies')
    output_bk['reserved_copies'] = raw_bk.get('totalReservationCopies')
    return output_bk
