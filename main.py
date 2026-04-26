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
# FETCH
############################

def fetch_pairs():

    searches=[
      "pump",
      "pepe",
      "frog",
      "inu",
      "solana meme",
      "bsc meme"
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


############################
# FILTERS
############################

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


def clean_symbol(sym):

    return bool(
      re.match(
       r'^[A-Za-z0-9]+$',
       sym
      )
    )


def chain(ca):
    if str(ca).startswith(
      "0x"
    ):
      return "bsc"

    return "solana"


def link(ca):

    if chain(ca)=="bsc":
       return (
       "https://dexscreener.com/bsc/"
       +ca
       )

    return (
      "https://dexscreener.com/solana/"
      +ca
    )


############################
# SCORE
############################

def metrics(p):

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

      return (
       mc,liq,vol,buys,ratio
      )

    except:
      return (0,0,0,0,0)


def score(p):

    mc,liq,vol,buys,ratio=metrics(p)

    s=0

    # microcap sweet spot
    if 10000<mc<50000:
       s+=35
    elif mc<100000:
       s+=20

    if liq>7000:
       s+=20

    if vol>15000:
       s+=20

    # tighter imbalance
    if ratio>3:
       s+=20

    if buys>120:
       s+=10

    return s


############################
# MAIN
############################

def run():

    alpha=[]
    moon=[]
    grad=[]

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

        mc,liq,vol,buys,ratio=metrics(p)

        # simple fake-liq reject
        if liq>vol*5:
            continue

        ca=p.get(
         "baseToken",{}
        ).get(
         "address",""
        )

        s=score(p)

        if s<65:
            continue


        item={
         "sym":sym,
         "ca":ca,
         "score":s
        }


        # buckets
        if s>=80:
            moon.append(item)

        elif (
          15000<mc<40000
          and ratio>3
        ):
            grad.append(item)

        else:
            alpha.append(item)


      except:
        pass


    alpha=sorted(
      alpha,
      key=lambda x:x["score"],
      reverse=True
    )[:3]

    moon=sorted(
      moon,
      key=lambda x:x["score"],
      reverse=True
    )[:2]

    grad=sorted(
      grad,
      key=lambda x:x["score"],
      reverse=True
    )[:2]


    if not alpha and not moon and not grad:
       send(
        "No institutional-grade setups today."
       )
       return


    msg="🚀 ALPHA HUNTER V3\n\n"


    if alpha:
      msg+="ALPHA TRADES\n"

      for p in alpha:
        msg+=(
         f"{p['sym']}\n"
         f"Score {p['score']}\n"
         f"{link(p['ca'])}\n\n"
        )


    if moon:
      msg+="MOONSHOT LOTTERY\n"

      for p in moon:
        msg+=(
         f"{p['sym']}\n"
         f"🔥 Moonshot\n"
         f"{link(p['ca'])}\n\n"
        )


    if grad:
      msg+="NEAR GRADUATION\n"

      for p in grad:
        msg+=(
         f"{p['sym']}\n"
         f"Sniper Candidate\n"
         f"{link(p['ca'])}\n\n"
        )


    msg+=(
      "Rules:\n"
      "-20% SL\n"
      "+30% lock profits"
    )

    send(msg)



if __name__=="__main__":
   run()
