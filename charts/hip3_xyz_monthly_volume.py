import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.font_manager as fm
import numpy as np
from pathlib import Path

# ── Font ──
font_path = Path('/Users/ijaheun/Desktop/Project/data/assets/font/SUIT/SUIT-ttf/')
font_bold = fm.FontProperties(fname=str(font_path / 'SUIT-Bold.ttf'))

# ── Data (Google Sheet: gid=1186295259, cross-validated 2026-03-06) ──
# Dec-25: $9.72B, Jan-26: $23.31B (Google Sheet monthly sums)
months = ['Dec 2025', 'Jan 2026']
values = np.array([9.72, 23.31])  # in billions

# ── Plot ──
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

x = np.arange(len(months))

bars = ax.bar(
    x, values,
    width=0.4,
    color='#1a3a5c',
    edgecolor='#0a0a0a',
    linewidth=0.3,
    alpha=0.92,
)

# ── X axis ──
ax.set_xticks(x)
ax.set_xticklabels(months)
for label in ax.get_xticklabels():
    label.set_fontproperties(font_bold)
    label.set_fontsize(14)
    label.set_color('#747474')

# ── Y axis ──
y_max = 30
ticks = np.array([0, 10, 20, 30])
ax.set_ylim(0, y_max * 1.05)
ax.yaxis.set_major_locator(mticker.FixedLocator(ticks))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}B'))
for label in ax.get_yticklabels():
    label.set_fontproperties(font_bold)
    label.set_fontsize(14)
    label.set_color('#747474')

# ── Grid ──
ax.grid(axis='y', color='#787b86', alpha=0.5, linestyle=(0, (3.7, 1.6)), linewidth=1)
ax.grid(axis='x', visible=False)
ax.set_axisbelow(True)

# ── Spines ──
for spine in ax.spines.values():
    spine.set_visible(False)

# ── Ticks ──
ax.tick_params(axis='x', length=6, width=1, color='#747474')
ax.tick_params(axis='y', length=0)

fig.tight_layout()

# ── Save ──
out_dir = Path('/Users/ijaheun/Desktop/Project/data/outputs/charts/hip3')
out_dir.mkdir(parents=True, exist_ok=True)

png_path = out_dir / 'hip3_xyz_monthly_volume.png'
svg_path = out_dir / 'hip3_xyz_monthly_volume.svg'
fig.savefig(png_path, dpi=150, bbox_inches='tight', transparent=True)
fig.savefig(svg_path, format='svg', bbox_inches='tight', transparent=True)
plt.close(fig)

print(f"Jan-26: ${values[0]:.1f}B")
print(f"Feb-26: ${values[1]:.1f}B")
print(f"\nSaved: {png_path}")
print(f"Saved: {svg_path}")
