import os
import requests
import pendulum
from typing import Dict, List

# Add os.environ for authentication
APPLICATION_ID=os.environ['nlb_rest_app_id']
API_KEY=os.environ['nlb_rest_api_key']

def authenticate_into_nlb_rest(app_id, api_key):
    return { 'X-App-Code': app_id, 'X-API-KEY': api_key }


def get_rest_nlb_api(extension_url: str, 
                     input, 
                     app_id = APPLICATION_ID, 
                     api_key = API_KEY) -> Dict:
    
    """ Not sure if this is overly ambitious to whack all three API methods into 1 rest function... """
    
    headers = authenticate_into_nlb_rest(app_id, api_key)
    final_url = "https://openweb.nlb.gov.sg/api/v1/Catalogue/" + extension_url

    if extension_url == "SearchTitles/":
        payload = {'Title': input, 'Limit': 100, "Format": "BK"}
        
    else:
        payload = { 'BRN': input }
    
    return requests.get(final_url, headers=headers, params = payload).json()


def process_rest_bk_search(nlb_input: Dict) -> List[Dict]:
    """ To process get_search_by_title_keyword """
    # To make my life easier, I am transform the new variable names to the old variable names
    
    output = list()
    for bk_info in nlb_input.get("titles"):
        tmp = dict() 
        tmp['BID'] = bk_info['brn']
        tmp['TitleName'] = bk_info['title']
        tmp['Author'] = bk_info['author']
        tmp['PublishYear'] = bk_info['publishDate']
        
        output.append(tmp)
    return output

def process_rest_single_lib_avail(nlb_input: Dict):
    """ Process a single book availability from NLB rest API """
    output = dict()
    output['ItemNo'] = nlb_input['ItemNo']
    output['CallNumber'] = nlb_input['callNumber']
    output['BranchName'] = nlb_input.get('location').get("name")
    output['StatusDesc'] = nlb_input.get('transactionStatus').get("name")
    if output['StatusDesc'] == "On Loan":
        output['DueDate'] = nlb_input.get('transactionStatus').get(
                "date").split("T")[0]
    else:
        output['DueDate'] = None
    return output

def process_rest_all_lib_avail(nlb_input: List[Dict]):
    return [process_rest_single_lib_avail(i) for i in nlb_input.get("items")]


def process_rest_bk_info(nlb_input: Dict) -> Dict:
    """ Process book info output from NLB rest API """
    output = dict() 
    output['BID'] = nlb_input['brn']
    output['TitleName'] = nlb_input['title']
    output['Author'] = nlb_input['author']
    output['PublishYear'] = nlb_input['publishDate']
    
    return output


def process_single_bk_avail(lib_record: List[Dict]) -> List[Dict]:
    """ Process a single lib record to keep what I want"""
    output = dict()
    for items in lib_record:
        if items in ['ItemNo', 'BranchName', 'CallNumber', 'StatusDesc', 'DueDate']:
            output.update({items: lib_record[items]})
    
    output.update({ "InsertTime": pendulum.now().int_timestamp})

    return output
