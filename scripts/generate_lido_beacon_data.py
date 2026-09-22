"""
Build the Lido Beacon Chain staking dataset, matching the Lido Dune chart
"ETH Staked on BeaconChain through Lido middleware".

Stacked areas (left axis, ETH):
  - Lido Core | bc only   (bottom)
  - Others    | bc only   (middle)
  - Entry queue           (top, small)
Line (right axis, %):
  - Lido Share | bc only  = Lido Core / (Lido Core + Others)

Anchored to the Dune tooltip at 2024-06-22:
  Total bc+entry 32,984,557 | Others 23,337,997 | Lido Core 9,528,160
  Entry queue 118,400 | Lido Share bc only 28.99%

Base series: outputs/data/ethereum_staked_eth.csv (= bc-only total, Lido+Others).
Output: outputs/data/lido_beacon_staked.csv
"""

import pandas as pd
from pathlib import Path

# Lido Share | bc only (%) = Lido Core / (Lido Core + Others), monthly.
# Calibrated to the purple line: ramp through 2021, ~32% peak mid-2022/2023,
# 28.99% at 2024-06, declining to ~21% by mid-2026.
SHARE = {
    '2020-12': 0.5,
    '2021-01': 4.0, '2021-02': 7.0, '2021-03': 10.0, '2021-04': 12.0,
    '2021-05': 14.0, '2021-06': 15.5, '2021-07': 16.5, '2021-08': 17.5,
    '2021-09': 18.0, '2021-10': 18.8, '2021-11': 19.2, '2021-12': 19.5,
    '2022-01': 22.0, '2022-02': 25.0, '2022-03': 28.0, '2022-04': 30.0,
    '2022-05': 31.5, '2022-06': 32.0, '2022-07': 31.5, '2022-08': 31.0,
    '2022-09': 30.8, '2022-10': 31.0, '2022-11': 31.3, '2022-12': 31.7,
    '2023-01': 31.9, '2023-02': 32.0, '2023-03': 32.0, '2023-04': 32.0,
    '2023-05': 31.9, '2023-06': 31.6, '2023-07': 31.2, '2023-08': 30.7,
    '2023-09': 30.2, '2023-10': 29.8, '2023-11': 29.4, '2023-12': 29.2,
    '2024-01': 29.2, '2024-02': 29.1, '2024-03': 29.1, '2024-04': 29.0,
    '2024-05': 29.0, '2024-06': 28.99, '2024-07': 28.9, '2024-08': 28.8,
    '2024-09': 28.7, '2024-10': 28.5, '2024-11': 28.38, '2024-12': 28.2,
    '2025-01': 27.8, '2025-02': 27.4, '2025-03': 27.0, '2025-04': 26.5,
    '2025-05': 26.0, '2025-06': 25.5, '2025-07': 25.0, '2025-08': 24.5,
    '2025-09': 24.0, '2025-10': 23.6, '2025-11': 23.2, '2025-12': 22.8,
    '2026-01': 22.4, '2026-02': 22.0, '2026-03': 21.5, '2026-04': 21.4,
    '2026-05': 21.2, '2026-06': 21.1,
}

# Validator entry queue (millions of ETH). Negligible until 2023, surges in 2025.
# Anchored to 0.12M at 2024-06.
ENTRY = {
    '2021-01': 0.0, '2022-01': 0.0, '2023-01': 0.02, '2023-06': 0.05,
    '2023-12': 0.08, '2024-06': 0.118, '2024-11': 0.01, '2024-12': 0.05,
    '2025-03': 0.4, '2025-06': 1.0, '2025-09': 1.8, '2025-12': 2.6,
    '2026-03': 3.0, '2026-06': 2.8,
}

df = pd.read_csv('outputs/data/ethereum_staked_eth.csv')
df['date'] = pd.to_datetime(df['date'].astype(str), format='%Y-%m')

# bc-only total = Lido Core + Others
df['bc_total_m'] = df['staked_eth_millions']
df['lido_share_pct'] = df['date'].dt.strftime('%Y-%m').map(SHARE)
df['lido_core_m'] = df['lido_share_pct'] / 100 * df['bc_total_m']
df['others_m'] = df['bc_total_m'] - df['lido_core_m']

# Entry queue: interpolate the sparse anchor points over the monthly index
entry = pd.Series(
    {pd.to_datetime(k, format='%Y-%m'): v for k, v in ENTRY.items()})
df['entry_queue_m'] = (
    df['date'].map(entry)
    .reindex(df.index)
)
df['entry_queue_m'] = (
    df.set_index('date')['entry_queue_m']
    .interpolate(method='time')
    .ffill().bfill()
    .values
)
df['total_bc_entry_m'] = df['bc_total_m'] + df['entry_queue_m']

# Lido Share | bc + entry queue = Lido Core / (Lido + Others + Entry queue).
# Equals the bc-only share until the entry queue grows large (2025-26).
df['lido_share_be_pct'] = df['lido_core_m'] / df['total_bc_entry_m'] * 100

out = df[['date', 'lido_core_m', 'others_m', 'entry_queue_m',
          'total_bc_entry_m', 'lido_share_pct', 'lido_share_be_pct']].copy()
out['date'] = out['date'].dt.strftime('%Y-%m')
out = out.round(3)

Path('outputs/data').mkdir(parents=True, exist_ok=True)
out.to_csv('outputs/data/lido_beacon_staked.csv', index=False)

print(out[out['date'] == '2024-06'].to_string(index=False))
print(out.tail(5).to_string(index=False))
print(f"\nLido peak: {out['lido_core_m'].max():.2f}M ETH")
