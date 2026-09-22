"""
Refresh the hype_price_usd column of hype_etf_inflows_vs_price_ytd.csv directly
from CoinGecko (coin id "hyperliquid", market_chart range), keeping the ETF
inflow columns unchanged. Adds any newly-available trailing date (price only).
"""
import datetime as dt
import requests
import pandas as pd

CSV = "outputs/data/hype_etf_inflows_vs_price_ytd.csv"
FROM = int(dt.datetime(2025, 12, 31, tzinfo=dt.timezone.utc).timestamp())
TO = int(dt.datetime(2026, 6, 5, tzinfo=dt.timezone.utc).timestamp())

url = ("https://api.coingecko.com/api/v3/coins/hyperliquid/market_chart/range"
       f"?vs_currency=usd&from={FROM}&to={TO}")
r = requests.get(url, headers={"accept": "application/json"}, timeout=30)
r.raise_for_status()
prices = r.json()["prices"]

# CoinGecko daily snapshots at 00:00 UTC -> map date -> price
cg = {}
for ts_ms, px in prices:
    d = dt.datetime.fromtimestamp(ts_ms / 1000, tz=dt.timezone.utc).date()
    cg[pd.Timestamp(d)] = px

df = pd.read_csv(CSV, parse_dates=["date"])

# extend with any new trailing dates present in CoinGecko within YTD
last = df["date"].max()
new_dates = sorted(d for d in cg if d > last and d <= pd.Timestamp("2026-06-04"))
for d in new_dates:
    df = pd.concat([df, pd.DataFrame([{"date": d}])], ignore_index=True)

df = df.sort_values("date").reset_index(drop=True)

# overwrite price from CoinGecko (leave ETF inflow columns untouched)
matched = df["date"].map(cg)
before = df["hype_price_usd"].copy()
df["hype_price_usd"] = matched.fillna(df["hype_price_usd"])

changed = (before.round(6) != df["hype_price_usd"].round(6)) & before.notna()
df.to_csv(CSV, index=False)
print(f"CoinGecko points: {len(cg)}  | csv rows: {len(df)}  | new dates added: {len(new_dates)}")
print(f"existing prices changed: {int(changed.sum())}")
print(df.tail(4).to_string(index=False))
