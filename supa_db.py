import os
import time
import psycopg2
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


def query_user_info(db, username: str):
    """ Return user username and password from mongo DB """
    user_prop = ["UserName", "latest_login", "email_address", "preferred_lib",
                 "pw_ans", "pw_qn", "books_updated", "registered_time"]
    return supabase.table("users").select(", ".join(user_prop)).eq(
        "UserName", "cliffchew84").execute().data


DB_HOST = os.environ.get(SUPA_DB_HOST) 
DB_PORT = os.environ.get(SUPA_DB_PORT) 
DB_NAME = os.environ.get(SUPA_DB_NAME)
DB_USER = os.environ.get(SUPA_DB_USER)
DB_PASSWORD = os.environ.get(SUPA_DB_PASSWORD)

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
        cursor = connection.cursor()

        # Example of executing an SQL query
        cursor.execute(query)
        rows = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
        output = list()
        for row in rows:
            output.append(row)

    except Exception as e:
        print(f"Error connecting to the database: {e}")
    finally:
        # Close the connection
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection closed.")
    return output


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
