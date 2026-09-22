import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/hrc')
from config import setup_font, apply_style, COLORS, GRID_CONFIG, DPI

mpl.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('outputs/data/asxn_validator_stakes.csv')

# Shorten names to match ASXN dashboard label style
NAME_MAP = {
    'Hyper Foundation 1': 'Hyper Fdn 1',
    'Hyper Foundation 2': 'Hyper Fdn 2',
    'Hyper Foundation 3': 'Hyper Fdn 3',
    'Hyper Foundation 4': 'Hyper Fdn 4',
    'Hyper Foundation 5': 'Hyper Fdn 5',
    'Anchorage By Figment': 'Anchorage',
    'Nansen x HypurrCollective': 'HypurrCo',
    'Hypurrscanning': 'HypurrScan',
    'infinitefield.xyz': 'Infinite Field',
    'Kinetiq x Hyperion': 'Kinetiq',
    'Imperator.co - HypeRPC.app': 'Imperator',
    'USDT0 x Luganodes': 'USDT0',
    'Hyperbeat x P2P x Hypio': 'Hyperbeat',
    'Purrposeful x HyBridge x PiP': 'Purrposeful',
}
df['short'] = df['name'].map(lambda n: NAME_MAP.get(n, n))

# Convert to millions
df['stake_m'] = df['stake'] / 1e6

# HRC dark mint
BAR_COLOR = '#2d8a78'

setup_font()
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

ax.bar(df['short'], df['stake_m'], color=BAR_COLOR, width=0.7, zorder=2, linewidth=0)

# Y axis: 0 -> 60M, 5 ticks
y_max = 60
ax.set_ylim(0, y_max)
ax.set_yticks([0, 15, 30, 45, 60])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v:.0f}M'))

apply_style(fig, ax, 'bar')

# X axis tick rotation
ax.tick_params(axis='x', labelsize=13, length=0, colors=COLORS['text_secondary'], rotation=45)
plt.setp(ax.xaxis.get_majorticklabels(), ha='right', rotation_mode='anchor')
ax.tick_params(axis='y', labelsize=18, length=0, colors=COLORS['text_secondary'])

ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

output_dir = 'outputs/charts/hyperliquid/staking'
Path(output_dir).mkdir(parents=True, exist_ok=True)

png_path = f"{output_dir}/asxn_validator_stake_distribution.png"
svg_path = f"{output_dir}/asxn_validator_stake_distribution.svg"

fig.savefig(png_path, dpi=DPI, facecolor='none', edgecolor='none', bbox_inches='tight')
fig.savefig(svg_path, format='svg', facecolor='none', edgecolor='none', bbox_inches='tight')

plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
