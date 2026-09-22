"""
Rebuild hype_pe_buyback_ytd.csv from source APIs.

P/E = HYPE market cap / annualized Assistance Fund buyback run-rate
  - 14d line: mcap / (14d MA daily buyback x 365)
  - 30d line: mcap / (30d MA daily buyback x 365)

Sources (live):
  - Buybacks: ASXN  api-data.asxn.xyz/api/data/hl-buybacks
      daily Assistance Fund buyback notional USD (field "ntl").
      Cross-check: vs DefiLlama Hyperliquid daily revenue (buyback/rev ~0.86 YTD).
  - Market cap: CoinGecko coins/hyperliquid/market_chart/range ("market_caps"),
      first (00:00 UTC) snapshot per day.

Buyback history is pulled from SEED_START so the 30d moving average is fully
seeded by YTD_START; the output is then clipped to [YTD_START, END_DATE].

Usage:
  .venv/bin/python scripts/build_hype_pe_buyback.py
"""
import datetime as dt
import requests
import pandas as pd

CSV = "outputs/data/hype_pe_buyback_ytd.csv"
YTD_START = pd.Timestamp("2026-01-01")
END_DATE = pd.Timestamp("2026-06-03")   # last full day to include
SEED_START = dt.datetime(2025, 12, 1, tzinfo=dt.timezone.utc)  # >30d before YTD
TRADING_DAYS = 365  # annualization factor (buybacks run daily, incl. weekends)


def fetch_buybacks():
    """ASXN daily Assistance Fund buyback notional USD -> {Timestamp: usd}."""
    url = "https://api-data.asxn.xyz/api/data/hl-buybacks"
    r = requests.get(url, headers={"accept": "application/json"}, timeout=30)
    r.raise_for_status()
    rows = []
    for rec in r.json():
        d = pd.Timestamp(rec["date"]).tz_localize(None).normalize()
        rows.append((d, float(rec["ntl"])))
    s = pd.DataFrame(rows, columns=["date", "buyback_usd"])
    return s.sort_values("date").reset_index(drop=True)


def fetch_marketcap():
    """CoinGecko HYPE market cap, first (00:00 UTC) snapshot per day -> {Timestamp: usd}."""
    frm = int(SEED_START.timestamp())
    to = int((END_DATE.tz_localize("UTC") + pd.Timedelta(days=1)).timestamp())
    url = ("https://api.coingecko.com/api/v3/coins/hyperliquid/market_chart/range"
           f"?vs_currency=usd&from={frm}&to={to}")
    r = requests.get(url, headers={"accept": "application/json"}, timeout=30)
    r.raise_for_status()
    mcap = {}
    for ts_ms, mc in r.json()["market_caps"]:
        d = pd.Timestamp(dt.datetime.fromtimestamp(ts_ms / 1000, tz=dt.timezone.utc).date())
        if d not in mcap:           # keep first (00:00 UTC) snapshot of each day
            mcap[d] = mc
    return mcap


def main():
    df = fetch_buybacks()
    df = df[df["date"] >= pd.Timestamp(SEED_START.date())].reset_index(drop=True)

    # annualized buyback run-rate (rolling MA of daily notional x 365)
    df["ann14"] = df["buyback_usd"].rolling(14).mean() * TRADING_DAYS
    df["ann30"] = df["buyback_usd"].rolling(30).mean() * TRADING_DAYS

    # market cap (CoinGecko) joined by date
    mcap = fetch_marketcap()
    df["mcap"] = df["date"].map(mcap)

    # clip to YTD window where every input is present
    df = df[(df["date"] >= YTD_START) & (df["date"] <= END_DATE)].reset_index(drop=True)
    df = df[df["mcap"].notna()].reset_index(drop=True)

    df["pe_14d"] = df["mcap"] / df["ann14"]
    df["pe_30d"] = df["mcap"] / df["ann30"]

    df = df[["date", "mcap", "buyback_usd", "ann14", "ann30", "pe_14d", "pe_30d"]]
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    df.to_csv(CSV, index=False)

    print(f"Wrote {len(df)} rows to {CSV}")
    print(df.head(3).to_string(index=False))
    print("...")
    print(df.tail(3).to_string(index=False))


if __name__ == "__main__":
    main()
