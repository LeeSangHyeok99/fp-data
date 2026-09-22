"""SKHX(로컬) vs SKHY(ADR) 펀딩레이트 + 가격.

레이아웃 2종을 렌더한다:
  v1  hip3_skhx_skhy_funding_2panel  : 위 가격 / 아래 펀딩 (2단)
  v2  hip3_skhx_skhy_funding_dual    : 1단, 좌 Rate / 우 Price (레퍼런스 스펙)

가격은 두 버전 모두 시작가=100 인덱스. SKHX(~$1.2k)와 SKHY(~$170)는 스케일이
8배 차이라 실가격을 한 축에 얹으면 SKHY가 바닥에 눌린다. 인덱스로 맞추면
두 종목의 등락폭을 서로 직접 비교할 수도 있다.
"""
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, save_chart, DPI, AXIS_CONFIG, GRID_CONFIG, COLORS

setup_font()

# SK 공식 CI (skhynix.com/company/UI-FR-CP0402)
SKHX_COLOR = '#EA002C'   # Local shares / SK Red (Pantone 186C)
SKHY_COLOR = '#F47725'   # ADR / SK Orange (Pantone 158C)

Y_TICK_FS = 18
X_TICK_FS = 18

# 가격은 점선, 펀딩은 실선. 선 모양으로 지표를 구분한다(색은 종목 구분용).
PRICE_STYLE = dict(linewidth=1.4, alpha=0.5, linestyle=(0, (4, 2)))

OUT_DIR = 'outputs/charts/hyperliquid/hip3'

skhx = pd.read_csv('outputs/data/hip3_skhx_funding_jul10_15.csv', parse_dates=['time'])
skhy = pd.read_csv('outputs/data/hip3_skhy_funding_jul10_15.csv', parse_dates=['time'])
SERIES = ((skhx, SKHX_COLOR), (skhy, SKHY_COLOR))

XMIN, XMAX = skhx['time'].min(), skhx['time'].max()

# 펀딩 틱은 깔끔한 값(±0.10%)으로 두되, 한계는 넓혀 라인이 잘리지 않게 한다.
RATE_LIM, RATE_TICKS = (-0.13, 0.13), np.array([-0.10, -0.05, 0.00, 0.05, 0.10])
PX_LIM, PX_TICKS = (76, 124), np.array([80, 90, 100, 110, 120])


def indexed(df):
    return df['close'] / df['close'].iloc[0] * 100


def style_axis(ax, ticks, labels, color=None, grid=True):
    ax.set_yticks(ticks)
    ax.set_yticklabels(labels, fontsize=Y_TICK_FS, fontweight='bold',
                       color=color or COLORS['text_secondary'])
    ax.tick_params(axis='y', length=0, labelsize=Y_TICK_FS,
                   pad=AXIS_CONFIG['y_tick']['pad'],
                   colors=color or COLORS['text_secondary'])
    ax.set_xlim(XMIN, XMAX)
    for spine in ax.spines.values():
        spine.set_visible(False)
    if grid:
        ax.grid(True, axis='y', color=GRID_CONFIG['color'],
                alpha=GRID_CONFIG['alpha'], linestyle=GRID_CONFIG['linestyle'],
                linewidth=GRID_CONFIG['linewidth'])
        ax.set_axisbelow(True)


def style_xaxis(ax, visible=True):
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    if not visible:
        ax.tick_params(axis='x', labelbottom=False, length=0)
        return
    ax.tick_params(axis='x', labelsize=X_TICK_FS, colors=COLORS['text_secondary'],
                   length=AXIS_CONFIG['x_tick']['length'],
                   width=AXIS_CONFIG['x_tick']['width'],
                   pad=AXIS_CONFIG['x_tick']['pad'])
    for label in ax.xaxis.get_majorticklabels():
        label.set_fontweight('bold')
        label.set_rotation(AXIS_CONFIG['x_tick']['rotation'])
        label.set_ha(AXIS_CONFIG['x_tick']['ha'])


def plot_funding(ax):
    ax.axhline(0, color=COLORS['grid'], alpha=0.55, linewidth=1.1, zorder=3)
    for df, color in SERIES:
        ax.plot(df['time'], df['fundingRate'] * 100, color=color, linewidth=2.0,
                zorder=4, solid_capstyle='round', solid_joinstyle='round')
    ax.set_ylim(*RATE_LIM)


def render_2panel():
    fig, (ax_px, ax_fr) = plt.subplots(
        2, 1, figsize=(10.67, 6.6), dpi=DPI, sharex=True,
        gridspec_kw={'height_ratios': [1, 1], 'hspace': 0.18})
    fig.patch.set_alpha(0)
    for a in (ax_px, ax_fr):
        a.set_facecolor('none')

    for df, color in SERIES:
        ax_px.plot(df['time'], indexed(df), color=color, linewidth=2.0,
                   solid_capstyle='round', solid_joinstyle='round')
    ax_px.set_ylim(*PX_LIM)
    style_axis(ax_px, PX_TICKS, [str(v) for v in PX_TICKS])
    style_xaxis(ax_px, visible=False)

    plot_funding(ax_fr)
    style_axis(ax_fr, RATE_TICKS, [f'{v:.2f}%' for v in RATE_TICKS])
    style_xaxis(ax_fr)

    fig.tight_layout()
    save_chart(fig, 'hip3_skhx_skhy_funding_2panel', OUT_DIR)
    plt.close()


def _dual_base():
    fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')
    return fig, ax


def _finish_dual(fig, ax, name):
    ax.set_zorder(2)
    ax.patch.set_visible(False)
    plot_funding(ax)
    style_axis(ax, RATE_TICKS, [f'{v:.2f}%' for v in RATE_TICKS])
    style_xaxis(ax)
    fig.tight_layout()
    save_chart(fig, name, OUT_DIR)
    plt.close()


def render_pct():
    """우축 = 7/10 대비 변동률(%). 좌축 0 = 우축 0% 에 그리드가 겹치도록
    틱/한계 비율을 좌축과 동일하게 맞춘다: 0.10/0.13 == 20/26."""
    fig, ax = _dual_base()
    ax_px = ax.twinx()
    for df, color in SERIES:
        ax_px.plot(df['time'], indexed(df) - 100, color=color, **PRICE_STYLE)
    half = 20 * RATE_LIM[1] / RATE_TICKS.max()
    ax_px.set_ylim(-half, half)
    ticks = np.array([-20, -10, 0, 10, 20])
    style_axis(ax_px, ticks, [f'{v:+d}%' if v else '0%' for v in ticks], grid=False)
    ax_px.set_zorder(1)
    _finish_dual(fig, ax, 'hip3_skhx_skhy_funding_pct')


def _band_lim(ticks, lo_frac, hi_frac):
    """ticks 의 최소/최대가 축 높이의 lo_frac..hi_frac 에 놓이도록 ylim 계산."""
    t0, t1 = float(min(ticks)), float(max(ticks))
    height = (t1 - t0) / (hi_frac - lo_frac)
    lo = t0 - lo_frac * height
    return lo, lo + height


def render_split():
    """우축을 위/아래로 쪼개 각 종목의 실달러 밴드를 준다.
    아래 = SKHY(~$169), 위 = SKHX(~$1,249). 종목마다 축이 따로라 두 가격
    라인의 상하 위치는 비교 의미가 없다(각자 밴드 안에서만 읽는다)."""
    fig, ax = _dual_base()

    # 밴드당 틱 2개(하한/상한)만. 밴드 지오메트리는 그대로 두고 라벨만 줄인다.
    for (df, color), ticks, band in (
        ((skhy, SKHY_COLOR), np.array([150, 190]), (0.04, 0.42)),
        ((skhx, SKHX_COLOR), np.array([1200, 1500]), (0.58, 0.96)),
    ):
        ax_b = ax.twinx()
        ax_b.plot(df['time'], df['close'], color=color, **PRICE_STYLE)
        ax_b.set_ylim(*_band_lim(ticks, *band))
        style_axis(ax_b, ticks, [f'${v:,}' for v in ticks], grid=False)
        ax_b.set_zorder(1)

    _finish_dual(fig, ax, 'hip3_skhx_skhy_funding_split')


render_2panel()
render_pct()
render_split()
for n in ('2panel', 'pct', 'split'):
    print(f'Saved: {OUT_DIR}/hip3_skhx_skhy_funding_{n}.png')
