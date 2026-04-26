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


BAD={"AI","SOL","ETH","BTC","DOGE","CAT","TOKEN"}


def fetch():
    queries=[
      "pump",
      "pump fun",
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
        )[:60]

      except:
        pass

    return pairs


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


def grad_score(p):

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


      # anti rug sanity
      if liq<5000:
         return 0

      if mc>0 and liq/mc<0.12:
         return 0


      s=0

      if 25000<mc<70000:
         s+=35

      elif 15000<mc<100000:
         s+=20


      if liq>8000:
         s+=20

      if vol>10000:
         s+=15

      if ratio>2:
         s+=15

      if buys>100:
         s+=15


      ca=str(
        p.get(
         "baseToken",{}
        ).get(
         "address",""
        )
      ).lower()


      if "pump" in ca:
         s+=10


      return s

    except:
      return 0


def conviction(s):

    if s>=80:
       return "🔥 Imminent"

    if s>=65:
       return "🚀 Near"

    return "Watch"



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


        s=grad_score(p)

        if s>=50:

           ca=p.get(
            "baseToken",{}
           ).get(
            "address",""
           )

           picks.append({
             "sym":sym,
             "score":s,
             "conv":conviction(s),
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
        "No near migration candidates today."
       )
       return


    msg="🚀 FINAL GRADUATION SNIPER\n\n"


    for p in picks:

      msg+=(
       f"{p['sym']}\n"
       f"{p['conv']}\n"
       f"Graduation Score {p['score']}\n"
       f"{link(p['ca'])}\n\n"
      )


    msg+=(
      "Focus:\n"
      "Near DEX migration candidates\n"
      "Pump.fun style setups"
    )


    send(msg)


if __name__=="__main__":
   run()
