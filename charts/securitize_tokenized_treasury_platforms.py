"""
Tokenized Treasury Assets by Platform (four-pillars theme) — split into two charts.
  bar  : Treasury assets by platform, Securitize highlighted
  line : Securitize share of tokenized treasuries

Charts are separate files but sit side-by-side in one infographic;
combined width must stay within 550 pt (wide slot).
Same figure height so they align.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append(".claude/skills/design/four-pillars")
from config import setup_font, COLORS, DPI  # noqa: E402

# ---- reference colors (내재화: 레퍼런스 그대로) ----
LAVENDER = "#b0a5f5"   # non-highlighted bars
MINT = "#7fe3bd"       # Securitize highlight bar
LINE = "#57d6b5"       # share line + markers

GRID = dict(color=COLORS["grid"], alpha=0.5, linestyle=(0, (3.7, 1.6)), linewidth=1.0)
TXT = COLORS["text"]
TXT2 = COLORS["text_secondary"]
# uniform scale so bar+line render (in the design tool, at 96dpi ×1.333)
# fit the 550 px wide slot together: bar_pt + line_pt ~= 390pt -> ~520px + gap
S = 0.645
H = 4.046 * S          # shared height, tied to S so shrinking width keeps the
                       # original chart aspect (3.5in @ S=0.865)
FS_VAL = 11 * S        # value/point labels
FS_TICK = 10 * S       # tick labels
FS_XBAR = 9 * S        # bar x-labels (two lines)

bars = pd.read_csv("outputs/data/securitize_treasury_platforms.csv")
bars["label"] = bars["label"].str.replace("\\n", "\n", regex=False)
share = pd.read_csv("outputs/data/securitize_treasury_share.csv", parse_dates=["date"])

setup_font()
out = Path("outputs/charts/securitize/treasury")
out.mkdir(parents=True, exist_ok=True)


def save(fig, name):
    for ext in ("png", "svg"):
        fig.savefig(out / f"{name}.{ext}", facecolor="none", edgecolor="none",
                    bbox_inches="tight", transparent=True, dpi=DPI)


def strip(ax):
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", length=3.5 * S, width=1.0, color=TXT2)  # x ticks only
    ax.tick_params(axis="y", length=0)
    for s in ax.spines.values():
        s.set_visible(False)


def _lighten(c, amt):
    r, g, b = mcolors.to_rgb(c)
    return (r + (1 - r) * amt, g + (1 - g) * amt, b + (1 - b) * amt)


def grad_bar(ax, xi, v, w, base, zorder=3):
    """Vertical gradient bar: base color at bottom -> lighter at top."""
    cmap = LinearSegmentedColormap.from_list("", [base, _lighten(base, 0.34)])
    g = np.linspace(0, 1, 256).reshape(-1, 1)
    ax.imshow(g, extent=[xi - w / 2, xi + w / 2, 0, v], origin="lower",
              aspect="auto", cmap=cmap, zorder=zorder)


# ======================= chart 1: bar =======================
fig, ax = plt.subplots(figsize=(4.62 * S, H), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor("none")
x = np.arange(len(bars))
W = 0.62
for xi, v, hl in zip(x, bars["assets_b"], bars["highlight"]):
    grad_bar(ax, xi, v, W, MINT if hl else LAVENDER)
    ax.text(xi, v + 0.08, f"${v:.1f}B", ha="center", va="bottom",
            fontsize=FS_VAL, fontweight="bold", color=TXT, zorder=4)
ax.set_xlim(-0.5, len(bars) - 0.5)
ax.set_ylim(0, 3.5)
ax.set_yticks([0, 1, 2, 3])
ax.set_yticklabels(["$0B", "$1B", "$2B", "$3B"], fontsize=FS_TICK, color=TXT2)
ax.set_xticks(x)
ax.set_xticklabels(bars["label"], fontsize=FS_XBAR, color=TXT2, linespacing=1.4)
ax.grid(True, axis="y", **GRID)
strip(ax)
fig.tight_layout()
save(fig, "securitize_treasury_platforms_bar")
plt.close(fig)

# ======================= chart 2: line =======================
fig, ax = plt.subplots(figsize=(4.02 * S, H), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor("none")
xd = mdates.date2num(share["date"])
ax.plot(xd, share["share_pct"], color=LINE, linewidth=2.4, zorder=3)
ax.scatter(xd, share["share_pct"], s=60, color=LINE, zorder=4,
           edgecolors=COLORS["background"], linewidths=1.5)
for xi, yi, lbl in zip(xd, share["share_pct"], share["label"]):
    off = 2.2 if lbl != "Jul 2026" else -3.6
    va = "bottom" if lbl != "Jul 2026" else "top"
    ax.text(xi, yi + off, f"{yi:g}%", ha="center", va=va,
            fontsize=FS_VAL, fontweight="bold", color=LINE, zorder=5)
ax.set_ylim(0, 52)
ax.set_yticks([0, 20, 40])
ax.set_yticklabels(["0%", "20%", "40%"], fontsize=FS_TICK, color=TXT2)
pad = (xd.max() - xd.min()) * 0.08
ax.set_xlim(xd.min() - pad, xd.max() + pad)
ax.set_xticks(xd)
ax.set_xticklabels(share["label"], fontsize=FS_TICK, color=TXT2, rotation=45, ha="right")
ax.grid(True, axis="y", **GRID)
strip(ax)
fig.tight_layout()
save(fig, "securitize_treasury_share_line")
plt.close(fig)
print("done")
