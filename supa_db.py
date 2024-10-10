import os
import time
import psycopg2
import psycopg2.extras
from typing import Dict, List
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv()

# This script uses supabase to handle internal data operations, and is a
# migration from MongoDB. I still need to figure out how to handle NLB API side
# issues...
# The 3 tables of user_books, books_info and books_avail remain the same

# Supabase credentials
DB_HOST = os.environ.get("SUPA_DB_HOST") 
DB_PORT = os.environ.get("SUPA_DB_PORT") 
DB_NAME = os.environ.get("SUPA_DB_NAME")
DB_USER = os.environ.get("SUPA_DB_USER")
DB_PASSWORD = os.environ.get("SUPA_DB_PASSWORD")
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def connect_sdb():
    supabase: Client = create_client(url, key)
    return supabase 

# Add Methods
def add_user(db, username: str, hashed_pw: str):
    return db.table('users').insert({
        "UserName": username,
        "HashedPassword": hashed_pw
    }).execute()


def add_user_book(db, username: str, bid_no):
    return db.table("user_books").insert({
        'UserName': username, "BID": bid_no
    }).execute()


def add_avail_bks(db, books_avail: List[Dict]):
    return db.table("books_avail").insert(books_avail).execute()


def add_book_info(db, books_info: Dict):
    return db.table("books_info").insert(books_info).execute()


def insert_status(db, username: str):
    return db.table("user_status").insert({
        "UserName": username, 'status': True}).execute()


def delete_status(db, username: str):
    return db.table('user_status').delete().eq('UserName', username).execute()


def q_status(db, username: str):
    user_d = db.table('user_status').select("status").eq(
        'UserName', username).execute().data

    user = {}
    for d in user_d:
        user.update(d)
    return user


def update_user_info(db, username: str, values_to_add: Dict):
    """ Update user info """
    db.table("users").update(values_to_add).eq("UserName", username).execute()
    return f"Tracked {values_to_add} for {username}"


# Deletes
def delete_bk_avail(db, bid_no):
    return db.table('books_avail').delete().eq('BID', bid_no).execute()


def delete_bk_info(db, bid_no):
    return db.table('books_info').delete().eq('BID', bid_no).execute()


def delete_user_bk(db, bid_no, username: str):
    return db.table('user_books').delete().eq(
        "UserName", username).eq(
        'BID', bid_no).execute()


def delete_user(db, username: str):
    return db.table('users').delete().eq('UserName', username).execute()


# Queries
def q_username_by_email(db, email: str) -> str:
    """ Extract UserName using ( Google ) auth email """
    return db.table("users").select("UserName").eq(
        "email_address", email).execute().data[0].get("UserName")


def q_user_bks_bids(db, username: str):
    """ To extract a list of user saved books BIDs """
    return db.table("user_books").select("BID").eq(
        "UserName", username).execute().data


def q_user_bks(db, username: str):
    """ To extract a list of user saved books BIDs """
    return db.table("user_books").select("BID").eq(
        "UserName", username).execute().data


def q_username(db, username: str):
    """ Return user information from Supabase 
        Note that I have to convert List[Dict] output into a Dict
    """
    user_d = db.table("users").select("*").eq(
        "UserName", username).execute().data
    user = {}
    for d in user_d:
        user.update(d)
    return user


def q_user_info(db, username: str):
    """ Return user username and password from mongo DB """

    user_prop = ["UserName", "latest_login", "email_address", "preferred_lib",
                 "pw_ans", "pw_qn", "books_updated", "registered_time"]

    user_d = db.table("users").select(", ".join(user_prop)).eq(
        "UserName", username).execute().data

    user = {}
    for d in user_d:
        user.update(d)

    return user


def pg_query(query: str):
    """ Performs complex SQL queries on Supabase PostgreSQL"""
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = connection.cursor(
            cursor_factory = psycopg2.extras.RealDictCursor)

        # Example of executing an SQL query
        cursor.execute(query)
        rows = cursor.fetchall()
        output = list()
        for row in rows:
            output.append(dict(row))
        print("Query was successful")

    except Exception as e:
        print(f"Error connecting to the database: {e}")

    finally:
        # Close the connection
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection closed.")
    return output


full_query = """
WITH user_bks AS (
    SELECT 
        ub."UserName",
        ub."BID"
    FROM user_books AS ub
    WHERE "UserName" = '{username}'
), bks_info AS (
    SELECT * 
    FROM books_info
    RIGHT JOIN user_bks
    USING ("BID")
)
SELECT 
    bi."TitleName",
    bi."Author",
    ba."BranchName",
    ba."CallNumber",
    ba."StatusDesc",
    ba."DueDate",
    ba."InsertTime",
    CAST(bi."BID" AS TEXT) AS "BID",
    bi."Subjects",
    bi."Publisher",
    bi."isbns"
FROM books_avail AS ba
INNER JOIN bks_info AS bi
USING ("BID")
"""

def q_user_bks(username: str, query: str=full_query):
    return pg_query(query.format(username=username))


subset_query = """
WITH user_bks AS (
    SELECT 
        ub."UserName",
        ub."BID"
    FROM user_books AS ub
    WHERE "UserName" = '{username}'
), bks_info AS (
    SELECT * 
    FROM books_info
    RIGHT JOIN user_bks
    USING ("BID")
)
SELECT DISTINCT 
    ba."CallNumber",
    bi."TitleName",
    bi."Author",
    CAST(bi."BID" AS TEXT) AS "BID",
    bi."Subjects",
    bi."Publisher",
    bi."isbns"
FROM books_avail AS ba
RIGHT JOIN bks_info AS bi
USING ("BID")
"""


def q_user_bks_subset(username: str, query: str=subset_query):
    return pg_query(query.format(username=username))


smallest_set_query = """
WITH user_bks AS (
    SELECT 
        ub."UserName",
        ub."BID"
    FROM user_books AS ub
    WHERE "UserName" = '{username}'
), bks_info AS (
    SELECT * 
    FROM books_info
    RIGHT JOIN user_bks
    USING ("BID")
)
SELECT DISTINCT 
    bi."TitleName",
    CAST(bi."BID" AS TEXT) AS "BID"
FROM books_avail AS ba
RIGHT JOIN bks_info AS bi
USING ("BID")
"""


def q_user_bks_info(username: str, query: str=smallest_set_query):
    return pg_query(query.format(username=username))


bid_counter_query = """
SELECT COUNT("BID")
FROM user_books AS ub
WHERE ub."BID" = {bid}
"""

def q_bid_counter(bid_no: int, query: str=bid_counter_query):
    return pg_query(query.format(bid=str(bid_no)))[0].get("count")


# EventTracking
def event_tracking(db, table_name, username: str, event_name: str):
    """ Tracks the timestamp of an event"""
    login_time = int(time.mktime(datetime.now().timetuple()))
    newvalues = {event_name: login_time}
    db.table(table_name).update(newvalues).eq("UserName", username).execute()

    return f"Tracked {event_name} in {table_name} for {username}"


def user_search_tracking(db, table_name, username: str, search_params: Dict):
    """ Tracks user search on title and / or author """
    search_time = int(time.mktime(datetime.now().timetuple()))
    values_to_insert = {"UserName": username, "search_time": search_time}
    values_to_insert.update(search_params)
    print(values_to_insert)
    db.table(table_name).insert(values_to_insert).execute()

    return "Search Tracking done"
