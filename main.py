import os
import requests

BOT_TOKEN=os.getenv('BOT_TOKEN')
CHAT_ID=os.getenv('CHAT_ID')


def send(msg):
    requests.post(
      f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
      json={
       "chat_id":CHAT_ID,
       "text":msg
      },
      timeout=20
    )


##########################
# Pump.fun source
##########################
# NOTE:
# endpoint bisa berubah; kalau berubah kita adjust.
# ini contoh memakai coins feed.

def fetch_candidates():

    urls=[
      "https://frontend-api.pump.fun/coins/latest",
      "https://frontend-api.pump.fun/coins/king-of-the-hill"
    ]

    out=[]

    for u in urls:
      try:
         r=requests.get(
           u,
           timeout=20
         )

         data=r.json()

         if isinstance(data,list):
            out+=data[:100]

      except:
         pass

    return out


##########################
# Graduation Score
##########################

def grad_score(c):

    try:
        # nama field bisa berubah antar endpoint,
        # kita handle fallback.

        bonding=float(
          c.get('bonding_curve_progress')
          or c.get('bondingProgress')
          or 0
        )

        buys=float(
          c.get('buys_24h')
          or c.get('buys')
          or 0
        )

        volume=float(
          c.get('volume_24h')
    run()
