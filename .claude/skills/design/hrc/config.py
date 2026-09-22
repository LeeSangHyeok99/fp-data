"""
HRC (Hashed Research Center) Design Configuration
matplotlib 차트 스타일 설정
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path

# =============================================================================
# 색상 정의
# =============================================================================
COLORS = {
    'background': '#0a3a34',
    'text': '#ffffff',
    'text_secondary': '#747474',
    'grid': '#1a5c52',
}

# 차트 시리즈 색상
SERIES_COLORS = [
    '#00d4ff',  # 네온 시안
    '#7c3aed',  # 일렉트릭 퍼플
    '#10b981',  # 네온 그린
    '#f59e0b',  # 앰버
    '#ec4899',  # 핑크
    '#06b6d4',  # 틸
]

# 증감 표시용
POSITIVE_COLOR = '#10b981'
NEGATIVE_COLOR = '#ef4444'

# =============================================================================
# 폰트 설정
# =============================================================================
def setup_font():
    """SUIT Bold 폰트 설정 (로컬 assets), 없으면 Arial Bold 폴백"""
    font_path = Path('assets/font/SUIT/SUIT-ttf/SUIT-Bold.ttf')
    if font_path.exists():
        fm.fontManager.addfont(str(font_path))
        plt.rcParams['font.family'] = 'SUIT'
    else:
        plt.rcParams['font.family'] = 'Arial'

    plt.rcParams['font.weight'] = 'bold'

# =============================================================================
# 차트 크기
# =============================================================================
# Default: 1600 x 700 px @ 150 DPI = 10.67 x 4.67 inch
DEFAULT_FIGSIZE = (10.67, 4.67)

FIGURE_SIZES = {
    'line': DEFAULT_FIGSIZE,
    'area': DEFAULT_FIGSIZE,
    'stacked': DEFAULT_FIGSIZE,
    'stacked_bar': DEFAULT_FIGSIZE,
    'bar': DEFAULT_FIGSIZE,
    'horizontal_bar': DEFAULT_FIGSIZE,
    'pie': DEFAULT_FIGSIZE,
    'donut': DEFAULT_FIGSIZE,
}

DPI = 150

# =============================================================================
# 축 설정
# =============================================================================
AXIS_CONFIG = {
    'y_label': {
        'fontsize': 20,
        'fontweight': 'bold',
        'labelpad': 20,
        'color': COLORS['text_secondary'],
    },
    'y_tick': {
        'fontsize': 18,
        'fontweight': 'bold',
        'pad': 15,
        'length': 0,
        'color': COLORS['text_secondary'],
        'max_ticks': 6,  # Y축 틱 5~6개
    },
    'x_tick': {
        'fontsize': 16,
        'fontweight': 'bold',
        'pad': 10,
        'rotation': 45,
        'ha': 'right',
        'length': 6,
        'width': 1,
        'color': COLORS['text_secondary'],
    },
}

# =============================================================================
# 그리드 설정
# =============================================================================
GRID_CONFIG = {
    'color': '#787b86',
    'alpha': 0.5,
    'linestyle': (0, (3.7, 1.6)),  # 점선 (Four Pillars 동일)
    'linewidth': 1.0,
}

# =============================================================================
# 스타일 적용 함수
# =============================================================================
def apply_style(fig, ax, chart_type='line'):
    """HRC 스타일을 차트에 적용"""

    # 배경 투명
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    # 그리드
    ax.grid(
        True,
        axis='y',
        color=GRID_CONFIG['color'],
        alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'],
        linewidth=GRID_CONFIG['linewidth'],
    )
    ax.set_axisbelow(True)

    # 축 spine 숨김
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Y축 설정
    ax.yaxis.label.set_fontsize(AXIS_CONFIG['y_label']['fontsize'])
    ax.yaxis.label.set_fontweight(AXIS_CONFIG['y_label']['fontweight'])
    ax.yaxis.labelpad = AXIS_CONFIG['y_label']['labelpad']
    ax.yaxis.label.set_color(AXIS_CONFIG['y_label']['color'])

    ax.tick_params(
        axis='y',
        labelsize=AXIS_CONFIG['y_tick']['fontsize'],
        pad=AXIS_CONFIG['y_tick']['pad'],
        length=AXIS_CONFIG['y_tick']['length'],
        colors=AXIS_CONFIG['y_tick']['color'],
    )

    # X축 설정
    ax.tick_params(
        axis='x',
        labelsize=AXIS_CONFIG['x_tick']['fontsize'],
        pad=AXIS_CONFIG['x_tick']['pad'],
        rotation=AXIS_CONFIG['x_tick']['rotation'],
        colors=AXIS_CONFIG['x_tick']['color'],
        length=AXIS_CONFIG['x_tick']['length'],
        width=AXIS_CONFIG['x_tick']['width'],
    )
    plt.setp(ax.xaxis.get_majorticklabels(), ha=AXIS_CONFIG['x_tick']['ha'])

    # 레이아웃
    fig.tight_layout()

def create_figure(chart_type='line'):
    """차트 타입에 맞는 Figure 생성"""
    setup_font()
    figsize = FIGURE_SIZES.get(chart_type, (18, 10))
    fig, ax = plt.subplots(figsize=figsize, dpi=DPI)
    return fig, ax

def save_chart(fig, filename, output_dir='outputs/charts'):
    """PNG와 SVG로 저장"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # PNG 저장 (투명 배경)
    png_path = output_path / f"{filename}.png"
    fig.savefig(
        png_path,
        dpi=DPI,
        facecolor='none',
        edgecolor='none',
        bbox_inches='tight',
        transparent=True,
    )

    # SVG 저장 (투명 배경)
    svg_path = output_path / f"{filename}.svg"
    fig.savefig(
        svg_path,
        format='svg',
        facecolor='none',
        edgecolor='none',
        bbox_inches='tight',
        transparent=True,
    )

    return str(png_path), str(svg_path)


# =============================================================================
# 사용 예시
# =============================================================================
"""
from config import create_figure, apply_style, save_chart, SERIES_COLORS

# 차트 생성
fig, ax = create_figure('line')

# 데이터 플롯
ax.plot(x_data, y_data, color=SERIES_COLORS[0], linewidth=2.5)

# 스타일 적용
apply_style(fig, ax, 'line')

# 저장
save_chart(fig, 'my_chart')
"""
