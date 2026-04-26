import os,requests

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


##################################
# SEARCH FRESH PUMP COINS
##################################

def fetch():

    r=requests.get(
      "https://api.dexscreener.com/latest/dex/search?q=pump",
      timeout=20
    )

    return r.json().get(
      "pairs",[]
    )[:150]


##################################
# NEAR GRADUATION SCORE
##################################

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

      # proxy near graduation zone
      if 20000<mc<80000:
          s+=35

      if liq>8000:
          s+=20

      if vol>12000:
          s+=20

      if ratio>2:
          s+=15

      if buys>100:
          s+=10

      return s

    except:
      return 0


def run():

    picks=[]

    seen=set()

    for p in fetch():

      try:

        sym=p.get(
         "baseToken",{}
        ).get(
         "symbol","?"
        ).upper()

        if sym in seen:
            continue

        seen.add(sym)

        ca=p.get(
         "baseToken",{}
        ).get(
         "address",""
        )

        # focus pump-like only
        if "pump" not in ca.lower():
            continue

        s=score(p)

        if s>=60:

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
       "No near-migration candidates."
      )

      return


    msg="🚀 PUMP MIGRATION SNIPER\n\n"

    for p in picks:

      msg+=(
       f"{p['sym']}\n"
       f"Near Graduation Score {p['score']}\n"
       f"https://dexscreener.com/solana/{p['ca']}\n\n"
      )


    msg+=(
      "Focus:\n"
      "Pre migration candidates\n"
      "Potential Pump→DEX moves"
    )


    send(msg)



if __name__=="__main__":
   run()
