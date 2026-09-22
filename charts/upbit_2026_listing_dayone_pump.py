"""
Day-One Pump of Every Fresh Upbit KRW Listing in 2026
레퍼런스 내재화 (bar). 데이터: Upbit 공개 API (candles/days, candles/minutes/60).
day-one pump = 상장 후 첫 24시간 고가 / 최초 체결가 - 1
four-pillars dark theme.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, str(Path('.claude/skills/design/four-pillars')))
from config import setup_font, COLORS, GRID_CONFIG, save_chart  # noqa: E402

setup_font()

TEXT = COLORS['text']
TEXT2 = COLORS['text_secondary']
WHITE = '#ffffff'
MINT = '#7ee8c0'          # Jun 15 이전
MINT_DIM = '#3f8f78'      # Jun 15 이후
CUT = pd.Timestamp('2026-06-15')

# 레퍼런스 모집단에 맞춰 제외. 스테이블/금은 애초에 펌프 대상이 아니고,
# legacy 5종은 KRW 마켓만 신규일 뿐 토큰 자체는 기존 상장 자산이라 "fresh"가 아니다.
EXCLUDE = {'XAUT', 'USDE', 'USDS', 'USDG', 'RLUSD',   # 스테이블 / 금
           'ICP', 'TRAC', 'CFX', 'WIF', 'TAO'}        # legacy

# ---------------------------------------------------------------- data
df = pd.read_csv('outputs/data/upbit_2026_krw_listing_dayone.csv',
                 parse_dates=['first_trade_kst'])
df = df[~df['ticker'].isin(EXCLUDE)]
df = df.sort_values('first_trade_kst').reset_index(drop=True)
x = np.arange(len(df))
y = df['day_one_pump_pct'].values
post = (df['first_trade_kst'] >= CUT).values

med_pre = float(np.median(y[~post]))
med_post = float(np.median(y[post]))
split = int(np.argmax(post))          # 첫 post 인덱스

# ---------------------------------------------------------------- figure
fig = plt.figure(figsize=(10.67, 4.67), dpi=150)
fig.patch.set_alpha(0)
ax = fig.add_subplot(111)
ax.set_facecolor('none')
for s in ax.spines.values():
    s.set_visible(False)

ax.bar(x, y, width=0.62, color=np.where(post, MINT_DIM, MINT),
       linewidth=0, zorder=3)

# ---------------------------------------------------------------- median lines
for x0, x1, m in ((-0.7, split - 0.5, med_pre), (split - 0.5, len(df) - 0.3, med_post)):
    ax.hlines(m, x0, x1, color=WHITE, linewidth=1.8, linestyle=(0, (5, 3)), zorder=5)

ax.text(11, med_pre + 6, f'Median +{med_pre:.0f}%', color=WHITE,
        fontsize=11, style='italic', ha='left', va='bottom', zorder=6)
ax.text(len(df) - 0.3, 40, f'Median +{med_post:.0f}%', color=WHITE,
        fontsize=11, style='italic', ha='right', va='bottom', zorder=6)

# ---------------------------------------------------------------- Jun 15 divider
ax.axvline(split - 0.5, color=TEXT2, linewidth=1.2, linestyle=(0, (5, 4)), zorder=4)
ax.text(split - 1.0, 252, 'Jun 15', color=TEXT2, fontsize=11, style='italic',
        ha='right', va='top', zorder=6)

# ---------------------------------------------------------------- bar labels
# (ticker, dx, ha) - CFG/EDGE는 인접해서 좌우로 벌린다
LABELS = [('ELSA', 0, 'center'), ('CFG', -0.5, 'right'), ('EDGE', 0.5, 'left'),
          ('BLEND', 0, 'center'), ('SLX', 0, 'center'), ('HOME', 0, 'center')]
for t, dx, ha in LABELS:
    i = int(df.index[df['ticker'] == t][0])
    ax.text(i + dx, y[i] + 8, f'{t} +{y[i]:.0f}%', color=WHITE, fontsize=10.5,
            ha=ha, va='bottom', zorder=6)

# ---------------------------------------------------------------- axes
ax.set_xlim(-1.0, len(df) - 0.2)
ax.set_ylim(0, 258)
ax.set_yticks([0, 50, 100, 150, 200])
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'+{v:.0f}%' if v else '0%'))

# 월 첫 상장 위치에 월 라벨
month_first = df.groupby(df['first_trade_kst'].dt.to_period('M')).apply(
    lambda g: g.index[0], include_groups=False)
ax.set_xticks(list(month_first.values))
ax.set_xticklabels([p.strftime('%b') for p in month_first.index])

ax.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
ax.tick_params(axis='y', labelsize=13, pad=8, length=0, colors=TEXT2)
ax.tick_params(axis='x', labelsize=13, pad=8, length=5, width=1, colors=TEXT2)

fig.tight_layout()
png, svg = save_chart(fig, 'upbit_2026_listing_dayone_pump',
                      'outputs/charts/korea_cex/listing')
print(f'n={len(df)} | median pre={med_pre:.1f}% post={med_post:.1f}%')
print(png)
print(svg)
