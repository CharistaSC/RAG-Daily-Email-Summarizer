Inbox + Calendar Summariser (Gmail + Google Calendar + LLM)

A tiny Python toolchain that:
- reads recent Gmail messages,
- fetches Google Calendar events for a chosen window,
- stitches both into prompt templates, and
- asks a local LLM (Ollama) to produce helpful summaries (and a conflict check). 

Features
- OAuth helper with a “superset” of sensible scopes and token caching. (auth.py)
- Gmail inbox fetcher (read-only; returns from, subject, id) using lightweight metadata. (getMail.py)
- Calendar fetcher for today, 2weeks, or 2months, defaulting to Asia/Singapore time and printing a readable timeline. (getCalendar)
- LLM wrapper using Ollama (e.g., mistral) to generate the summaries from your prompt templates. (getResponse)
- Main driver that loads two prompt files—prompts/summary.md and prompts/conflict.md—fills placeholders, and prints the two LLM outputs. (main.py)

Prerequisites
- Python 3.10+ (recommended; zoneinfo is used by Calendar code) 
- Google Cloud OAuth client (client_secret_*.json)
- Ollama installed locally (and a pulled model, e.g. mistral) for getResponse.py. 

Configuration
1) OAuth / tokens
Edit auth.py to point to your OAuth client JSON (or pass arguments when you call get_creds). The helper requests a superset of common scopes and caches tokens in token.json. First run: a browser window opens; the refresh token is stored for reuse. (auth.py)

2) Scopes
- Gmail read: https://www.googleapis.com/auth/gmail.readonly
- Calendar read: https://www.googleapis.com/auth/calendar.readonly
- (Optionally) send mail / edit calendar are present in SCOPES_ALL to be expanded later. (auth.py)

3) Prompts
Create two prompt files used by main.py:
- prompts/summary.md
- prompts/conflict.md (Next Stage)

They can contain placeholders:
{today_date}
{emails_text}
{calendar_text}

main.py safely fills only the keys you pass and leaves unknown braces untouched. 

Troubleshooting

Token has wrong scopes
If you initially authenticated with fewer scopes, delete token.json and re-run auth.py to mint a token that matches your needs. (auth.py)

Ollama not found / model missing
Install Ollama, run it, and ollama pull mistral (or whichever you set in getResponse.py). 

No Calendar events printing
Ensure the time window actually contains events; getCalendar_v2 prints a count and items for the selected mode. (getCalendar.py)

Gmail results empty
The current fetcher queries INBOX only and returns the latest messages; adjust max_results or add a query filter (e.g., labels) if required. (getMail.py)
