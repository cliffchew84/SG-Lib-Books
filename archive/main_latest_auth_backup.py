from fastapi import (
    FastAPI,
    status,
    Request,
    Form,
    Depends,
    BackgroundTasks,
    HTTPException,
    Response,
    Cookie,
)
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from supabase import create_client, Client

from urllib.parse import urlencode
from jose import JWTError, jwt
from dotenv import load_dotenv
import httpx

load_dotenv()
import os

from datetime import timedelta, datetime
from typing import Optional
import urllib.parse
import pendulum
import time
import re

import supa_db as s_db
import nlb_api as n_api
import process as p

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Environment setup
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_SECRET = os.getenv("GOOGLE_SECRET")
SECRET_KEY = os.getenv("SUPABASE_JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Application code
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_db():
    return s_db.connect_sdb()


# Dependency to check for access token in cookies
async def get_current_user(access_token: str = Cookie(None)):
    if access_token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return access_token  # Return the access token


# Utility function to get JWT from headers
def get_token_from_header(request: Request):
    token = request.cookies.get("access_token")
    print(token)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing access token"
        )
    return token


# Function to decode and verify JWT token
def verify_token(token: str):
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")  # Get user ID from the token
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )


@app.get("/login-google")
async def login():
    try:
        # Construct the Google OAuth URL for Authorization Code Flow
        params = {
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": "http://localhost:8000/auth/callback",
            "response_type": "code",
            "scope": "openid email profile",  # Add other scopes as needed
            "prompt": "select_account",  # Forces Google login screen
        }
        google_auth_url = (
            f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"
        )

        # Redirect the user to the Google login page
        return RedirectResponse(google_auth_url)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error initiating Google OAuth: {str(e)}"
        )


@app.get("/auth/callback")
async def auth_callback(code: str, response: Response):
    try:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_SECRET,
                    "redirect_uri": "http://localhost:8000/auth/callback",
                    "grant_type": "authorization_code",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        tokens = token_response.json()
        access_token = tokens.get("access_token")

        if not access_token:
            raise HTTPException(status_code=400, detail="Access token not received")

        # Set the access token in a cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # Set to True if using HTTPS in production
            domain="localhost",  # Ensure correct domain
            path="/",  # Make sure it's available for the whole app
            samesite="lax",
        )

        # Redirect to the protected route
        return RedirectResponse(
            url="/protected-route", status_code=303, headers=response.headers
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error in OAuth callback: {str(e)}"
        )


# Protected Route
@app.get("/protected-route", response_class=HTMLResponse)
async def protected_route(request: Request, access_token: str = Cookie(None)):
    # Test if I can get supbase user info
    async with httpx.AsyncClient() as client:
        user_info_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    user_info = user_info_response.json()
    if user_info is None:
        raise HTTPException(status_code=401, detail="Could not retrieve user info")

    db = s_db.connect_sdb()
    username = s_db.q_username_by_email(db, user_info.get("email"))

    query = s_db.q_user_bks(username)
    response = p.process_user_bks(query)

    # Processing necessary statistics
    all_unique_books = p.get_unique_bks(response)
    all_avail_books = p.get_avail_bks(response)
    unique_libs = p.get_unique_libs(response)
    avail_bks_by_lib = p.get_avail_bks_by_lib(response)
    lib_book_summary = p.get_lib_bk_summary(unique_libs, avail_bks_by_lib)

    update_status = None
    if s_db.q_status(db=db, username=username):
        update_status = "Updating In Progress!"

    # Check if user has a default library
    user_info = s_db.q_user_info(db, username)
    preferred_lib = user_info.get("preferred_lib")

    if preferred_lib:
        preferred_lib = preferred_lib.lower()
        output = []
        for book in response:
            if preferred_lib in book["BranchName"].lower():
                output.append(book)
    else:
        preferred_lib = "all"
        output = response

    lib_avail = len(p.get_avail_bks(output))
    lib_all = len(p.get_unique_bks(output))

    return templates.TemplateResponse(
        "main.html",
        {
            "request": request,
            "username": username,
            "api_data": output,
            "all_avail_books": all_avail_books,
            "all_unique_books": all_unique_books,
            "avail_books": avail_bks_by_lib,
            "lib_book_summary": lib_book_summary,
            "lib_avail": lib_avail,
            "lib_all": lib_all,
            "library": preferred_lib,
            "status": update_status,
        },
    )


# Main Page
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("google_page.html", {"request": request})


# Logout route to remove the JWT token
@app.get("/logout")
def logout():
    response = RedirectResponse("/")
    response.delete_cookie("access_token")
    return response
