import os
import time
import requests
import pendulum
from typing import Dict, List

# This script focuses on functions that interacts with the NLB API. I added
# more robust code to check if code hits statusCode 429, which is the rate 
# limiting error from NLB.
#
# I added .get("var_name", None) to my dicts to make them more robust
#
# Lastly, I refactored my get_bk_data to include GetTitles, to make my NLB API
# calls more consistent. I am also trying to see if I can use GetTitles rather
# than GetTitleDetails, but GetTitles do not use BRN

# Add os.environ for authentication
APPLICATION_ID = os.environ['nlb_rest_app_id']
API_KEY = os.environ['nlb_rest_api_key']


def auth_nlb(app_id, api_key):
    return {'X-App-Code': app_id, 'X-API-KEY': api_key}


def get_bk_data(ext_url: str,
                input_dict: Dict,
                offset=None,
                app_id: str = APPLICATION_ID,
                api_key: str = API_KEY) -> Dict:
    """ Get all NLB REST API books data
        ext_url: GetAvailabilityInfo 
                 GetTitleDetails ( to delete )
                 GetTitles
        input_dict: {"Author": input}
                    {"Title": input}
                    {"BRN": input}
    [TODO]
    - GetTitleDetails provide less info then GetTitles. However, GetTitles can't
      use BRN, which makes sense cos GetTitles does a general search, while 
      using BRN is a very specific search. Closest usage is ISBN, but that
      isn't unique like BRN.
    - For now, consider just adding details from GetTitleDetails first 
    """

    headers = auth_nlb(app_id, api_key)
    final_url = "https://openweb.nlb.gov.sg/api/v2/Catalogue/" + ext_url
    # [TODO] - Should I consider just make all limit == 30 ? 
    if ext_url == "GetAvailabilityInfo" or ext_url == "GetTitleDetails":
        input_dict.update({"limit": 100})

    elif ext_url == "GetTitles":
        # GetTitles don't accept BRN in input_dict
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


def process_bk_info(nlb_input: Dict) -> Dict:
    """ Process book info output from NLB API - GetTitleDetails"""

    subjects = " | ".join(list(set([i.replace(".", "") for i in nlb_input.get('subjects')])))
    isbns = " | ".join(" | ".join(nlb_input.get('isbns', None)).split(","))

    return {
        'BID' : nlb_input.get('brn', None),
        'TitleName': nlb_input.get('title', None),
        'Author': nlb_input.get('author', None),
        'PublishYear' : nlb_input.get('publishDate', None),
        'Subjects' : subjects,
        'Publisher' : nlb_input.get('publisher', None),
        'isbns' : nlb_input.get("isbns", None)
    }


def get_process_bk_info(bid_no):
    """ Make API calls to book info and ingest into DB """
    raw_bk_title = get_bk_data("GetTitleDetails", input_dict={"BRN": bid_no})
    bk_title = process_bk_info(raw_bk_title) 
    bk_title.update({"BID": str(bid_no)})

    title = bk_title.get("TitleName", None)
    if title:
        bk_title['TitleName'] = title.split("/", 1)[0]
    return bk_title


def check_bk_avail(bid_no: int):
    """ To check the availability of book by count 
        if bk.get('count') == 0, this means that this
        book isn't searchable on the actual NLB app!
    """
    bk = get_bk_data("GetAvailabilityInfo", input_dict={"BRN": bid_no})
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
