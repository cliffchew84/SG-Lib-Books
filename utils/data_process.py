import random
import polyline
import geopy.distance
import pandas as pd
import numpy as np
from . import onemap_fun as om


def create_mdb_query_w_df_cols(df: pd.DataFrame):
    """
    Creates mongoDB query from dataframe,
    list or string of known column names
    """

    if type(df) is pd.DataFrame:
        col_names = df.columns.tolist()
    elif type(df) is list:
        col_names = df
    elif type(df) is str:
        col_names = [i.strip() for i in df.split(',')]

    col_dict = dict()
    col_filter = {"_id": 0}

    for name in col_names:
        col_dict[name] = {"$exists": True}
        col_filter[name] = 1

    return col_dict, col_filter


def table_select_from_pt(df: pd.DataFrame,
                         loc_ll: tuple,
                         select=True,
                         radius=1000) -> pd.DataFrame:
    """ Takes a Tuple Lat-Long input, a set of tables with Lat-Longs,
    and filters for records that are included or excluded by a radius
    distance
    """

    df_lat, df_long = df['LATITUDE'].tolist(), df['LONGITUDE'].tolist()
    df['dist'] = [geopy.distance.geodesic(
        (float(i), float(j)), loc_ll).m for i, j in zip(df_lat, df_long)]

    if select:
        selected_df = df[df['dist'] <= radius].reset_index(drop=True)
    else:
        selected_df = df[df['dist'] > radius].reset_index(drop=True)

    return selected_df


def create_route(start_latlong: tuple,
                 end_latlong: tuple,
                 route_type: str = 'walk') -> (list, float):
    """ Creates route from start_latlong and end_latlong
    Output two outputs:
    1. List of coordiate tuples that traces out a route
    2. Total distance of route
    """

    # Route creation
    route_output = om.make_route_api(
        start_latlong, end_latlong, route_type=route_type)
    total_d = om.get_total_route_dist(route_output)

    # Processing walking route
    route_g = route_output.json().get('route_geometry')
    line = polyline.decode(route_g)
    routing = pd.concat([pd.Series(line), pd.Series(line)], axis=1)
    routing[1] = routing[1].shift(-1)
    route_list = [(i, j) for i, j in zip(routing[0], routing[1])
                  if j is not None]

    return route_list, total_d


def generate_color():
    """
    Generate random values for red, green, and blue
    Wants to eventually change this to a selection of more chart friendly
    colours.
    """
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    return f"rgb({r}, {g}, {b})"


def process_df_lease_left(df: pd.DataFrame) -> pd.DataFrame:
    """ Process """
    if 'lease_left' in df.columns.tolist():
        df['lease_left'] = [i.replace('s', '') for i in df['lease_left']]
        df['lease_left'] = [i.replace(' year', 'y') for i in df['lease_left']]
        df['lease_left'] = [i.replace(' month', 'm') for i in df['lease_left']]

        df['lease_yrs'] = [
            int(i[0])*12 for i in df['lease_left'].str.split("y")]

        df['lease_mths'] = [0 if i[-1].strip().replace('m', '') == '' else int(
            i[-1].strip().replace('m', '')) for i in df['lease_left'].str.split("y")]

        df['total_lease'] = df['lease_yrs'] + df['lease_mths']

        del df['lease_left']
        del df['lease_yrs']
        del df['lease_mths']

        df.rename(columns={'total_lease': 'lease_mths'}, inplace=True)
        df['lease_mths'] = df['lease_mths'].astype(np.int32)

    return df


def process_df_flat(df: pd.DataFrame) -> pd.DataFrame:
    if "flat" in df.columns.tolist():
        df['flat'] = [i.replace(" ROOM", "R") for i in df['flat']]
        df['flat'] = [i.replace("EXECUTIVE", "EC") for i in df['flat']]
        df['flat'] = [i.replace("MULTI-GENERATION", "MG") for i in df['flat']]
        df['flat'] = df['flat'].astype(str)

    return df
