import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, apply_style, COLORS, DPI

mpl.rcParams['axes.unicode_minus'] = False
# SVG의 모든 글자를 <text> 요소로 저장 (path 변환 X) -> 편집 가능
mpl.rcParams['svg.fonttype'] = 'none'

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
pm = pd.read_csv('outputs/data/seoul_mayor_polymarket_1min.csv')
vm = pd.read_csv('outputs/data/seoul_mayor_vote_margin.csv')

x_pm = pm['Min from 18:00']
oh = pm['Oh Se-hoon Yes (¢)']
jung = pm['Jung Won-oh Yes (¢)']

vm_valid = vm.dropna(subset=['Margin (Oh − Jung)'])
x_vm = vm_valid['Min from 18:00']
margin = vm_valid['Margin (Oh − Jung)']

# Colors
C_OH = '#ee6666'      # red
C_JUNG = '#5470c6'    # blue
C_MARGIN = '#9a60b4'  # purple
C_FLIP = '#4ade80'    # mint green (lead flip)
C_GRAY = COLORS['text_secondary']

# ---------------------------------------------------------------------------
# Figure: dual y-axis (left = ¢ price, right = vote margin)
# ---------------------------------------------------------------------------
setup_font()
fig, axL = plt.subplots(figsize=(11.5, 5.2), dpi=DPI)
axR = axL.twinx()

XMIN, XMAX = -8, 935

# Left axis = Polymarket Yes price (cents) 0-100
axL.set_xlim(XMIN, XMAX)
axL.set_ylim(0, 100)

# Right axis = vote margin, mapped so 0¢ -> -400K, 100¢ -> +100K (20¢ = 100K)
axR.set_ylim(-400_000, 100_000)
axR.set_xlim(XMIN, XMAX)

# --- Vote margin (right axis): purple dashed line w/ open-circle markers ---
axR.plot(x_vm, margin, color=C_MARGIN, linewidth=2.0, linestyle=(0, (5, 3)),
         zorder=3)
# sparse derived markers (open circles) on the news/derived points
sparse = vm_valid[vm_valid['Type'].str.contains('news|Derived', case=False)]
sparse = sparse.iloc[::4]  # thin out so circles read like the reference
axR.scatter(sparse['Min from 18:00'], sparse['Margin (Oh − Jung)'],
            facecolors='none', edgecolors=C_MARGIN, s=42, linewidths=1.6,
            zorder=4)

# --- Polymarket prices (left axis) ---
axL.plot(x_pm, jung, color=C_JUNG, linewidth=1.7, zorder=5)
axL.plot(x_pm, oh, color=C_OH, linewidth=1.7, zorder=6)

# ---------------------------------------------------------------------------
# Annotations
# ---------------------------------------------------------------------------
# 1) Exit poll vertical marker at 18:00 (x = 0) — 마커만
axL.axvline(0, color=C_GRAY, linewidth=1.3, linestyle=(0, (4, 3)), alpha=0.7,
            zorder=2)

# 2) Lead flip at 07:16 (x = 796), margin crosses 0
#    박스는 녹색선 기준 오른쪽에 배치
FLIP_X = 796
axL.axvline(FLIP_X, color=C_FLIP, linewidth=2.4, alpha=0.85, zorder=3)
axR.scatter([FLIP_X], [0], color=C_FLIP, s=70, zorder=11, edgecolors='none')
axL.annotate('Lead flips 07:16\nmargin crosses 0',
             xy=(FLIP_X, 64), xytext=(806, 64),
             fontsize=11, color=C_FLIP, va='center', ha='left', zorder=10)

# 3) Oh Se-hoon low 0.8¢ at 23:35 (x = 335) — 강조 + 시간대
LOW_X, LOW_Y = 335, 0.8
axL.scatter([LOW_X], [LOW_Y], color='#ffffff', s=110, zorder=9,
            edgecolors=C_OH, linewidths=2.2)
# 박스는 x축 아래에 배치 (라인과 겹치지 않게)
axL.annotate('Low 0.8¢, 23:35', xy=(LOW_X, LOW_Y), xytext=(LOW_X, -17),
             fontsize=11.5, fontweight='bold', color='#ffffff',
             va='top', ha='center', zorder=12, annotation_clip=False,
             arrowprops=dict(arrowstyle='-', color=C_OH, lw=1.2, alpha=0.9))

# ---------------------------------------------------------------------------
# Axis styling
# ---------------------------------------------------------------------------
apply_style(fig, axL, 'line')

# Left ticks: cents
axL.set_yticks([0, 20, 40, 60, 80, 100])
axL.set_yticklabels([f'{v}¢' for v in [0, 20, 40, 60, 80, 100]])

# Right ticks: vote margin (K), aligned 1:1 with left gridlines
rticks = [-400_000, -300_000, -200_000, -100_000, 0, 100_000]
axR.set_yticks(rticks)
axR.set_yticklabels(['-400K', '-300K', '-200K', '-100K', '0K', '+100K'])
for spine in axR.spines.values():
    spine.set_visible(False)
axR.tick_params(axis='y', labelsize=15, length=0, colors=COLORS['text_secondary'],
                pad=10)

# Bottom x ticks: time (KST)
xt = [0, 120, 240, 360, 480, 600, 720, 840]
xlabels = ['18:00', '20:00', '22:00', '00:00', '02:00', '04:00', '06:00', '08:00']
axL.set_xticks(xt)
axL.set_xticklabels(xlabels, rotation=0, ha='center')
axL.tick_params(axis='x', labelsize=14, colors=COLORS['text_secondary'],
                length=0, pad=8)

# Top x axis: share of votes counted
axT = axL.twiny()
axT.set_xlim(XMIN, XMAX)
top_pos = [250, 320, 510, 658, 796, 930]
top_lab = ['7%', '20%', '50%', '80%', '94%', '97.7%']
axT.set_xticks(top_pos)
axT.set_xticklabels(top_lab, fontsize=12.5)
axT.tick_params(axis='x', colors=COLORS['text_secondary'], length=0, pad=6)
for spine in axT.spines.values():
    spine.set_visible(False)

# Left tick label color/size to match style
axL.tick_params(axis='y', labelsize=15, colors=COLORS['text_secondary'])

# Legend (상단 배치)
legend_handles = [
    Line2D([0], [0], color=C_OH, lw=2.4, label='Oh Se-hoon (Yes price)'),
    Line2D([0], [0], color=C_JUNG, lw=2.4, label='Jung Won-oh (Yes price)'),
    Line2D([0], [0], color=C_MARGIN, lw=2.4, linestyle=(0, (5, 3)),
           marker='o', markerfacecolor='none', markersize=7,
           label='Vote margin (Oh − Jung)'),
]
leg = axL.legend(handles=legend_handles, loc='lower center',
                 bbox_to_anchor=(0.5, 1.16), ncol=3, frameon=False,
                 handlelength=2.2, columnspacing=1.8, handletextpad=0.6,
                 fontsize=11.5)
for txt in leg.get_texts():
    txt.set_color(COLORS['text'])

fig.tight_layout()

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
out_dir = Path('outputs/charts/macro/election')
out_dir.mkdir(parents=True, exist_ok=True)
stem = 'seoul_mayor_polymarket_vs_margin'
fig.savefig(out_dir / f'{stem}.png', dpi=DPI, facecolor='none',
            bbox_inches='tight', transparent=True)
svg_path = out_dir / f'{stem}.svg'
fig.savefig(svg_path, facecolor='none', bbox_inches='tight', transparent=True)


def embed_font(svg_file, ttf_path='assets/font/Pretendard/Pretendard-Bold.ttf',
               family='Pretendard'):
    """SVG에 Pretendard 폰트를 @font-face(base64)로 내장.
    디자인 툴/브라우저에 폰트가 설치돼 있지 않아도 Pretendard로 렌더된다."""
    import base64
    ttf = Path(ttf_path)
    if not ttf.exists():
        return
    b64 = base64.b64encode(ttf.read_bytes()).decode('ascii')
    style = (
        '<style type="text/css"><![CDATA[\n'
        '@font-face {{ font-family: "{fam}"; font-weight: 400 900; '
        'src: url(data:font/ttf;base64,{b64}) format("truetype"); }}\n'
        ']]></style>'
    ).format(fam=family, b64=b64)
    svg = Path(svg_file).read_text()
    # 첫 <defs> 직후(없으면 <svg ...> 직후)에 삽입
    if '<defs>' in svg:
        svg = svg.replace('<defs>', '<defs>\n' + style, 1)
    else:
        idx = svg.find('>', svg.find('<svg')) + 1
        svg = svg[:idx] + '\n' + style + svg[idx:]
    Path(svg_file).write_text(svg)


def merge_multiline(svg_file, first_line, second_line):
    """연속된 두 <text> 줄을 하나의 <text>(+<tspan>)로 합쳐
    디자인 툴에서 한 개의 텍스트 레이어로 함께 이동되게 한다."""
    import re
    svg = Path(svg_file).read_text()
    pat = re.compile(
        r'(<text style="(fill: #4ade80;[^"]*)" '
        r'transform="translate\(([\d.]+) ([\d.]+)\)">' + re.escape(first_line) +
        r'</text>)\s*'
        r'<text style="[^"]*" transform="translate\([\d.]+ ([\d.]+)\)">' +
        re.escape(second_line) + r'</text>'
    )

    def repl(m):
        style = m.group(2)
        x, y1, y2 = m.group(3), float(m.group(4)), float(m.group(5))
        dy = y2 - y1
        return ('<text style="{s}" transform="translate({x} {y1})">{l1}'
                '<tspan x="0" dy="{dy:.6f}">{l2}</tspan></text>').format(
            s=style, x=x, y1=y1, l1=first_line, dy=dy, l2=second_line)

    Path(svg_file).write_text(pat.sub(repl, svg))


merge_multiline(svg_path, 'Lead flips 07:16', 'margin crosses 0')
embed_font(svg_path)
print('saved', out_dir / f'{stem}.png')
