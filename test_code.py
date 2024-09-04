import os
from nlb_api import get_bk_data 

APPLICATION_ID = os.environ['nlb_rest_app_id']
API_KEY = os.environ['nlb_rest_api_key']


def test_api_call():
    print('Simple test get_bk_data API call')
    output = get_bk_data(ext_url="SearchTitles", input="Python")
    assert (output.get('hasMoreRecords') is True)
