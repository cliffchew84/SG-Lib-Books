from pymongo import mongo_client
from typing import Dict, List
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
