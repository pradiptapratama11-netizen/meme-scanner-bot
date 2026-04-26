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

def fetch():

    queries=[
      "pump",
      "pump fun",
      "microcap solana",
      "new solana meme"
    ]

    pairs=[]

    for q in queries:
      try:
        r=requests.get(
         f"https://api.dexscreener.com/latest/dex/search?q={q}",
         timeout=20
        )

        pairs += r.json().get(
          "pairs",[]
        )[:70]

      except:
        pass

    return pairs


########################
# HELPERS
########################

def fresh(p):

    try:
      c=p.get("pairCreatedAt")

      if not c:
         return True

      age=(time.time()*1000-c)/3600000

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


def link(ca):

    if str(ca).startswith("0x"):
      return (
       "https://dexscreener.com/bsc/"
       +ca
      )

    return (
      "https://dexscreener.com/solana/"
      +ca
    )


########################
# SCORE ENGINE
########################

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

    ch=(p.get("priceChange") or {})

    h1=float(
      ch.get("h1") or 0
    )

    h24=float(
      ch.get("h24") or 0
    )


    ##################
    # anti trap
    ##################

    if liq<7000:
       return 0

    if mc>0 and liq/mc<0.15:
       return 0


    s=0

    ##################
    # graduation
    ##################

    if 25000<mc<70000:
       s+=30

    elif mc<100000:
       s+=15

    if liq>10000:
       s+=20

    if vol>15000:
       s+=15

    if ratio>2:
       s+=15

    if buys>100:
       s+=10


    ##################
    # pullback entry
    ##################

    if h24>50:
       s+=10

    if -35<h1<-8:
       s+=15


    ##################
    # SMART WALLET PROXY
    ##################

    smart=0

    # clustered buying
    if buys>150:
       smart+=20

    # aggressive accumulation
    if ratio>3:
       smart+=20

    # volume expansion vs mcap
    if vol>mc*0.5:
       smart+=20

    # high activity concentration
    if buys+sells>250:
       smart+=20

    # microcap asymmetry bonus
    if mc<50000:
       smart+=10

    s += smart

    return round(s,2)

 except:
    return 0


def grade(s):

   if s>=135:
      return "👑 GOD MODE CONFIRMED"

   if s>=115:
      return "🎯 A+ Smart Wallet"

   if s>=95:
      return "🔥 A Setup"

   return "Watch"


########################
# MAIN
########################

def run():

 picks=[]
 seen=set()

 for p in fetch():

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


   s=score(p)

   if s<95:
      continue

   ca=p.get(
     "baseToken",{}
   ).get(
     "address",""
   )

   picks.append({
    "sym":sym,
    "score":s,
    "grade":grade(s),
    "ca":ca
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
    "No smart-wallet confirmed setups today."
   )
   return


 msg="🚀 SMART WALLET GOD MODE\n\n"

 for p in picks:

   msg+=(
    f"{p['sym']}\n"
    f"{p['grade']}\n"
    f"Alpha Score {p['score']}\n"
    f"{link(p['ca'])}\n\n"
   )


 msg+=(
 "Sizing:\n"
 "A Setup = 0.5R\n"
 "A+ Smart Wallet = 0.75R\n"
 "God Mode Confirmed = 1R\n\n"

 "Risk:\n"
 "-20% SL\n"
 "+30% move stop above entry\n"
 "2x take principal\n"
 "let moonbag hunt 10x-100x"
 )

 send(msg)


if __name__=="__main__":
 run()
