from collections import defaultdict

from fastapi import APIRouter, status, HTTPException

from src.api.deps import SDBDep, CurrentUser, MailerDep
from src.crud.email_items import email_items_crud

router = APIRouter()


@router.post("")
async def send_emails(db: SDBDep, user: CurrentUser, mailer: MailerDep):
    if user != "super":
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "User is not authorized to send emails"
        )

    try:
        email_items = await email_items_crud.get_all(db)
        if not email_items:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, "No new email items to send."
            )

        # Group email items by user email
        email_groups = defaultdict(list)
        for item in email_items:
            email_groups[item.email].append(item)

        # Iterate over each group and send an email
        success = 0
        for email, items in email_groups.items():
            email_status = mailer.send_daily_email(email, email, items)
            if email_status.startswith("202"):
                success += 1

        print(
            "Emails sent success rate: {success} / {total}".format(
                success=success, total=len(email_groups)
            )
        )

    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, f"An error occurred: {str(e)}"
        )
