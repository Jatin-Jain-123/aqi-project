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

## Run it on your own device

You need **Python 3.11 or newer**, **Git** and a **Telegram** account. It works
on Windows, macOS and Linux, including a Raspberry Pi.

### 1. Download and install

```bash
git clone https://github.com/Jatin-Jain-123/aqi-project.git
cd aqi-project
python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate
```

Then install the dependencies:

```bash
pip install -r requirements.txt
```

### 2. Create your Telegram bot

1. In Telegram, open [@BotFather](https://t.me/BotFather), send `/newbot`
   and follow the prompts. You'll get a token like `8123456789:AAH...`.
2. Copy `.env.example` to a new file called `.env` and paste the token after
   `TELEGRAM_BOT_TOKEN=`.
3. Open your new bot (`https://t.me/<your_bot_username>`) and send it any
   message. It won't reply, and that's expected; a bot can only message you
   after you've messaged it.
4. Get your chat id:

   ```bash
   python main.py --find-chat-id
   ```

   It prints something like `{123456789: 'YourName'}`. Put that number after
   `TELEGRAM_CHAT_ID=` in `.env`.

Keep `.env` private. It's already in `.gitignore`.

### 3. Set your location and limits

Edit `config.toml`:

- **latitude / longitude**: right-click your area in Google Maps and click
  the coordinates to copy them.
- **thresholds**: the values that trigger an alert. Delete a line to stop
  watching that pollutant.

### 4. Try it

```bash
python main.py --report --dry-run   # print current readings, send nothing
python main.py --report             # send current readings to Telegram
python main.py                      # check once and alert if a limit is crossed
```

### 5. Keep it running

Pick one:

- **Simplest:** leave a terminal open with `python main.py --watch 30`
  (checks every 30 minutes; stop with Ctrl+C).
- **Windows Task Scheduler:** create a task that repeats every 30 minutes with
  - Program: `<project folder>\.venv\Scripts\python.exe`
  - Arguments: `main.py`
  - Start in: `<project folder>`
- **macOS / Linux / Raspberry Pi (cron):** run `crontab -e` and add
  ```
  */30 * * * * cd /path/to/aqi-project && .venv/bin/python main.py
  ```

## Tests

```bash
pytest
```

## Ideas for later

- Morning summary message at 8 am
- Use the nearest CPCB station instead of modelled data
- A Home Assistant sensor so the readings show up on my dashboard
