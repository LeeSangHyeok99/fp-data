"""
Weekend Price Discovery on Hyperliquid: Korean Stocks — bar chart
Source: Hyperliquid API (HIP-3 daily candles), Yahoo Finance
        (KRX: 005930.KS, 000660.KS, 005380.KS / NYSE: EWY)
Style: four-pillars, transparent BG, no title/legend/source.

HL weekend direction vs actual KRX/NYSE Monday open gap (Feb–Jun 2026).
Direction accuracy %, with a 50% coin-flip reference line.
Values are explicit in the source image (no approximation).
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter
from config import setup_font, save_chart, apply_style, COLORS

setup_font()

GREEN = '#34a853'
RED = '#e0473e'

# ----------------------------------------------------------------------
# Data (direction accuracy %, hit counts from the source image)
# ----------------------------------------------------------------------
rows = [
    ('Samsung\n(15/16)', 93.75, GREEN),
    ('Hyundai\n(13/16)', 81.25, GREEN),
    ('SK Hynix\n(10/16)', 62.50, RED),
    ('EWY\n(7/13)',       53.85, RED),
]
df = pd.DataFrame(rows, columns=['label', 'accuracy', 'color'])
df[['label', 'accuracy']].to_csv(
    'outputs/data/hl_weekend_korean_stocks_accuracy.csv', index=False)

x = range(len(df))

# ----------------------------------------------------------------------
# Figure
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=150)

ax.bar(x, df['accuracy'], width=0.62, color=df['color'].tolist(), zorder=3)

# 50% coin-flip reference line
COIN_FLIP = '#e0a23a'  # amber
ax.axhline(50, color=COIN_FLIP, linewidth=1.3,
           linestyle=(0, (4, 3)), alpha=0.9, zorder=2)
ax.annotate('coin flip', xy=(len(df) - 0.5, 50), xytext=(6, 4),
            textcoords='offset points', ha='left', va='bottom',
            fontsize=12, fontweight='bold', color=COIN_FLIP)

# Value labels on top of bars
for xi, acc in zip(x, df['accuracy']):
    ax.annotate(f'{acc:.0f}%', xy=(xi, acc), xytext=(0, 8),
                textcoords='offset points', ha='center', va='bottom',
                fontsize=18, fontweight='bold', color=COLORS['text'])

# ----------------------------------------------------------------------
# Axes
# ----------------------------------------------------------------------
ax.set_ylim(0, 100)
ax.yaxis.set_major_locator(MultipleLocator(25))   # 0,25,50,75,100
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:.0f}%'))
ax.set_xticks(list(x))
ax.set_xticklabels(df['label'])
ax.set_xlim(-0.6, len(df) - 0.4)

apply_style(fig, ax, 'bar')
# bar chart: horizontal x labels, centered (override rotated default)
ax.tick_params(axis='x', rotation=0)
plt.setp(ax.xaxis.get_majorticklabels(), ha='center')

out_dir = 'outputs/charts/hyperliquid/hip3'
png, svg = save_chart(fig, 'hl_weekend_korean_stocks_accuracy', out_dir)
plt.close(fig)

print('saved:', png)
print(df[['label', 'accuracy']].to_string(index=False))
