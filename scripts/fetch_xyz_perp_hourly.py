import json, time, urllib.request, csv
def post(p):
    r=urllib.request.Request("https://api.hyperliquid.xyz/info",data=json.dumps(p).encode(),
                             headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(r,timeout=30) as f: return json.load(f)
def dump(coin,start,end,out):
    c=post({"type":"candleSnapshot","req":{"coin":coin,"interval":"1h","startTime":start,"endTime":end}})
    rows=[(time.strftime("%Y-%m-%d %H:%M",time.gmtime(x["t"]/1000)),float(x["c"]),float(x["h"]),float(x["l"]),float(x["v"])) for x in c]
    with open(out,"w",newline="") as f:
        w=csv.writer(f); w.writerow(["ts","close","high","low","base_volume"]); w.writerows(rows)
    print(coin,len(rows),rows[0],rows[-1])
import calendar,datetime
def ms(y,m,d,h=0): return calendar.timegm((y,m,d,h,0,0,0,0,0))*1000
dump("xyz:CBRS",ms(2026,5,13),ms(2026,5,15,1),"outputs/data/tradexyz_cbrs_perp_hourly.csv")
dump("xyz:SPCX",ms(2026,6,11),ms(2026,6,13,1),"outputs/data/tradexyz_spcx_perp_hourly.csv")
