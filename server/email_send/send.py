from email.message import EmailMessage
from googleapiclient.discovery import build
import base64

from email_send.auth import get_credentials


def send_email(to_email, subject, body):
    creds = get_credentials()

    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    message = EmailMessage()

    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    service.users().messages().send(
        userId="me",
        body={"raw": encoded_message}
    ).execute()

    print(f"Email sent to {to_email}")

