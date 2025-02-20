from mailersend import emails
from src.modals.email_items import EmailItems

# Email template generated from ./maizzle
TEMPLATE = """
<!DOCTYPE html>
<html lang="en" xmlns:v="urn:schemas-microsoft-com:vml" style="font-family: InterVariable,Roboto,system-ui,ui-sans-serif,system-ui,sans-serif,'Apple Color Emoji','Segoe UI Emoji',Segoe UI Symbol,'Noto Color Emoji'">
<head>
  <meta charset="utf-8">
  <meta name="x-apple-disable-message-reformatting">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="format-detection" content="telephone=no, date=no, address=no, email=no, url=no">
  <meta name="color-scheme" content="light dark">
  <meta name="supported-color-schemes" content="light dark">
  <!--[if mso]>
  <noscript>
    <xml>
      <o:OfficeDocumentSettings xmlns:o="urn:schemas-microsoft-com:office:office">
        <o:PixelsPerInch>96</o:PixelsPerInch>
      </o:OfficeDocumentSettings>
    </xml>
  </noscript>
  <style>
    td,th,div,p,a,h1,h2,h3,h4,h5,h6 {{font-family: "Segoe UI", sans-serif; mso-line-height-rule: exactly;}}
    .mso-break-all {{word-break: break-all;}}
  </style>
  <![endif]-->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet" media="screen">
  <style>
    .hover-bg-slate-800:hover {{
      background-color: #1e293b !important
    }}
    @media (max-width: 600px) {{
      .sm-p-6 {{
        padding: 24px !important
      }}
      .sm-px-4 {{
        padding-left: 16px !important;
        padding-right: 16px !important
      }}
      .sm-px-6 {{
        padding-left: 24px !important;
        padding-right: 24px !important
      }}
    }}
  </style>
</head>
<body style="margin: 0; width: 100%; background-color: #f8fafc; padding: 0; -webkit-font-smoothing: antialiased; word-break: break-word">
  <div style="display: none">
    Daily Book Updates
    &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847; &#8199;&#65279;&#847;
  </div>
  <div role="article" aria-roledescription="email" aria-label lang="en">
    <div class="sm-px-4" style="background-color: #f8fafc; font-family: Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif">
      <table align="center" style="margin: 0 auto" cellpadding="0" cellspacing="0" role="none">
        <tr>
          <td style="width: 552px; max-width: 100%">
            <div role="separator" style="line-height: 24px">&zwj;</div>
            <table style="width: 100%" cellpadding="0" cellspacing="0" role="none">
              <tr>
                <td class="sm-p-6" style="border-radius: 8px; background-color: #fffffe; padding: 24px 36px; border: 1px solid #e2e8f0">
                  <a href="https://sg-lib-books.web.app/" style="font-size: 20px; letter-spacing: -0.025em; color: #0f172a; text-decoration: none">
                    SG Lib Books
                  </a>
                  <div role="separator" style="line-height: 24px">&zwj;</div>
                  <h1 style="margin: 0 0 24px; font-size: 24px; line-height: 32px; font-weight: 600; color: #1e293b">
                    Daily Book Arrivals
                  </h1>
                  <p style="margin: 0 0 24px; font-size: 16px; line-height: 24px; color: #475569">
                    The following books are now available to be borrowed! Do check them out before they are gone!
                  </p>
                  <table style="width: 100%" cellpadding="0" cellspacing="0" role="none">
                  {table_rows}
                  </table>
                  <div role="separator" style="line-height: 24px">&zwj;</div>
                  <div style="text-align: center">
                    <a href="https://sg-lib-books.web.app/dashboard" style="display: inline-block; text-decoration: none; padding: 16px 24px; font-size: 16px; line-height: 1; border-radius: 4px; color: #fffffe; margin-left: auto; margin-right: auto; background-color: #020617" class="hover-bg-slate-800">
                      <!--[if mso]><i style="mso-font-width: 150%; mso-text-raise: 31px" hidden>&emsp;</i><![endif]-->
                      <span style="mso-text-raise: 16px">Checkout More Books</span>
                      <!--[if mso]><i hidden style="mso-font-width: 150%">&emsp;&#8203;</i><![endif]-->
                    </a>
                  </div>
                  <div role="separator" style="height: 1px; line-height: 1px; background-color: #cbd5e1; margin-top: 24px; margin-bottom: 24px">&zwj;</div>
                  <p class="mso-break-all" style="margin: 0; font-size: 12px; line-height: 20px; color: #475569">
                    This message was sent to wongzhaowu@gmail.com. Please remember you can always go to your <a href="https://sg-lib-books.web.app/dashboard/settings" style="color: #0f172a">Account Settings</a> page to adjust your account and contact info, privacy controls and email preferences.
                  </p>
                </td>
              </tr>
            </table>
            <table style="width: 100%" cellpadding="0" cellspacing="0" role="none">
              <tr>
                <td class="sm-px-6" style="padding: 24px 36px">
                  <p style="margin: 0; font-size: 12px; color: #64748b">
                    &copy; 2025 SG Lib Books . All rights reserved.
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </div>
  </div>
</body>
</html>
"""

TABLE_ROW_TEMPLATE = """
                    <tr style="border-radius: 8px; border-color: #94a3b8; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)">
                      <td style="width: 150px; padding: 24px">
                        <a href="{url}">
                          <img src="{cover_url}" alt="{TitleName}" style="max-width: 100%; vertical-align: middle; border-radius: 8px">
                        </a>
                      </td>
                      <td style="padding-top: 24px; padding-bottom: 24px; padding-right: 12px; font-size: 14px">
                        <a href="{url}" <h3 style="margin-bottom: 12px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 18px; font-weight: 600; color: #334155">{TitleNameShort} </a>
                        <p style="font-size: 14px; color: #64748b">By {Author}</p>
                        <p style="font-size: 14px; color: #64748b">Available at:</p>
                        <ul style="color: #64748b">
                        {library_rows}
                        </ul>
                      </td>
                    </tr>
"""

LIBRARY_TEMPLATE = """
                          <li style="margin-top: 4px; margin-bottom: 0">{BranchName}</li>
"""


class Mailer:
    def __init__(self, api_key: str, sender_email: str, sender_name: str):
        self.mailer = emails.NewEmail(api_key)
        self.sender_email = sender_email
        self.sender_name = sender_name

    def format_email_content(self, items: list[EmailItems]) -> str:
        """Format the email content based on the list of EmailItems."""
        table_rows = []
        for item in items:
            table_rows.append(
                TABLE_ROW_TEMPLATE.format(
                    TitleNameShort=item.TitleName[:30] + "..."
                    if item.TitleName and len(item.TitleName) > 30
                    else item.TitleName,
                    library_rows="".join(
                        LIBRARY_TEMPLATE.format(BranchName=branch)
                        for branch in item.BranchName
                    ),
                    **item.model_dump(),
                )
            )
        return TEMPLATE.format(table_rows="".join(table_rows))

    def send_daily_email(
        self, recipient_email: str, recipient_name: str, items: list[EmailItems]
    ):
        """Send an email to the given recipient with the list of EmailItems."""
        mail_body = {}

        mail_from = {
            "name": self.sender_name,
            "email": self.sender_email,
        }

        recipients = [
            {
                "name": recipient_name,
                "email": recipient_email,
            }
        ]

        self.mailer.set_mail_from(mail_from, mail_body)
        self.mailer.set_mail_to(recipients, mail_body)
        self.mailer.set_subject("Daily Book Arrivals", mail_body)
        self.mailer.set_html_content(self.format_email_content(items), mail_body)
        self.mailer.set_plaintext_content(
            "New books are available. Check your email for details.", mail_body
        )
        print(mail_body)

        return self.mailer.send(mail_body)
