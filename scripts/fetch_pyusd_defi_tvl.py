"""
Fetch PYUSD DeFi TVL daily time series from DefiLlama yields API.

Steps:
1. Pull all yield pools from https://yields.llama.fi/pools
2. Filter for PYUSD-relevant pools (symbol contains PYUSD/PYUSD0/SUSDAI)
3. Fetch per-pool historical chart from https://yields.llama.fi/chart/{pool_id}
4. Aggregate daily tvlUsd into per-protocol columns + pure/with-SUSDAI totals
5. Save raw JSON + daily CSV + monthly CSV under outputs/data/

Note: SUSDAI (USD AI synthetic) is backed partially by PYUSD but its pool TVL
includes non-PYUSD assets, so it is excluded from the "pure" PYUSD aggregate
and reported separately in the with-SUSDAI column.
"""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

OUT_DIR = Path("/Users/ijaheun/Desktop/Project/data/outputs/data")
OUT_DIR.mkdir(parents=True, exist_ok=True)

POOLS_URL = "https://yields.llama.fi/pools"
CHART_URL = "https://yields.llama.fi/chart/{pool_id}"

# Confirmed pool IDs (from user)
KNOWN_POOLS = {
    "712ce948-bd9e-4f4a-8916-b72c447f7578": ("USD AI / SUSDAI", "Arbitrum", "susdai"),
    "995b269a-8409-4c55-b97e-868f443b432e": ("SparkLend PYUSD", "Ethereum", "sparklend"),
    "fa55aa2b-e244-4ce4-ab00-9e96b39df32b": ("Euler V2 ePYUSD-6", "Ethereum", "euler_v2"),
    "eaece65e-ffb2-4631-a95e-7f267cb2f1ba": ("Kamino Lend PYUSD", "Solana", "kamino_lend"),
    "1e2030e0-0b74-4119-a03d-0f6a126ede33": ("Euler V2 ePYUSD-8", "Ethereum", "euler_v2"),
    "d118f505-e75f-4152-bad3-49a2dc7482bf": ("Aave V3 PYUSD", "Ethereum", "aave_v3"),
    "4d33c615-a969-4c55-9acf-49d8d14a1063": ("Spark Savings PYUSD", "Ethereum", "spark_savings"),
    "107c6769-4a4f-4279-9a5e-f181d78d09dd": ("MORE Markets PYUSD0", "Flow", "more_markets"),
    "2467d092-aeb9-4e9e-b0e7-01d8733a890e": ("Project 0 PYUSD", "Solana", "project_0"),
    "2ff19c9c-c568-44f5-b1c3-7e1704b78f1e": ("Save / Solend PYUSD", "Solana", "save"),
}

SUSDAI_POOL = "712ce948-bd9e-4f4a-8916-b72c447f7578"


def normalize_project_key(project: str) -> str:
    return (
        project.lower()
        .replace("-", "_")
        .replace(" ", "_")
        .replace(".", "")
    )


def discover_pyusd_pools() -> tuple[list[dict], list[dict]]:
    """Return (pyusd_pools, all_pools) filtered for single-asset PYUSD pools.

    DefiLlama RWA page reports 15 pools at $250m DeFi Active TVL. Those are
    single-asset PYUSD lending/savings deposits, NOT DEX LP pairs (which would
    double-count via the paired asset). So we restrict to pools whose symbol
    is exactly PYUSD or PYUSD0 (LayerZero wrap). SUSDAI is handled separately.
    """
    print(f"[1/3] Fetching pool list from {POOLS_URL} ...")
    r = requests.get(POOLS_URL, timeout=60)
    r.raise_for_status()
    payload = r.json()
    all_pools = payload.get("data", [])
    print(f"      total pools returned: {len(all_pools):,}")

    PURE_SYMBOLS = {"PYUSD", "PYUSD0"}
    matches = []
    for p in all_pools:
        sym = (p.get("symbol") or "").upper().strip()
        if sym in PURE_SYMBOLS or sym == "SUSDAI":
            matches.append(p)
    print(f"      single-asset PYUSD/PYUSD0/SUSDAI pools: {len(matches)}")
    return matches, all_pools


_SESSION = requests.Session()
_SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://defillama.com",
    "Referer": "https://defillama.com/",
})


def fetch_chart(pool_id: str, retries: int = 4) -> dict:
    url = CHART_URL.format(pool_id=pool_id)
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            r = _SESSION.get(url, timeout=60)
            if r.status_code == 403 or r.status_code == 429:
                # backoff and retry
                wait = 2 ** attempt
                time.sleep(wait)
                last_err = requests.HTTPError(f"{r.status_code} on attempt {attempt+1}")
                continue
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            last_err = e
            time.sleep(2 ** attempt)
    raise last_err if last_err else RuntimeError("fetch_chart failed")


def chart_to_df(pool_id: str, label: str, chart: dict) -> pd.DataFrame:
    rows = chart.get("data", []) or []
    if not rows:
        return pd.DataFrame(columns=["date", "pool_id", "label", "tvlUsd"])
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["timestamp"]).dt.tz_localize(None).dt.normalize()
    df = df.groupby("date", as_index=False)["tvlUsd"].last()
    df["pool_id"] = pool_id
    df["label"] = label
    return df[["date", "pool_id", "label", "tvlUsd"]]


def main() -> None:
    pyusd_pools, _ = discover_pyusd_pools()

    # Build the working set: union of KNOWN_POOLS and discovered PYUSD-symbol pools.
    # Any SUSDAI-symbol pool (regardless of host protocol — Fluid, Pendle, Morpho)
    # routes to the "susdai" bucket since the asset itself is the SUSDAI synthetic,
    # not raw PYUSD. That keeps the pure-PYUSD aggregate clean.
    pool_meta: dict[str, dict] = {}
    for p in pyusd_pools:
        pid = p.get("pool")
        if not pid:
            continue
        proj = p.get("project", "")
        sym = (p.get("symbol") or "").upper().strip()
        chain = p.get("chain", "")
        if sym == "SUSDAI":
            proto_key = "susdai"
        else:
            proto_key = normalize_project_key(proj)
        pool_meta[pid] = {
            "project": proj,
            "symbol": sym,
            "chain": chain,
            "label": f"{proj} {sym}",
            "protocol_key": proto_key,
        }

    # Overlay known pool labels to ensure consistent protocol grouping
    for pid, (label, chain, proto_key) in KNOWN_POOLS.items():
        meta = pool_meta.get(pid, {})
        meta.setdefault("project", label.split(" ")[0].lower())
        meta.setdefault("symbol", "PYUSD")
        meta["chain"] = chain
        meta["label"] = label
        meta["protocol_key"] = proto_key
        pool_meta[pid] = meta

    print(f"\n[2/3] Fetching charts for {len(pool_meta)} pools ...")
    raw_dump: dict[str, dict] = {}
    frames: list[pd.DataFrame] = []
    for i, (pid, meta) in enumerate(pool_meta.items(), 1):
        try:
            chart = fetch_chart(pid)
        except Exception as e:
            print(f"      [{i}/{len(pool_meta)}] {pid} FAILED: {e}")
            continue
        raw_dump[pid] = {"meta": meta, "chart": chart}
        df = chart_to_df(pid, meta["label"], chart)
        if not df.empty:
            df["protocol_key"] = meta["protocol_key"]
            frames.append(df)
            latest = df.sort_values("date").iloc[-1]
            print(
                f"      [{i}/{len(pool_meta)}] {meta['label']:<35} rows={len(df):>4} "
                f"latest={latest['date'].date()} tvl=${latest['tvlUsd']:,.0f}"
            )
        else:
            print(f"      [{i}/{len(pool_meta)}] {meta['label']} EMPTY")
        time.sleep(1.0)  # polite — DefiLlama 403s on burst calls

    raw_path = OUT_DIR / "pyusd_defi_tvl_raw.json"
    raw_path.write_text(json.dumps(raw_dump, indent=2, default=str))
    print(f"\n      raw written: {raw_path}")

    if not frames:
        print("No data fetched. Aborting.")
        return

    long_df = pd.concat(frames, ignore_index=True)

    # Per-pool daily wide (one column per pool_id) for traceability, plus per-protocol pivot
    proto_daily = (
        long_df.groupby(["date", "protocol_key"], as_index=False)["tvlUsd"].sum()
    )
    proto_wide = proto_daily.pivot(index="date", columns="protocol_key", values="tvlUsd").sort_index()

    # Forward-fill so totals reflect last-known TVL per pool on dates where a pool has no point
    proto_wide_ff = proto_wide.ffill().fillna(0.0)

    # SUSDAI excluded from pure
    susdai_col = "susdai" if "susdai" in proto_wide_ff.columns else None
    pure_cols = [c for c in proto_wide_ff.columns if c != susdai_col]

    proto_wide_ff["total_tvl_usd_pure"] = proto_wide_ff[pure_cols].sum(axis=1)
    proto_wide_ff["total_tvl_usd_with_susdai"] = (
        proto_wide_ff["total_tvl_usd_pure"]
        + (proto_wide_ff[susdai_col] if susdai_col else 0.0)
    )

    # Reorder columns
    front = ["total_tvl_usd_pure", "total_tvl_usd_with_susdai"]
    others = [c for c in proto_wide_ff.columns if c not in front]
    proto_wide_ff = proto_wide_ff[front + others]
    proto_wide_ff = proto_wide_ff.reset_index()
    proto_wide_ff["date"] = proto_wide_ff["date"].dt.strftime("%Y-%m-%d")

    daily_path = OUT_DIR / "pyusd_defi_tvl_daily.csv"
    proto_wide_ff.to_csv(daily_path, index=False)
    print(f"      daily CSV written: {daily_path}  rows={len(proto_wide_ff)}")

    # Monthly resample (month-end last value)
    monthly = proto_wide_ff.copy()
    monthly["date"] = pd.to_datetime(monthly["date"])
    monthly = (
        monthly.set_index("date")
        .resample("ME")
        .last()
        .reset_index()
    )
    monthly["date"] = monthly["date"].dt.strftime("%Y-%m-%d")
    monthly_path = OUT_DIR / "pyusd_defi_tvl_monthly.csv"
    monthly.to_csv(monthly_path, index=False)
    print(f"      monthly CSV written: {monthly_path}  rows={len(monthly)}")

    # Summary
    print("\n[3/3] Summary")
    print(f"      pools used: {len(pool_meta)}")
    last_row = proto_wide_ff.iloc[-1]
    first_row = proto_wide_ff.iloc[0]
    print(f"      date range: {first_row['date']} -> {last_row['date']}")
    print(f"      latest pure-PYUSD TVL : ${last_row['total_tvl_usd_pure']:>15,.0f}")
    print(f"      latest with-SUSDAI TVL: ${last_row['total_tvl_usd_with_susdai']:>15,.0f}")
    print("      per-protocol latest:")
    proto_cols = [c for c in proto_wide_ff.columns if c not in {"date", "total_tvl_usd_pure", "total_tvl_usd_with_susdai"}]
    rank = sorted(((c, float(last_row[c])) for c in proto_cols), key=lambda x: -x[1])
    for k, v in rank:
        print(f"        {k:<20} ${v:>15,.0f}")


if __name__ == "__main__":
    main()
