from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse


from src.api.deps import SDBDep, MDBDep, UsernameDep
from src import supa_db as s_db
from src import m_db
from src import process as p
from src.utils import templates


router = APIRouter()


@router.get("", response_class=HTMLResponse)
async def user_profile(
    request: Request, db: SDBDep, mdb: MDBDep, username: UsernameDep
):
    if not username:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    query = s_db.q_user_bks(username=username)
    response = p.process_user_bks(query)
    unique_libs = p.get_unique_libs(response)
    update_status = None
    if m_db.q_status(db=mdb.nlb, username=username):
        update_status = " "

    # Query user profile info from database
    user_info = s_db.q_user_info(db, username)
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "username": username,
            "email_address": user_info.get("email_address", None),
            "preferred_lib": user_info.get("preferred_lib", None),
            "pw_qn": user_info.get("pw_qn", None),
            "pw_ans": user_info.get("pw_ans", None),
            "all_unique_lib": unique_libs,
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
    new_dict = {
        "email_address": email_address,
        "preferred_lib": preferred_lib,
        "pw_qn": pw_qn,
        "pw_ans": pw_ans,
    }

    s_db.update_user_info(db, username, new_dict)
    return RedirectResponse("/user/", status_code=status.HTTP_302_FOUND)


@router.delete("", response_class=HTMLResponse)
async def delete_user(db: SDBDep, username: UsernameDep):
    if not username:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    s_db.delete_user(db, username=username)
    # TODO: Remove all books belongs to user

    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
