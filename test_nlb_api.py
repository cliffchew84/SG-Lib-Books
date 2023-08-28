import os
from nlb_rest_api import get_rest_nlb_api

APPLICATION_ID = os.environ['nlb_rest_app_id']
API_KEY = os.environ['nlb_rest_api_key']


def test_api_call():
    output = get_rest_nlb_api(extension_url="SearchTiles",
                              input="Python",
                              search_on="Title")
    assert (output.get('setId') == 502893088)
