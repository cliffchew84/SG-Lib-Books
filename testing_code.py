import os
import nlb_rest_api as nlb

APPLICATION_ID = os.environ['nlb_rest_app_id']
API_KEY = os.environ['nlb_rest_api_key']


def test_api_call():
    output = get_rest_nlb_api(extension_url="SearchTitles",
                              input="Python",
                              search_on="Title")

    assert (output.get('hasMoreRecords') is True)
