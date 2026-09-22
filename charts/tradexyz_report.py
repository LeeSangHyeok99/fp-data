"""Shared setup for the Trade[XYZ] report charts.

Every chart in this set uses the HRC dark spec: four text roles plus one point
colour, and Trade[XYZ] always takes the point colour. Two or three series get
the point colour against the grey ladder; only go looking for more hues when
the series count makes grey unreadable.

Outputs all land in outputs/charts/tradexyz/oi/.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

sys.path.append('charts')
from tradexyz_ch4_palette import TITLE, BODY, NOTE, POINT  # noqa: F401,E402
from tradexyz_ch4_palette import VENUE_INK  # noqa: E402
from tradexyz_ch7_palette import DIM, setup_font, base_axes  # noqa: F401,E402

DPI = 150
OUT_DIR = Path('outputs/charts/tradexyz/oi')
PREVIEW_BG = '#1a1a1a'   # the report ground; files themselves save transparent

INK = VENUE_INK['trade.xyz']  # readable label ink on top of the point colour

# Second series colour, for charts whose two lines are peers rather than a
# hero and its backdrop (7D against 14D of the same thing). Grey reads as
# "supporting cast" next to the point colour, which is wrong when neither
# series is the point. Bone carries the same visual weight as the gold and
# keeps the set inside the four-colour spec instead of adding a fifth hue.
PEER = '#D9D9D9'

# every chart in the set is drawn on the same canvas
FIGSIZE = (13.0, 6.0)
Y_TICK_SIZE = 18
X_TICK_SIZE = 17


def axes(ax):
    """base_axes plus the report's tick sizing."""
    base_axes(ax)
    ax.tick_params(axis='y', labelsize=Y_TICK_SIZE, pad=8)
    ax.tick_params(axis='x', labelsize=X_TICK_SIZE, length=5, width=1.1,
                   color=NOTE, pad=5)


def save(fig, name):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ('png', 'svg'):
        fig.savefig(OUT_DIR / f'{name}.{ext}', dpi=DPI, facecolor='none',
                    edgecolor='none', transparent=True, bbox_inches='tight')
    fig.patch.set_alpha(1)
    fig.patch.set_facecolor(PREVIEW_BG)
    fig.savefig(OUT_DIR / f'_preview_{name}.png', dpi=DPI,
                facecolor=PREVIEW_BG, bbox_inches='tight')
    plt.close(fig)
    print('saved', OUT_DIR / f'{name}.png')
