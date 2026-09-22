"""
Tokenized RWA Market, 2024-H1 2026 ($B, ex-stablecoins) - Stacked Area
Four Pillars design theme
Data: sources/rwa-token-timeseries-export-1784173745761.csv (rwa.xyz export)
Colors: rwa.xyz asset_classes palette (app.rwa.xyz __NEXT_DATA__)

출력 2종:
  rwa_tokenized_market_stacked      기존버전, 549x309 (작은 figure + 작은 폰트)
  rwa_tokenized_market_stacked_tall four-pillars 표준 스타일, 550x800
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from pathlib import Path
from config import COLORS, apply_style, setup_font, save_chart, DPI

SRC = 'sources/rwa-token-timeseries-export-1784173745761.csv'
OUTPUT_DIR = 'outputs/charts/rwa/market'
END_DATE = '2026-07-06'
START_DATE = '2024-01-01'

# colors match the user's 6-item legend: 5 named classes + everything else = Others.
# ordered bottom -> top (ascending by current value)
OTHERS = '#7d7d7e'
STACK = [
    ('Real Estate', OTHERS),
    ('Diversified Credit', OTHERS),
    ('Venture Capital', OTHERS),
    ('Private Equity', OTHERS),
    ('non-US Government Debt', OTHERS),
    ('Active Strategies', OTHERS),
    ('Corporate Credit', OTHERS),
    ('Stocks', '#89195a'),
    ('Specialty Finance', '#5c239c'),
    ('Asset-Backed Credit', '#4a6226'),
    ('Commodities', '#967129'),
    ('US Treasury Debt', '#0d2e53'),
]

df = pd.read_csv(SRC)
df['Date'] = pd.to_datetime(df['Date'])
for col, _ in STACK:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0) / 1e9

df = df[(df['Date'] >= START_DATE) & (df['Date'] <= END_DATE)].sort_values('Date')
assert len(df) > 700, f'unexpected row count: {len(df)}'


def _plot(ax, line_lw):
    dates = df['Date']
    cumulative = np.cumsum([df[c].values for c, _ in STACK], axis=0)

    for i, (_, color) in enumerate(STACK):
        bottom = cumulative[i - 1] if i > 0 else np.zeros(len(dates))
        ax.fill_between(dates, bottom, cumulative[i], color=color,
                        alpha=0.95, linewidth=0, zorder=2)

    ax.plot(dates, cumulative[-1], color='#7aa6d6', linewidth=line_lw,
            alpha=0.9, zorder=4)

    ax.set_xlim(dates.iloc[0], dates.iloc[-1])
    ax.set_ylim(0, 40)
    ax.yaxis.set_major_locator(mticker.FixedLocator([0, 10, 20, 30, 40]))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%gB'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))


def draw_original():
    """기존버전: 549x309."""
    setup_font()
    fig, ax = plt.subplots(figsize=(3.55, 1.95), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    _plot(ax, line_lw=0.8)

    ax.grid(True, axis='y', color=COLORS['grid'], alpha=0.5,
            linestyle=(0, (3.7, 1.6)), linewidth=0.5)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.tick_params(axis='y', labelsize=6, pad=4, length=0,
                   colors=COLORS['text_secondary'])
    ax.tick_params(axis='x', labelsize=5.5, pad=3, length=0,
                   colors=COLORS['text_secondary'])
    plt.setp(ax.xaxis.get_majorticklabels(), ha='right', rotation=45)

    fig.tight_layout(pad=0.3)
    return fig


def draw_tall(figsize=(5.5, 8.0)):
    """four-pillars 표준 스타일, 550x800 세로 비율."""
    setup_font()
    fig, ax = plt.subplots(figsize=figsize, dpi=100)

    _plot(ax, line_lw=1.8)
    apply_style(fig, ax, 'stacked')

    # 표준 폰트(10.67in 폭에 24/22pt)를 이 figure 폭에 맞춰 축소
    s = figsize[0] / 10.67
    ax.tick_params(axis='y', labelsize=24 * s, pad=15 * s, length=0)
    ax.tick_params(axis='x', labelsize=22 * s, pad=10 * s, length=0)
    for gl in ax.get_ygridlines():
        gl.set_linewidth(1.0 * s)

    fig.tight_layout()
    return fig


def save_at_width(fig, filename, target_px):
    """save_chart와 동일한 투명 배경 저장, 단 가로 픽셀을 target_px에 맞춘 dpi로."""
    from PIL import Image
    out = Path(OUTPUT_DIR)
    out.mkdir(parents=True, exist_ok=True)
    kw = dict(facecolor='none', edgecolor='none', bbox_inches='tight',
              transparent=True)
    dpi = target_px / fig.get_size_inches()[0]
    for _ in range(4):  # bbox_inches='tight'가 폭을 바꾸므로 dpi를 보정
        fig.savefig(out / f'{filename}.png', dpi=dpi, **kw)
        w = Image.open(out / f'{filename}.png').size[0]
        if abs(w - target_px) <= 2:
            break
        dpi *= target_px / w
    fig.savefig(out / f'{filename}.svg', format='svg', **kw)
    return out / f'{filename}.png'


if __name__ == '__main__':
    last = df.iloc[-1]
    print(f'{last["Date"].date()} total: ${sum(last[c] for c, _ in STACK):.2f}B')

    fig = draw_original()
    png, _ = save_chart(fig, 'rwa_tokenized_market_stacked', output_dir=OUTPUT_DIR)
    print(f'  -> {png}')
    plt.close(fig)

    fig = draw_tall()
    print(f'  -> {save_at_width(fig, "rwa_tokenized_market_stacked_tall", 550)}')
    plt.close(fig)
