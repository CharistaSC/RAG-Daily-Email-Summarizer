from googleapiclient.discovery import build
from auth import get_creds  # your existing helper

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def accept_invite(event_id: str, calendar_id: str = "primary"):
    creds = get_creds(SCOPES)
    svc = build("calendar", "v3", credentials=creds)

    ev = svc.events().get(calendarId=calendar_id, eventId=event_id).execute()

    attendees = ev.get("attendees", []) or []
    changed = False
    for a in attendees:
        if a.get("self"):
            if a.get("responseStatus") != "accepted":
                a["responseStatus"] = "accepted"
                changed = True
            break

    if not changed:
        return ev  # already accepted or no self-attendee found

    ev["attendees"] = attendees
    # sendUpdates: 'all' | 'externalOnly' | 'none'
    updated = svc.events().update(
        calendarId=calendar_id,
        eventId=event_id,
        body=ev
    ).execute()

    # If you want email updates to the organizer/guests:
    # updated = svc.events().update(calendarId=calendar_id, eventId=event_id,
    #                               body=ev, sendUpdates="all").execute()

    return updated
