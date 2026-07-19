# Endflo

Endflo AI project assistant — lives in WhatsApp/Telegram, manages tasks, meetings, and triage.

## Files

- **miniapp/** — Telegram Mini App backend (FastAPI + frontend)
  - main.py, db.py, auth.py, seeds, static/
- **endflo_telegram.py** — Telegram session logger (Telethon). Pipes messages to n8n webhooks for chat ingestion and group events.
- **website_v3/** — **canonical** marketing site (static, no build step). Supersedes `website_v2/` and `website/`, which are kept as history. See `website_v3/site/README.md`.

## Mini App

```bash
cd miniapp
pip install -r requirements.txt
python main.py
```

## Telegram Logger

```bash
python endflo_telegram.py
```
