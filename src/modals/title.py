from pydantic import BaseModel
from pydantic.fields import computed_field

from nlb_catalogue_client.models import Title as NLBTitle


class Title(BaseModel):
    TitleName: str | None
    Author: str | None
    BID: str | None
    DigitalID: str | None
    PublishYear: str | None
    type: str | None
    disabled: bool = False

    @staticmethod
    def from_nlb(title: NLBTitle) -> "Title":
        return Title(
            TitleName=title.title if title.title else None,
            Author=title.author if title.author else None,
            BID=str(title.brn) if title.brn else None,
            DigitalID=title.digital_id if title.digital_id else None,
            PublishYear=title.publish_date if title.publish_date else None,
            type=title.format_.name if title.format_ else None,
        )
