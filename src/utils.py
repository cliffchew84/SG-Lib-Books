from fastapi.templating import Jinja2Templates

# Jinja2 Templates
templates = Jinja2Templates(directory="templates")


# TODO: Remove this as used in deps instead
def username_email_resol(user_info: str):
    """In the current new flow, username == email
    To cover legacy situation where username != email
    """
    email, username = user_info.split(" | ")
    if not username:
        username = email
    return username
