import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, save_chart, COLORS

df = pd.read_csv('outputs/data/kalshi_oi_term_structure.csv')

SERIES = {
    'Corn': '#1f77b4',
    'Live Cattle': '#ff7f0e',
    'Soybean': '#2ca02c',
    'Wheat SRW': '#d62728',
}

# label placement near each line's start point: (dx, dy, ha, va)
LABEL_OFFSET = {
    'Corn': (-0.6, -0.06, 'right', 'top'),
    'Live Cattle': (0.6, 0.03, 'left', 'bottom'),
    'Soybean': (-0.6, 0.06, 'right', 'bottom'),
    'Wheat SRW': (-0.6, 0.04, 'right', 'bottom'),
}

fig, ax = create_figure('line')
fig.set_size_inches(13, 6.5)

# shaded region: expiries 6+ months out
ax.axvspan(6, 40, color='#4a7a5a', alpha=0.08, zorder=0)
ax.axvline(6, color=COLORS['grid'], alpha=0.6, linestyle=(0, (1.5, 1.5)),
           linewidth=1.0, zorder=1)
ax.text(6.4, 1.06, '6 Months Out', fontsize=12, fontweight='bold',
        color=COLORS['text_secondary'], va='bottom', ha='left')

avg_far_share = df.groupby('product')['far_oi_share_6m_plus'].first().mean()
ax.annotate(
    f'Expiries 6+ Months Out Still Hold ~{avg_far_share * 100:.0f}% of\n'
    'Each Product’s Open Interest',
    xy=(6, 1.0), xytext=(13, 0.86),
    fontsize=13, fontweight='bold', color='#4a7a5a',
    ha='left', va='center',
    arrowprops=dict(arrowstyle='-', color='#4a7a5a', linewidth=1.3),
)

for product, color in SERIES.items():
    sub = df[df['product'] == product].sort_values('months_to_expiry')
    ax.plot(sub['months_to_expiry'], sub['norm_open_interest'],
            color=color, linewidth=2.2, marker='o', markersize=5,
            zorder=3, solid_capstyle='round', clip_on=False)

    x0 = sub['months_to_expiry'].iloc[0]
    y0 = sub['norm_open_interest'].iloc[0]
    dx, dy, ha, va = LABEL_OFFSET[product]
    ax.text(x0 + dx, y0 + dy, product, fontsize=13, fontweight='bold',
            color=color, ha=ha, va=va, zorder=6)

ax.set_xlim(-1, 40)
ax.set_xticks([0, 5, 10, 15, 20, 25, 30, 35, 40])
ax.set_xticklabels(['0', '5', '10', '15', '20', '25', '30', '35', '40'])

ax.set_ylim(0, 1.1)
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])

ax.set_xlabel('Months Until Expiry', fontsize=17, fontweight='bold',
              color=COLORS['text_secondary'], labelpad=14)

apply_style(fig, ax, 'line')

ax.tick_params(axis='x', rotation=0)
plt.setp(ax.xaxis.get_majorticklabels(), ha='center')

Path('outputs/charts/kalshi/oi_term_structure').mkdir(parents=True, exist_ok=True)
png_path, svg_path = save_chart(fig, 'kalshi_oi_term_structure', 'outputs/charts/kalshi/oi_term_structure')
plt.close(fig)

print(png_path)
print(svg_path)
