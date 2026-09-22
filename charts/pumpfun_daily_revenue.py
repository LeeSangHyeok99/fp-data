import sys
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MPath

sys.path.append('.claude/skills/design/four-pillars')
from config import apply_style, setup_font

# =============================================================================
# Data: DefiLlama daily revenue (pump.fun)
# =============================================================================
df = pd.read_csv('outputs/data/pumpfun_daily_revenue.csv', parse_dates=['date'])

COLOR_REV = '#55D292'   # pump.fun 브랜드 그린

# 하루당 픽셀을 정수로 고정해야 막대/간격이 균일하게 렌더된다.
# 축 폭 = 일수 x DAY_PX, 막대 폭 = BAR_PX (나머지 픽셀이 간격)
DPI = 150
DAY_PX, BAR_PX = 6, 4
LEFT_PX, RIGHT_PX, BOTTOM_PX, TOP_PX = 130, 12, 150, 20
AX_W = len(df) * DAY_PX
AX_H = 530
FIG_W = LEFT_PX + AX_W + RIGHT_PX
FIG_H = TOP_PX + AX_H + BOTTOM_PX

setup_font()
fig, ax = plt.subplots(figsize=(FIG_W / DPI, FIG_H / DPI), dpi=DPI)

ax.set_yticks([0, 0.5, 1.0, 1.5, 2.0])
ax.set_yticklabels(['$0M', '$0.5M', '$1.0M', '$1.5M', '$2.0M'])
ax.set_ylim(0, 2.1)

ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
# 하루가 정확히 DAY_PX가 되도록 양끝을 반나절씩만 띄운다
ax.set_xlim(df['date'].min() - pd.Timedelta(hours=12),
            df['date'].max() + pd.Timedelta(hours=12))

# 막대는 한 장의 세로 그라데이션 이미지를 막대 실루엣으로 클립해서 그린다
# (막대마다 imshow 를 부르면 243장이 되므로 하나로 합친다)
verts, codes = [], []
half = pd.Timedelta(days=BAR_PX / DAY_PX / 2)
for d, v in zip(df['date'], df['revenue_usd'] / 1e6):
    left, right = mdates.date2num(d - half), mdates.date2num(d + half)
    verts += [(left, 0), (right, 0), (right, v), (left, v), (left, 0)]
    codes += [MPath.MOVETO, MPath.LINETO, MPath.LINETO, MPath.LINETO,
              MPath.CLOSEPOLY]
clip = PathPatch(MPath(verts, codes), facecolor='none', edgecolor='none',
                 transform=ax.transData)
ax.add_patch(clip)

r, g, b = mcolors.to_rgb(COLOR_REV)
FLOOR = 0.62  # 바닥 밝기. 1에 가까울수록 그라데이션이 약하다
factor = FLOOR + (1 - FLOOR) * np.linspace(0, 1, 256) ** 0.5
gradient = np.stack([r * factor, g * factor, b * factor,
                     np.ones(256)], axis=-1)[:, None, :]
img = ax.imshow(gradient, aspect='auto', origin='lower', zorder=2,
                interpolation='bilinear',
                extent=[*ax.get_xlim(), 0, ax.get_ylim()[1]])
img.set_clip_path(clip)

apply_style(fig, ax, 'bar')  # tight_layout 포함 → 위치 지정은 그 뒤에
ax.tick_params(axis='y', labelsize=13)
ax.tick_params(axis='x', labelsize=12)
ax.set_position([LEFT_PX / FIG_W, BOTTOM_PX / FIG_H, AX_W / FIG_W, AX_H / FIG_H])

out = Path('outputs/charts/pumpfun/revenue')
out.mkdir(parents=True, exist_ok=True)
for ext in ('png', 'svg'):
    # bbox_inches='tight' 는 크롭이 소수 픽셀로 밀려 정렬이 깨지므로 쓰지 않는다
    fig.savefig(out / f'pumpfun_daily_revenue.{ext}', dpi=DPI, transparent=True)
print(out / 'pumpfun_daily_revenue.png')
