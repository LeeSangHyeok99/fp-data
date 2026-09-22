"""rwa.xyz 자산클래스별 시계열 수집 + YoY 계산.

tRPC 응답은 base64 -> gzip -> 바이트역순 JSON으로 감싸여 있고, base64 앞뒤로
랜덤 문자열이 붙는다. query()가 그걸 풀어준다.

주의: rwa.xyz는 자산을 뒤늦게 색인하면 그 자산의 과거 데이터가 통째로 없다.
(Asset-Backed Credit이 2025-09에 $0.9B -> $12.8B로 점프한 건 Figure 온보딩이지
시장 성장이 아니다.) 그래서 '전체' YoY에는 커버리지 확장이 섞인다. 1년 전에도
값이 있던 자산만 남긴 코호트 YoY가 like-for-like 성장률이라 둘 다 출력한다.

사용: python scripts/fetch_rwaxyz_asset_classes.py [기준일 YYYY-MM-DD]
출력: outputs/data/rwaxyz_asset_class_yoy.csv
"""
import base64
import datetime as dt
import json
import re
import sys
import urllib.parse
import urllib.request
import zlib
from pathlib import Path

import pandas as pd

BASE = "https://app.rwa.xyz/api/trpc/tokenTimeseries.queryTimeseries"
OUT = Path("outputs/data/rwaxyz_asset_class_yoy.csv")

# rwa.xyz asset_class_id -> 표시 이름
CLASSES = {51: "Asset-Backed Credit", 32: "Corporate Credit", 42: "Diversified Credit",
           55: "Specialty Finance", 27: "US Treasury Debt", 34: "Stocks", 37: "Commodities",
           30: "non-US Government Debt", 35: "Private Equity", 36: "Real Estate",
           52: "Active Strategies", 56: "Venture Capital"}

# 차트 지표 -> 구성 자산클래스. Stablecoins(28)는 RWA 총계에서 제외한다.
METRICS = {
    "Total RWA Value": list(CLASSES.values()),
    "U.S. T-Bills (RWA)": ["US Treasury Debt"],
    "Private Credit (RWA)": ["Asset-Backed Credit", "Corporate Credit",
                             "Diversified Credit", "Specialty Finance"],
    "Stocks (RWA)": ["Stocks"],
    "Commodities (RWA)": ["Commodities"],
}


def query(measure, group_by="asset_class", since="2025-06-01", extra_filters=None):
    filters = [{"field": "measure_slug", "operator": "equals", "value": measure},
               {"field": "date", "operator": "gte", "value": since}]
    filters += extra_filters or []
    inp = {"query": {
        "aggregate": {"groupBy": group_by, "aggregateFunction": "sum",
                      "interval": "day", "mode": "stock", "groupLimit": 500},
        "filter": {"operator": "and", "filters": filters},
        "sort": {"direction": "asc", "field": "date"},
        "pagination": {"page": 1, "perPage": 500},
    }}
    req = urllib.request.Request(
        BASE + "?input=" + urllib.parse.quote(json.dumps(inp)),
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                               "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36",
                 "Referer": "https://app.rwa.xyz/", "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=120) as r:
        raw = json.loads(r.read())["result"]["data"]
    # base64 본문은 '=' 패딩에서 끝난다. 패딩이 없으면 4의 배수로 자르고 남는
    # 쓰레기는 decompressobj가 unused_data로 버린다.
    s = re.match(r"[A-Za-z0-9+/]+={0,2}", raw[raw.index("H4sIA"):]).group(0)
    if not s.endswith("="):
        s = s[:len(s) // 4 * 4]
    b = base64.b64decode(s, validate=False)
    return json.loads(zlib.decompressobj(31).decompress(b)[::-1])


def class_frame(cid, since):
    """자산클래스 하나의 자산별 시가총액 시계열 DataFrame."""
    d = query("market_value_dollar", group_by="asset", since=since,
              extra_filters=[{"field": "asset_class_id", "operator": "equals", "value": cid}])
    S = {r["group"]["name"]: pd.Series({dt.date.fromisoformat(a): v for a, v in r["points"]})
         for r in d["results"] if r["points"]}
    return pd.DataFrame(S).sort_index() if S else pd.DataFrame()


def main(d=None):
    D = dt.date.fromisoformat(d) if d else dt.date.today() - dt.timedelta(days=1)
    P = D - dt.timedelta(days=365)
    since = (P - dt.timedelta(days=60)).isoformat()

    frames = {}
    for cid, name in CLASSES.items():
        frames[name] = class_frame(cid, since)
        print(f"{name:26} assets_with_data={len(frames[name].columns)}")

    rows = []
    for metric, cols in METRICS.items():
        an = ab = cn = cb = 0.0
        for c in cols:
            df = frames[c]
            if df.empty:
                continue
            now = df.apply(lambda s: s.asof(D))
            before = df.apply(lambda s: s.asof(P))
            coh = before.notna() & (before > 0) & now.notna()
            an += now.fillna(0).sum()
            ab += before.fillna(0).sum()
            cn += now[coh].sum()
            cb += before[coh].sum()
        rows.append({"metric": metric, "date": D, "prev_date": P,
                     "all_now": an, "all_prev": ab,
                     "all_yoy_pct": (an / ab - 1) * 100 if ab else None,
                     "cohort_now": cn, "cohort_prev": cb,
                     "cohort_yoy_pct": (cn / cb - 1) * 100 if cb else None})

    out = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    print(f"\n기준일 D={D}, 비교일 P={P}")
    print(out[["metric", "all_yoy_pct", "cohort_yoy_pct", "cohort_now", "cohort_prev"]]
          .round(0).to_string(index=False))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
