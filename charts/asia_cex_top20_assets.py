"""Asia CEX — Top 20 traded assets per venue (HashKey excluded).
Ranked leaderboard, symbol colored by tier (BTC / ETH / majors / tail).
Rendered as a styled table in four-pillars dark palette (transparent bg).
Source: asia-cex-analytics.vercel.app (D_TAIL.tail.top_assets + D_API.benchmark_history.top_assets).
"""
import json
import sys
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnnotationBbox, OffsetImage

sys.path.insert(0, ".claude/skills/design/four-pillars")
from config import DPI, COLORS, setup_font, save_chart  # noqa: E402

ICON_DIR = Path("assets/icons")
# OffsetImage applies a dpi correction, so on-screen px = native * zoom * dpi/72.
# Solve for a true ICON_PX icon from the 64px source at DPI.
ICON_PX = 44
ICON_ZOOM = (ICON_PX / 64) * (72 / DPI)

D = json.loads(Path("outputs/data/asia_cex_top20_assets.json").read_text())
TIER = D["tier_colors"]
venues = D["venues"]
assets = D["top_assets"]

setup_font()
fig, ax = plt.subplots(figsize=(17.5, 9.2), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor("none")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")
# fixed axes box so transData is stable for all px<->data measurements
fig.subplots_adjust(left=0.008, right=0.992, top=0.99, bottom=0.01)

RANK_X = 0.012
COL0_X = 0.075         # first symbol column start
SHARE_GAP_PX = 80      # px gap: symbol end -> its %
HEAD_Y = 0.965
ROW0_Y = 0.905
DY = 0.0448
ICON_SLOT_PX = ICON_PX + 10
ICON_GAP_PX = 22

gray = COLORS["text_secondary"]
white = "#e8eaed"

fig.canvas.draw()
renderer = fig.canvas.get_renderer()
td = ax.transData
inv = td.inverted()
to_px = lambda dx: td.transform((dx, 0))[0]
to_dx = lambda px: inv.transform((px, 0))[0]


def text_w(s, fs):
    """Rendered pixel width of a bold string (measured then discarded)."""
    tt = ax.text(0.5, 0.5, s, fontsize=fs, fontweight="bold")
    w = tt.get_window_extent(renderer).width
    tt.remove()
    return w


# measure widest symbol and widest % per venue column
max_sym = [max(text_w(sym, 18) for sym, _, _ in assets[v["key"]]) for v in venues]
max_pct = [max(text_w(f"{sh:.1f}%", 16.5) for _, sh, _ in assets[v["key"]])
           for v in venues]
content_w = [max_sym[i] + SHARE_GAP_PX + max_pct[i] for i in range(len(venues))]

# lay columns out so the gap between one column's %-end and the next column's
# symbol-start (INTER) is identical everywhere, filling to the right edge
col_start0 = to_px(COL0_X)
right_limit = to_px(0.99)
inter = (right_limit - col_start0 - sum(content_w)) / (len(venues) - 1)
col_start_px, share_px = [], []
cur = col_start0
for i in range(len(venues)):
    col_start_px.append(cur)
    share_px.append(cur + max_sym[i] + SHARE_GAP_PX)
    cur += content_w[i] + inter
COL_X = [to_dx(p) for p in col_start_px]
SHARE_X = [to_dx(p) for p in share_px]

ax.text(RANK_X, HEAD_Y, "#", color=gray, fontsize=18.5, fontweight="bold",
        va="center", ha="left")
ax.plot([0, 1], [HEAD_Y - 0.028, HEAD_Y - 0.028], color=gray, alpha=0.35, lw=1.0)

# rows
for r in range(20):
    y = ROW0_Y - r * DY
    ax.text(RANK_X, y, str(r + 1), color=gray, fontsize=17,
            fontweight="bold", va="center", ha="left")
    for i, v in enumerate(venues):
        rows = assets[v["key"]]
        if r >= len(rows):
            ax.text(COL_X[i], y, "—", color=gray, alpha=0.5, fontsize=17.5,
                    fontweight="bold", va="center", ha="left")
            continue
        sym, share, tier = rows[r]
        ax.text(COL_X[i], y, sym, color=TIER[tier], fontsize=18,
                fontweight="bold", va="center", ha="left")
        ax.text(SHARE_X[i], y, f"{share:.1f}%", color=gray, fontsize=16.5,
                fontweight="bold", va="center", ha="left")

# header: center (logo + name) over each column's cell (symbol-left .. %-right)
for i, v in enumerate(venues):
    cell_right_px = share_px[i] + max_pct[i]
    center_px = (col_start_px[i] + cell_right_px) / 2
    name_w = text_w(v["label"], 20.5)
    group_w = ICON_SLOT_PX + ICON_GAP_PX + name_w
    start_px = center_px - group_w / 2
    icon_x = to_dx(start_px + ICON_SLOT_PX / 2)
    t = ax.text(to_dx(start_px + ICON_SLOT_PX + ICON_GAP_PX), HEAD_Y, v["label"],
                color=white, fontsize=20.5, fontweight="bold",
                va="center", ha="left")
    ext = t.get_window_extent(renderer)
    icon_y = inv.transform((0, (ext.y0 + ext.y1) / 2))[1]
    img = mpimg.imread(ICON_DIR / f"venue_{v['key']}.png")
    oi = OffsetImage(img, zoom=ICON_ZOOM, interpolation="antialiased")
    ab = AnnotationBbox(oi, (icon_x, icon_y), frameon=False, zorder=5,
                        box_alignment=(0.5, 0.5))
    ax.add_artist(ab)
png, svg = save_chart(fig, "asia_cex_top20_assets",
                      "outputs/charts/asia-cex/listings")
print(png)
print(svg)

# sanity: Upbit #1 must be BTC 9.7%, Binance #2 USDC 22.0%
assert assets["upbit"][0][0] == "BTC" and abs(assets["binance"][1][1] - 22.02) < 0.01
