import json
import sys
import importlib.util
from pathlib import Path

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates

sys.path.append('.claude/skills/design/hrc')
from config import setup_font, apply_style, COLORS, GRID_CONFIG, DPI

# 그라데이션 바 이펙트는 four-pillars 쪽에만 있어서 별도 이름으로 로드
_spec = importlib.util.spec_from_file_location(
    'fp_config', '.claude/skills/design/four-pillars/config.py')
fp_config = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fp_config)
gradient_rounded_bar = fp_config.gradient_rounded_bar

mpl.rcParams['axes.unicode_minus'] = False

CSV = 'outputs/data/hl_af_weekly_buyback_h1_2026.csv'
START, END = pd.Timestamp('2026-01-01'), pd.Timestamp('2026-06-30')

if not Path(CSV).exists():
    d = pd.DataFrame(json.load(open('outputs/data/asxn_hl_buybacks_daily.json')))
    d['date'] = pd.to_datetime(d['date']).dt.tz_localize(None).dt.normalize()
    d['ntl'] = d['ntl'].astype(float)
    d = d[(d['date'] >= START) & (d['date'] <= END)].copy()
    # 주 시작(월요일) 기준 집계. 첫/마지막 주는 반기 경계로 잘린 부분 주.
    d['week_start'] = d['date'] - pd.to_timedelta(d['date'].dt.dayofweek, unit='D')
    (d.groupby('week_start')['ntl'].sum().div(1e6).round(4)
       .rename('buyback_musd').reset_index().to_csv(CSV, index=False))

df = pd.read_csv(CSV, parse_dates=['week_start'])

HYPE_MINT = '#50e3c2'

setup_font()
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

ax.set_ylim(0, 23)
ax.set_yticks([0, 5, 10, 15, 20])
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.0f}M'))

ax.set_xlim(mdates.date2num(df['week_start'].min() - pd.Timedelta(days=8)),
            mdates.date2num(df['week_start'].max() + pd.Timedelta(days=8)))
# ISO 주 라벨 (4주 간격). 첫 바(12/29 시작)는 ISO상 2026-W01.
ticks = df['week_start'][::4]
ax.set_xticks([mdates.date2num(t) for t in ticks])
ax.set_xticklabels([f"{t.isocalendar().year % 100:02d}W{t.isocalendar().week:02d}"
                    for t in ticks])

apply_style(fig, ax, 'bar')
ax.tick_params(axis='y', labelsize=20, length=0)
ax.tick_params(axis='x', labelsize=18, length=6, width=1, pad=8, rotation=45,
               colors=COLORS['text_secondary'])
# 틱마크가 허공에 뜨지 않게 베이스라인을 깐다 (spine은 숨김 상태)
ax.axhline(0, color=COLORS['text_secondary'], alpha=0.6, linewidth=1, zorder=4)
plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
ax.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
fig.canvas.draw()  # gradient_rounded_bar가 픽셀 변환을 쓰므로 축 확정 후 그린다

for ts, v in zip(df['week_start'], df['buyback_musd']):
    gradient_rounded_bar(ax, mdates.date2num(ts), 4.6, v, HYPE_MINT, floor=0.22)

# 첫 주, 최대 주, 마지막 주만 값 라벨
peak = df['buyback_musd'].idxmax()
for i in (0, peak, len(df) - 1):
    ts, v = df['week_start'][i], df['buyback_musd'][i]
    ax.text(mdates.date2num(ts), v + 0.6, f'${v:.1f}M', color=COLORS['text'],
            fontsize=15, fontweight='bold', ha='center', va='bottom', zorder=5)

out = 'outputs/charts/hyperliquid/revenue'
Path(out).mkdir(parents=True, exist_ok=True)
for ext in ('png', 'svg'):
    fig.savefig(f'{out}/hleco_af_weekly_buyback_h1_2026.{ext}', dpi=DPI,
                facecolor='none', edgecolor='none', bbox_inches='tight',
                transparent=True)
plt.close(fig)
print(f'{out}/hleco_af_weekly_buyback_h1_2026.png  total=${df["buyback_musd"].sum():.1f}M  weeks={len(df)}')
