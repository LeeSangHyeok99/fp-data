import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import matplotlib as mpl
import numpy as np
import pandas as pd
from matplotlib.animation import FuncAnimation
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, GRID_CONFIG, DPI

mpl.rcParams['axes.unicode_minus'] = False

# =============================================================================
# 데이터 로드
# =============================================================================
df = pd.read_csv('outputs/data/Stake_by_module.csv')
df['day'] = pd.to_datetime(df['day'])
df = df.sort_values('day').reset_index(drop=True)
df = df[df['total_lido_stake'] > 0]

df['csm_stake'] = df['csm_stake'].fillna(0)
df['sdvt_stake'] = df['sdvt_stake'].fillna(0)
df['curated_stake'] = df['curated_stake'].fillna(0)

curated = df['curated_stake'].values / 1e6
sdvt = df['sdvt_stake'].values / 1e6
csm = df['csm_stake'].values / 1e6
x = df['day'].values

# 주간 샘플링
step = 7
indices = list(range(0, len(df), step))
if indices[-1] != len(df) - 1:
    indices.append(len(df) - 1)

# 3초 목표, 30fps = 90프레임
target_frames = 90
if len(indices) > target_frames:
    sample_step = max(1, len(indices) // target_frames)
    indices = indices[::sample_step]
    if indices[-1] != len(df) - 1:
        indices.append(len(df) - 1)

colors = ['#00A3FF', '#F69988', '#FFC170']

# =============================================================================
# Figure (기존 svg와 동일한 스타일)
# =============================================================================
setup_font()
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=150)

# 다크 배경
fig.patch.set_facecolor('#141414')
fig.patch.set_alpha(1.0)
ax.set_facecolor('#141414')

for spine in ax.spines.values():
    spine.set_visible(False)

# Y축 (기존 svg 동일)
ax.set_ylim(0, 10)
ax.set_yticks([0, 2.5, 5, 7.5, 10])
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f'{v:.1f}M'))

# X축 (기존 svg 동일)
ax.set_xlim(x[0], x[-1])
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# 기존 svg 폰트 크기 그대로
ax.tick_params(axis='y', labelsize=14, pad=15, length=0, colors=COLORS['text_secondary'])
ax.tick_params(axis='x', labelsize=12, pad=10, length=0, colors=COLORS['text_secondary'])

# 그리드 (기존 svg 동일: #787b86, 50% alpha)
ax.grid(True, axis='y',
        color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

fig.tight_layout()

# =============================================================================
# 애니메이션
# =============================================================================
fills = []
lines = []

def init():
    return []

def animate(frame_num):
    global fills, lines

    for f in fills:
        f.remove()
    for l in lines:
        l.remove()
    fills.clear()
    lines.clear()

    end_idx = indices[frame_num] + 1
    x_sub = x[:end_idx]
    series = [curated[:end_idx], sdvt[:end_idx], csm[:end_idx]]

    # Stacked area (alpha 0.75 = 선형 75%)
    result = ax.stackplot(x_sub, *series, colors=colors, alpha=0.75, edgecolor='none', linewidth=0)
    fills.extend(result)

    # 경계선
    bottom = np.zeros(end_idx)
    for i, s in enumerate(series):
        bottom = bottom + s
        line, = ax.plot(x_sub, bottom, color=colors[i], linewidth=1.2)
        lines.append(line)

    return fills + lines

n_frames = len(indices)
print(f"Rendering {n_frames} frames (~{n_frames/30:.1f}s at 30fps)...")

anim = FuncAnimation(
    fig, animate, init_func=init,
    frames=n_frames, interval=33, blit=False,
)

output_dir = 'outputs/charts/lido'
Path(output_dir).mkdir(parents=True, exist_ok=True)
output_path = f"{output_dir}/lido_stake_by_module_animated.mp4"

anim.save(
    output_path,
    writer='ffmpeg',
    fps=30,
    dpi=150,
    savefig_kwargs={'facecolor': '#141414'},
)

plt.close(fig)
print(f"Saved: {output_path}")
print(f"Frames: {n_frames}, Duration: {n_frames/30:.1f}s")
