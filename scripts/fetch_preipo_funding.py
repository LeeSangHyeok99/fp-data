"""대표 프리IPO 퍼프 3종의 펀딩 히스토리 (Binance USD-M).

  SPCX       SpaceX      2026-05-21 상장, 06-12 나스닥 IPO 후 PREMARKET → EQUITY
  OPENAI     OpenAI      2026-05-26 상장
  ANTHROPIC  Anthropic   2026-06-02 상장

연환산 = fundingRate x (24/정산주기시간) x 365. 주기는 /fapi/v1/fundingInfo 의
fundingIntervalHours 로 종목마다 확인한다. 4시간짜리가 섞여 있어 3배로 박으면
안 된다.

출력: outputs/data/preipo_funding_8h.csv  (symbol, time, funding_rate, annualized_pct)
"""

import datetime as dt
import json
import time
import urllib.request
from pathlib import Path

import pandas as pd

FAPI = "https://fapi.binance.com"
SYMBOLS = ["SPCXUSDT", "OPENAIUSDT", "ANTHROPICUSDT"]


def utc_ms(s):
    return int(dt.datetime.strptime(s, "%Y-%m-%d")
               .replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


START = utc_ms("2026-05-01")   # 셋 다 상장 전
END = utc_ms("2026-08-08")     # 오늘 24:00 UTC


def get(url, tries=6):
    for i in range(tries):
        try:
            return json.load(urllib.request.urlopen(url, timeout=40))
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(4 * (i + 1))


def hours(sym):
    """정산 주기(시간). fundingInfo 에 없으면 바이낸스 기본값 8."""
    for r in get(f"{FAPI}/fapi/v1/fundingInfo"):
        if r["symbol"] == sym:
            return int(r["fundingIntervalHours"])
    return 8


def history(sym):
    rows, cur = [], START
    while True:
        page = get(f"{FAPI}/fapi/v1/fundingRate?symbol={sym}"
                   f"&startTime={cur}&endTime={END}&limit=1000")
        if not page:
            break
        rows += page
        if len(page) < 1000:
            break
        cur = page[-1]["fundingTime"] + 1
    return rows


def main():
    out = []
    for sym in SYMBOLS:
        h = hours(sym)
        rows = history(sym)
        df = pd.DataFrame({
            "symbol": sym.replace("USDT", ""),
            "time": pd.to_datetime([r["fundingTime"] for r in rows], unit="ms"),
            "funding_rate": [float(r["fundingRate"]) for r in rows],
        })
        df["annualized_pct"] = df["funding_rate"] * (24 / h) * 365 * 100
        out.append(df)
        print(f"{sym:14s} {h}h  n={len(df):4d}  "
              f"{df['time'].iloc[0]:%Y-%m-%d} ~ {df['time'].iloc[-1]:%Y-%m-%d}  "
              f"avg {df['annualized_pct'].mean():+.2f}%  "
              f"min {df['annualized_pct'].min():+.1f}  "
              f"max {df['annualized_pct'].max():+.1f}  "
              f"zeros {(df['annualized_pct'] == 0).sum()}")

    Path("outputs/data").mkdir(parents=True, exist_ok=True)
    pd.concat(out).to_csv("outputs/data/preipo_funding_8h.csv", index=False)


if __name__ == "__main__":
    main()
