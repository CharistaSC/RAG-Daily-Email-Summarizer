# auth.py
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Ask for everything you expect to need (superset)
SCOPES_ALL = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]

def get_creds(scopes=None, client_secret_file="add your client file dir here", token_file="token.json"):
    # default to the wide set if none provided
    if scopes is None:
        scopes = SCOPES_ALL

    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)
            # first time only: opens browser, stores refresh token
            creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
        with open(token_file, "w") as f:
            f.write(creds.to_json())
    return creds

if __name__ == "__main__":
    _ = get_creds(SCOPES_ALL)
    print("All scopes granted and cached in token.json.")
