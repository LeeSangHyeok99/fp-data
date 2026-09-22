"""
Illustrative payoff of a locked-share carry trade
Four Pillars 스타일 (와이드)

레퍼런스 재현. 외부 데이터 없음, 순수 페이오프 산식이다.
  long  = x + 15     락업 주식을 15% 할인에 매입 (진입 -15)
  short = -x         동일 노셔널 주식 퍼프 숏
  net(할인만)  = 15
  net(펀딩포함) = 15 + 5.5 = 20.5   (연 +10.9% 펀딩 캐리 × 6개월 홀드)
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(".claude/skills/design/four-pillars")))
from config import apply_style, create_figure, save_chart

LONG = "#e8710a"    # 오렌지, 락업 주식 롱
SHORT = "#3ba272"   # 틸, 퍼프 숏
NET = "#4285f4"     # 블루, 펀딩 포함 순손익
DIM = "#787b86"     # 그레이, 할인분만

DISCOUNT = 15.0                    # 할인 폭 (%p)
FUNDING = 5.5                      # 6개월 펀딩 캐리 (%p), 연 +10.9% 기준
OUT = "outputs/charts/four_pillars/carry"

x = np.array([-30.0, 30.0])
long_pnl = x + DISCOUNT
short_pnl = -x

fig, ax = create_figure("line")

ax.axhline(0, color=DIM, alpha=0.55, linewidth=1.2, zorder=1)
ax.plot(x, long_pnl, color=LONG, linewidth=2.6, zorder=4,
        solid_capstyle="round")
ax.plot(x, short_pnl, color=SHORT, linewidth=2.6, zorder=4,
        solid_capstyle="round")
ax.plot(x, [DISCOUNT, DISCOUNT], color=DIM, linewidth=2.4, zorder=3,
        linestyle=(0, (5, 3)))
ax.plot(x, [DISCOUNT + FUNDING] * 2, color=NET, linewidth=3.0, zorder=5)


def label(text, y, color, dy=0, size=15):
    """라인 오른쪽 끝 바깥에 붙는 인라인 라벨. dy는 겹침 회피용 픽셀 오프셋."""
    ax.annotate(text, xy=(30, y), xytext=(12, dy), textcoords="offset points",
                ha="left", va="center", fontsize=size, fontweight="bold",
                color=color, zorder=6, clip_on=False)


label("Long Locked Shares\n(Entered −15%)", long_pnl[-1], LONG)
label("Short Perp Hedge", short_pnl[-1], SHORT)
label(f"Net Incl. Funding  +{DISCOUNT + FUNDING:.1f}", DISCOUNT + FUNDING, NET, dy=6)
label(f"Net, Discount Only  +{DISCOUNT:.0f}", DISCOUNT, DIM, dy=-6)

ax.set_xlim(-30, 30)
ax.set_ylim(-34, 49)
ax.set_xticks(range(-30, 31, 10))
ax.set_xticklabels([f"{v:+d}%".replace("+0%", "0%") for v in range(-30, 31, 10)])
ax.set_yticks([-30, -15, 0, 15, 30, 45])
ax.set_yticklabels(["-30", "-15", "0", "+15", "+30", "+45"])

apply_style(fig, ax, "line")
ax.tick_params(axis="x", labelsize=18, rotation=0)
ax.tick_params(axis="y", labelsize=20)
ax.set_xlabel("Stock Price At Exit Vs Entry Mark", fontsize=16,
              fontweight="bold", color=DIM, labelpad=12)

print("saved:", *save_chart(fig, "locked_share_carry_payoff", OUT))
plt.close(fig)
