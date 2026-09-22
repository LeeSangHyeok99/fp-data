import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, save_chart, COLORS

df = pd.read_csv('outputs/data/kalshi_oi_accumulation.csv')

# group -> (display label, color, linewidth)
SERIES = {
    'weather_monthly': ('Weather 3-45d', '#466da3', 2.4),
    'weather_seasonal': ('Weather >45d', '#a3b9d4', 1.6),
    'sports_monthly': ('Sports 3-45d', '#a35f5d', 2.4),
    'sports_seasonal': ('Sports >45d', '#dba39d', 1.6),
}

fig, ax = create_figure('line')
fig.set_size_inches(12.5, 6.5)

# half of final OI reference line
ax.axhline(0.5, color=COLORS['grid'], alpha=0.7, linestyle=(0, (3.7, 1.6)),
           linewidth=1.0, zorder=1)
ax.text(1, 0.515, 'Half of Final OI', fontsize=13, fontweight='bold',
        color=COLORS['text_secondary'], va='bottom', ha='left', zorder=2)

# label placement per series: (dx, dy, ha, va) offset from the half marker
LABEL_OFFSET = {
    'weather_monthly': (-2, 0.035, 'right', 'bottom'),
    'weather_seasonal': (-2, 0.035, 'right', 'bottom'),
    'sports_monthly': (2, -0.06, 'left', 'top'),
    'sports_seasonal': (-2, 0.035, 'right', 'bottom'),
}

for group, (label, color, lw) in SERIES.items():
    sub = df[df['group'] == group].sort_values('life_elapsed_pct')
    ax.plot(sub['life_elapsed_pct'], sub['norm_open_interest'],
            color=color, linewidth=lw, zorder=3, solid_capstyle='round')

    half = sub[sub['is_half_marker'] == 1]
    if not half.empty:
        hx = half['life_elapsed_pct'].iloc[0]
        hy = half['norm_open_interest'].iloc[0]
        remaining = half['remaining_pct_label'].iloc[0]
        ax.scatter([hx], [hy], color=color, s=70, zorder=5, edgecolors='none')
        dx, dy, ha, va = LABEL_OFFSET[group]
        ax.text(hx + dx, hy + dy, f'{label}\n{remaining:.0f}% Left',
                fontsize=13, fontweight='bold', color=color,
                ha=ha, va=va, zorder=6, linespacing=1.3)

ax.set_xlim(0, 100)
ax.set_xticks([0, 20, 40, 60, 80, 100])
ax.set_xticklabels(['0', '20', '40', '60', '80', '100'])

ax.set_ylim(0, 1.05)
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])

ax.set_xlabel('Contract Life Elapsed (%)\n0% = Trading Opens / 100% = Settlement',
              fontsize=15, fontweight='bold',
              color=COLORS['text_secondary'], labelpad=14, linespacing=1.8)

apply_style(fig, ax, 'line')

ax.tick_params(axis='x', rotation=0)
plt.setp(ax.xaxis.get_majorticklabels(), ha='center')

Path('outputs/charts/kalshi/oi_accumulation').mkdir(parents=True, exist_ok=True)
png_path, svg_path = save_chart(fig, 'kalshi_oi_accumulation', 'outputs/charts/kalshi/oi_accumulation')
plt.close(fig)

print(png_path)
print(svg_path)
