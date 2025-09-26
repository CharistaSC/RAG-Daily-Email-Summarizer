# gmail_list.py
import csv
import time
from googleapiclient.discovery import build
from auth import get_creds

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def _iter_parts(payload):
    """Yield all parts (flattened) including the top payload."""
    if not payload:
        return
    stack = [payload]
    while stack:
        p = stack.pop()
        yield p
        for child in (p.get("parts") or []):
            stack.append(child)

def _looks_like_invite(payload):
    """
    Heuristics:
    - Any part with mimeType 'text/calendar'
    - Any part/attachment with filename ending '.ics'
    """
    has_text_calendar = False
    has_ics_filename = False
    for part in _iter_parts(payload):
        mt = part.get("mimeType", "").lower()
        fn = (part.get("filename") or "").lower()
        if mt == "text/calendar":
            has_text_calendar = True
        if fn.endswith(".ics"):
            has_ics_filename = True
        if has_text_calendar or has_ics_filename:
            return True
    return False

def get_mail(max_results=50, csv_path="user_data\gmail_inbox.csv"):
    """
    Fetch messages from INBOX, label each as 'invite' or 'email',
    and write to CSV: id, threadId, date_utc, from, subject, category.
    """
    creds = get_creds(SCOPES)
    service = build("gmail", "v1", credentials=creds)

    items = []
    page_token = None
    fetched = 0

    while fetched < max_results:
        page_size = min(100, max_results - fetched)  # Gmail max is 500; 100 is polite
        resp = service.users().messages().list(
            userId="me",
            labelIds=["INBOX"],
            maxResults=page_size,
            pageToken=page_token,
        ).execute()
        ids = resp.get("messages", [])
        if not ids:
            break

        for m in ids:
            # Use format='full' so we can inspect MIME parts for invites
            msg = service.users().messages().get(
                userId="me",
                id=m["id"],
                format="full"
            ).execute()

            payload = msg.get("payload", {}) or {}
            headers = {h["name"]: h["value"] for h in payload.get("headers", [])}

            from_ = headers.get("From", "")
            subject = headers.get("Subject", "")
            # internalDate is ms since epoch
            ts_ms = int(msg.get("internalDate", "0"))
            date_utc = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts_ms / 1000)) if ts_ms else ""

            category = "invite" if _looks_like_invite(payload) else "email"

            items.append({
                "id": msg.get("id", ""),
                "threadId": msg.get("threadId", ""),
                "date_utc": date_utc,
                "from": from_,
                "subject": subject,
                "category": category,
            })

        fetched += len(ids)
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    # Write CSV
    fieldnames = ["id", "threadId", "date_utc", "from", "subject", "category"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items)

    return items

if __name__ == "__main__":
    rows = get_mail(max_results=50, csv_path="user_data\gmail_inbox.csv")
    print(f"Wrote {len(rows)} rows to gmail_inbox.csv")
