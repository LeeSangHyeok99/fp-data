"""Onchain barbell 차트용 YoY 지표 수집.

각 지표의 일별 시계열을 받아 outputs/data/onchain_barbell_yoy_series.csv에 long 포맷으로
저장하고, 공통 기준일 D(모든 지표의 최신 가용일 중 가장 이른 날)에서 YoY를 계산해 출력한다.

- stock 지표(가격/TVL/OI/시총): D 시점 값 vs D-365 시점 값
- flow 지표(거래량/매출): D까지 30일 합 vs D-365까지 30일 합
"""
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

CACHE = Path("/private/tmp/claude-501/-Users-a--Desktop-project-fp-data/"
             "caeb09e7-0d9f-476c-ae8c-4e8fe7f3cc7e/scratchpad/cache")
CACHE.mkdir(parents=True, exist_ok=True)
OUT = Path("outputs/data/onchain_barbell_yoy_series.csv")

LLAMA = "https://api.llama.fi"


def get(url, key=None):
    """URL -> JSON. 같은 URL은 파일 캐시에서 재사용."""
    f = CACHE / (url.replace("/", "_").replace(":", "").replace("?", "_")[-120:] + ".json")
    if not f.exists():
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as r:
            f.write_bytes(r.read())
    d = json.loads(f.read_bytes())
    return d[key] if key else d


def series(pairs):
    """[[ts, v], ...] -> UTC date 인덱스 Series."""
    idx = [datetime.fromtimestamp(int(t), timezone.utc).date() for t, _ in pairs]
    s = pd.Series([float(v or 0) for _, v in pairs], index=pd.Index(idx))
    return s[~s.index.duplicated(keep="last")].sort_index()


# ---------------------------------------------------------------- 소스별 로더
def llama_chart(path):
    return series(get(f"{LLAMA}/{path}", "totalDataChart"))


def llama_protocol_tvl(slug):
    rows = get(f"{LLAMA}/protocol/{slug}", "tvl")
    return series([[r["date"], r["totalLiquidityUSD"]] for r in rows])


def category_tvl(category, top_n):
    """카테고리 상위 top_n 프로토콜의 TVL 합. 카테고리 히스토리는 유료 API라 근사."""
    protos = get(f"{LLAMA}/protocols")
    picks = sorted((p for p in protos if p.get("category") == category),
                   key=lambda p: -(p.get("tvl") or 0))[:top_n]
    slugs = [p["slug"] for p in picks]
    covered = sum(p.get("tvl") or 0 for p in picks)
    total = sum(p.get("tvl") or 0 for p in protos if p.get("category") == category)
    print(f"   {category}: 상위 {len(slugs)}개로 현재 TVL의 {covered / total:.1%} 커버")
    with ThreadPoolExecutor(8) as ex:
        parts = list(ex.map(llama_protocol_tvl, slugs))
    return pd.concat(parts, axis=1).sort_index().ffill().fillna(0).sum(axis=1)


def binance_close(symbol):
    """일봉 종가. 무료, 히스토리 제한 없음."""
    start = int((datetime.now(timezone.utc) - timedelta(days=520)).timestamp() * 1000)
    rows = get(f"https://api.binance.com/api/v3/klines?symbol={symbol}"
               f"&interval=1d&startTime={start}&limit=1000")
    return series([[k[0] // 1000, k[4]] for k in rows])


def chain_tvl():
    return series([[r["date"], r["tvl"]] for r in get(f"{LLAMA}/v2/historicalChainTvl")])


def stablecoin_mc():
    rows = get("https://stablecoins.llama.fi/stablecoincharts/all")
    return series([[r["date"], r["totalCirculatingUSD"]["peggedUSD"]] for r in rows])


# ---------------------------------------------------------------- 지표 정의
# name: (group, kind, loader)
METRICS = {
    "pump.fun Revenue":   ("Speculative", "flow", lambda: llama_chart("summary/fees/pump.fun?dataType=dailyRevenue")),
    "fomo Revenue":       ("Speculative", "flow", lambda: llama_chart("summary/fees/fomo?dataType=dailyRevenue")),
    "Polymarket Volume":  ("Speculative", "flow", lambda: llama_chart("summary/dexs/polymarket")),
    "Polymarket OI":      ("Speculative", "stock", lambda: llama_chart("summary/open-interest/polymarket")),
    "Kalshi Volume":      ("Speculative", "flow", lambda: llama_chart("summary/dexs/kalshi")),
    "Kalshi OI":          ("Speculative", "stock", lambda: llama_chart("summary/open-interest/kalshi")),
    "Perp DEXs OI":       ("Speculative", "stock", lambda: llama_chart("overview/open-interest?excludeTotalDataChartBreakdown=true")),
    "BTC Price":          ("Onchain Native", "stock", lambda: binance_close("BTCUSDT")),
    "ETH Price":          ("Onchain Native", "stock", lambda: binance_close("ETHUSDT")),
    "DeFi TVL":           ("Onchain Native", "stock", chain_tvl),
    "LST TVL":            ("Onchain Native", "stock", lambda: category_tvl("Liquid Staking", 15)),
    "Restaking TVL":      ("Onchain Native", "stock", lambda: category_tvl("Restaking", 8)),
    "DEX Spot Volume":    ("Onchain Native", "flow", lambda: llama_chart("overview/dexs?excludeTotalDataChartBreakdown=true")),
    "Stablecoin MC":      ("TradFi-linked", "stock", stablecoin_mc),
    "Total RWA Value":    ("TradFi-linked", "stock", lambda: category_tvl("RWA", 25)),
}


def yoy(s, kind, d):
    """기준일 d에서의 YoY(%). 데이터가 없으면 None."""
    prev = d - timedelta(days=365)
    if kind == "stock":
        now, before = s.asof(d), s.asof(prev)
    else:  # flow: 30일 합
        now = s[(s.index > d - timedelta(days=30)) & (s.index <= d)].sum()
        before = s[(s.index > prev - timedelta(days=30)) & (s.index <= prev)].sum()
    if not before or pd.isna(before) or pd.isna(now):
        return None
    return (now / before - 1) * 100


def main():
    data = {}
    for name, (_, _, load) in METRICS.items():
        print(f"-> {name}")
        data[name] = load()

    # 시리즈 저장 (long)
    long = pd.concat(
        [pd.DataFrame({"metric": n, "date": s.index, "value": s.values}) for n, s in data.items()]
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT, index=False)

    # 각 지표의 최신 가용일 -> 공통 기준일 D
    latest = {n: s.index.max() for n, s in data.items()}
    d = min(latest.values())
    print(f"\n공통 기준일 D = {d}  (지표별 최신일 중 가장 이른 날)")
    print(f"{'metric':22} {'latest':12} {'YoY@D':>10}   {'YoY@latest':>10}")
    for n, s in data.items():
        g = yoy(s, METRICS[n][1], d)
        gl = yoy(s, METRICS[n][1], latest[n])
        f = lambda v: "n/a" if v is None else f"{v:+.0f}%"
        print(f"{n:22} {str(latest[n]):12} {f(g):>10}   {f(gl):>10}")


if __name__ == "__main__":
    main()
