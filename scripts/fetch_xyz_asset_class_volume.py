"""Daily notional volume per xyz (HIP-3) market from Hyperliquid candleSnapshot.

v * typical price per 1d candle reproduces dayNtlVlm for HIP-3 markets.
Output: outputs/data/xyz_daily_volume_by_coin.csv (date, coin, notional_usd)
"""
import csv, json, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

URL = "https://api.hyperliquid.xyz/info"
START = 1767139200000   # 2025-12-31 00:00 UTC (Q1 + Q2 2026)
END = 1783036800000   # 2026-07-03 00:00 UTC


def post(payload):
    req = urllib.request.Request(URL, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            if attempt == 7:
                raise
            time.sleep(5 * (attempt + 1))


coins = [c["name"] for c in post({"type": "meta", "dex": "xyz"})["universe"]]


def fetch(coin):
    candles = post({"type": "candleSnapshot", "req": {
        "coin": coin, "interval": "1d", "startTime": START, "endTime": END}}) or []
    rows = []
    for c in candles:
        px = (float(c["h"]) + float(c["l"]) + float(c["o"]) + float(c["c"])) / 4
        rows.append((time.strftime("%Y-%m-%d", time.gmtime(c["t"] / 1000)),
                     coin.split(":")[-1], float(c["v"]) * px))
    return rows


with ThreadPoolExecutor(max_workers=3) as ex:
    out = [r for rows in ex.map(fetch, coins) for r in rows]

out.sort()
with open("outputs/data/xyz_daily_volume_by_coin.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["date", "coin", "notional_usd"])
    w.writerows(out)
print(len(out), "rows,", len(coins), "coins")
