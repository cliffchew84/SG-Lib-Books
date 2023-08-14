import os
import pendulum
from typing import List, Dict, OrderedDict
from zeep import Client, helpers

PRODUCTION_URL = "https://openweb.nlb.gov.sg/OWS/CatalogueService.svc?singleWsdl"
client = Client(wsdl=PRODUCTION_URL)

## New code
def call_nlb_bk_avail_api_by_keyword(
        API: str, 
        keyword: str, 
        client=client) -> OrderedDict:
    
    """ Call NLB API to get the libraries that this books is as a dict"""

    avail_books = {
        "APIKey": API,
        "SearchItems": {"SearchItem": {
            "SearchField": "Title", 
            "SearchTerms": keyword
            }},
        "Modifiers" : {
            "StartRecordPosition": 1,
            "MaximumRecords": 50,
        },
    }
    output = client.service.GetAvailabilityInfo(**avail_books)
    return helpers.serialize_object(output)


def call_nlb_bk_avail_api(API: str, bid_no: str, client=client) -> OrderedDict:
    """ Call NLB API to get the libraries that this books is as a dict"""
    avail_books = {
        "APIKey": API,
        "BID": bid_no,
        "Modifiers" : {
            "StartRecordPosition": 1,
            "MaximumRecords": 50,
        },
    }
    output = client.service.GetAvailabilityInfo(**avail_books)
    return helpers.serialize_object(output)


def search_book_by_title_keyword(
        API: str, 
        keyword: str, 
        client=client) -> List[OrderedDict]:
    
    """ Make API call to NLB to search their books """
    avail_books = {
        "APIKey": API,
        "SearchItems": {"SearchItem": [
            {"SearchField": "Title", "SearchTerms": keyword }, 
            {"SearchField": "MediaCode", "SearchTerms": "BK"}
        ]},
        "Modifiers" : {
            "StartRecordPosition": 1,
            "MaximumRecords": 50,
        },
    }
    output = client.service.Search(**avail_books)
    return helpers.serialize_object(output)


def search_book_by_title_keyword_next_page(
        API: str, 
        setid: str, 
        client=client) -> List[OrderedDict]:
    
    """ Make API call to NLB to search on next page of already made API call """
    avail_books = {
        "APIKey": API,
        "Modifiers" : {
            "StartRecordPosition": 1,
            "MaximumRecords": 50,
            "SetId": setid
        },
    }
    output = client.service.Search(**avail_books)
    return helpers.serialize_object(output)


def remove_book_by_property_name(
        book_dict_values: OrderedDict, 
        property: str, 
        value: str) -> List[OrderedDict]:
    
    """ Filter away books with unwanted property values """
    output_list = []
    for book in book_dict_values:
        try:
            if value in book.get(property):
                pass
            else:
                output_list.append(book)
        except:
            pass
    
    return output_list


def get_bk_availability_info(book: OrderedDict) -> List:
    """ Get the needed book info in the nested Dict"""
    return book.get("Items").get("Item")


def call_nlb_bk_info_api(API: str, bid_no: str, client=client):
    """ Get title from NLB API """

    title_inputs = { "APIKey": API, "BID": bid_no }
    title_output = client.service.GetTitleDetails(**title_inputs)
    return helpers.serialize_object(title_output)


def process_single_bk_avail(lib_record: List[Dict]) -> List[Dict]:
    """ Process a single lib record to keep what I want"""
    output = OrderedDict()
    for items in lib_record:
        if items in ['ItemNo', 'BranchName', 'CallNumber', 'StatusDesc', 'DueDate']:
            output.update({items: lib_record[items]})
    
    output.update({ "InsertTime": pendulum.now('Asia/Singapore').int_timestamp})

    return output


def process_all_bk_avail(lib_record: List[Dict]) -> List[List[Dict]]:
    """ Process all the libraries of the book """

    entire_lib_list: List[List[Dict]] = []
    for item in lib_record:
        entire_lib_list.append(process_single_bk_avail(item))
    return entire_lib_list


def process_bk_info(title_record: List[Dict]) -> List[Dict]:
    """ Process a single lib record to keep what I want"""
    output = OrderedDict()
    for items in title_record:
        if items == 'BID':
            output.update({items: title_record[items]})
        elif items == 'TitleName':
            try:
                output.update({items: title_record[items].split("/")[0].strip()})
            except: 
                output.update({items: title_record[items]})

    return output
