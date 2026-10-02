"""Check air quality and message me on Telegram when it gets bad.

    python main.py                 check once (good for Task Scheduler / cron)
    python main.py --watch 30      keep checking every 30 minutes
    python main.py --report        send the current readings right now
    python main.py --dry-run       print messages instead of sending them
    python main.py --find-chat-id  show your chat id after you message the bot
"""

import argparse
import json
import os
import sys
import time
import tomllib
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

import air_quality
import alerts
import telegram_bot

HERE = Path(__file__).parent
STATE_FILE = HERE / "state.json"


def load_config():
    with open(HERE / "config.toml", "rb") as f:
        return tomllib.load(f)


def load_active_alerts():
    if STATE_FILE.exists():
        return set(json.loads(STATE_FILE.read_text())["active"])
    return set()


def save_active_alerts(active):
    STATE_FILE.write_text(json.dumps({"active": sorted(active)}))


def env(name):
    value = os.environ.get(name)
    if not value:
        sys.exit(f"{name} is not set. Copy .env.example to .env and fill it in (or use --dry-run).")
    return value


def notify(text, dry_run):
    if dry_run:
        print("--- would send ---\n" + text + "\n------------------")
        return
    telegram_bot.send_message(env("TELEGRAM_BOT_TOKEN"), env("TELEGRAM_CHAT_ID"), text)


def run_check(config, dry_run, report=False):
    place = config["location"]
    readings = air_quality.fetch(place["latitude"], place["longitude"])
    print(f"[{datetime.now():%H:%M}] AQI {readings['aqi']} ({readings['category']}), "
          f"PM2.5 {readings.get('pm2_5')}, PM10 {readings.get('pm10')}")

    if report:
        notify(alerts.summary(readings, place["name"]), dry_run)
        return

    messages, active = alerts.check(readings, config["thresholds"], load_active_alerts())
    if messages:
        header = f"Air quality alert for {place['name']} (AQI {readings['aqi']}, {readings['category']})"
        notify(header + "\n\n" + "\n".join(messages), dry_run)
    if not dry_run:
        save_active_alerts(active)


def main():
    parser = argparse.ArgumentParser(description="AQI alerts on Telegram")
    parser.add_argument("--watch", type=int, metavar="MINUTES", help="check repeatedly")
    parser.add_argument("--report", action="store_true", help="send current readings")
    parser.add_argument("--dry-run", action="store_true", help="print instead of sending")
    parser.add_argument("--find-chat-id", action="store_true")
    args = parser.parse_args()

    # Windows terminals default to cp1252, which can't print "NO₂" or emoji
    sys.stdout.reconfigure(encoding="utf-8")

    load_dotenv(HERE / ".env")
    if args.find_chat_id:
        chats = telegram_bot.find_chat_ids(env("TELEGRAM_BOT_TOKEN"))
        print(chats or "No messages yet - send your bot a message on Telegram and try again.")
        return

    config = load_config()
    if not args.watch:
        run_check(config, args.dry_run, args.report)
        return

    while True:
        try:
            run_check(config, args.dry_run, args.report)
        except requests.RequestException as err:
            # Wi-Fi drops or the API is down; just try again next time.
            print(f"Check failed: {err}")
        time.sleep(args.watch * 60)


if __name__ == "__main__":
    main()
