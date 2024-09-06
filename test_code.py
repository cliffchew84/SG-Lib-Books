import os
import time
import pytest
from nlb_api import get_bk_data, bk_search

APPLICATION_ID = os.environ['nlb_rest_app_id']
API_KEY = os.environ['nlb_rest_api_key']

# run pytest -s -v test_code.py to perform the pytest

@pytest.mark.skip(reason="Skip for now")
def test_simple_api_call():
    """ Test a basic API call """
    time.sleep(1)
    output = get_bk_data(ext_url="SearchTitles", input="Python")
    assert (output.get('hasMoreRecords') is True)


@pytest.mark.skip(reason="Skip for now")
def test_multiple_api_calls():
    """ Test a basic API call """
    time.sleep(1)
    output = get_bk_data(ext_url="SearchTitles", input="Python")
    assert (output.get('totalRecords') >= 1)

@pytest.mark.skip(reason="Skip for now")
def test_simple_get_avail():
    time.sleep(1)
    bid_no = 14484799
    output = get_bk_data("GetAvailabilityInfo", input=bid_no)
    assert (output.get("totalRecords") >= 1)


@pytest.mark.skip(reason="Skip for now")
def test_simple_get_title():
    time.sleep(1)
    bid_no = 14484799
    output = get_bk_data("GetTitleDetails", input=bid_no)
    assert (output.get("title") == "Python for data analysis / Wes McKinney.")


@pytest.mark.skip(reason="Skip for now")
def test_error_input():
    time.sleep(1)
    wrong_data = "xxssyrtarar"
    output = get_bk_data("GetAvailabilityInfo", input=wrong_data)
    assert (output.get('statusCode') == 400)


@pytest.mark.skip(reason="Skip for now")
def test_not_available_brn():
    time.sleep(1)
    bid_no = 13706621
    output = get_bk_data("GetAvailabilityInfo", input=bid_no)
    assert (output.get("count") == 0)


def test_spss_for_dummies_search():
    time.sleep(1)
    search_input={"Title": "SPSS for dummies"}
    titles = bk_search(input_dict=search_input)
    total_records = titles.get("totalRecords")

    output = []
    for i in titles.get('titles'): 
        if i.get('format', None).get('name', None) == "Book": 
            output += [f"{str(i.get('availability'))} | {str(i.get('brn'))}",]
    assert(output == ["False | 12849865", "False | 13706621", "True | 202345779"])
