"""
Rebuild hip3_ma_volume_vs_hype_ytd.csv with HIP-3 daily volume sourced from
the authoritative S3 extraction (outputs/data/hip3_daily_volume_ytd.csv,
built by scripts/hip3_extract.py from Hyperliquid node_fills_by_block).

NOTE: previously this script used hand-entered ASXN dashboard numbers that were
~4-5x too low (mean $0.41B/day vs the true $1.74B/day shown on ASXN). The S3
extraction matches the ASXN dashboard ($B scale, ~$6B peak) and is now the source.

HYPE price column is carried over unchanged from the existing CSV (CoinGecko).
Moving averages use min_periods=1 (no pre-2026 history available in the S3 file),
so the first ~30 days reflect a ramp rather than a fully seeded 30d window.
"""
import pandas as pd

SRC = "outputs/data/hip3_daily_volume_ytd.csv"   # authoritative S3 daily volume
CSV = "outputs/data/hip3_ma_volume_vs_hype_ytd.csv"
YTD_START = "2026-01-01"

df = pd.read_csv(SRC, parse_dates=["date"]).sort_values("date").reset_index(drop=True)
df = df[df["date"] >= YTD_START].reset_index(drop=True)
df["hip3_vol_ma14"] = df["hip3_volume_usd"].rolling(14, min_periods=1).mean()
df["hip3_vol_ma30"] = df["hip3_volume_usd"].rolling(30, min_periods=1).mean()

# carry HYPE price (CoinGecko) from existing CSV
old = pd.read_csv(CSV, parse_dates=["date"])
df = df.merge(old[["date", "hype_price_usd"]], on="date", how="left")

# align to the date range the price series covers (drops any trailing partial day)
df = df[df["hype_price_usd"].notna()].reset_index(drop=True)

df.to_csv(CSV, index=False)
print(f"Wrote {len(df)} rows to {CSV}")
print(df.head(3).to_string(index=False))
print("...")
print(df.tail(3).to_string(index=False))
