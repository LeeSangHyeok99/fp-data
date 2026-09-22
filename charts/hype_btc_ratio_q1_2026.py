import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/hrc')
from config import setup_font, apply_style, COLORS, GRID_CONFIG, DPI

import matplotlib.font_manager as fm
fm.fontManager.addfont('assets/font/Pretendard/Pretendard-Bold.ttf')

mpl.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('outputs/data/hype_btc_ratio_q1_2026.csv', parse_dates=['date'])

# Hyperliquid brand mint (matches HRC neon-mint family)
HYPE_COLOR = '#50e3c2'

setup_font()
plt.rcParams['font.family'] = ['SUIT', 'Pretendard']

fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# Filled area
ax.fill_between(
    df['date'], df['hype_btc_ratio'], 0,
    color=HYPE_COLOR, alpha=0.20, linewidth=0, zorder=2,
)
# Line
ax.plot(
    df['date'], df['hype_btc_ratio'],
    color=HYPE_COLOR, linewidth=2.5, zorder=3,
)

SUBSCRIPT = str.maketrans('0123456789', '\u2080\u2081\u2082\u2083\u2084\u2085\u2086\u2087\u2088\u2089')

def fmt_btc(val, _pos):
    if val <= 0:
        return '\u20bf0'
    s = f'{val:.10f}'.rstrip('0').rstrip('.')
    decimal = s.split('.')[1] if '.' in s else ''
    leading = len(decimal) - len(decimal.lstrip('0'))
    rest = decimal.lstrip('0')
    if leading >= 2:
        n_sub = str(leading).translate(SUBSCRIPT)
        return f'\u20bf0.0{n_sub}{rest}'
    return f'\u20bf{val:.6f}'

ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_btc))
ax.yaxis.set_major_locator(MaxNLocator(nbins=5))

y_min = df['hype_btc_ratio'].min()
y_max = df['hype_btc_ratio'].max()
pad = (y_max - y_min) * 0.10
ax.set_ylim(y_min - pad, y_max + pad)

month_starts = pd.date_range(start='2026-01-01', end='2026-04-01', freq='MS')
ax.set_xticks(month_starts)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(df['date'].iloc[0], pd.Timestamp('2026-04-01'))

apply_style(fig, ax, 'area')

ax.tick_params(axis='y', labelsize=20, length=0)
ax.tick_params(axis='x', labelsize=18, length=0, pad=20)

ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

output_dir = 'outputs/charts/hyperliquid/token'
Path(output_dir).mkdir(parents=True, exist_ok=True)

png_path = f"{output_dir}/hype_btc_ratio_q1_2026.png"
svg_path = f"{output_dir}/hype_btc_ratio_q1_2026.svg"

fig.savefig(png_path, dpi=DPI, facecolor='none', edgecolor='none', bbox_inches='tight')
fig.savefig(svg_path, format='svg', facecolor='none', edgecolor='none', bbox_inches='tight')

plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
