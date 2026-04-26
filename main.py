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
    # cari meme related pairs instead of generic solana
    queries=[
      "meme",
      "doge",
      "pepe",
      "solana"
    ]

    pairs=[]

    for q in queries:

        try:
            url=f"https://api.dexscreener.com/latest/dex/search?q={q}"

            r=requests.get(
               url,
               timeout=20
            )

            data=r.json()

            pairs += data.get(
               "pairs",
               []
            )[:40]

        except:
            pass

    return pairs


def score(p):

    try:

        liq=float(
         (p.get("liquidity") or {}).get("usd") or 0
        )

        vol=float(
         (p.get("volume") or {}).get("h24") or 0
        )

        tx=(p.get("txns") or {}).get(
           "h24",{}
        )

        buys=float(
         tx.get("buys") or 0
        )

        # much simpler alpha score
        s=(
         min(liq/1000,30)+
         min(vol/1000,40)+
         min(buys/5,30)
        )

        return round(s,2)

    except:
        return 0


def run_scanner():

    pairs=fetch_pairs()

    ranked=[]

    seen=set()

    for p in pairs:

        try:

            symbol=p.get(
              "baseToken",{}
            ).get(
              "symbol","?"
            )

            if symbol in seen:
                continue

            seen.add(symbol)

            s=score(p)

            if s>15:   # jauh dilonggarkan
                ranked.append({
                  "symbol":symbol,
                  "score":s
                })

        except:
            pass


    ranked=sorted(
      ranked,
      key=lambda x:x["score"],
      reverse=True
    )[:5]


    if not ranked:
        send("No setups today.")
        return


    msg="🚀 TOP MEME MOMENTUM PICKS\n\n"

    for i,p in enumerate(
      ranked,
      1
    ):
        msg+=(
         f"{i}. "
         f"{p['symbol']} "
         f"| Score {p['score']}\n"
        )

    msg+=(
      "\nPotential Zone:\n"
      "2x-10x momentum watchlist\n\n"
      "SL -20%\n"
      "Profit Lock +30%"
    )

    send(msg)


if __name__=="__main__":
    run_scanner()
