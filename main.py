import os,time,requests,re

BOT_TOKEN=os.getenv("BOT_TOKEN")
CHAT_ID=os.getenv("CHAT_ID")


def send(msg):

    requests.post(
      f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
      json={
       "chat_id":CHAT_ID,
       "text":msg
      },
      timeout=20
    )


BAD={
"AI","SOL","ETH","BTC",
"DOGE","CAT","TOKEN"
}


############################
# SEARCH
############################

def fetch_pairs():

    searches=[
      "pump",
      "pepe",
      "frog",
      "inu",
      "bsc meme",
      "solana meme"
    ]

    pairs=[]

    for q in searches:

      try:

        r=requests.get(
         f"https://api.dexscreener.com/latest/dex/search?q={q}",
         timeout=20
        )

        pairs+=r.json().get(
         "pairs",[]
        )[:100]

      except:
        pass

    return pairs


############################
# AGE
############################

def fresh(p):

    try:
      c=p.get(
       "pairCreatedAt"
      )

      if not c:
         return True

      age=(
       time.time()*1000-c
      )/3600000

      return age<24

    except:
      return True


############################
# CLEAN TICKERS
############################

def clean_symbol(sym):

    return bool(
      re.match(
       r'^[A-Za-z0-9]+$',
       sym
      )
    )


############################
# CHAIN DETECT
############################

def detect_chain(ca):

    ca=str(ca)

    if ca.startswith(
      "0x"
    ):
       return "BSC"

    return "SOL"


############################
# SCORE
############################

def score(p):

    try:

      mc=float(
       p.get("fdv") or 0
      )

      liq=float(
       (p.get("liquidity") or {}
       ).get("usd") or 0
      )

      vol=float(
       (p.get("volume") or {}
       ).get("h24") or 0
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

      if 10000<mc<60000:
          s+=35
      elif mc<120000:
          s+=20

      if liq>5000:
          s+=20

      if vol>10000:
          s+=20

      if ratio>2:
          s+=20

      if buys>100:
          s+=10

      return s

    except:
      return 0


def label(s):

    if s>=75:
      return "🔥 Moonshot"

    if s>=55:
      return "🚀 High Conviction"

    return "Watch"


############################
# MAIN
############################

def run():

    sol=[]
    bsc=[]

    seen=set()

    for p in fetch_pairs():

      try:

        if not fresh(p):
            continue

        sym=p.get(
         "baseToken",{}
        ).get(
         "symbol","?"
        ).upper()

        if sym in BAD:
           continue

        if not clean_symbol(sym):
           continue

        if sym in seen:
           continue

        seen.add(sym)

        ca=p.get(
         "baseToken",{}
        ).get(
         "address",""
        )

        s=score(p)

        if s<55:
           continue

        item={
         "sym":sym,
         "ca":ca,
         "score":s,
         "label":label(s)
        }

        if detect_chain(ca)=="SOL":
           sol.append(item)
        else:
           bsc.append(item)

      except:
        pass


    sol=sorted(
      sol,
      key=lambda x:x["score"],
      reverse=True
    )[:3]

    bsc=sorted(
      bsc,
      key=lambda x:x["score"],
      reverse=True
    )[:3]


    if not sol and not bsc:
      send(
       "No moonshot candidates today."
      )
      return


    msg="🚀 DUAL CHAIN 100X HUNTER\n\n"


    if sol:

      msg+="SOLANA PICKS\n"

      for p in sol:
         msg+=(
          f"{p['sym']} "
          f"{p['label']}\n"
          f"CA {p['ca']}\n\n"
         )


    if bsc:

      msg+="BSC PICKS\n"

      for p in bsc:
         msg+=(
          f"{p['sym']} "
          f"{p['label']}\n"
          f"CA {p['ca']}\n\n"
         )


    msg+=(
      "Fresh <24h\n"
      "3x-100x asymmetry zone\n\n"
      "SL -20%\n"
      "Profit lock +30%"
    )

    send(msg)


if __name__=="__main__":
   run()
