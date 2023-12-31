from pymongo import mongo_client
from typing import Dict, List
from datetime import datetime
import time
import os

# MongoDB credentials
MONGO_PASSWORD = os.environ["mongo_pw"]
base_url = "mongodb+srv://cliffchew84:"
end_url = "cliff-nlb.t0whddv.mongodb.net/?retryWrites=true&w=majority"
mongo_url = f"{base_url}{MONGO_PASSWORD}@{end_url}"


def connect_mdb():
    return mongo_client.MongoClient(mongo_url, serverSelectionTimeoutMS=5000)


# Add Methods
def mg_add_user(db, username: str, hashed_pw: str):
    return db['users'].insert_one({
        'UserName': username,
        'HashedPassword': hashed_pw})


def mg_add_user_book(db, username: str, bid_no):
    return db['user_books'].insert_one({'UserName': username, 'BID': bid_no})


def mg_add_book_avail(db, books_avail: Dict):
    db_books_avail = db.books_avail
    if db_books_avail.find_one(books_avail):
        return ("The record already exist")
    else:
        return db.books_avail.insert_one(books_avail)


def mg_add_entire_book_avail(db, books_avail: List[Dict]):
    db_books_avail = db.books_avail
    if db_books_avail.find_one(books_avail):
        return ("The record already exist")
    else:
        return db.books_avail.insert_many(books_avail)


def mg_add_book_info(db, books_info_input: Dict):
    db_books_info = db.books_info
    if db_books_info.find_one(books_info_input):
        return ("The record already exist")
    else:
        return db.books_info.insert_one(books_info_input)


def mg_insert_status(db, username: str):
    return db.user_status.insert_one({'UserName': username, "status": True})


def mg_delete_status(db, username: str):
    return db.user_status.delete_many({'UserName': username})


def mg_query_status(db, username: str):
    return db.user_status.find_one({"UserName": username})


def mg_update_user_info(db, username: str, dict_values_to_add: Dict):
    """ Update user info """

    new_dict = {"UserName": username}
    new_dict.update(dict_values_to_add)

    newvalues = {"$set": new_dict}

    db['users'].update_one({"UserName": username}, newvalues)
    return f"Tracked {dict_values_to_add} for {username}"


# Deletes
def mg_delete_bk_avail_records(db, bid_no):
    return db.books_avail.delete_many({'BID': bid_no})


def mg_delete_bk_info_records(db, bid_no):
    """ When multiple users use the app,
        I don't think I need / want to delete this.
        This can be kept, but future inserts will
        need to account for such a variable.
    """
    return db.books_info.delete_one({'BID': bid_no})


def mg_delete_bk_user_records(db, bid_no, username):
    return db.user_books.delete_many({'UserName': username, 'BID': bid_no})


def mg_delete_user(db, username):
    return db.users.delete_one({'UserName': username})


# Queries
def mg_query_book_title_by_bid(db, bid_no):

    return db.books_info.find_one({"BID": str(bid_no)}).get("TitleName")


def mg_query_user_books_w_bid(db, username: str):
    """ To delete books at scale """
    output = []
    for i in db['user_books'].find({"UserName": username},
                                   {"_id": 0, "user_book_id": 0}):
        output.append(i)
    return output


def mg_query_user_by_username(db, username: str):
    """ Return user username and password from mongo DB """
    return db['users'].find_one({"UserName": username}, {"_id": 0})


def mg_query_user_info(db, username: str):
    """ Return user username and password from mongo DB """
    return db['users'].find_one({"UserName": username},
                                {"_id": 0, "HashedPassword": 0})


def mg_query_user_bookmarked_books(db, username: str):
    """ query_user_bookmarked_books """
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
            "BranchName": "$books_avail.BranchName",
            "CallNumber": "$books_avail.CallNumber",
            "StatusDesc": "$books_avail.StatusDesc",
            "DueDate": "$books_avail.DueDate",
            "InsertTime": "$books_avail.InsertTime",
            "BID": "$books_info.BID"
        }},
    ])

    return [i for i in books_avail_users]


def mg_query_user_books(db, username: str):
    user_books = db.user_books.aggregate([
        # connect all tables

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
        }},
    ])

    return [i for i in user_books]


def get_user_saved_books(db, username: str):
    """ Query books that a user saved from MongoDB"""

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
            "BID": "$books_info.BID"
        }}
    ])

    return list({dic['TitleName']: dic for dic in output}.values())


# Query NLB library events
def get_lib_events(db, library: str):
    """ Refactor query logic to focus on the library events that I need

    Note: Events datetime format are "%Y-%m-%dT%H:%M:%S"

    """
    today = datetime.today()
    output = db.lib_events.aggregate([{
        '$addFields': {
            'new_date': {
                '$dateFromString': {
                    'dateString': '$end',
                    'format': '%Y-%m-%dT%H:%M:%S'
                }},
            "end_date": {"$arrayElemAt": [{"$split": ["$end", "T"]}, 0]},
            "start_time": {"$arrayElemAt": [{"$split": ["$start", "T"]}, 1]},
            "end_time": {"$arrayElemAt": [{"$split": ["$end", "T"]}, 1]}
        }},
        {
            '$match': {
                'new_date': {'$gte': today},
                "lib_filter": library,
                "available": True

            }
    },
        {"$project": {
            "_id": 0,
            "end_day": "$end_day",
            "end_date": "$end_date",
            "start_time": "$start_time",
            "end_time": "$end_time",
            "category": "$category",
            "url": "$url",
            "name": "$name"
        }},
    ])

    return [i for i in output]


# EventTracking
def mg_event_tracking(db, table, username: str, event_name: str):
    """ Tracks the timestamp of an event"""
    login_time = time.mktime(datetime.now().timetuple())
    newvalues = {"$set": {"UserName": username,
                          event_name: login_time}}

    db[table].update_one({"UserName": username}, newvalues)
    return f"Tracked {event_name} in {table} for {username}"


def mg_user_search_tracking(db, table, username: str, search_params: Dict):
    """ Tracks user search on title and / or author """

    search_time = time.mktime(datetime.now().timetuple())
    values_to_insert = {"UserName": username, "search_time": search_time}
    values_to_insert.update(search_params)

    db[table].insert_one(values_to_insert)

    return "Search Tracking done"
