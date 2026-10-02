# aqi-project

Every winter Delhi's air gets bad, and I usually find out after I'm already
outside. This script checks the air quality where I live and sends me a
Telegram message when the AQI or a specific pollutant crosses a limit I set.
It sends another message once things improve.

```
Air quality alert for New Delhi (AQI 214, Poor)

🔴 AQI is 214 (your limit: 200)
🔴 PM2.5 is 96.3 µg/m³ (your limit: 90)
```

## How it works

- Air quality data comes from the free [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api)
  (no API key needed).
- The **Indian AQI** is calculated from the last 24 hours of PM2.5 and PM10,
  using CPCB's breakpoints. The official AQI uses ground stations and more
  pollutants, so treat this as an estimate.
- You only get **one** alert when a value crosses its limit, not one every
  check. The "back to normal" message is sent once the value drops below 90%
  of the limit, so a value that hovers around the limit doesn't spam you.
- Messages go out through the Telegram Bot API with plain `requests`.

## Setup

```bash
pip install -r requirements.txt
```

1. On Telegram, talk to [@BotFather](https://t.me/BotFather), send `/newbot`
   and copy the token it gives you.
2. Copy `.env.example` to `.env` and paste the token in.
3. Send any message to your new bot, then run
   `python main.py --find-chat-id` and put that id in `.env` too.
4. Set your location and limits in `config.toml`.

## Usage

```bash
python main.py --report --dry-run   # see current readings, send nothing
python main.py --report             # send current readings to Telegram
python main.py                      # check once and alert if needed
python main.py --watch 30           # keep checking every 30 minutes
```

I run `python main.py` every 30 minutes with Windows Task Scheduler. `cron`
works the same way on Linux.

## Tests

```bash
pytest
```

## Ideas for later

- Morning summary message at 8 am
- Use the nearest CPCB station instead of modelled data
- A Home Assistant sensor so the readings show up on my dashboard
