import os
import time
from nlb_api import get_bk_data 

APPLICATION_ID = os.environ['nlb_rest_app_id']
API_KEY = os.environ['nlb_rest_api_key']


def test_simple_api_call():
    """ Test a basic API call """
    output = get_bk_data(ext_url="SearchTitles", input="Python")
    assert (output.get('hasMoreRecords') is True)


def test_multiple_api_calls():
    """ Test a basic API call """
    output = get_bk_data(ext_url="SearchTitles", input="Python")
    assert (output.get('totalRecords') >= 1)


def test_simple_get_avail():
    bid_no = 14484799
    output = get_bk_data("GetAvailabilityInfo", input=bid_no)
    assert (output.get("totalRecords") >= 1)


def test_simple_get_title():
    bid_no = 14484799
    output = get_bk_data("GetTitleDetails", input=bid_no)
    assert (output.get("title") == "Python for data analysis / Wes McKinney.")
