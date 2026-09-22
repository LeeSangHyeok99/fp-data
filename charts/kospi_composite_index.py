"""
KOSPI Composite Index (^KS11) — line/area chart reproduction
Source reference: Yahoo Finance (KSE delayed quote, KRW)
Style: four-pillars, transparent BG, no title/legend/source.

Reproduces the Jan 2025 -> Jun 2026 rally from ~2,400 to a ~8,700 peak,
closing at 8,160.59 (-5.54%) on Jun 5, 2026.
Data extracted from the reference image (weekly anchor points).
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter, MultipleLocator
from config import setup_font, save_chart, apply_style, area_glow, endpoint_dot, COLORS

setup_font()

KOSPI_BLUE = '#3b82f6'

# ----------------------------------------------------------------------
# Data — weekly anchor points read off the reference image
# ----------------------------------------------------------------------
rows = [
    ('2025-01-06', 2380), ('2025-01-13', 2420), ('2025-01-20', 2450), ('2025-01-27', 2440),
    ('2025-02-03', 2480), ('2025-02-10', 2520), ('2025-02-17', 2500), ('2025-02-24', 2540),
    ('2025-03-03', 2560), ('2025-03-10', 2550), ('2025-03-17', 2580), ('2025-03-24', 2560),
    ('2025-03-31', 2570), ('2025-04-07', 2540), ('2025-04-14', 2560), ('2025-04-21', 2600),
    ('2025-04-28', 2620), ('2025-05-05', 2650), ('2025-05-12', 2680), ('2025-05-19', 2700),
    ('2025-05-26', 2720), ('2025-06-02', 2760), ('2025-06-09', 2800), ('2025-06-16', 2820),
    ('2025-06-23', 2850), ('2025-06-30', 2880), ('2025-07-07', 2950), ('2025-07-14', 3010),
    ('2025-07-21', 2950), ('2025-07-28', 2980), ('2025-08-04', 3050), ('2025-08-11', 3100),
    ('2025-08-18', 3080), ('2025-08-25', 3120), ('2025-09-01', 3180), ('2025-09-08', 3220),
    ('2025-09-15', 3250), ('2025-09-22', 3280), ('2025-09-29', 3320), ('2025-10-06', 3400),
    ('2025-10-13', 3500), ('2025-10-20', 3550), ('2025-10-27', 3620), ('2025-11-03', 3760),
    ('2025-11-10', 3950), ('2025-11-17', 4100), ('2025-11-24', 4260), ('2025-12-01', 4460),
    ('2025-12-08', 4660), ('2025-12-15', 4820), ('2025-12-22', 4960), ('2025-12-29', 5060),
    ('2026-01-05', 5210), ('2026-01-12', 5410), ('2026-01-19', 5560), ('2026-01-26', 5720),
    ('2026-02-02', 5900), ('2026-02-09', 6060), ('2026-02-16', 5820), ('2026-02-23', 5520),
    ('2026-03-02', 5410), ('2026-03-09', 5560), ('2026-03-16', 5700), ('2026-03-23', 5760),
    ('2026-03-30', 5860), ('2026-04-06', 6010), ('2026-04-13', 6210), ('2026-04-20', 6420),
    ('2026-04-27', 6620), ('2026-05-04', 6900), ('2026-05-11', 7120), ('2026-05-18', 7360),
    ('2026-05-25', 7620), ('2026-06-01', 8120), ('2026-06-03', 8520), ('2026-06-04', 8700),
    ('2026-06-05', 8160.59),
]
df = pd.DataFrame(rows, columns=['date', 'index'])
df['date'] = pd.to_datetime(df['date'])
df.to_csv('outputs/data/kospi_composite_index.csv', index=False)

x = df['date']
y = df['index']

# ----------------------------------------------------------------------
# Figure
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=150)

ax.plot(x, y, color=KOSPI_BLUE, linewidth=2.6, zorder=4, solid_capstyle='round')
area_glow(ax, x, y, color=KOSPI_BLUE, max_alpha=0.16, power=2.0)

# Endpoint dot + close label
endpoint_dot(ax, x.iloc[-1], y.iloc[-1], color=KOSPI_BLUE, size=60)
ax.annotate(f"{y.iloc[-1]:,.0f}",
            xy=(x.iloc[-1], y.iloc[-1]), xytext=(-8, 16),
            textcoords='offset points', ha='right', va='bottom',
            fontsize=15, fontweight='bold', color=KOSPI_BLUE)

# ----------------------------------------------------------------------
# Axes
# ----------------------------------------------------------------------
ax.set_ylim(2000, 9000)
ax.yaxis.set_major_locator(MultipleLocator(2000))  # 2000,4000,6000,8000 -> 4 clean ticks
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))

ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(x.iloc[0], x.iloc[-1] + pd.Timedelta(days=5))

apply_style(fig, ax, 'line')

out_dir = 'outputs/charts/macro/equities'
png, svg = save_chart(fig, 'kospi_composite_index', out_dir)
plt.close(fig)

print('saved:', png)
print('start:', f"{y.iloc[0]:,.0f}", '| peak', f"{y.max():,.0f}", '| close', f"{y.iloc[-1]:,.0f}")
