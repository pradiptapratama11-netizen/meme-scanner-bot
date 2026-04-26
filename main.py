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


def fetch_pairs():

    searches=[
      "pump",
      "pepe",
      "frog",
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
        )[:300]

      except:
        pass

    return pairs


def fresh(p):

    try:
      c=p.get("pairCreatedAt")
      if not c:
         return True

      age=(
       time.time()*1000-c
      )/3600000

      return age<24

    except:
      return True


# SOLANA ADDRESS FILTER
def solana_only(ca):

    ca=str(ca)

    if ca.startswith("0x"):
        return False

    # base58-ish solana addresses
    if len(ca)<32:
        return False

    return True


# latin only symbols
def clean_symbol(sym):

    if not re.match(
      r'^[A-Za-z0-9]+$',
      sym
    ):
       return False

    return True


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

      return s

    except:
      return 0


def label(s):

    if s>=75:
      return "🔥 Moonshot"

    if s>=55:
      return "🚀 High Conviction"

    return "Watch"


def run():

    picks=[]
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

        ca=p.get(
         "baseToken",{}
        ).get(
         "address",""
        )

        if not solana_only(ca):
            continue

        seen.add(sym)

        s=score(p)

        if s>=55:

           picks.append({
             "sym":sym,
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
        "No clean Solana moonshots today."
       )
       return


    msg="🚀 SOLANA 100X HUNTER\n\n"

    for i,p in enumerate(
      picks,
      1
    ):
      msg+=(
       f"{i}) {p['sym']}\n"
       f"{p['label']}\n"
       f"Score {p['score']}\n"
       f"CA {p['ca']}\n\n"
      )

    msg+=(
      "Solana only | <24h\n"
      "SL -20% | Profit lock +30%"
    )

    send(msg)


if __name__=="__main__":
    run()
