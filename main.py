from getMail import *
from getCalendar import *
from getResponse import *
import io, sys
from pathlib import Path

def load_prompt(path: str, **kwargs) -> str:
    text = Path(path).read_text(encoding="utf-8")
    # Safe formatting: only replace keys you pass; leave others untouched
    class SafeDict(dict):
        def __missing__(self, key):  # keep {missing} as-is
            return "{" + key + "}"
    return text.format_map(SafeDict(**kwargs))

if __name__ == "__main__":
    emails = getMail()
    emails_text = "\n".join(
        f'From: {e["from"]} | Subject: {e["subject"]}' for e in emails
    )
    calendar_text = getCalendar("2weeks")

    # print(emails_text)
    # print(calendar_text)

    prompt = load_prompt(
        "prompts/summary.md",
        today_date=datetime.now().strftime("%d %b %Y"),
        emails_text=emails_text,
        calendar_text=calendar_text,
    )

    print(generate_response(prompt))

    prompt = load_prompt(
        "prompts/conflict.md",
        today_date=datetime.now().strftime("%d %b %Y"),
        emails_text=emails_text,
        calendar_text=calendar_text,
    )

    print(generate_response(prompt))