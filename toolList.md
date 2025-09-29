getMail(max_results: int = 10)

- Description: Fetches recent Gmail messages from the Inbox (read-only) and returns lightweight metadata for each message.

- Parameters: max_results — Maximum number of messages to fetch (default 10).

- Output: list[dict] where each item includes:
    • from — Sender (email header).
    • subject — Message subject.
    • id — Gmail message ID (for follow-up reads).

----------------------------------------------------------------------------------------------------------------------
getCalendar(mode: str = "today", max_results: int = 100)

- Description: Retrieves events from the user’s primary Google Calendar over a preset time window.

- Parameters:
    • mode — Time window selector: "today", "2weeks", or "2months" (default "today").
    • max_results — Maximum number of events to return (default 100).

- Output: list[dict] of Google Calendar event objects (e.g., keys like start, end, summary, etc.).