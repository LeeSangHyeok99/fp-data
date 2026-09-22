"""
Non-Dollar Sovereign Debt Exists in the Real World, but Not Onchain
Dollar vs. Non-Dollar Sovereign Debt Markets, Real-World and Onchain Market Size
Four Pillars design theme

실물 시장은 $T, 온체인은 $B로 1000배 차이나므로 좌우 패널을 분리하고
각 패널이 자기 축을 쓴다. 눈금 비율(45:48 == 15:16)을 맞춰 그리드는 정렬된다.

Data: 사용자 제공 (SIFMA, OECD, rwa.xyz)
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from config import COLORS, apply_style, setup_font, save_chart, gradient_rounded_bar

OUTPUT_DIR = 'outputs/charts/rwa/market'

C_USD = '#85bb65'      # 그린백 그린 (달러 지폐 색)
C_NONUSD = '#5470c6'   # 블루
TICK_FONTSIZE = 16
LABEL_FONTSIZE = 18
VALUE_FONTSIZE = 16
BAR_WIDTH = 0.5
GRAD_FLOOR = 0.5  # 바닥 밝기. 기본 0.15는 검정에 가까워 색상 계열이 사라진다

# (패널 라벨, [(카테고리, 값, 색)], y틱, ylim, 값 표기 포맷)
PANELS = [
    ('Real-World', [('USD', 30.3, C_USD), ('Non-USD', 42.8, C_NONUSD)],
     [0, 15, 30, 45], 48, '$%.1fT'),
    ('Onchain', [('USD', 15.9, C_USD), ('Non-USD', 1.4, C_NONUSD)],
     [0, 5, 10, 15], 16, '$%.1fB'),
]

# 눈금 최대값 대비 축 상단 비율이 양쪽 동일해야 그리드가 맞는다
assert PANELS[0][2][-1] / PANELS[0][3] == PANELS[1][2][-1] / PANELS[1][3]
for _, bars, ticks, ylim, _ in PANELS:
    assert max(v for _, v, _ in bars) < ylim, 'bar overflows axis'


def draw(panel, figsize=(5.5, 5.5)):
    """패널 하나를 1:1 비율 차트로. 두 장을 나란히 놓으면 그리드가 맞는다."""
    group, bars, ticks, ylim, fmt = panel
    setup_font()
    fig, ax = plt.subplots(figsize=figsize, dpi=150)

    ax.set_xlim(-0.7, len(bars) - 0.3)
    ax.set_ylim(0, ylim)
    ax.yaxis.set_major_locator(mticker.FixedLocator(ticks))
    ax.yaxis.set_major_formatter(
        mticker.FormatStrFormatter(fmt.replace('%.1f', '%g')))
    ax.set_xticks(range(len(bars)))
    ax.set_xticklabels([name for name, _, _ in bars])
    apply_style(fig, ax, 'bar')

    # 라운드 코너 계산이 축 좌표에 의존하므로 xlim/ylim 확정 후에 그린다
    for i, (_, value, color) in enumerate(bars):
        gradient_rounded_bar(ax, i, BAR_WIDTH, value, color, floor=GRAD_FLOOR)
        ax.text(i, value + ylim * 0.03, fmt % value, ha='center', va='bottom',
                fontsize=VALUE_FONTSIZE, fontweight='bold',
                color='white', zorder=5)

    ax.set_xlabel(group, fontsize=LABEL_FONTSIZE, fontweight='bold',
                  color=COLORS['text_secondary'], labelpad=14)
    ax.tick_params(axis='y', labelsize=TICK_FONTSIZE)
    ax.tick_params(axis='x', labelsize=TICK_FONTSIZE, rotation=0, length=0)
    plt.setp(ax.xaxis.get_majorticklabels(), ha='center')

    fig.tight_layout()
    return fig


def draw_combined(figsize=(10.67, 4.67)):
    """y축 없이 4개 바를 한 차트에. 그룹별로 자기 최대값에 맞춰 정규화하므로
    그룹 내 비율은 정확하고, 그룹 간 높이 비교는 의미가 없다 (단위가 $T와 $B)."""
    setup_font()
    fig, ax = plt.subplots(figsize=figsize, dpi=150)

    gap = 1.5  # 그룹 사이 간격
    positions, heights, colors, texts, ticks, tick_labels = [], [], [], [], [], []
    group_centers = []
    for g, (group, bars, _, _, fmt) in enumerate(PANELS):
        top = max(v for _, v, _ in bars)
        base = g * (len(bars) - 1 + gap)
        for i, (name, value, color) in enumerate(bars):
            positions.append(base + i)
            heights.append(value / top)
            colors.append(color)
            texts.append(fmt % value)
            ticks.append(base + i)
            tick_labels.append(name)
        group_centers.append((group, base + (len(bars) - 1) / 2))

    ax.set_xlim(positions[0] - 0.7, positions[-1] + 0.7)
    ax.set_ylim(0, 1.18)
    ax.set_xticks(ticks)
    ax.set_xticklabels(tick_labels)
    apply_style(fig, ax, 'bar')

    # y축과 그리드를 전부 제거
    ax.grid(False)
    ax.yaxis.set_visible(False)

    for x, h, color, text in zip(positions, heights, colors, texts):
        gradient_rounded_bar(ax, x, BAR_WIDTH, h, color, floor=GRAD_FLOOR)
        ax.text(x, h + 0.03, text, ha='center', va='bottom',
                fontsize=LABEL_FONTSIZE, fontweight='bold',
                color=COLORS['text_secondary'], zorder=5)

    # 그룹 사이 구분선. 좌우 스케일이 다르다는 신호
    ax.axvline((group_centers[0][1] + group_centers[1][1]) / 2, ymin=0.02, ymax=0.92,
               color=COLORS['grid'], alpha=0.4, linestyle=(0, (3.7, 1.6)), linewidth=1.0)

    for group, x in group_centers:
        ax.text(x, -0.19, group, ha='center', va='top', transform=ax.get_xaxis_transform(),
                fontsize=LABEL_FONTSIZE, fontweight='bold', color=COLORS['text_secondary'])

    ax.tick_params(axis='x', labelsize=TICK_FONTSIZE, rotation=0, length=0)
    plt.setp(ax.xaxis.get_majorticklabels(), ha='center')
    fig.tight_layout()
    return fig


if __name__ == '__main__':
    for panel in PANELS:
        group, bars, _, _, fmt = panel
        total = sum(v for _, v, _ in bars)
        for name, value, _ in bars:
            print(f'{group:11s} {name:8s} {fmt % value:>8s}  ({value / total:.1%})')

        name = 'sovereign_debt_' + group.lower().replace('-', '_')
        fig = draw(panel)
        png, svg = save_chart(fig, name, output_dir=OUTPUT_DIR)
        print(f'  -> {png}')
        plt.close(fig)

    fig = draw_combined()
    png, svg = save_chart(fig, 'sovereign_debt_combined', output_dir=OUTPUT_DIR)
    print(f'  -> {png}')
    plt.close(fig)
