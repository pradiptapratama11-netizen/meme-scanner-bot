import os
import time
import requests

BOT_TOKEN=os.getenv("BOT_TOKEN")
CHAT_ID=os.getenv("CHAT_ID")


############################
# TELEGRAM
############################

def send(msg):

    url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        json={
          "chat_id":CHAT_ID,
          "text":msg
        },
        timeout=20
    )


############################
# MULTI SEARCH FOR FRESH MEMES
############################

def fetch_pairs():

    searches=[
      "pump",
      "meme",
      "pepe",
      "dog",
      "cat",
      "frog",
      "ai",
      "moon",
      "solana",
      "inu"
    ]

    all_pairs=[]

    for q in searches:

        try:
            url=f"https://api.dexscreener.com/latest/dex/search?q={q}"

            r=requests.get(
               url,
               timeout=20
            )

            data=r.json()

            all_pairs += data.get(
                "pairs",
                []
            )[:300]

        except:
            pass

    return all_pairs


############################
# AGE FILTER <24H
############################

def fresh_launch(p):

    try:

        created=p.get(
          "pairCreatedAt"
        )

        if not created:
            return True

        age_hours=(
          time.time()*1000-created
        )/3600000

        return age_hours <24

    except:
        return True


############################
# 100X HUNTER SCORE
############################

def alpha_score(p):

    try:

        mc=float(
          p.get("fdv") or 0
        )

        liq=float(
         (p.get("liquidity") or {}).get(
          "usd"
         ) or 0
        )

        vol=float(
         (p.get("volume") or {}).get(
          "h24"
         ) or 0
        )

        tx=(p.get("txns") or {}).get(
          "h24",
          {}
        )

        buys=float(
         tx.get("buys") or 0
        )

        sells=float(
         tx.get("sells") or 1
        )

        buy_ratio=buys/sells

        score=0

        # sweet spot small caps
        if 15000<mc<60000:
            score+=30

        elif mc<120000:
            score+=15


        if liq>5000:
            score+=20

        if vol>10000:
            score+=20

        if buy_ratio>1.5:
            score+=20

        if buys>50:
            score+=10


        return round(score,2)

    except:
        return 0


############################
# CONVICTION LABEL
############################

def conviction(s):

    if s>=75:
        return "🔥 Moonshot"

    if s>=55:
        return "🚀 High Conviction"

    return "Watch"


############################
# MAIN SCANNER
############################

def run_scanner():

    pairs=fetch_pairs()

    picks=[]

    seen=set()


    for p in pairs:

        try:

            if not fresh_launch(p):
                continue

            symbol=p.get(
             "baseToken",{}
            ).get(
             "symbol","?"
            )

            ca=p.get(
             "baseToken",{}
            ).get(
             "address","N/A"
            )

            if symbol in seen:
                continue

            seen.add(symbol)

            score=alpha_score(p)

            if score>=45:

                picks.append({
                 "symbol":symbol,
                 "ca":ca,
                 "score":score,
                 "label":conviction(score)
                })

        except:
            pass


    picks=sorted(
      picks,
      key=lambda x:x["score"],
      reverse=True
    )[:5]


    if not picks:
        send(
          "No fresh 100x candidates today."
        )
        return


    msg="🚀 100X HUNTER SCANNER\n\n"


    for i,p in enumerate(
      picks,
      1
    ):

        msg+=(
         f"{i}) {p['symbol']}\n"
         f"{p['label']}\n"
         f"Score: {p['score']}\n"
         f"CA: {p['ca']}\n\n"
        )


    msg+=(
     "Setup:\n"
     "Age <24h\n"
     "Asymmetric alpha candidates\n\n"
     "Risk:\n"
     "SL -20%\n"
     "Move stop above entry at +30%"
    )

    send(msg)



if __name__=="__main__":
    run_scanner()
