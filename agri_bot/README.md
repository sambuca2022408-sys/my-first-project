# AgriNepal Bot (starter)

This is a small starter Telegram bot that provides current weather and simple agriculture advice for Nepal (and elsewhere).

Quick start

1. Copy `.env.example` to `.env` and fill in values for `TELEGRAM_TOKEN` and `OWM_API_KEY`.

2. Install dependencies (use a virtualenv):

```bash
pip install -r requirements.txt
```

3. Run the bot (long-polling):

```bash
python -m agri_bot.bot
```

Commands

- `/start` — welcome message
- `/weather <city>` — current weather + simple farming advice
- `/help` — list commands

Notes & next steps

- Add market price feeds (local Nepali markets) — could be scraped or integrated via APIs.
- Add Nepali language (translation) support.
- Add irrigation scheduling, alerts, and crop-specific advice.
- Deploy to a small cloud VM or serverless platform and use webhooks for scale.
