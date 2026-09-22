"""Hashrate Index(hashrateindex.com) 데이터 수집.

api.hashrateindex.com/graphql은 API 키가 필요하지만, 사이트가 쓰는
data.hashrateindex.com/hi-api/* REST 프록시는 키 없이 열려 있다.

  span=ALL은 bucket=7D(주봉)만 허용, 일봉은 span=5Y까지.

사용: python scripts/fetch_hashrateindex.py  -> outputs/data/hashrateindex_*.csv
"""

import csv
import json
import urllib.request
from pathlib import Path

BASE = "https://data.hashrateindex.com/hi-api/hashrateindex"
OUT = Path("outputs/data")


def get(path):
    req = urllib.request.Request(f"{BASE}/{path}", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["data"]


def write(name, rows, header):
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"{name}.csv"
    with p.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(p, len(rows))


def hashprice(currency, span, bucket):
    rows = get(f"hashprice?hashunit=PHS&currency={currency}&span={span}&bucket={bucket}")
    return sorted((r["timestamp"][:10], r["price"]) for r in rows)


if __name__ == "__main__":
    # 주봉 전체 기간(2016-12~). currency=BTC는 BTC/PH/Day 표시 해시프라이스다.
    write("hashrateindex_hashprice_usd_7d", hashprice("USD", "ALL", "7D"), ["date", "usd_per_ph_day"])
    write("hashrateindex_hashprice_btc_7d", hashprice("BTC", "ALL", "7D"), ["date", "btc_per_ph_day"])
    # 일봉은 최근 5년치만 제공
    write("hashrateindex_hashprice_usd_1d", hashprice("USD", "5Y", "1D"), ["date", "usd_per_ph_day"])

    price = get("coin/bitcoin/price?span=ALL&bucket=7D")
    write("hashrateindex_btc_price_7d",
          sorted((r["openTime"][:10], r["closePrice"]) for r in price),
          ["date", "close_usd"])
