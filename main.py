import os
import requests

BOT_TOKEN=os.getenv("BOT_TOKEN")
CHAT_ID=os.getenv("CHAT_ID")


def send(msg):
    url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
      url,
      json={
        "chat_id":CHAT_ID,
        "text":msg
      },
      timeout=20
    )


def fetch_pairs():

    url="https://api.dexscreener.com/latest/dex/search?q=solana"

    r=requests.get(
      url,
      timeout=20
    )

    data=r.json()

    return data.get("pairs",[])[:100]


def valid(p):

    try:

        mc=float(p.get("fdv") or 0)

        liq=float(
         (p.get("liquidity") or {}).get("usd") or 0
        )

        vol=float(
         (p.get("volume") or {}).get("h24") or 0
        )

        # LONGGARIN FILTER
        if mc<10000 or mc>250000:
            return False

        if liq<3000:
            return False

        if vol<3000:
            return False

        return True

    except:
        return False


def score(p):

    try:

        mc=float(
         p.get("fdv") or 1
        )

        vol=float(
         (p.get("volume") or {}).get("h24") or 0
        )

        liq=float(
         (p.get("liquidity") or {}).get("usd") or 0
        )

        tx=(p.get("txns") or {}).get(
           "h24",{}
        )

        buys=float(
         tx.get("buys") or 0
        )

        s=(
          min(vol/5000,30)+
          min(liq/5000,30)+
          min(buys/10,20)+
          (20 if mc<60000 else 10)
        )

        return round(s,2)

    except:
        return 0


def run_scanner():

    pairs=fetch_pairs()

    picks=[]
    watchlist=[]

    for p in pairs:

        if valid(p):

            s=score(p)

            token={
              "symbol":
               p.get(
                "baseToken",{}
               ).get(
                "symbol","?"
               ),

              "score":s,

              "mc":
                int(
                 float(
                  p.get("fdv") or 0
                 )
                )
            }

            if s>60:
                picks.append(token)

            elif s>35:
                watchlist.append(token)


    picks=sorted(
      picks,
      key=lambda x:x["score"],
      reverse=True
    )[:3]


    watchlist=sorted(
      watchlist,
      key=lambda x:x["score"],
      reverse=True
    )[:3]


    msg="🚀 MEME SCANNER REPORT\n\n"


    if picks:

        msg+="A+ PICKS\n"

        for i,p in enumerate(
         picks,
         1
        ):
            msg+=(
             f"{i}. "
             f"{p['symbol']} "
             f"(Score {p['score']}) "
             f"MC ${p['mc']}\n"
            )

    if watchlist:

        msg+="\nWATCHLIST\n"

        for i,p in enumerate(
          watchlist,
          1
        ):
            msg+=(
             f"{i}. "
             f"{p['symbol']} "
             f"(Score {p['score']})\n"
            )


    if not picks and not watchlist:
        msg="No setups today."


    msg += (
      "\n\nRule:\n"
      "SL -20%\n"
      "Profit Lock +30%"
    )

    send(msg)


if __name__=="__main__":
    run_scanner()
