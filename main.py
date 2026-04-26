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
        )[:120]

      except:
        pass

    return pairs


############################
# HELPERS
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


############################
# METRICS
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
       mc,liq,vol,
       buys,sells,ratio
      )

    except:
      return(
       0,0,0,
       0,1,0
      )


############################
# SCORE
############################

def alpha(p):

    mc,liq,vol,buys,sells,ratio=metrics(p)

    s=0

    if 15000<mc<70000:
        s+=30

    elif mc<120000:
        s+=15

    if liq>10000:
        s+=25

    if vol>15000:
        s+=20

    if ratio>2:
        s+=15

    if buys>80:
        s+=10

    return s


############################
# MAIN
############################

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

        if not clean(sym):
           continue

        if sym in seen:
           continue

        seen.add(sym)


        mc,liq,vol,buys,sells,ratio=metrics(p)


        ################################
        # ANTI LIQUIDITY TRAPS
        ################################

        # hard floor
        if liq<5000:
            continue

        # liquidity vs fdv sanity
        if mc>0 and liq/mc<0.15:
            continue

        # fake volume proxy
        if buys>0 and vol>buys*1500:
            continue

        # weak flow reject
        if buys+sells<40:
            continue

        # weak imbalance reject
        if ratio<1.5:
            continue


        s=alpha(p)

        if s<60:
           continue


        ca=p.get(
         "baseToken",{}
        ).get(
         "address",""
        )


        picks.append({
          "sym":sym,
          "ca":ca,
          "score":s
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
        "No tradeable low-trap setups today."
       )

       return


    msg="🚀 ANTI-LIQUIDITY HUNTER V5\n\n"

    for p in picks:

      msg+=(
       f"{p['sym']}\n"
       f"Conviction A\n"
       f"{link(p['ca'])}\n\n"
      )


    msg+=(
      "Filters:\n"
      "Liquidity trap removed\n"
      "Fresh <24h only\n\n"
      "Risk:\n"
      "-20% stop\n"
      "+30% profit lock"
    )


    send(msg)



if __name__=="__main__":
   run()
