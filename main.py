import os
import time
import requests

BOT_TOKEN=os.getenv("BOT_TOKEN")
CHAT_ID=os.getenv("CHAT_ID")


################################
# TELEGRAM
################################

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


################################
# FETCH
################################

def fetch_pairs():

    searches=[
      "pump",
      "pepe",
      "frog",
      "moon",
      "inu",
      "solana meme"
    ]

    pairs=[]

    for q in searches:

        try:
            url=f"https://api.dexscreener.com/latest/dex/search?q={q}"

            r=requests.get(
              url,
              timeout=20
            )

            data=r.json()

            pairs+=data.get(
               "pairs",
               []
            )[:80]

        except:
            pass

    return pairs


################################
# FRESH <24h
################################

def fresh(p):

    try:

        created=p.get(
          "pairCreatedAt"
        )

        if not created:
            return True

        age=(
         time.time()*1000-created
        )/3600000

        return age<24

    except:
        return True


################################
# BLACKLIST NOISE
################################

BAD={
"AI","SOL","ETH","BTC",
"DOGE","CAT","TOKEN",
"TEST","USD"
}


################################
# PUMP FILTER
################################

def looks_like_pump(ca):

    ca=str(ca).lower()

    return (
      "pump" in ca
      or len(ca)>30
    )


################################
# ALPHA SCORE
################################

def score(p):

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
          "h24",{}
        )

        buys=float(
         tx.get("buys") or 0
        )

        sells=float(
         tx.get("sells") or 1
        )

        ratio=buys/sells


        s=0


        # microcaps sweet spot
        if 10000<mc<50000:
            s+=35

        elif mc<100000:
            s+=20


        if liq>5000:
            s+=20

        if vol>10000:
            s+=20

        if ratio>2:
            s+=20

        if buys>100:
            s+=10

        return round(s,2)

    except:
        return 0


################################
# LABEL
################################

def label(s):

    if s>=75:
        return "🔥 Moonshot"

    if s>=55:
        return "🚀 High Conviction"

    return "Watch"


################################
# SCANNER
################################

def run_scanner():

    pairs=fetch_pairs()

    seen=set()

    picks=[]


    for p in pairs:

        try:

            if not fresh(p):
                continue


            symbol=p.get(
              "baseToken",{}
            ).get(
              "symbol","?"
            ).upper()


            if symbol in BAD:
                continue


            if symbol in seen:
                continue

            seen.add(symbol)


            ca=p.get(
             "baseToken",{}
            ).get(
             "address","N/A"
            )


            if not looks_like_pump(ca):
                continue


            s=score(p)


            # tighter threshold
            if s>=55:

                picks.append({

                 "symbol":symbol,
                 "ca":ca,
                 "score":s,
                 "label":label(s)

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
         "No high-conviction pump candidates today."
        )
        return


    msg="🚀 PUMP 100X HUNTER\n\n"


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
      "Focus:\n"
      "Fresh <24h Pump Candidates\n"
      "Microcap Asymmetry Zone\n\n"
      "Rules:\n"
      "SL -20%\n"
      "Profit lock +30%"
    )

    send(msg)


if __name__=="__main__":
    run_scanner()
