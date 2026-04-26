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


################################
# FETCH
################################

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
        )[:500]

      except:
        pass

    return pairs


################################
# HELPERS
################################

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


################################
# METRICS
################################

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
       mc,liq,vol,buys,sells,ratio
      )

    except:
      return (0,0,0,0,1,0)


################################
# RUG RISK FILTER
################################

def rug_risk(p):

    mc,liq,vol,buys,sells,ratio=metrics(p)

    risk=0


    # thin liquidity danger
    if mc>0:

      liq_ratio=liq/mc

      if liq_ratio<0.08:
         risk+=40

      elif liq_ratio<0.12:
         risk+=20


    # fake volume proxy
    if buys>0:

      if vol > buys*1500:
          risk+=30


    # dead tx flow
    if buys+sells <40:
       risk+=20


    if ratio<1.2:
       risk+=20


    return risk


################################
# ALPHA SCORE
################################

def alpha_score(p):

    mc,liq,vol,buys,sells,ratio=metrics(p)

    s=0

    if 10000<mc<50000:
       s+=35

    elif mc<100000:
       s+=20

    if liq>7000:
       s+=20

    if vol>15000:
       s+=20

    if ratio>3:
       s+=20

    if buys>120:
       s+=10

    return s


def conviction(s):

    if s>=80:
       return "A+"

    return "A"


def risk_label(r):

    if r<=10:
      return "LOW"

    if r<=30:
      return "MED"

    return "HIGH"


################################
# MAIN
################################

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

        seen.add(sym)


        r=rug_risk(p)

        # reject garbage
        if r>30:
            continue


        s=alpha_score(p)

        # elite only
        if s<70:
            continue


        ca=p.get(
         "baseToken",{}
        ).get(
         "address",""
        )


        picks.append({

         "sym":sym,
         "ca":ca,
         "score":s,
         "risk":r

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
       "No elite low-rug setups today."
      )
      return


    msg="🚀 ALPHA HUNTER V4\n\n"

    for p in picks:

      msg+=(
       f"{p['sym']}\n"
       f"Conviction {conviction(p['score'])}\n"
       f"Rug Risk {risk_label(p['risk'])}\n"
       f"{link(p['ca'])}\n\n"
      )


    msg+=(
      "Filters:\n"
      "Low rug risk only\n"
      "Fresh <24h\n\n"
      "Risk:\n"
      "-20% stop\n"
      "+30% profit lock"
    )

    send(msg)



if __name__=="__main__":
    run()
