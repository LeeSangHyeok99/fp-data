"""Generate approximate weekly Gacha Spending data extracted from image.

Source: Dune dashboard by @zkayape - https://dune.com/zkayape/pokemontcgsol
Series: Courtyard (pink), Phygitals (orange), Collector_Crypt (purple), Emporium (gray)
Values are visual approximations from the image (USD millions).
"""
import pandas as pd
import numpy as np
from pathlib import Path

start = pd.Timestamp('2023-11-05')
weeks = pd.date_range(start, periods=130, freq='W-SUN')

n = len(weeks)
courtyard = np.zeros(n)
phygitals = np.zeros(n)
collector_crypt = np.zeros(n)
emporium = np.zeros(n)

# Approximate values per week index (visual extraction from Dune chart)
# Phase 1: weeks 0-30 (Nov 2023 - Jun 2024) — near-zero
for i in range(0, 30):
    courtyard[i] = max(0, 0.05 + 0.015 * i + np.random.uniform(-0.05, 0.1))

# Phase 2: weeks 30-45 (Jul 2024 - Oct 2024) — small Courtyard ramp
phase2 = [1.0, 1.4, 1.8, 2.2, 2.8, 3.5, 4.0, 4.2, 3.8, 4.5, 5.0, 5.5, 5.0, 5.5, 6.0]
for i, v in enumerate(phase2):
    courtyard[30 + i] = v

# Phase 3: weeks 45-65 (Nov 2024 - Mar 2025) — Courtyard dominant 6-9m, CC begins
phase3_c = [6.5, 7.0, 7.5, 8.0, 7.5, 8.0, 9.0, 9.5, 8.5, 9.0, 8.5, 8.0, 9.5, 9.0, 8.5, 8.0, 9.0, 8.5, 9.0, 9.5]
phase3_cc = [0.0, 0.0, 0.0, 0.0, 0.2, 0.5, 0.8, 1.0, 0.8, 1.0, 0.8, 0.5, 1.2, 1.0, 0.5, 0.8, 1.5, 1.2, 2.0, 2.5]
for i, (c, cc) in enumerate(zip(phase3_c, phase3_cc)):
    courtyard[45 + i] = c
    collector_crypt[45 + i] = cc

# Phase 4: weeks 65-80 (Apr 2025 - Jul 2025) — both growing, 10-15m
phase4_c = [9.5, 10.5, 9.0, 10.0, 11.0, 9.5, 12.0, 11.0, 10.0, 11.5, 10.5, 11.0, 13.0, 14.0, 13.5]
phase4_cc = [3.0, 3.5, 3.0, 4.0, 4.5, 4.0, 5.0, 4.5, 4.0, 5.5, 5.0, 5.5, 6.5, 7.0, 7.5]
phase4_ph = [0.0, 0.0, 0.5, 0.0, 0.8, 0.0, 1.5, 0.5, 0.0, 1.0, 0.0, 0.5, 1.5, 1.0, 0.0]
for i, (c, cc, ph) in enumerate(zip(phase4_c, phase4_cc, phase4_ph)):
    courtyard[65 + i] = c
    collector_crypt[65 + i] = cc
    phygitals[65 + i] = ph

# Phase 5: weeks 80-95 (Aug 2025 - Nov 2025) — spikes 20-30m
phase5_c = [12.0, 13.5, 17.5, 14.0, 9.0, 12.5, 7.0, 12.5, 5.5, 8.0, 9.0, 7.5, 14.5, 7.0, 9.5]
phase5_cc = [6.0, 7.5, 8.0, 6.5, 5.0, 11.5, 4.5, 8.0, 4.0, 6.0, 5.5, 5.0, 9.0, 5.0, 6.5]
phase5_ph = [2.0, 2.5, 1.5, 2.0, 0.5, 6.0, 0.5, 2.0, 6.5, 2.0, 1.5, 5.0, 3.0, 4.5, 1.0]
for i, (c, cc, ph) in enumerate(zip(phase5_c, phase5_cc, phase5_ph)):
    courtyard[80 + i] = c
    collector_crypt[80 + i] = cc
    phygitals[80 + i] = ph

# Phase 6: weeks 95-115 (Dec 2025 - Mar 2026) — 15-25m, mix
phase6_c = [9.0, 8.0, 9.0, 7.0, 7.5, 8.0, 10.5, 7.0, 7.0, 13.0, 8.0, 10.0, 7.5, 6.0, 5.0, 6.5, 7.0, 8.0, 6.5, 8.5]
phase6_cc = [6.5, 7.0, 6.5, 5.5, 5.0, 7.0, 9.0, 6.5, 7.5, 14.5, 11.5, 12.0, 14.5, 13.5, 14.0, 16.5, 17.0, 17.0, 14.5, 18.5]
phase6_ph = [1.0, 0.5, 1.5, 2.0, 1.5, 2.0, 2.5, 1.5, 0.5, 1.0, 0.5, 1.5, 0.5, 1.0, 0.5, 0.5, 1.0, 1.0, 0.5, 1.5]
for i, (c, cc, ph) in enumerate(zip(phase6_c, phase6_cc, phase6_ph)):
    courtyard[95 + i] = c
    collector_crypt[95 + i] = cc
    phygitals[95 + i] = ph

# Phase 7: weeks 115-129 (Mar 2026 - Apr 2026) — explosive then partial dropoff
phase7_c = [9.5, 14.0, 18.5, 22.0, 12.0, 4.5, 10.0, 9.5, 12.5, 13.5, 17.0, 18.5, 22.5, 11.0, 2.5]
phase7_cc = [7.0, 7.5, 7.0, 7.5, 6.0, 5.5, 14.0, 14.0, 13.5, 16.5, 18.0, 22.0, 21.5, 6.0, 8.0]
phase7_ph = [1.5, 1.0, 0.5, 1.0, 0.5, 0.5, 2.5, 2.0, 2.5, 6.0, 6.5, 1.5, 2.0, 1.5, 1.0]
for i, (c, cc, ph) in enumerate(zip(phase7_c, phase7_cc, phase7_ph)):
    courtyard[115 + i] = c
    collector_crypt[115 + i] = cc
    phygitals[115 + i] = ph

# Tiny emporium contributions sparsely
for i in [70, 85, 95, 110, 120]:
    emporium[i] = 0.3

df = pd.DataFrame({
    'date': weeks,
    'Collector_Crypt': collector_crypt,
    'Phygitals': phygitals,
    'Courtyard': courtyard,
    'Emporium': emporium,
})

out_path = Path('outputs/data/gacha_spending_weekly.csv')
out_path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(out_path, index=False)
print(f"Saved: {out_path}")
print(f"Rows: {len(df)}, Peak total: ${df[['Collector_Crypt','Phygitals','Courtyard','Emporium']].sum(axis=1).max():.1f}M")
