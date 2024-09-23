import os
import time
import pytest
from nlb_api import get_bk_data, get_process_bk_info

# run pytest -s -v test_code.py to perform the pytest

@pytest.mark.skip(reason="Skip for now")
def test_simple_api_call():
    """ Test a basic API call """
    time.sleep(1)
    output = get_bk_data(ext_url="GetTitles", input_dict={"Title": "Python"})
    assert (output.get('hasMoreRecords') is True)


@pytest.mark.skip(reason="Skip for now")
def test_multiple_api_calls():
    """ Test to go around any rate limiting issues """
    output_list = []
    for keyword in ['Python', "Scala", "AWS"]:
        output = get_bk_data(ext_url="GetTitles", input_dict={"Title": keyword})
        output_list.append(output.get("totalRecords"))
    assert (output_list == [1218, 106, 205])


@pytest.mark.skip(reason="Skip for now")
def test_get_avail():
    time.sleep(1)
    bid_no = 14484799
    output = get_bk_data("GetAvailabilityInfo", input_dict={"BRN": bid_no})
    assert (output.get("totalRecords") >= 1)


@pytest.mark.skip(reason="Skip for now")
def test_get_title():
    time.sleep(1)
    bid_no = 14484799
    output = get_bk_data("GetTitleDetails", input_dict={"BRN": bid_no})
    assert (output.get("title") == "Python for data analysis / Wes McKinney.")


@pytest.mark.skip(reason="Skip for now")
def test_error_input_error_msg():
    time.sleep(1)
    wrong_data = "xxssyrtarar"
    output = get_bk_data("GetAvailabilityInfo", input_dict={"Title": wrong_data})
    assert (output.get('statusCode') == 400)


@pytest.mark.skip(reason="Skip for now")
def test_not_available_brn():
    time.sleep(1)
    bid_no = 13706621
    output = get_bk_data("GetAvailabilityInfo", input_dict={"BRN": bid_no})
    assert (output.get("count") == 0)


@pytest.mark.skip(reason="Skip for now")
def test_spss_for_dummies_missing_search():
    time.sleep(1)
    search_input={"Title": "SPSS for dummies"}
    titles = get_bk_data("GetTitles", input_dict=search_input)
    total_records = titles.get("totalRecords")

    output = []
    for i in titles.get('titles'): 
        if i.get('format', None).get('name', None) == "Book": 
            output += [f"{str(i.get('availability'))} | {str(i.get('brn'))}",]
    assert(output == ["False | 12849865", "False | 13706621", "True | 202345779"])


def test_get_process_bk_info():
    time.sleep(1)
    bid_no=14484799
    output = get_process_bk_info(bid_no)
    output_to_check = [output.get("BID"), output.get("TitleName"),
                       output.get("Author"), output.get("PublishYear"),
                       output.get("Publisher"), output.get("Subjects")]
    assert (
        output_to_check == [
            '14484799', 'Python for data analysis ', 'Mckinney, Wes.', '2013.',
            ["Beijing : O'Reilly", ''],
            ['Python (Computer program language)', 'Data mining.', 'Programming languages (Electronic computers)']
        ]
    )

