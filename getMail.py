# gmail_list.py
from googleapiclient.discovery import build
from auth import get_creds

# Read-only scope to start safely; switch to modify/send scopes when needed
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def getMail(max_results=10):
    creds = get_creds(SCOPES)
    service = build("gmail", "v1", credentials=creds)
    results = service.users().messages().list(
        userId="me", labelIds=["INBOX"], maxResults=max_results
    ).execute()
    messages = results.get("messages", [])
    items = []
    for m in messages:
        msg = service.users().messages().get(
            userId="me",
            id=m["id"],
            format="metadata",
            metadataHeaders=["Subject","From"]
        ).execute()
        headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
        items.append({
            "from": headers.get("From",""),
            "subject": headers.get("Subject",""),
            "id": m["id"],
        })
    return items

if __name__ == "__main__":
    getMail()
