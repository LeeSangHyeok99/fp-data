import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.font_manager as fm
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, apply_style, COLORS, GRID_CONFIG, DPI

mpl.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('outputs/data/gacha_spending_weekly.csv', parse_dates=['date'])

setup_font()
fm.fontManager.addfont('assets/font/Pretendard/Pretendard-Medium.ttf')
plt.rcParams['font.family'] = 'Pretendard'
plt.rcParams['font.weight'] = 'medium'

fig, ax = plt.subplots(figsize=(12, 5.5), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

COLOR_COLLECTOR = '#7d7fc4'
COLOR_PHYGITALS = '#f49060'
COLOR_COURTYARD = '#d873b8'
COLOR_EMPORIUM = '#b0b3b8'

bar_width = 5.5

bottom = pd.Series(0.0, index=df.index)
for series, color in [
    ('Collector_Crypt', COLOR_COLLECTOR),
    ('Phygitals', COLOR_PHYGITALS),
    ('Courtyard', COLOR_COURTYARD),
    ('Emporium', COLOR_EMPORIUM),
]:
    ax.bar(df['date'], df[series], width=bar_width, bottom=bottom,
           color=color, linewidth=0, align='center')
    bottom = bottom + df[series]

ax.set_ylim(0, 50)
ax.set_yticks([0, 10, 20, 30, 40, 50])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.0f}M'))

ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 5, 9]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

ax.set_xlim(df['date'].min() - pd.Timedelta(days=14),
            df['date'].max() + pd.Timedelta(days=14))

apply_style(fig, ax, 'stacked_bar')

ax.tick_params(axis='y', labelsize=14, length=0, colors=COLORS['text_secondary'])
ax.tick_params(axis='x', labelsize=14, length=0, pad=10, rotation=45,
               colors=COLORS['text_secondary'])
plt.setp(ax.xaxis.get_majorticklabels(), ha='right', rotation_mode='anchor')

for label in ax.get_xticklabels() + ax.get_yticklabels():
    label.set_fontweight('medium')

ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

output_dir = 'outputs/charts/macro/gacha'
Path(output_dir).mkdir(parents=True, exist_ok=True)

png_path = f"{output_dir}/gacha_spending_weekly.png"
svg_path = f"{output_dir}/gacha_spending_weekly.svg"

fig.savefig(png_path, dpi=DPI, facecolor='none', edgecolor='none', bbox_inches='tight')
fig.savefig(svg_path, format='svg', facecolor='none', edgecolor='none', bbox_inches='tight')

plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
