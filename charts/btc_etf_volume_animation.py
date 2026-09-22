import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
from matplotlib.ticker import MaxNLocator
from pathlib import Path
import numpy as np
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, AXIS_CONFIG, DPI

mpl.rcParams['axes.unicode_minus'] = False

# =============================================================================
# 데이터 로드
# =============================================================================
df = pd.read_csv('outputs/data/btc_etf_daily_volume.csv', index_col=0, parse_dates=True)

main_etfs = ['IBIT', 'FBTC', 'GBTC', 'ARKB']
df['Others'] = df.drop(columns=main_etfs, errors='ignore').sum(axis=1)
df = df[main_etfs + ['Others']]
df = df / 1e9  # $B

ETF_COLORS = {
    'IBIT':   '#1a1a2e',
    'FBTC':   '#4CAF50',
    'GBTC':   '#8B8B8B',
    'ARKB':   '#FF6B35',
    'Others': '#5470c6',
}

stack_order = ['Others', 'ARKB', 'GBTC', 'FBTC', 'IBIT']

# =============================================================================
# Figure 설정
# =============================================================================
setup_font()
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=150)

# 다크 배경 (영상용이라 투명 대신 다크)
fig.patch.set_facecolor(COLORS['background'])
ax.set_facecolor(COLORS['background'])

# 축 스타일
for spine in ax.spines.values():
    spine.set_visible(False)

ax.tick_params(axis='y', labelsize=20, length=0, pad=15, colors=COLORS['text_secondary'])
ax.tick_params(axis='x', labelsize=16, length=0, pad=20, colors=COLORS['text_secondary'])

# Y축 고정
y_max = df.sum(axis=1).max() * 1.15
ax.set_ylim(0, y_max)
ax.set_xlim(df.index[0] - pd.Timedelta(days=2), df.index[-1] + pd.Timedelta(days=2))

def billions_formatter(x, pos):
    return f'${x:.0f}B'
ax.yaxis.set_major_formatter(mticker.FuncFormatter(billions_formatter))
ax.yaxis.set_major_locator(MaxNLocator(nbins=5))

# X축
start_date = df.index[0]
month_starts = pd.date_range(start='2025-11-01', end=df.index[-1], freq='MS')
tick_dates = [start_date] + list(month_starts)
ax.set_xticks(tick_dates)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.setp(ax.xaxis.get_majorticklabels(), ha='right', rotation=45)

# 그리드
ax.grid(True, axis='y', color='#404040', alpha=0.8, linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.set_axisbelow(True)

fig.tight_layout()

# =============================================================================
# 애니메이션
# =============================================================================
n_frames = len(df)
bar_containers = {}

def init():
    return []

def animate(frame_idx):
    # 기존 바 제거
    for p in list(ax.patches):
        p.remove()
    for c in list(ax.collections):
        c.remove()

    # frame_idx까지의 데이터만 그리기
    subset = df.iloc[:frame_idx + 1]

    bottom = pd.Series(0, index=subset.index)
    artists = []

    for etf in stack_order:
        bars = ax.bar(
            subset.index,
            subset[etf],
            bottom=bottom,
            width=0.8,
            color=ETF_COLORS[etf],
            edgecolor='#1a1a1a',
            linewidth=0.3,
        )
        bottom += subset[etf]
        artists.extend(bars)

    return artists

print(f"Rendering {n_frames} frames...")
anim = FuncAnimation(
    fig,
    animate,
    init_func=init,
    frames=n_frames,
    interval=50,  # 50ms per frame = 20fps 느낌
    blit=False,
)

output_dir = 'outputs/charts/etf'
Path(output_dir).mkdir(parents=True, exist_ok=True)
output_path = f"{output_dir}/btc_etf_daily_volume_animated.mp4"

anim.save(
    output_path,
    writer='ffmpeg',
    fps=20,
    dpi=150,
    savefig_kwargs={'facecolor': COLORS['background']},
)

plt.close(fig)
print(f"Saved: {output_path}")
print(f"Frames: {n_frames}, Duration: {n_frames/20:.1f}s")
