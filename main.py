import os
import requests

###################################
# YOUR GITHUB SECRETS
###################################

BOT_TOKEN=os.getenv("MEME_BOT_TOKEN")
CHAT_ID=os.getenv("MEME_CHAT_ID")


def send(msg):

    if not BOT_TOKEN or not CHAT_ID:
        print("Missing Telegram secrets")
        return

    requests.post(
      f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
      json={
       "chat_id":CHAT_ID,
       "text":msg
      },
      timeout=20
    )


###################################
# STABLE DATA SOURCE
###################################

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
         headers={
          "User-Agent":"Mozilla/5.0"
         },
         timeout=20
        )

        if r.status_code!=200:
            continue

        data=r.json()

        pairs+=data.get(
         "pairs",[]
        )[:50]

      except:
         pass

    return pairs



###################################
# GRADUATION SCORE
###################################

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


      # near migration zone
      if 20000<mc<80000:
          s+=35

      elif 10000<mc<120000:
          s+=20


      if liq>5000:
          s+=20

      if vol>10000:
          s+=15

      if ratio>2:
          s+=15

      if buys>80:
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



def label(s):

   if s>=80:
      return "🔥 Imminent"

   if s>=65:
      return "🚀 Near"

   return "Watch"



###################################
# MAIN
###################################

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


        s=score(p)

        if s>=50:

           ca=p.get(
             "baseToken",{}
           ).get(
             "address",""
           )

           picks.append({

             "sym":sym,
             "score":s,
             "label":label(s),
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


    msg="🚀 PUMP GRADUATION AGENT\n\n"


    for p in picks:

      msg+=(
        f"{p['sym']}\n"
        f"{p['label']}\n"
        f"Graduation Score {p['score']}\n"
        f"https://dexscreener.com/solana/{p['ca']}\n\n"
      )


    msg+=(
      "Focus:\n"
      "Pre DEX migration candidates\n"
      "Pump.fun sniper watch"
    )


    send(msg)



if __name__=="__main__":
    run()
