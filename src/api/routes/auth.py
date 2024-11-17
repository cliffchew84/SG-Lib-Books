import logging

import httpx
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import RedirectResponse
from postgrest import APIError
from urllib.parse import urlencode

from src.api.deps import SDBDep
from src.config import settings
from src.crud.users import user_crud
from src.modals.users import UserCreate

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
        user = await user_crud.get_user_by_email(db, email=user_email)
        if user is None:
            # Sign-Up User as not found in Supabase
            # TODO: Implement proper auth-signup with supabase
            # https://supabase.com/docs/reference/python/auth-signup
            new_user = UserCreate(
                UserName=user_email,
                email_address=user_email,
                HashedPassword="ThisIsGoogleLogin",
            )
            user = await user_crud.create(db, obj_in=new_user)
    except APIError as e:
        # Catch error when user has been created
        logging.error("Error in creating new user: ", e)
        raise HTTPException(status_code=400, detail="Could not create new user")
    except Exception as e:
        # Catch general error
        logging.error("Error in creating new user: ", e)
        raise HTTPException(
            status_code=500, detail="Could not retrieve user info or create new user"
        )

    user_info = user.email_address + " | " + user.UserName

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


# Logout route to remove the JWT token
@router.get("/logout")
def logout(
    response: Response,
):
    # response = RedirectResponse("/")
    response.delete_cookie("user_info")
    return RedirectResponse("/", status_code=303, headers=response.headers)
