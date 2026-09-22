import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import (setup_font, COLORS, GRID_CONFIG, DPI,
                    gradient_rounded_bar, area_glow, endpoint_dot)

setup_font()

# =============================================================================
# x402 activity (Artemis reproduction): Buyers (bars) + Transactions (line).
# Weekly, week ending Sunday, from the week containing May 29 -> Jun 21, 2026.
#   Source: Artemis daily CSV export (classic.artemis.ai/asset/x402).
#   Daily, May 29 -> Jun 23, 2026. The final day (Jun 24) is an incomplete
#   intraday pull (31K tx vs ~600K neighbors) and is dropped.
# =============================================================================
df = pd.read_csv('sources/Metric Comparison - x402.csv')
df['DateTime'] = pd.to_datetime(df['DateTime'])
df = df.set_index('DateTime').sort_index()

wk = pd.DataFrame({
    'tx': df['x402 - Transactions'],
    'buyers': df['x402 - Buyers'],
}).loc['2026-05-29':'2026-06-23']
wk.index.name = 'date'
Path('outputs/data').mkdir(parents=True, exist_ok=True)
wk.to_csv('outputs/data/x402_buyers_transactions_daily.csv')

days = wk.index
n = len(wk)
x = np.arange(n, dtype=float)

BUYERS_TOP = '#eccf72'    # Buyers bar: light gold (top)
BUYERS_BOT = '#9a7522'    # Buyers bar: dark gold, same family (bottom)
TX = '#8b7cf2'            # Artemis purple (Transactions, line)


def gold_gradient_bar(ax, x_center, width, height, c_top, c_bot, alpha=0.97):
    """Rounded-top bar with a gradient between two shades of the same hue
    (light gold at top -> dark gold at bottom), instead of fading to black."""
    import matplotlib.colors as mcolors
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path as MPath
    if height is None or height <= 0:
        return
    radius = min(width / 2, height * 0.06)
    rect_top = height - radius
    x_left, x_right = x_center - width / 2, x_center + width / 2
    theta = np.linspace(0, np.pi, 40)
    verts = [(x_left, 0), (x_right, 0), (x_right, rect_top)]
    verts += list(zip(x_center + radius * np.cos(theta),
                      rect_top + radius * np.sin(theta)))
    verts += [(x_left, rect_top), (x_left, 0)]
    codes = [MPath.MOVETO] + [MPath.LINETO] * (len(verts) - 2) + [MPath.CLOSEPOLY]
    clip = PathPatch(MPath(verts, codes), facecolor='none', edgecolor='none',
                     transform=ax.transData)
    ax.add_patch(clip)
    top = np.array(mcolors.to_rgb(c_top))
    bot = np.array(mcolors.to_rgb(c_bot))
    grad = np.zeros((256, 1, 4))
    for i in range(256):
        frac = i / 255  # 0 = bottom, 1 = top
        grad[i, 0, :3] = bot + (top - bot) * frac
        grad[i, 0, 3] = alpha
    im = ax.imshow(grad, aspect='auto', origin='lower',
                   extent=[x_left, x_right, 0, height], zorder=3,
                   interpolation='bilinear')
    im.set_clip_path(clip)

OUTPUT_DIR = 'outputs/charts/platform/m2m'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


def make_chart(figsize, suffix):
    fig, ax = plt.subplots(figsize=figsize, dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')
    ax2 = ax.twinx()
    ax2.set_facecolor('none')

    # Buyers: gold-on-gold gradient rounded bars (left axis)
    for xi, h in zip(x, wk['buyers']):
        gold_gradient_bar(ax, x_center=xi, width=0.74, height=h,
                          c_top=BUYERS_TOP, c_bot=BUYERS_BOT)

    # Transactions: clean line + glow + endpoint dot (right axis)
    area_glow(ax2, x, wk['tx'].to_numpy(), color=TX, max_alpha=0.16)
    ax2.plot(x, wk['tx'], color=TX, linewidth=3.0, zorder=6,
             solid_capstyle='round', solid_joinstyle='round')
    endpoint_dot(ax2, x[-1], wk['tx'].iloc[-1], color=TX, size=64)

    # left axis: Buyers (5 ticks)
    ax.set_yticks([0, 4000, 8000, 12000, 16000])
    ax.set_yticklabels(['0K', '4K', '8K', '12K', '16K'], fontsize=13,
                       fontweight='bold', color=COLORS['text_secondary'])
    ax.set_ylim(0, 16000)

    # right axis: Transactions (5 ticks, aligned to left gridlines)
    ax2.set_yticks([0, 3e5, 6e5, 9e5, 12e5])
    ax2.set_yticklabels(['0M', '0.3M', '0.6M', '0.9M', '1.2M'], fontsize=13,
                        fontweight='bold', color=COLORS['text_secondary'])
    ax2.set_ylim(0, 12e5)

    # x axis: daily, label every ~5 days as "Mon DD"
    tick_idx = list(range(0, n, 5))
    if tick_idx[-1] != n - 1:
        tick_idx.append(n - 1)
    ax.set_xticks([x[i] for i in tick_idx])
    ax.set_xticklabels([days[i].strftime('%b %d') for i in tick_idx],
                       fontsize=14, fontweight='bold', color=COLORS['text'])
    ax.set_xlim(-0.7, n - 0.3)

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
    ax.tick_params(axis='x', length=6, width=1,
                   color=COLORS['text_secondary'])

    fig.tight_layout()
    for fmt in ['png', 'svg']:
        fig.savefig(f'{OUTPUT_DIR}/x402_buyers_transactions_daily_{suffix}.{fmt}',
                    dpi=DPI, facecolor='none', edgecolor='none',
                    bbox_inches='tight', transparent=True,
                    format=fmt if fmt == 'svg' else None)
    plt.close()


make_chart((10.67, 5.2), 'wide')
print('Done: x402_buyers_transactions_daily')
print(f"  range {days[0].strftime('%b %d')} -> {days[-1].strftime('%b %d')}, "
      f"{n} days")
print(f"  tx max={wk['tx'].max()/1e6:.2f}M  buyers max={wk['buyers'].max()/1e3:.1f}K")
