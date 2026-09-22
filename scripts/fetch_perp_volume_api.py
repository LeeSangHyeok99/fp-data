"""알트 퍼프 vs 주식 퍼프 30일 평균 일거래대금 (실API).

  알트  : Binance USD-M USDT 퍼프, 시총 상위 30 알트 (BTC/ETH/스테이블 제외)
  주식  : Binance underlyingType=EQUITY 퍼프 + Hyperliquid HIP-3 주식/지수 퍼프

출력: outputs/data/equity_vs_alt_perp_volume_api.csv (30일 이동평균, 단위 $B)
"""

import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

START = int(time.mktime(time.strptime("2025-11-25", "%Y-%m-%d"))) * 1000
END = int(time.mktime(time.strptime("2026-08-07", "%Y-%m-%d"))) * 1000
FAPI = "https://fapi.binance.com"

# 주식 퍼프 판정은 exchangeInfo 의 underlyingType 으로 한다.
# 이 필드는 7종이고, "EQUITY" 하나만 보면 미국 밖 상장사와 프리IPO 계약이 통째로
# 빠진다. 실제로 그렇게 빠졌던 종목:
#   PREMARKET  OPENAI, ANTHROPIC        (sub=['Pre-IPO','TradFi'])
#   KR_EQUITY  SAMSUNG, SKHYNIX, HYUNDAI
#   HK_EQUITY  TENCENT, ZHIPU, MINIMAX 등 7종
# COMMODITY(XAU, CL 등 8종)와 INDEX(BTCDOM, DEFI, ALL)는 주식이 아니라 제외.
# 참고: SPCX 는 2026-06-12 나스닥 상장 후 PREMARKET → EQUITY 로 재분류됐다.
EQUITY_TYPES = {"EQUITY", "HK_EQUITY", "KR_EQUITY", "PREMARKET"}

# 알트 라인이 단일종목 30개라서, 주식 라인도 단일종목으로 맞춘다. 지수/ETF
# 바스켓을 섞으면 사과 대 오렌지가 된다. 실제로 HL 의 XYZ100(100종목 바스켓)
# 하나가 2026-01-10 시작값의 76% 를 차지하고 있었다.
# 확실한 것만 넣는다. 애매한 티커는 단일종목으로 남긴다.
BINANCE_ETF = {"QQQ", "SPY", "SOXL", "SOXS", "IWM", "XLE", "XBI", "EWY", "EWJ",
               "EWT", "EWZ", "URNM", "UVXY", "TQQQ", "SQQQ", "TMF", "TBT",
               "BITO", "SMH", "KORU", "TZA", "KWEB",
               # 2026-08 신규 상장분. CSOP*2L 은 2배 레버리지 ETF 라서 지금
               # 라인을 지배하는 SK하이닉스/삼성 익스포저를 한 번 더 얹는다.
               "GDX", "KODEX200", "CSOPSAMSUNG2L", "CSOPSKHYNIX2L"}

# 같은 기초자산이 두 계약으로 잡히는 것들. 명목을 두 번 세지 않는다.
#   SKHY  = SK하이닉스 ADR (1 ADR : 1/7 주). SKHYNIX(KR) 과 같은 회사
#   SPCXUSD1 = SPCXUSDT 와 같은 SpaceX, 담보자산만 USD1
DUP_SYMBOLS = {"SKHYUSDT", "SPCXUSD1"}
HL_BASKET = {"XYZ100", "US500", "USTECH", "USA500", "USA100", "JPN225", "SEMI",
             "SMALL2000", "GLDMINE", "USENERGY", "MAG7", "SEMIS", "ROBOT",
             "INFOTECH", "NUCLEAR", "DEFENSE", "ENERGY", "BIOTECH", "KWEB",
             "EWY", "H100"}

# 시총 상위 알트 (CoinGecko 2026-08-06 스냅샷, 스테이블/래핑 제외)
MCAP30 = ["BNB", "XRP", "SOL", "TRX", "HYPE", "DOGE", "ZEC", "ADA", "XMR", "LINK",
          "XLM", "BCH", "LTC", "HBAR", "AVAX", "1000SHIB", "SUI", "XAUT", "UNI",
          "NEAR", "TAO", "DOT", "AAVE", "APT", "ETC", "ARB", "ICP", "FIL"]
# HIP-3에서 주식이 아닌 것 (원자재, FX, 금리, 크립토, 변동성)
NON_EQUITY = {"GOLD", "SILVER", "PLATINUM", "PALLADIUM", "COPPER", "ALUMINIUM",
              "URANIUM", "NATGAS", "CL", "BRENTOIL", "OIL", "GAS", "WTI", "USOIL",
              "CORN", "WHEAT", "SOY", "TTF", "JPY", "EUR", "GBP", "KRW", "DXY",
              "USBOND", "10Y", "BTC", "ETH", "XMR", "USDE", "TOTAL2", "OTHERS",
              "BTCD", "VIX", "VOL", "PURRDAT"}


def get(url, tries=6):
    for i in range(tries):
        try:
            return json.load(urllib.request.urlopen(url, timeout=40))
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(5 * (i + 1))  # 429 백오프


def hl_info(payload, tries=6):
    for i in range(tries):
        try:
            req = urllib.request.Request(
                "https://api.hyperliquid.xyz/info", data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"})
            return json.load(urllib.request.urlopen(req, timeout=40))
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(5 * (i + 1))  # 429 백오프


def binance_daily(symbols):
    """일별 quote volume (USD 명목)."""
    def one(sym):
        try:
            rows = get(f"{FAPI}/fapi/v1/klines?symbol={sym}&interval=1d"
                       f"&startTime={START}&endTime={END}&limit=500")
        except Exception as e:
            print("skip", sym, e)
            return sym, {}
        return sym, {time.strftime("%Y-%m-%d", time.gmtime(r[0] / 1000)): float(r[7])
                     for r in rows}

    with ThreadPoolExecutor(max_workers=3) as pool:
        return dict(pool.map(one, symbols))


def hyperliquid_daily(coins):
    """HIP-3 일별 USD 명목 (캔들 base volume x 평균가). dayNtlVlm 대비 수% 이내."""
    def one(coin):
        c = hl_info({"type": "candleSnapshot", "req": {
            "coin": coin, "interval": "1d", "startTime": START, "endTime": END}})
        out = {}
        for k in c or []:
            px = (float(k["o"]) + float(k["h"]) + float(k["l"]) + float(k["c"])) / 4
            day = time.strftime("%Y-%m-%d", time.gmtime(k["t"] / 1000))
            out[day] = out.get(day, 0) + float(k["v"]) * px
        return coin, out

    with ThreadPoolExecutor(max_workers=3) as pool:
        return dict(pool.map(one, coins))


def main():
    ex = get(f"{FAPI}/fapi/v1/exchangeInfo")
    alt_syms = [a + "USDT" for a in MCAP30
                if any(s["symbol"] == a + "USDT" for s in ex["symbols"])]
    eq_syms = [s["symbol"] for s in ex["symbols"]
               if s.get("underlyingType") in EQUITY_TYPES
               and s["baseAsset"] not in BINANCE_ETF
               and s["symbol"] not in DUP_SYMBOLS]
    print(f"binance: 알트 {len(alt_syms)}, 주식 {len(eq_syms)}")

    coins = []
    for d in [x["name"] for x in hl_info({"type": "perpDexs"}) if x]:
        if d == "hyna":  # 크립토 전용 dex
            continue
        coins += [a["name"] for a in hl_info({"type": "meta", "dex": d})["universe"]]
    eq_coins = [c for c in coins
                if c.split(":", 1)[1] not in NON_EQUITY | HL_BASKET]
    print(f"hyperliquid HIP-3 주식/지수 {len(eq_coins)}")

    # HL 메인 dex 의 같은 알트 30종. 파랑 라인의 거래소 집합을 주황과 맞추려면
    # 필요하다. 1000SHIB 는 HL 에서 kSHIB, XAUT 는 상장이 없다.
    hl_main = {a["name"] for a in hl_info({"type": "meta"})["universe"]}
    alt_coins = [c for c in [{"1000SHIB": "kSHIB"}.get(a, a) for a in MCAP30]
                 if c in hl_main]
    print(f"hyperliquid 알트 {len(alt_coins)}")

    def total(d):
        f = pd.DataFrame(d).sort_index().fillna(0)
        f.index = pd.to_datetime(f.index)
        return f.sum(axis=1)

    df = pd.DataFrame({
        "alt_binance": total(binance_daily(alt_syms)),
        "alt_hyperliquid": total(hyperliquid_daily(alt_coins)),
        "equity_binance": total(binance_daily(eq_syms)),
        "equity_hyperliquid": total(hyperliquid_daily(eq_coins)),
    }).fillna(0).sort_index()

    ma = df.rolling(30).mean()
    ma["alt_total"] = ma["alt_binance"] + ma["alt_hyperliquid"]
    ma["equity_total"] = ma["equity_binance"] + ma["equity_hyperliquid"]
    out = (ma.loc["2026-01-10":] / 1e9).round(4)
    out.index.name = "date"
    Path("outputs/data").mkdir(parents=True, exist_ok=True)
    out.to_csv("outputs/data/equity_vs_alt_perp_volume_api.csv")
    print(out.iloc[[0, -1]].to_string())


if __name__ == "__main__":
    main()
