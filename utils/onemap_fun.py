import os
import requests
import numpy as np
import en_core_web_sm
from typing import Optional

cols_2_del = ['SEARCHVAL', 'BLK_NO', 'ROAD_NAME', 'BUILDING',
              'ADDRESS', 'POSTAL', "LONGTITUDE"]
om_base_url = "https://www.onemap.gov.sg/api/"

# Write some OneMap API functions
# The old set of APIs for routing has changed!


def loc_req(search: str, page=1):
    """
    Extracts the first page result of the keyword location search from the
    OneMap API. The OneMap API can return more than 1 page of results. This
    is dealt with another function.
    """
    api_url = "common/elastic/"
    search_ = f'search?searchVal={search}&'
    page_ = f'returnGeom=Y&getAddrDetails=Y&pageNum={page}'
    api_query = om_base_url + api_url + search_ + page_
    return requests.get(api_query)


def full_loc_req(keyword: str) -> list:
    """ Returns all results based on keyword search on OneMap location as a
    list of dictionary key-value pairs with the following keys:
        'SEARCHVAL',
        'BLK_NO',
        'ROAD_NAME',
        'BUILDING',
        'ADDRESS',
        'POSTAL',
        'X',
        'Y',
        'LATITUDE',
        'LONGITUDE',
    """
    output = None
    api_request = loc_req(keyword)

    # Get number of pagination from API call
    page_count = api_request.json().get('totalNumPages')

    try:
        if page_count > 0:
            api_results = []
            for i in range(1, page_count+1):
                api_results.append(
                    loc_req(
                        keyword, page=i).json().get('results')
                )

            output = [item for sublist in api_results for item in sublist]
    except:
        pass

    return output


def loc_best_match(keyword: str) -> dict:
    """
    Returns OneMap API result that has the closest similarity match with the
    keyword searched
    """
    nlp = en_core_web_sm.load()
    high_value = 0
    index = 0

    result_list: Optional[list] = full_loc_req(keyword)
    lowcase_keyword: str = nlp(keyword.lower())
    location_match: dict = {'search_keyword': keyword}

    if result_list:
        for i in range(len(result_list)):

            kw_2_check = nlp(result_list[i].get('SEARCHVAL').lower())
            kw_simi_score = lowcase_keyword.similarity(kw_2_check)
            if high_value < kw_simi_score:
                high_value = kw_simi_score
                index = i

        location_match = result_list[index]
        location_match['score'] = high_value
        location_match['search_keyword'] = keyword

        # Keeping only the necessary key-value pairs
        # for item in cols_2_del:
        #    del location_match[item]

    return location_match


def get_loc_latlong(keyword: str) -> dict:
    """
    Extends onemap_location_best_match by allow for search results
    that originally only had one output
    """
    api_address = full_loc_req(keyword)

    if api_address and len(api_address) == 1:
        result_xy = api_address[0]
        result_xy['search_keyword'] = keyword
        result_xy['score'] = np.nan

        for item in cols_2_del:
            del result_xy[item]

    else:
        result_xy = loc_best_match(keyword)

    return result_xy


def get_om_token():

    url = om_base_url + "auth/post/getToken"
    payload = {
        "email": os.environ.get('onemap_email'),
        "password": os.environ.get('onemap_pw')
    }
    response = requests.request("POST", url, json=payload)
    return response.json().get('access_token')


token = get_om_token()


def make_route_api(start_ll: list, end_ll: list, route_type: str = 'drive'):
    """
    Give start lat_long and end lat_long and returns route json
    Default route_type is drive, but this can be changed to pt (public
    transport), cycle or walk
    """
    api_url = "public/routingsvc/route?"
    route_ll = f"start={start_ll[0]},{start_ll[1]}&end={end_ll[0]},{end_ll[1]}"
    url_route_type = f"&routeType={route_type}"
    final_url = om_base_url + api_url + route_ll + url_route_type

    headers = {"Authorization": token}
    return requests.request("GET", final_url, headers=headers)


def get_total_route_dist(route_raw_data):
    """
    Extracts route distance from OneMap API
    """
    return eval(route_raw_data._content).get(
        'route_summary').get("total_distance")


def get_route_data(route_raw_data, parameter: str):
    """
    Get required route_raw_data
    """
    return eval(route_raw_data._content).get(
        'route_summary').get(parameter)
