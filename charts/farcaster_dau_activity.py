import sys

import matplotlib

matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import apply_style, setup_font

# =============================================================================
# Data: Dune query 3024331 (@pixelhack) — Farcaster cast, reaction, link volume
# =============================================================================
df = pd.read_csv('sources/Farcaster_cast_reaction_link_volume.csv',
                 parse_dates=['trunc_date']).sort_values('trunc_date')

COLOR_CAST = '#855DCD'      # Farcaster 퍼플 (레퍼런스 cast)
COLOR_REACTION = '#EE6666'  # 레드 (레퍼런스 reaction)
COLOR_LINK = '#787B86'      # 그레이 (레퍼런스 link)
COLOR_AVG = '#FAC858'       # 옐로우 (trailing avg 7d)

setup_font()

MONTHS = mdates.MonthLocator(bymonth=[3, 5, 7])
FMT = mdates.DateFormatter('%b %Y')


# 두 차트를 한 슬롯에 나란히 넣는 전제라 동일한 반쪽 폭 비율(≈1.47:1)을 쓴다
FIGSIZE = (7.2, 4.9)


def finish(fig, ax, y_ticks, y_labels, y_max, pad_days):
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.set_ylim(0, y_max)
    ax.xaxis.set_major_locator(MONTHS)
    ax.xaxis.set_major_formatter(FMT)
    ax.set_xlim(df['trunc_date'].min() - pd.Timedelta(days=pad_days),
                df['trunc_date'].max() + pd.Timedelta(days=pad_days))
    apply_style(fig, ax, 'bar')
    ax.tick_params(axis='y', labelsize=13)
    ax.tick_params(axis='x', labelsize=12)
    # tight bbox 대신 고정 마진: y 라벨 폭('40K' vs '3M')이 달라도 두 차트의
    # 캔버스 크기와 플롯 영역이 픽셀 단위로 같아진다 (나란히 놓았을 때 정렬)
    fig.subplots_adjust(left=0.125, right=0.985, top=0.955, bottom=0.19)


def save(fig, filename, out_dir):
    from pathlib import Path
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    for ext in ('png', 'svg'):
        fig.savefig(f'{out_dir}/{filename}.{ext}', dpi=150, transparent=True)
    print(f'{out_dir}/{filename}.png')


# =============================================================================
# 1) Farcaster DAU — uniq cast fid / uniq reaction fid (overlay) + 7d 평균
# =============================================================================
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=150)

# bar 대신 vlines: 일별 시리즈에서 픽셀 반올림 줄무늬를 피한다
ax.vlines(df['trunc_date'], 0, df['unique_fids_casts'],
          color=COLOR_CAST, linewidth=1.6, capstyle='butt', zorder=2)
ax.vlines(df['trunc_date'], 0, df['unique_fids_reactions'],
          color=COLOR_REACTION, linewidth=1.6, capstyle='butt', alpha=0.8,
          zorder=3)
ax.plot(df['trunc_date'], df['avg_7day_unique_users_casts'],
        color=COLOR_AVG, linewidth=2.2, zorder=4)

finish(fig, ax, [0, 10000, 20000, 30000, 40000],
       ['0K', '10K', '20K', '30K', '40K'], 41000, 1)
save(fig, 'farcaster_dau', 'outputs/charts/farcaster/metrics')
plt.close(fig)

# =============================================================================
# 2) Cast / Reaction / Link volume — 스택 에어리어
# =============================================================================
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=150)

ax.stackplot(df['trunc_date'],
             df['count_casts'] / 1e6,
             df['count_reactions'] / 1e6,
             df['count_links'] / 1e6,
             colors=[COLOR_CAST, COLOR_REACTION, COLOR_LINK],
             linewidth=0)

finish(fig, ax, [0, 1, 2, 3], ['0M', '1M', '2M', '3M'], 3.0, 0)
save(fig, 'farcaster_cast_reaction_link_volume', 'outputs/charts/farcaster/volume')
plt.close(fig)
