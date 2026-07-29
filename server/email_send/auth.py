# gmail_auth.py

import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

BASE_DIR = Path(__file__).resolve().parent

CREDENTIALS_FILE = BASE_DIR / "credentials.json"

# Separate token file so Calendar is untouched
TOKEN_FILE = BASE_DIR / "gmail_token.json"

# Gmail-only scope
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]


def get_credentials():
    creds = None
    print("inside credentials")

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(
            str(TOKEN_FILE),
            SCOPES
        )
    print("working")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE),
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())

    return creds


if __name__ == "__main__":
    get_credentials()
    print("✅ Gmail authentication successful.")