import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, GRID_CONFIG, DPI

setup_font()

# =============================================================================
# Data: REAL values from Paymentscan (paymentscan.xyz)
#   Extracted from the dashboard hydration payload (default view:
#   includeTopups=true, includeOffchainData=true). Verified anchor:
#   May 2026 total volume = $866.1M, total users = 375.3K (matches reference).
#   - Bars = Monthly Crypto Card Volumes ($M), stacked by card program (img 2)
#   - Line = Monthly Crypto Card Users (total, K addresses) (img 3 -> line)
# =============================================================================
df = pd.read_csv('outputs/data/crypto_card_volumes_users.csv')
# 앞부분(Mar~Oct 2023)은 사실상 0이라 Nov 2023부터 시작
df = df[df['month'] >= '2023-11'].reset_index(drop=True)
months = pd.to_datetime(df['month'] + '-01')
n = len(df)
idx = np.arange(n)

# stack order (bottom -> top): Other, small ones, EtherFi, KAST, RedotPay
PROGRAMS = [
    ('Other (16)', '#8a8a8a'),
    ('Kolo',       '#6b3fc4'),
    ('Tria',       '#4aa8e0'),
    ('Karta',      '#e0a64a'),
    ('Plasma One', '#6cc24a'),
    ('EtherFi',    '#a838c4'),
    ('KAST',       '#1f5673'),
    ('RedotPay',   '#e8623a'),
]

LINE_COLOR = '#f2f2f2'  # users line (white, pops over orange bars)

OUTPUT_DIR = 'outputs/charts/platform/crypto_cards'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


def make_chart(figsize, suffix):
    fig, ax = plt.subplots(figsize=figsize, dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')
    ax2 = ax.twinx()
    ax2.set_facecolor('none')

    x = idx.astype(float)
    width = 0.82

    # stacked bars (volume, left axis)
    bottom = np.zeros(n)
    for name, color in PROGRAMS:
        vals = df[name].to_numpy()
        ax.bar(x, vals, width=width, bottom=bottom, color=color,
               linewidth=0, zorder=2)
        bottom = bottom + vals

    # line (users, right axis)
    users = df['total_users_k'].to_numpy()
    ax2.plot(x, users, color=LINE_COLOR, linewidth=2.6, zorder=5,
             solid_capstyle='round', solid_joinstyle='round')
    ax2.scatter(x[-1], users[-1], color=LINE_COLOR, s=42,
                zorder=6, edgecolors='none')

    # left axis: volume $M (5 ticks)
    ax.set_yticks([0, 200, 400, 600, 800])
    ax.set_yticklabels([f'${t}M' for t in [0, 200, 400, 600, 800]],
                       fontsize=13, fontweight='bold',
                       color=COLORS['text_secondary'])
    ax.set_ylim(0, 900)

    # right axis: users K (5 ticks, aligned to left gridlines)
    ax2.set_yticks([0, 100, 200, 300, 400])
    ax2.set_yticklabels([f'{t}K' for t in [0, 100, 200, 300, 400]],
                        fontsize=13, fontweight='bold', color=LINE_COLOR)
    ax2.set_ylim(0, 450)

    # x axis: Mon YYYY every 4 months
    tick_pos = [i for i in range(n) if i % 4 == 0]
    ax.set_xticks(tick_pos)
    ax.set_xticklabels([months[i].strftime('%b %Y') for i in tick_pos],
                       fontsize=12, fontweight='bold', color=COLORS['text'])
    ax.tick_params(axis='x', rotation=45)
    plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
    ax.set_xlim(-0.8, n - 0.2)

    # grid (left axis only; right ticks align)
    ax.grid(True, axis='y', color=GRID_CONFIG['color'],
            alpha=GRID_CONFIG['alpha'], linestyle=GRID_CONFIG['linestyle'],
            linewidth=GRID_CONFIG['linewidth'])
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for spine in ax2.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis='y', length=0)
    ax2.tick_params(axis='y', length=0)
    ax.tick_params(axis='x', length=6, width=1, colors=COLORS['text_secondary'])

    fig.tight_layout()
    for fmt in ['png', 'svg']:
        fig.savefig(f'{OUTPUT_DIR}/crypto_card_volumes_users_{suffix}.{fmt}',
                    dpi=DPI, facecolor='none', edgecolor='none',
                    bbox_inches='tight', transparent=True,
                    format=fmt if fmt == 'svg' else None)
    plt.close()


make_chart((10.67, 5.2), 'wide')
tv = df['total_volume_musd']
print('Done: crypto_card_volumes_users (REAL data)')
print(f"  Volume peak ${tv.max():.1f}M ({df['month'][tv.idxmax()]})")
print(f"  Users peak {df['total_users_k'].max():.1f}K")
