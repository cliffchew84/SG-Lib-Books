import os
import pendulum
from mixpanel import Mixpanel
from ua_parser import user_agent_parser


# Load environment variables
project_id = os.environ["MP_PROJECT_ID"]
mp = Mixpanel(project_id) 


def get_sg_now_time():
    # return pendulum.now(tz='Asia/Singapore').strftime("%Y-%m-%d %H:%M")
    return pendulum.now(tz='Asia/Singapore') - pendulum.Duration(hours=8)

# User Profile functions
def user_register(user_id, mp=mp):
    register_time = get_sg_now_time()
    return mp.people_set(user_id, {"$name": user_id, "Registered Time": register_time})


def user_login(user_id, mp=mp):
    login_time = get_sg_now_time()
    mp.people_set(user_id, {"$name": user_id, "Latest Login": login_time})
    return login_time


def user_change_book_count(user_id, book_change, mp=mp):
    # Note that count is on BID instead of TitleName
    return mp.people_increment(user_id, {"Book Count": book_change})


def user_book_list_add(user_id, book_change_list, mp=mp):
    # Note that count is on BID instead of TitleName
    return mp.people_union(user_id, {"Book List": book_change_list})


def user_book_list_remove(user_id, book_change_list, mp=mp):
    # Note that count is on BID instead of TitleName
    return mp.people_remove(user_id, {"Book List": book_change_list})


# Event functions
def event_register(user_id, mp=mp):
    mp.track(user_id, 'Register', {})


def event_login(user_id, mp=mp):
    mp.track(user_id, 'Login', {})


def event_select_library(user_id, library, mp=mp):
    mp.track(user_id, 'Select Library', {
        'BranchName': library
        })


def event_update_book(user_id, bid, mp=mp):
    mp.track(user_id, 'Update Book', { 'BID': bid,})


def event_search_book(user_id, keyword, mp=mp):
    mp.track(user_id, 'Search Book', { 'Keyword': keyword })


def event_add_book(user_id, bid, mp=mp):
    mp.track(user_id, 'Add Book', { 'BID': bid })


def event_select_current_saved_book(user_id, mp=mp):
    mp.track(user_id, 'View Saved Books', {})


def event_delete_book(user_id, bid, mp=mp):
    mp.track(user_id, 'Delete Book', { 'BID': bid })
