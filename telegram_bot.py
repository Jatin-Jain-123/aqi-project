"""Minimal Telegram Bot API helpers (no extra library needed)."""

import requests

API = "https://api.telegram.org/bot{token}/{method}"


def send_message(token, chat_id, text):
    response = requests.post(
        API.format(token=token, method="sendMessage"),
        json={"chat_id": chat_id, "text": text},
        timeout=15,
    )
    response.raise_for_status()


def find_chat_ids(token):
    """Chats that recently messaged the bot. Send your bot any message first."""
    response = requests.get(API.format(token=token, method="getUpdates"), timeout=15)
    response.raise_for_status()
    chats = {}
    for update in response.json().get("result", []):
        chat = update.get("message", {}).get("chat")
        if chat:
            chats[chat["id"]] = chat.get("first_name") or chat.get("title", "")
    return chats
