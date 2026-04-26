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


########################
# FETCH
########################

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


########################
# HELPERS
########################

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


def clean(sym):
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


########################
# METRICS
########################

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

      return(
       mc,liq,vol,
       buys,sells,ratio
      )

    except:
      return(
       0,0,0,
       0,1,0
      )


########################
# RISK SCORE
########################

def risk(p):

    mc,liq,vol,buys,sells,ratio=metrics(p)

    r=0

    if mc>0:

      lr=liq/mc

      if lr<0.06:
          r+=30

      elif lr<0.10:
          r+=15


    if buys+sells<20:
        r+=15


    if ratio<1.3:
        r+=15


    if buys>0 and vol>buys*2000:
        r+=20

    return r


########################
# ALPHA SCORE
########################

def alpha(p):

    mc,liq,vol,buys,sells,ratio=metrics(p)

    s=0

    if 10000<mc<60000:
       s+=30
    elif mc<120000:
       s+=15

    if liq>5000:
       s+=20

    if vol>10000:
       s+=20

    if ratio>2:
       s+=20

    if buys>70:
       s+=10

    return s


########################
# MAIN
########################

def run():

    elite=[]
    spec=[]

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

        if not clean(sym):
           continue

        if sym in seen:
           continue

        seen.add(sym)

        r=risk(p)

        if r>50:
           continue


        s=alpha(p)

        if s<60:
           continue


        item={
          "sym":sym,
          "ca":p.get(
             "baseToken",{}
           ).get(
             "address",""
           ),
          "score":s,
          "risk":r
        }

        if r<=25:
            elite.append(item)

        else:
            spec.append(item)

      except:
        pass


    elite=sorted(
      elite,
      key=lambda x:x["score"],
      reverse=True
    )[:3]

    spec=sorted(
      spec,
      key=lambda x:x["score"],
      reverse=True
    )[:3]


    if not elite and not spec:
      send(
       "No balanced setups today."
      )
      return


    msg="🚀 BALANCED HUNTER V4.5\n\n"


    if elite:
      msg+="ELITE PICKS\n"

      for p in elite:

        msg+=(
         f"{p['sym']}\n"
         f"Risk LOW\n"
         f"{link(p['ca'])}\n\n"
        )


    if spec:
      msg+="SPECULATIVE\n"

      for p in spec:

        msg+=(
         f"{p['sym']}\n"
         f"Risk MED\n"
         f"{link(p['ca'])}\n\n"
        )


    msg+=(
     "Focus:\n"
     "Fresh <24h\n"
     "3x-100x asymmetry\n\n"
     "SL -20%\n"
     "Profit lock +30%"
    )

    send(msg)



if __name__=="__main__":
   run()
