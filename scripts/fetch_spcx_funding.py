"""SpaceX 프리IPO 퍼프(Binance SPCXUSDT) 8시간 펀딩 히스토리.

레퍼런스 창: 2026-05-22 ~ 07-15. SPCX 상장이 05-21 16:00 UTC라 실질 전구간.
연환산 = fundingRate * 3 * 365 (8시간 정산, 하루 3회)
  정산 주기는 /fapi/v1/fundingInfo 의 fundingIntervalHours=8 로 확인함.
  일부 종목은 4시간이라 배수를 상수로 박으면 안 된다.

창 경계는 UTC 로 못박는다. time.mktime 은 로컬(KST) 기준이라 END 가 9시간
당겨지면서 7/15 16:00 UTC 정산 1건이 조용히 잘려나갔었다.

구간 평균은 끝점을 어떻게 자르냐에 ±0.2%p 흔들린다 (10.77 ~ 11.16%).
레퍼런스의 +10.9% 는 그 범위 안이지만 어떤 깔끔한 절단과도 정확히 일치하진 않는다.

출력: outputs/data/spcx_funding_8h.csv
"""

import datetime as dt
import json
import time
import urllib.request
from pathlib import Path

import pandas as pd

FAPI = "https://fapi.binance.com"
SYMBOL = "SPCXUSDT"


def utc_ms(s):
    return int(dt.datetime.strptime(s, "%Y-%m-%d")
               .replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


START = utc_ms("2026-05-01")   # 상장(05-21 16:00 UTC) 이전, 전구간 확보용
END = utc_ms("2026-07-16")     # 레퍼런스 창 종료일의 24:00 UTC


def get(url, tries=6):
    for i in range(tries):
        try:
            return json.load(urllib.request.urlopen(url, timeout=40))
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(4 * (i + 1))


def main():
    rows, cur = [], START
    while True:
        page = get(f"{FAPI}/fapi/v1/fundingRate?symbol={SYMBOL}"
                   f"&startTime={cur}&endTime={END}&limit=1000")
        if not page:
            break
        rows += page
        if len(page) < 1000:
            break
        cur = page[-1]["fundingTime"] + 1

    df = pd.DataFrame({
        "time": pd.to_datetime([r["fundingTime"] for r in rows], unit="ms"),
        "funding_rate": [float(r["fundingRate"]) for r in rows],
    })
    df["annualized_pct"] = df["funding_rate"] * 3 * 365 * 100

    Path("outputs/data").mkdir(parents=True, exist_ok=True)
    df.to_csv("outputs/data/spcx_funding_8h.csv", index=False)
    print(f"n={len(df)}  {df['time'].iloc[0]} ~ {df['time'].iloc[-1]}")
    print(f"period avg annualized = {df['annualized_pct'].mean():.2f}%")


if __name__ == "__main__":
    main()
