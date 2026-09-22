"""
Amazon net sales 1994-1999 (log scale) with milestone annotation cards.
Reference reproduction in the four-pillars dark theme.
"""
import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from config import setup_font, save_chart, COLORS, GRID_CONFIG, DPI

LINE = '#5470c6'
FLOOR = 1.2e5        # 로그축에 $0을 못 찍는다. 1994년은 틱마크 바로 위에 앉힌다

df = pd.read_csv('outputs/data/amazon/amazon_revenue_1994_1999.csv')
x = df['year'].to_numpy(float)
y = np.where(df['revenue_usd'] > 0, df['revenue_usd'], FLOOR).astype(float)

setup_font()
fig, ax = plt.subplots(figsize=(11.6, 6.0), dpi=DPI)
fig.subplots_adjust(left=0.085, right=0.975, top=0.98, bottom=0.10)
fig.patch.set_alpha(0)
ax.set_facecolor('none')
ax.set_yscale('log')
ax.set_xlim(1993.90, 1999.10)  # 마커 반지름만큼만 여유
ax.set_ylim(1e5, 1e10)   # 틱($1M~$1B) 위아래로 정확히 1 decade씩

# 축/그리드
for s in ax.spines.values():
    s.set_visible(False)
ax.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=0.25,
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
ax.set_xticks(df['year'])
ax.set_xticklabels([str(int(v)) for v in df['year']])
ax.set_yticks([1e6, 1e7, 1e8, 1e9])
ax.set_yticklabels([r'\$1M', r'\$10M', r'\$100M', r'\$1B'])
ax.tick_params(axis='y', labelsize=16, pad=10, length=0,
               colors=COLORS['text_secondary'])
ax.tick_params(axis='y', which='minor', length=0)
ax.tick_params(axis='x', labelsize=16, pad=8, length=7, width=1.4,
               direction='out', colors=COLORS['text_secondary'])
for lab in ax.get_xticklabels() + ax.get_yticklabels():
    lab.set_fontweight('bold')

# 라인 + 에어리어
ax.fill_between(x, 1e5, y, color=LINE, alpha=0.13, linewidth=0, zorder=2)
ax.plot(x, y, color=LINE, lw=3.2, zorder=4, solid_capstyle='round',
        clip_on=False)
ax.plot(x, y, 'o', ms=9, mfc='#ffffff', mec=LINE, mew=3.0, zorder=5,
        clip_on=False)   # 바닥에 앉은 1994 마커가 잘리지 않게

# 값 라벨 (위/아래 배치는 레퍼런스 그대로)
# (dx, dy, ha) 오프셋. 축 끝 두 점은 안쪽으로 밀어 잘리지 않게 한다
off = {1994: (6, 20, 'left'), 1995: (0, -24, 'center'), 1996: (0, 20, 'center'),
       1997: (0, -24, 'center'), 1998: (0, 20, 'center'), 1999: (-8, 20, 'right')}
for _, r in df.iterrows():
    yr, yv = int(r['year']), (r['revenue_usd'] or FLOOR)
    dx, dy, ha = off[yr]
    ax.annotate(r['label'].replace('$', r'\$'),
                xy=(yr, yv), xytext=(dx, dy), textcoords='offset points', ha=ha,
                va='bottom' if dy > 0 else 'top',
                fontsize=14, fontweight='bold', color=COLORS['text'], zorder=6)

# --- 밀스톤 카드 ---------------------------------------------------------
def a2d(xf, yf):
    """axes fraction -> data coords"""
    return ax.transData.inverted().transform(ax.transAxes.transform((xf, yf)))

def card(x0, x1, y0, y1, year, accent, title, lines, conn_y=None,
         conn_val=None, align='right'):
    """박스 없이 글만, 오른쪽 정렬. (x0..x1, y0..y1)은 텍스트 블록 axes fraction 영역.

    conn_y는 점선 시작 높이(axes fraction), conn_val은 같은 것을 데이터 값으로
    준다(예: 100M 그리드선에 맞추려면 1e8).
    """
    px, py = year, float(df.loc[df['year'] == year, 'revenue_usd'].iloc[0] or FLOOR)
    tx = a2d(x1 if align == 'right' else (x0 + x1) / 2, 0)[0]
    ax.text(tx, a2d(0, y1 - (y1 - y0) * 0.18)[1], title, ha=align, va='center',
            fontsize=14.5, fontweight='bold', color=accent, zorder=11)
    for i, ln in enumerate(lines):
        ax.text(tx, a2d(0, y1 - (y1 - y0) * (0.39 + 0.21 * i))[1], ln,
                ha=align, va='center', fontsize=13, fontweight='bold',
                color=COLORS['text_secondary'], zorder=11)

    # 포인트로 내려/올라가는 점선
    _, dy0 = a2d(x0, y0)
    _, dy1 = a2d(x0, y1)
    edge_y = (conn_val if conn_val is not None else
              a2d(0, conn_y)[1] if conn_y is not None else
              (dy0 if dy0 > py else dy1))
    ax.plot([px, px], [edge_y, py], color=accent, lw=1.6, ls=(0, (4, 3.2)),
            alpha=0.6, zorder=8)

card(0.075, 0.345, 0.455, 0.665, 1995, '#9aa0ab', 'Bounded Catalog (1995)',
     ['Books Only, 1M+ Titles', 'Online Store Opens'], conn_val=1e7)
card(0.335, 0.665, 0.775, 0.995, 1997, LINE, 'Lower Checkout Friction (1997)',
     ['1-Click + Recommendations', 'Repeat Orders: >58%'], conn_val=1e9)
card(0.455, 0.865, 0.325, 0.545, 1998, '#3ba272', 'Category Expansion (1998)',
     ['Music, Video + International Stores', 'Repeat Orders: >64%'],
     conn_val=1e8, align='center')
card(0.585, 0.985, 0.075, 0.295, 1999, '#fc8452', 'General Commerce (1999)',
     ['Toys, Electronics + zShops/Payments', 'Repeat Orders: >73%'], conn_val=1e6)

save_chart(fig, 'amazon_revenue_milestones',
           output_dir='outputs/charts/amazon/revenue', tight=False)
plt.close()
print('saved')
