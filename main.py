import os,time,requests,re
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
