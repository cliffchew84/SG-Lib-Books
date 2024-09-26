import os
import time
from typing import Dict, List
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv()

# This script uses supabase to handle internal data operations, and is a
# migration from MongoDB. I still need to figure out how to handle NLB API side
# issues...
# The 3 tables of user_books, books_info and books_avail remain the same

# Supabase  credentials
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# Add Methods
def add_user(username: str, hashed_pw: str):
    return supabase.table('users').insert({
        "UserName": username, "HashedPassword": hashed_pw
    }).execute()


def add_user_book(username: str, bid_no):
    return supabase.table("user_books").insert({
        'UserName': username, "BID": bid_no
    }).execute()


def add_avail_bk(books_avail: Dict):
    """ Add single book """
    return supabase.table("books_avail").insert(books_avail).execute()

# add_avail_bk and add_avail_bks is redundant
def add_avail_bks(books_avail: List[Dict]):
    return supabase.table("books_avail").insert(books_avail).execute()


def add_book_info(books_info: Dict):
    return supabase.table("books_info").insert(books_info)


def insert_status(username: str):
    return supabase.table("user_status").insert({
        "UserName": username, 'status': True
    })


def delete_status(username: str):
    return supabase.table('user_status').delete().eq('UserName', username).execute()


def query_status(username: str):
    return supabase.table('user_status').select().eq('UserName', username).execute()


def update_user_info(username: str, values_to_add: Dict):
    """ Update user info """
    supabase.table("users").update(values_to_add).eq("UserName", username)
    return f"Tracked {values_to_add} for {username}"


# Deletes
def delete_bk_avail(db, bid_no):
    return supabase.table('books_avail').delete().eq('BID', bid_no).execute()


def delete_bk_info(db, bid_no):
    return supabase.table('books_info').delete().eq('BID', bid_no).execute()


def delete_user_bk(db, bid_no, username):
    return supabase.table('user_books').delete().eq(
        "UserName", username).eq(
        'BID', bid_no).execute()


def delete_user(db, username):
    return supabase.table('users').delete().eq('UserNane', username).execute()


# Queries
def q_user_bks_bids(db, username: str):
    """ To extract a list of user saved books BIDs """
    return supabase.table("user_books").select("*").eq("UserName", 'cliffchew84').execute()


def q_username(db, username: str):
    """ Return user username and password from mongo DB """
    return supabase.table("users").select("*").eq("UserName", 'cliffchew84').execute()

# def query_user_info(db, username: str):
#     """ Return user username and password from mongo DB """
#
#     return db['users'].find_one({"UserName": username},
#                                 {"_id": 0, "HashedPassword": 0})


def q_user_bks_full(db, username: str):
    """ Fuller query of user saved books """
    books_avail_users = db.user_books.aggregate([
        # connect all tables
        {"$lookup": {
            "from": "books_avail",
            "localField": "BID",
            "foreignField": "BID",
            "as": "books_avail"
        }},
        {"$unwind": '$books_avail'},
        {"$lookup": {
            "from": "books_info",
            "localField": "BID",
            "foreignField": "BID",
            "as": "books_info"
        }},
        {"$unwind": '$books_info'},
        {"$match": {"UserName": username}},
        {"$project": {
            "_id": 0,
            # 'UserName': 1,
            "TitleName": "$books_info.TitleName",
            "Author": "$books_info.Author",
            "BranchName": "$books_avail.BranchName",
            "CallNumber": "$books_avail.CallNumber",
            "StatusDesc": "$books_avail.StatusDesc",
            "DueDate": "$books_avail.DueDate",
            "InsertTime": "$books_avail.InsertTime",
            "BID": "$books_info.BID",
            "Subjects": "$books_info.Subjects",
            "Publisher": "$books_info.Publisher",
            "isbns": "$books_info.isbns",
        }},
    ])
    return [i for i in books_avail_users]


def q_user_bks_subset(db, username: str):
    """ Query user saved books for lesser columns for efficiency """
    output = db.user_books.aggregate([
        {"$lookup": {
            "from": "books_info",
            "localField": "BID",
            "foreignField": "BID",
            "as": "books_info"
        }},
        {"$unwind": '$books_info'},
        {"$lookup": {
            "from": "books_avail",
            "localField": "BID",
            "foreignField": "BID",
            "as": "books_avail"
        }},
        {"$unwind": '$books_avail'},
        {"$match": {"UserName": username}},
        {"$project": {
            "_id": 0,
            "CallNumber": "$books_avail.CallNumber",
            "TitleName": "$books_info.TitleName",
            "Author": "$books_info.Author",
            "BID": "$books_info.BID",
            "Subjects": "$books_info.Subjects",
            "Publisher": "$books_info.Publisher",
            "isbns": "$books_info.isbns",

        }}
    ])
    return list({dic['TitleName']: dic for dic in output}.values())


# EventTracking
def event_tracking(db, table, username: str, event_name: str):
    """ Tracks the timestamp of an event"""
    login_time = time.mktime(datetime.now().timetuple())
    newvalues = {"$set": {"UserName": username,
                          event_name: login_time}}

    db[table].update_one({"UserName": username}, newvalues)
    return f"Tracked {event_name} in {table} for {username}"


def user_search_tracking(db, table, username: str, search_params: Dict):
    """ Tracks user search on title and / or author """
    search_time = time.mktime(datetime.now().timetuple())
    values_to_insert = {"UserName": username, "search_time": search_time}
    values_to_insert.update(search_params)
    db[table].insert_one(values_to_insert)

    return "Search Tracking done"
