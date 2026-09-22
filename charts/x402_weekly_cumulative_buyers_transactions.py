import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, GRID_CONFIG, DPI, area_glow

setup_font()

# =============================================================================
# x402 weekly CUMULATIVE chart (Artemis reproduction):
#   Buyers (gold bars, left axis)  = cumulative weekly buyers
#   Transactions (purple line, right axis) = cumulative weekly transactions
#
# Source: sources/Metric Comparison - x402 (2).csv  (weekly, week-ending Sun).
#   IMPORTANT: the source "Buyers" column is a 7-DAY AVERAGE (fractional), so it
#   is converted to a weekly total (x7) BEFORE cumulating. Cumulating the raw
#   average would understate the total ~7x. The cumulative buyers therefore
#   represent cumulative buyer-activity (buyer-days), not unique buyers.
#   Weeks Mar 23 -> Jun 15 (week-start labels), 13 weeks.
# =============================================================================
df = pd.read_csv('sources/Metric Comparison - x402 (2).csv')
df.columns = ['dt', 'tx', 'buyers']
df['dt'] = pd.to_datetime(df['dt'])
df = df.sort_values('dt').reset_index(drop=True)

df['buyers_weekly'] = (df['buyers'] * 7).round()          # 7-day avg -> weekly total
df['buyers_cum'] = df['buyers_weekly'].cumsum()
df['tx_cum'] = df['tx'].cumsum()
labels = (df['dt'] - pd.Timedelta(days=6)).dt.strftime('%b %-d')  # week-start (Mon)

n = len(df)
x = np.arange(n, dtype=float)

BUYERS_TOP = '#eccf72'    # Buyers bar: light gold (top)
BUYERS_BOT = '#9a7522'    # Buyers bar: dark gold, same family (bottom)
TX = '#8b7cf2'            # Artemis purple (Transactions, line)


def gold_gradient_bar(ax, x_center, width, height, c_top, c_bot, alpha=0.97):
    """Rounded-top bar with a gradient between two shades of the same hue
    (light gold at top -> dark gold at bottom)."""
    import matplotlib.colors as mcolors
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path as MPath
    if height is None or height <= 0:
        return
    radius = min(width / 2, height * 0.05)
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

    # Buyers: gold-on-gold gradient rounded bars (left axis), cumulative
    for xi, h in zip(x, df['buyers_cum']):
        gold_gradient_bar(ax, x_center=xi, width=0.70, height=h,
                          c_top=BUYERS_TOP, c_bot=BUYERS_BOT)

    # Transactions: clean cumulative line + subtle glow (right axis)
    area_glow(ax2, x, df['tx_cum'].to_numpy(), color=TX, max_alpha=0.12)
    ax2.plot(x, df['tx_cum'], color=TX, linewidth=3.0, zorder=6,
             solid_capstyle='round', solid_joinstyle='round')

    # left axis: cumulative Buyers (0 -> 800K)
    ax.set_yticks([0, 200000, 400000, 600000, 800000])
    ax.set_yticklabels(['0', '200K', '400K', '600K', '800K'], fontsize=13,
                       fontweight='bold', color=COLORS['text_secondary'])
    ax.set_ylim(0, 800000)

    # right axis: cumulative Transactions (0 -> 15M)
    ax2.set_yticks([0, 5e6, 10e6, 15e6])
    ax2.set_yticklabels(['0', '5M', '10M', '15M'], fontsize=13,
                        fontweight='bold', color=COLORS['text_secondary'])
    ax2.set_ylim(0, 15e6)

    # x axis: every week labelled (week-start), slight rotation
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=13, fontweight='bold',
                       color=COLORS['text_secondary'], rotation=30, ha='right')
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
    ax.tick_params(axis='x', length=6, width=1, color=COLORS['text_secondary'])

    fig.tight_layout()
    for fmt in ['png', 'svg']:
        fig.savefig(
            f'{OUTPUT_DIR}/x402_weekly_cumulative_buyers_transactions.{fmt}',
            dpi=DPI, facecolor='none', edgecolor='none', bbox_inches='tight',
            transparent=True, format=fmt if fmt == 'svg' else None)
    plt.close()


make_chart((10.67, 4.6), 'wide')
print('Done: x402_weekly_cumulative_buyers_transactions')
print(f"  weeks {labels.iloc[0]} -> {labels.iloc[-1]}, {n} weeks")
print(f"  buyers_cum end = {df['buyers_cum'].iloc[-1]:,.0f}  "
      f"tx_cum end = {df['tx_cum'].iloc[-1]/1e6:.2f}M")
