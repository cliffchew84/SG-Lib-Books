import pandas as pd
import numpy as np


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
