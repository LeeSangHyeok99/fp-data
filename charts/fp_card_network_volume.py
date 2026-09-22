"""Monthly Stablecoin Card Volumes by card network (Visa vs Mastercard).

Data: FP Research Payment Dashboard (research.4pillars.io/en/data/payment),
extracted from the recharts component props (2024-01 ~ 2026-07).
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MPath

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, GRID_CONFIG, DPI, save_chart

setup_font()

df = pd.read_csv('outputs/data/fp_card_network_monthly_volume.csv')
df['visa'] /= 1e6
df['mastercard'] /= 1e6
months = pd.to_datetime(df['date'] + '-01')
x = np.arange(len(df))

VISA_COLOR = '#3f43c4'    # Visa navy at the base, darkens toward the top
MC_COLOR = '#eb2c46'      # reference: red Mastercard sliver

BAR_W = 0.72
FLOOR = 0.32              # 그라데이션 최상단 밝기(0~1)


def visa_gradient_bar(ax, xc, height):
    """레퍼런스와 같은 방향: 위가 어둡고 아래로 갈수록 밝다."""
    x0, x1 = xc - BAR_W / 2, xc + BAR_W / 2
    verts = [(x0, 0), (x1, 0), (x1, height), (x0, height), (x0, 0)]
    codes = [MPath.MOVETO] + [MPath.LINETO] * 3 + [MPath.CLOSEPOLY]
    clip = PathPatch(MPath(verts, codes), facecolor='none', edgecolor='none',
                     transform=ax.transData)
    ax.add_patch(clip)

    rgb = np.array(mcolors.to_rgb(VISA_COLOR))
    frac = np.linspace(1, 0, 256)[:, None]  # 아래(1) -> 위(0)
    grad = np.ones((256, 1, 4))
    grad[:, 0, :3] = rgb * (FLOOR + (1 - FLOOR) * np.sqrt(frac))
    im = ax.imshow(grad, aspect='auto', origin='lower',
                   extent=[x0, x1, 0, height], zorder=3, interpolation='bilinear')
    im.set_clip_path(clip)


def make_chart(figsize, suffix):
    fig, ax = plt.subplots(figsize=figsize, dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    y_ticks = [0, 300, 600, 900, 1200]
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f'${v:,}M' for v in y_ticks],
                       fontsize=15, fontweight='bold', color=COLORS['text_secondary'])
    ax.set_ylim(0, 1200)
    ax.set_xlim(-0.7, len(df) - 0.3)
    ax.tick_params(axis='y', length=0, pad=10)

    for i in x:
        visa_gradient_bar(ax, i, df['visa'].iloc[i])
    ax.bar(x, df['mastercard'], bottom=df['visa'], width=BAR_W,
           color=MC_COLOR, zorder=4)

    pos = list(range(0, len(df), 2))  # Jan 2024부터 한 달 걸러
    ax.set_xticks(pos)
    ax.set_xticklabels([months[i].strftime('%b %Y') for i in pos],
                       fontsize=13, fontweight='bold',
                       color=COLORS['text_secondary'], rotation=45, ha='right',
                       rotation_mode='anchor')  # 앵커 정렬: 라벨마다 틱 기준 위치 동일
    ax.tick_params(axis='x', length=6, width=1, colors=COLORS['text_secondary'])

    ax.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
            linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
    ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_visible(False)

    fig.tight_layout()
    save_chart(fig, f'fp_card_network_volume{suffix}',
               output_dir='outputs/charts/crypto-payments/volume')
    plt.close(fig)


make_chart((10.67, 4.67), '')
make_chart((7.5, 7.5), '_square')

latest = df.iloc[-1]
total = df['visa'] + df['mastercard']
print(f"{df['date'].iloc[0]} ~ {df['date'].iloc[-1]}, {len(df)} months")
print(f"Jul 2026: Visa ${latest.visa:.1f}M + MC ${latest.mastercard:.1f}M "
      f"= ${total.iloc[-1]:.1f}M, Visa {latest.visa/total.iloc[-1]*100:.1f}%")
print(f"Cumulative Visa share: {df['visa'].sum()/total.sum()*100:.1f}%")
assert abs(total.iloc[-1] - (latest.visa + latest.mastercard)) < 1e-6
