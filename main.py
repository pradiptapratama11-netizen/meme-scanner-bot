import os
import requests

BOT_TOKEN=os.getenv("BOT_TOKEN")
CHAT_ID=os.getenv("CHAT_ID")

def send():
    url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
      url,
      json={
        "chat_id":CHAT_ID,
        "text":"🚀 DAILY MEME PICKS TEST"
      }
    )

send()
