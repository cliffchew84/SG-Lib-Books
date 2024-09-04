import os
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
    assert (output.get('hasMoreRecords') is True)
