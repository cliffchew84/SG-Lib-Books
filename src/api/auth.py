from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import RedirectResponse

import httpx
from urllib.parse import urlencode

from src.api.deps import SDBDep
from src import supa_db as s_db
from src.config import settings

router = APIRouter()


@router.get("/login-google")
async def login():
    try:
        # Construct the Google OAuth URL for Authorization Code Flow
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
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


@router.get("/callback")
async def auth_callback(code: str, response: Response, db: SDBDep):
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    access_token = token_response.json().get("access_token")

    if not access_token:
        raise HTTPException(status_code=400, detail="Access token not received")

    # Retrieve user email from google userinfo API
    async with httpx.AsyncClient() as client:
        user_info_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    user_email = user_info_response.json().get("email")
    if not user_email:
        raise HTTPException(status_code=401, detail="Could not retrieve user info")

    try:
        username = s_db.q_username_by_email(db, user_email)
    except Exception:
        # Sign-Up User as not found in Supabase
        # TODO: Implement proper auth-signup with supabase
        # https://supabase.com/docs/reference/python/auth-signup
        username = user_email
        db.table("users").insert(
            {
                "UserName": username,
                "HashedPassword": "ThisIsGoogleLogin",
                "email_address": username,
            }
        ).execute()

    user_info = user_email + " | " + username

    # Set the access token in a cookie
    response.set_cookie(
        key="user_info",
        value=user_info,
        httponly=True,
        secure=True,  # Set to True if using HTTPS in production
        domain=(
            "localhost"
            if "localhost" in settings.GOOGLE_REDIRECT_URI
            else "sg-nlb-available-books.onrender.com"
        ),
        path="/",  # Make sure it's available for the whole app
        samesite="lax",
        # samesite="none"
    )

    # Redirect to the protected route
    return RedirectResponse(url="/main", status_code=303, headers=response.headers)
