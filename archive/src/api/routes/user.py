from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse


from src import m_db
from src.api.deps import SDBDep, MDBDep, UsernameDep
from src.crud.users import user_crud
from src.crud.book_avail import book_avail_crud
from src.crud.book_info import book_info_crud
from src.modals.book_response import BookResponse
from src.modals.users import UserUpdate
from src.utils import templates


router = APIRouter()


@router.get("", response_class=HTMLResponse)
async def user_profile(
    request: Request, db: SDBDep, mdb: MDBDep, username: UsernameDep
):
    if not username:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    # Retrieve user_info if available
    user_info = await user_crud.get(db, i=username)
    if not user_info:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    book_infos = await book_info_crud.get_multi_by_owner(db, username=username)
    book_avails = await book_avail_crud.get_multi_by_owner(
        db, username=username, BIDs=[book_info.BID for book_info in book_infos]
    )
    book_response = BookResponse(book_infos=book_infos, book_avails=book_avails)

    update_status = None
    if m_db.q_status(db=mdb.nlb, username=username):
        update_status = " "

    # Query user profile info from database
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "username": username,
            "email_address": user_info.email_address,
            "preferred_lib": user_info.preferred_lib,
            "pw_qn": user_info.pw_qn,
            "pw_ans": user_info.pw_ans,
            "all_unique_lib": book_response.all_unique_libs,
            "status": update_status,
        },
    )


@router.post("", response_class=HTMLResponse)
async def update_user(
    db: SDBDep,
    username: UsernameDep,
    email_address: str = Form(None),
    preferred_lib: str = Form(None),
    pw_qn: str = Form(None),
    pw_ans: str = Form(None),
    password: str = Form(None),
):
    if not username:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    # Update info
    await user_crud.update(
        db,
        i=username,
        obj_in=UserUpdate(
            UserName=username,
            email_address=email_address,
            preferred_lib=preferred_lib,
            pw_qn=pw_qn,
            pw_ans=pw_ans,
        ),
    )

    return RedirectResponse("/user/", status_code=status.HTTP_302_FOUND)


@router.delete("", response_class=HTMLResponse)
async def delete_user(db: SDBDep, username: UsernameDep):
    if not username:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    await user_crud.delete(db, i=username)
    # TODO: Remove all books belongs to user

    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
