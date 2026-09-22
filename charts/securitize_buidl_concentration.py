"""
Securitize Platform Value and BUIDL Concentration - Stacked Area Chart (Gradient)
Data source: RWA.xyz token timeseries export (Securitize platform tokens)
"""

import colorsys
import re
import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import numpy as np
import pandas as pd
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
from matplotlib.patches import Polygon
from pathlib import Path
from PIL import Image
from config import create_figure, apply_style, COLORS, DPI

# Font
pretendard_path = Path('assets/font/Pretendard/Pretendard-Bold.ttf')
if pretendard_path.exists():
    fm.fontManager.addfont(str(pretendard_path))
    pretendard_font = fm.FontProperties(fname=str(pretendard_path))
else:
    pretendard_font = None


# ─── Gradient stacked area helper ──────────────────────────────────────
def gradient_band(ax, x, y_bottom, y_top, color, l_floor=0.58, s_floor=0.65,
                  nx=2000, ny=600):
    """Fill a band with a gradient from a dark shade of the colour up to the
    colour itself.

    Ramps HLS lightness, holding hue so the dark end stays in the same colour
    family. Scaling RGB (equivalently, HSV value) instead fades toward black and
    drains the hue out of the bottom of the band. Saturation eases off slightly
    into the shadow too: holding it flat while dropping lightness pushes a
    saturated colour toward a harsh, electric version of itself.

    At each x the ramp is normalised between that column's own bottom and top
    edge, so a thin ribbon shows the full dark-to-bright range just like a thick
    band does. A single image ramped along the axes instead leaves any thin band
    sampling one narrow slice of the ramp, which reads as flat colour.

    Drawn as one image clipped to the band polygon: stacking fill_between layers
    instead leaves antialiased seams that read as stripes wherever the daily data
    is jagged.
    """
    h, l, s = colorsys.rgb_to_hls(*mcolors.to_rgb(color))
    ramp = np.array([colorsys.hls_to_rgb(h, l_floor + (l - l_floor) * f,
                                         s * (s_floor + (1 - s_floor) * f))
                     for f in np.linspace(0, 1, 256)])

    xn = mdates.date2num(x)
    y_bottom = np.broadcast_to(np.asarray(y_bottom, float), xn.shape)

    xs = np.linspace(xn.min(), xn.max(), nx)
    lo = np.interp(xs, xn, y_bottom)
    hi = np.interp(xs, xn, y_top)
    ys = np.linspace(lo.min(), hi.max(), ny)
    frac = (ys[:, None] - lo[None, :]) / np.maximum(hi - lo, 1e-9)[None, :]
    img = ramp[(np.clip(frac, 0, 1) * 255).astype(int)]

    im = ax.imshow(img, aspect='auto', origin='lower', zorder=2,
                   extent=[xn.min(), xn.max(), ys.min(), ys.max()],
                   interpolation='bilinear')
    verts = np.concatenate([np.column_stack([xn, y_top]),
                            np.column_stack([xn[::-1], y_bottom[::-1]])])
    im.set_clip_path(Polygon(verts, closed=True, transform=ax.transData))


# ─── Data ───────────────────────────────────────────────────────────────
BUIDL_COL = 'BlackRock USD Institutional Digital Liquidity Fund'

df = pd.read_csv('sources/rwa-token-timeseries-export-1783317290925.csv')
df['Date'] = pd.to_datetime(df['Date'])
token_cols = [c for c in df.columns if c not in ('Timestamp', 'Date', 'Measure')]
df[token_cols] = df[token_cols].fillna(0)

df['BUIDL'] = df[BUIDL_COL]
df['Non-BUIDL'] = df[[c for c in token_cols if c != BUIDL_COL]].sum(axis=1)
df = df[df['Date'] >= '2024-01-01'].set_index('Date')

out = df[['BUIDL', 'Non-BUIDL']] / 1e9
out.to_csv('outputs/data/securitize_buidl_concentration.csv')

x = out.index
buidl = out['BUIDL'].values
total = (out['BUIDL'] + out['Non-BUIDL']).values

# Sampled from the reference exhibit rather than eyeballed
BUIDL_COLOR = '#615be3'
NON_BUIDL_COLOR = '#8dd3b8'

# Export target: 550px wide once placed, keeping the stacked-chart aspect ratio.
# Matplotlib writes the SVG canvas in pt, and Figma reads pt as CSS px (96/72),
# so the pt target is 3/4 of the px we want to see in the layout.
TARGET_WIDTH_PX = 550
TARGET_WIDTH_PT = TARGET_WIDTH_PX * 0.75
TICK_FONTSIZE = 7
LABEL_FONTSIZE = 7

# ─── Chart ──────────────────────────────────────────────────────────────
fig, ax = create_figure('stacked')

Y_MAX = 5
gradient_band(ax, x, 0, buidl, BUIDL_COLOR)
gradient_band(ax, x, buidl, total, NON_BUIDL_COLOR)

apply_style(fig, ax, 'stacked')

# Tick fonts: one size per axis, scaled down for the 550px-wide export
ax.tick_params(axis='y', labelsize=TICK_FONTSIZE)
ax.tick_params(axis='x', labelsize=TICK_FONTSIZE)

ax.set_xlim(x.min(), x.max())
ax.set_ylim(0, Y_MAX)
ax.set_yticks([0, 1, 2, 3, 4, 5])
ax.set_yticklabels([f'${v}B' for v in [0, 1, 2, 3, 4, 5]])

ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

# In-plot series labels
ax.text(pd.Timestamp('2025-08-15'), 1.15, 'BUIDL', color='#ffffff',
        fontsize=LABEL_FONTSIZE, fontweight='bold', ha='center', va='center',
        fontproperties=pretendard_font, zorder=5)
ax.text(pd.Timestamp('2026-02-20'), 4.6, 'Non-BUIDL', color=NON_BUIDL_COLOR,
        fontsize=LABEL_FONTSIZE, fontweight='bold', ha='center', va='center',
        fontproperties=pretendard_font, zorder=5)

out_dir = Path('outputs/charts/rwa/securitize')
out_dir.mkdir(parents=True, exist_ok=True)
name = 'securitize_buidl_concentration'
svg, png = out_dir / f'{name}.svg', out_dir / f'{name}.png'


def export_svg():
    fig.savefig(svg, format='svg', bbox_inches='tight',
                facecolor='none', edgecolor='none', transparent=True)
    return float(re.search(r'width="([\d.]+)pt"', svg.read_text()).group(1))


# bbox_inches='tight' trims the canvas, so shrink the figure until the
# trimmed SVG lands on the target width
for _ in range(6):
    width_pt = export_svg()
    if abs(width_pt - TARGET_WIDTH_PT) < 0.02:
        break
    w_in, h_in = fig.get_size_inches()
    scale = TARGET_WIDTH_PT / width_pt
    fig.set_size_inches(w_in * scale, h_in * scale)

fig.savefig(png, dpi=DPI, bbox_inches='tight',
            facecolor='none', edgecolor='none', transparent=True)
print(svg, f'{width_pt:.1f}pt wide -> {width_pt / 0.75:.1f}px placed')
print(png, Image.open(png).size)
print(f"latest: BUIDL ${buidl[-1]:.2f}B / total ${total[-1]:.2f}B "
      f"({100 * buidl[-1] / total[-1]:.1f}%)")
