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


def fetch():

    r=requests.get(
      "https://api.dexscreener.com/latest/dex/search?q=pump",
      timeout=20
    )

    return r.json().get(
      "pairs",[]
    )[:200]


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


def grad_score(p):

    mc,liq,vol,buys,sells,ratio=metrics(p)

    s=0

    # graduation proxy zone
    if 25000<mc<70000:
        s+=35

    elif 15000<mc<100000:
        s+=20


    if liq>8000:
        s+=20

    if vol>10000:
        s+=15

    if vol>20000:
        s+=10

    if ratio>2:
        s+=15

    if buys>100:
        s+=10

    ca=p.get(
      "baseToken",{}
    ).get(
      "address",""
    ).lower()

    if "pump" in ca:
        s+=10

    return round(s,2)


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

        sym=p.get(
         "baseToken",{}
        ).get(
         "symbol","?"
        ).upper()

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
             "ca":ca,
             "score":s,
             "conv":conviction(s)
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
       "No graduation candidates today."
       )
       return


    msg="🚀 PUMP FUN GRADUATION SNIPER\n\n"

    for p in picks:

      msg+=(
       f"{p['sym']}\n"
       f"{p['conv']}\n"
       f"Graduation Score {p['score']}\n"
       f"https://dexscreener.com/solana/{p['ca']}\n\n"
      )


    msg+=(
      "Focus:\n"
      "Pre-DEX migration candidates\n"
      "Pump→Raydium style setups"
    )

    send(msg)


if __name__=="__main__":
   run()
