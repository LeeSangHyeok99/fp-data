import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, COLORS, DPI

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('outputs/data/cefi_lending_market_size.csv')

quarters = df['quarter'].tolist()
stable = df['tether_stablecoin_issuers'].values
surviving = df['surviving_lenders'].values
collapsed = df['collapsed_lenders'].values
totals = stable + surviving + collapsed

# =============================================================================
# Figure
# =============================================================================
fig, ax = create_figure('stacked_bar')
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# Category colors from reference image
COLOR_STABLE = '#3DD598'      # green  – Tether & Stablecoin Issuers
COLOR_SURVIVING = '#B347E8'   # purple – Surviving Lenders
COLOR_COLLAPSED = '#7C8CAE'   # slate  – Collapsed Lenders

x = np.arange(len(quarters))
bar_w = 0.72

ax.bar(x, stable, bar_w, color=COLOR_STABLE, linewidth=0, zorder=3)
ax.bar(x, surviving, bar_w, bottom=stable, color=COLOR_SURVIVING,
       linewidth=0, zorder=3)
ax.bar(x, collapsed, bar_w, bottom=stable + surviving, color=COLOR_COLLAPSED,
       linewidth=0, zorder=3)

# =============================================================================
# Y-axis  (0 – 40, ticks every 10 → 5 ticks)
# =============================================================================
ax.set_ylim(0, 40)
ax.set_yticks([0, 10, 20, 30, 40])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${int(v)}B'))

# =============================================================================
# X-axis  (label every Q1)
# =============================================================================
q1_idx = [i for i, q in enumerate(quarters) if q.startswith('Q1')]
ax.set_xticks(q1_idx)
ax.set_xticklabels([quarters[i] for i in q1_idx])
ax.set_xlim(-0.8, len(quarters) - 0.2)

# =============================================================================
# Annotations
# =============================================================================
TXT = COLORS['text']
TXT_SEC = COLORS['text_secondary']

# 2022-2023 Credit Crisis – span label over the peak → trough region
crisis_start = quarters.index('Q1 2022')
crisis_end = quarters.index('Q2 2023')
mid = (crisis_start + crisis_end) / 2
ax.text(mid, 38.5, '2022–2023 Credit Crisis',
        ha='center', va='top', color=TXT_SEC, fontsize=13,
        fontweight='bold', zorder=5)

# Post-collapse trough callout
trough_idx = quarters.index('Q2 2023')
ax.annotate(
    'Post-collapse\ntrough',
    xy=(trough_idx, totals[trough_idx] + 0.5),
    xytext=(trough_idx - 0.2, 14.5),
    ha='center', va='center',
    color=TXT_SEC, fontsize=11, fontweight='bold', zorder=6,
    arrowprops=dict(arrowstyle='-', color=TXT_SEC,
                    lw=0.9, alpha=0.6,
                    connectionstyle='arc3,rad=0'),
)

# Recovery callout  ~$27B (Q4 2025)
recov_idx = quarters.index('Q4 2025')
recov_val = totals[recov_idx]
ax.annotate(
    f'Recovery\n~${recov_val:.0f}B (Q4 2025)',
    xy=(recov_idx, recov_val + 0.5),
    xytext=(recov_idx - 3.2, 33),
    ha='center', va='center',
    color=TXT, fontsize=11, fontweight='bold', zorder=6,
    arrowprops=dict(arrowstyle='-', color=TXT_SEC,
                    lw=0.9, alpha=0.7,
                    connectionstyle='arc3,rad=-0.15'),
    bbox=dict(boxstyle='round,pad=0.4',
              fc='#1f2230', ec=TXT_SEC, lw=0.8, alpha=0.95),
)

# =============================================================================
# Style
# =============================================================================
apply_style(fig, ax, 'stacked_bar')
ax.tick_params(axis='y', labelsize=14, length=0, pad=12)
ax.tick_params(axis='x', labelsize=12, length=0, pad=8, rotation=0,
               colors=TXT_SEC)
plt.setp(ax.xaxis.get_majorticklabels(), ha='center')

ax.grid(True, axis='y', color='#787b86', alpha=0.3,
        linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)

fig.tight_layout()

# =============================================================================
# Save
# =============================================================================
output_dir = 'outputs/charts/cefi/lending'
Path(output_dir).mkdir(parents=True, exist_ok=True)

png_path = f'{output_dir}/cefi_lending_market_size.png'
svg_path = f'{output_dir}/cefi_lending_market_size.svg'
fig.savefig(png_path, dpi=DPI, facecolor='none', edgecolor='none',
            bbox_inches='tight', transparent=True)
fig.savefig(svg_path, format='svg', facecolor='none', edgecolor='none',
            bbox_inches='tight', transparent=True)
plt.close(fig)

print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")

# =============================================================================
# Stats
# =============================================================================
peak_idx = int(np.argmax(totals))
trough_i = int(np.argmin(totals[crisis_start:crisis_end + 3])) + crisis_start
print(f"\n--- CeFi Lending Market Size ---")
print(f"Range:  {quarters[0]} – {quarters[-1]}")
print(f"Peak:   ${totals[peak_idx]:.1f}B ({quarters[peak_idx]})")
print(f"Trough: ${totals[trough_i]:.1f}B ({quarters[trough_i]})")
print(f"Latest: ${totals[-1]:.1f}B ({quarters[-1]})")
print(f"\nQ4 2025 breakdown:")
print(f"  Tether & Stablecoin Issuers: ${stable[-1]:.1f}B "
      f"({stable[-1] / totals[-1] * 100:.1f}%)")
print(f"  Surviving Lenders          : ${surviving[-1]:.1f}B "
      f"({surviving[-1] / totals[-1] * 100:.1f}%)")
print(f"  Collapsed Lenders          : ${collapsed[-1]:.1f}B "
      f"({collapsed[-1] / totals[-1] * 100:.1f}%)")
