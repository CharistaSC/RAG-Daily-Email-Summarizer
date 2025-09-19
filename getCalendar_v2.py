from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from googleapiclient.discovery import build
from auth import get_creds

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
LOCAL_TZ = ZoneInfo("Asia/Singapore")

VALID_MODES = ("today", "2weeks", "2months")

def _window(mode: str):
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be one of {VALID_MODES}")

    now_local = datetime.now(LOCAL_TZ)

    if mode == "today":
        start_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        end_local   = start_local + timedelta(days=1)
    elif mode == "2weeks":
        start_local = now_local
        end_local   = now_local + timedelta(days=14)
    elif mode == "2months":
        start_local = now_local
        end_local   = now_local + timedelta(days=60)

    start_utc_iso = start_local.astimezone(timezone.utc).isoformat()
    end_utc_iso   = end_local.astimezone(timezone.utc).isoformat()
    return start_utc_iso, end_utc_iso

def _fmt_event(ev):
    start = ev["start"].get("dateTime", ev["start"].get("date"))
    end   = ev["end"].get("dateTime", ev["end"].get("date"))
    title = ev.get("summary", "(no title)")
    return start, end, title

def getCalendar(mode: str = "today", max_results: int = 100):
    creds = get_creds(SCOPES)
    service = build("calendar", "v3", credentials=creds)

    tmin, tmax = _window(mode)

    events_result = service.events().list(
        calendarId="primary",
        timeMin=tmin,
        timeMax=tmax,
        singleEvents=True,
        orderBy="startTime",
        maxResults=max_results,
    ).execute()

    events = events_result.get("items", [])

    #Debug Mode
    if not events:
        print(f"No events found in range for mode='{mode}'.")
        return []

    if mode == "today":
        label = f"Today ({datetime.now(LOCAL_TZ).date()})"
    elif mode == "2weeks":
        label = "Next ~2 weeks"
    else:
        label = "Next ~2 months"

    print(f"{label}: {len(events)} event(s)")
    for ev in events:
        start, end, title = _fmt_event(ev)
        print(f"- {start} → {end}: {title}")

    return events

if __name__ == "__main__":

    getCalendar("2weeks")   # Date range of 'today', '2weeks', or '2months'.

