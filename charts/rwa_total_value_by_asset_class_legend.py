"""
Standalone legend strip for total_rwa_value_by_asset_class.
1 column, 11px gap between rows. Emits SVG directly (Figma-style markup).
"""
from pathlib import Path

from PIL import ImageFont

# same colors/order as charts/rwa_total_value_by_asset_class.py
ASSET_COLORS = {
    'US Treasury Debt':       '#14356B',
    'Commodities':            '#C9A13B',
    'Active Strategies':      '#4A7FA8',
    'Stocks':                 '#F4402A',
    'Asset-Backed Credit':    '#5F7F2B',
    'Specialty Finance':      '#C2185B',
    'Corporate Credit':       '#7B3FE4',
    'Private Equity':         '#F5C518',
    'non-US Government Debt': '#A9C2D9',
    'Venture Capital':        '#A8E0A0',
    'Diversified Credit':     '#1A2FF0',
    'Real Estate':            '#B8551E',
    'Public Equity':          '#F4512E',
    'Municipal Credit':       '#14803C',
}

SWATCH = 24
GAP = 11               # 행 간격
PITCH = SWATCH + GAP
TEXT_X = 42            # swatch(24) + 18 여백
FONT_SIZE = 28
BASELINE = 21.7969     # rect 상단 기준 텍스트 baseline
TEXT_FILL = '#D1D5DB'

font = ImageFont.truetype('assets/font/Pretendard/Pretendard-Medium.ttf', FONT_SIZE)
width = TEXT_X + max(font.getlength(name) for name in ASSET_COLORS)
height = (len(ASSET_COLORS) - 1) * PITCH + SWATCH

rows = []
for i, (name, color) in enumerate(ASSET_COLORS.items()):
    y = i * PITCH
    rows.append(
        f'<rect x="0" y="{y}" width="{SWATCH}" height="{SWATCH}" rx="6" fill="{color}"/>\n'
        f'<text x="{TEXT_X}" y="{y + BASELINE}" fill="{TEXT_FILL}" font-family="Pretendard" '
        f'font-size="{FONT_SIZE}" font-weight="500" letter-spacing="0em" '
        f'style="white-space: pre" xml:space="preserve">{name}</text>'
    )

svg = (
    f'<svg width="{width:g}" height="{height:g}" viewBox="0 0 {width:g} {height:g}" '
    f'fill="none" xmlns="http://www.w3.org/2000/svg">\n<g id="legend">\n'
    + '\n'.join(rows)
    + '\n</g>\n</svg>\n'
)

out = Path('outputs/charts/rwa/overview/total_rwa_value_by_asset_class_legend.svg')
out.write_text(svg)
print(f'{out} ({width:g} x {height:g}, {len(ASSET_COLORS)} rows)')
