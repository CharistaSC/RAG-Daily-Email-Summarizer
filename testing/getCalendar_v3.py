# calendar_list.py
import csv
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from googleapiclient.discovery import build
from auth import get_creds

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
LOCAL_TZ = ZoneInfo("Asia/Singapore")

def _window():

    now_local = datetime.now(LOCAL_TZ)
    start_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    end_local   = start_local + timedelta(days=30)

    start_utc_iso = start_local.astimezone(timezone.utc).isoformat()
    end_utc_iso   = end_local.astimezone(timezone.utc).isoformat()
    return start_utc_iso, end_utc_iso

def _parse_dt(value: str) -> datetime:
    """Robust ISO parser that also handles trailing 'Z'."""
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)

def _start_end_local_utc(ev: dict):
    """
    Returns: (start_local_str, end_local_str, start_utc_str, end_utc_str, all_day)
    - For all-day events (date), we treat start at 00:00 local and end at 00:00 next day local.
    """
    s = ev.get("start", {}) or {}
    e = ev.get("end", {}) or {}

    if "date" in s:  # all-day
        all_day = True
        s_local = datetime.fromisoformat(s["date"]).replace(tzinfo=LOCAL_TZ)
        e_local = datetime.fromisoformat(e["date"]).replace(tzinfo=LOCAL_TZ)
    else:  # dateTime
        all_day = False
        s_dt = _parse_dt(s["dateTime"])
        e_dt = _parse_dt(e["dateTime"])
        # Respect any per-event timeZone if present; otherwise assume the dt carries tzinfo.

        s_local = s_dt.astimezone(LOCAL_TZ)
        e_local = e_dt.astimezone(LOCAL_TZ)

    s_utc = s_local.astimezone(timezone.utc)
    e_utc = e_local.astimezone(timezone.utc)

    fmt_local = "%Y-%m-%d %H:%M:%S%z"
    fmt_utc   = "%Y-%m-%d %H:%M:%S%z"
    return (
        s_local.strftime(fmt_local),
        e_local.strftime(fmt_local),
        s_utc.strftime(fmt_utc),
        e_utc.strftime(fmt_utc),
        all_day,
    )

def _my_response(ev: dict) -> str:
    """Return your attendee responseStatus if present (accepted/tentative/declined/needsAction)."""
    for at in ev.get("attendees", []) or []:
        if at.get("self"):
            return at.get("responseStatus", "")
    return ""

def _flatten_event(ev: dict) -> dict:
    s_local, e_local, s_utc, e_utc, all_day = _start_end_local_utc(ev)
    attendees = ev.get("attendees", []) or []
    organizer = (ev.get("organizer") or {}).get("email", "")
    location  = ev.get("location", "")
    hangout   = ev.get("hangoutLink", "")
    my_resp   = _my_response(ev)

    return {
        "id": ev.get("id",""),
        "status": ev.get("status",""),
        "summary": ev.get("summary",""),
        "start_local": s_local,
        "end_local": e_local,
        "start_utc": s_utc,
        "end_utc": e_utc,
        "all_day": str(all_day),
        "location": location,
        "organizer_email": organizer,
        "attendees_count": len(attendees),
        "my_response": my_resp,
        "htmlLink": ev.get("htmlLink",""),
        "recurringEventId": ev.get("recurringEventId",""),
        "originalStartTime": (ev.get("originalStartTime") or {}).get("dateTime", "") or (ev.get("originalStartTime") or {}).get("date", ""),
        "conferenceData_confLink": hangout,
    }

def getCalendar(max_results: int = 100, csv_path: str = "user_data\calendar_events.csv"):
    """
    Fetch events into the given window and save as CSV.
    Returns the list of flattened event dicts.
    """
    creds = get_creds(SCOPES)
    service = build("calendar", "v3", credentials=creds)
    tmin, tmax = _window()

    items = []
    page_token = None
    fetched = 0

    while True:
        page_size = min(250, max_results - fetched)  # API allows up to 2500; keep it friendly
        if page_size <= 0:
            break

        resp = service.events().list(
            calendarId="primary",
            timeMin=tmin,
            timeMax=tmax,
            singleEvents=True,
            orderBy="startTime",
            maxResults=page_size,
            pageToken=page_token,
        ).execute()

        for ev in resp.get("items", []):
            if ev.get("status") == "cancelled":
                continue  # skip cancelled
            items.append(_flatten_event(ev))

        fetched += len(resp.get("items", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    # Write CSV
    if items:
        fieldnames = list(items[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(items)

    return items

if __name__ == "__main__":
    rows = getCalendar(max_results=300, csv_path="user_data\calendar_events.csv")
    print(f"Wrote {len(rows)} rows to calendar_events.csv")
