import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path as mPath
import numpy as np
from collections import defaultdict
from pathlib import Path

import sys
sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, save_chart, COLORS

# ══════════════════════════════════════════════════
# Data
# ══════════════════════════════════════════════════
_df = pd.read_csv('outputs/data/eip_status_sankey.csv')
flows = [(r.source, r.target, int(r.value)) for r in _df.itertuples(index=False)]

source_totals = defaultdict(int)
target_totals = defaultdict(int)
for s, t, v in flows:
    source_totals[s] += v
    target_totals[t] += v

node_order = ['Draft', 'New', 'Stagnant', 'Review', 'Last Call', 'Final', 'Withdrawn', 'Living']

# Colors (four-pillars palette)
node_colors = {
    'Draft':     '#9a60b4',
    'New':       '#ea7ccc',
    'Stagnant':  '#5470c6',
    'Review':    '#73c0de',
    'Last Call': '#3ba272',
    'Final':     '#91cc75',
    'Withdrawn': '#fc8452',
    'Living':    '#ee6666',
}

# ══════════════════════════════════════════════════
# Figure
# ══════════════════════════════════════════════════
setup_font()
fig, ax = plt.subplots(figsize=(14, 7), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')
ax.axis('off')

# ══════════════════════════════════════════════════
# Layout
# ══════════════════════════════════════════════════
L_X = 0.14
R_X = 0.86
BAR_W = 0.012
GAP = 0.012


def compute_positions(totals, order, gap):
    active = [(n, totals.get(n, 0)) for n in order if totals.get(n, 0) > 0]
    total_val = sum(v for _, v in active)
    n_gaps = len(active) - 1
    avail = 1.0 - n_gaps * gap
    scale = avail / total_val

    pos = {}
    y = 1.0
    for name, val in active:
        h = val * scale
        pos[name] = {'top': y, 'bottom': y - h, 'val': val}
        y = pos[name]['bottom'] - gap
    return pos, scale


left_pos, l_scale = compute_positions(source_totals, node_order, GAP)
right_pos, r_scale = compute_positions(target_totals, node_order, GAP)

# ══════════════════════════════════════════════════
# Draw node bars + labels
# ══════════════════════════════════════════════════
for node in node_order:
    c = node_colors[node]

    if node in left_pos:
        p = left_pos[node]
        h = p['top'] - p['bottom']
        ax.add_patch(mpatches.FancyBboxPatch(
            (L_X, p['bottom']), BAR_W, h,
            boxstyle="round,pad=0.002",
            facecolor=c, edgecolor='none', zorder=5))
        ax.text(L_X - 0.015, (p['top'] + p['bottom']) / 2,
                f"{node} ({source_totals[node]})",
                ha='right', va='center',
                color=COLORS['text'], fontsize=18, fontweight='bold')

    if node in right_pos:
        p = right_pos[node]
        h = p['top'] - p['bottom']
        ax.add_patch(mpatches.FancyBboxPatch(
            (R_X, p['bottom']), BAR_W, h,
            boxstyle="round,pad=0.002",
            facecolor=c, edgecolor='none', zorder=5))
        ax.text(R_X + BAR_W + 0.015, (p['top'] + p['bottom']) / 2,
                f"{node} ({target_totals[node]})",
                ha='left', va='center',
                color=COLORS['text'], fontsize=18, fontweight='bold')

# ══════════════════════════════════════════════════
# Allocate flow positions
# ══════════════════════════════════════════════════
src_groups = defaultdict(list)
for s, t, v in flows:
    src_groups[s].append((t, v))
for s in src_groups:
    src_groups[s].sort(key=lambda x: node_order.index(x[0]))

tgt_groups = defaultdict(list)
for s, t, v in flows:
    tgt_groups[t].append((s, v))
for t in tgt_groups:
    tgt_groups[t].sort(key=lambda x: node_order.index(x[0]))

flow_map = {}
src_offset = {n: 0.0 for n in node_order}
for s_node in node_order:
    for t_node, val in src_groups.get(s_node, []):
        h = val * l_scale
        y_top = left_pos[s_node]['top'] - src_offset[s_node]
        y_bot = y_top - h
        src_offset[s_node] += h
        flow_map[(s_node, t_node)] = {
            'src_top': y_top, 'src_bot': y_bot, 'value': val
        }

tgt_offset = {n: 0.0 for n in node_order}
for t_node in node_order:
    for s_node, val in tgt_groups.get(t_node, []):
        h = val * r_scale
        y_top = right_pos[t_node]['top'] - tgt_offset[t_node]
        y_bot = y_top - h
        tgt_offset[t_node] += h
        flow_map[(s_node, t_node)]['tgt_top'] = y_top
        flow_map[(s_node, t_node)]['tgt_bot'] = y_bot

# ══════════════════════════════════════════════════
# Draw flows
# ══════════════════════════════════════════════════
x0 = L_X + BAR_W
x1 = R_X
cx = (x0 + x1) / 2


def draw_flow(fd, source_name, alpha, zorder, edge_alpha=0):
    s_top, s_bot = fd['src_top'], fd['src_bot']
    t_top, t_bot = fd['tgt_top'], fd['tgt_bot']
    color = node_colors[source_name]

    verts = [
        (x0, s_top),
        (cx, s_top), (cx, t_top), (x1, t_top),
        (x1, t_bot),
        (cx, t_bot), (cx, s_bot), (x0, s_bot),
        (x0, s_top),
    ]
    codes = [
        mPath.MOVETO,
        mPath.CURVE4, mPath.CURVE4, mPath.CURVE4,
        mPath.LINETO,
        mPath.CURVE4, mPath.CURVE4, mPath.CURVE4,
        mPath.CLOSEPOLY,
    ]

    path = mPath(verts, codes)
    ec = color if edge_alpha > 0 else 'none'
    patch = mpatches.PathPatch(
        path, facecolor=color, edgecolor=ec,
        alpha=alpha, linewidth=0.8 if edge_alpha > 0 else 0,
        zorder=zorder)
    ax.add_patch(patch)


# Self-flows (large, subtle)
for (s, t), fd in flow_map.items():
    if s == t:
        draw_flow(fd, s, alpha=0.2, zorder=2)

# Cross-flows (thin, vivid, with edge)
for (s, t), fd in flow_map.items():
    if s != t:
        draw_flow(fd, s, alpha=0.55, zorder=3, edge_alpha=0.7)

# ══════════════════════════════════════════════════
# Axes & save
# ══════════════════════════════════════════════════
ax.set_xlim(0, 1)
ax.set_ylim(-0.02, 1.02)
fig.tight_layout(pad=0.5)

png_path, svg_path = save_chart(fig, 'eip_status_sankey', 'outputs/charts/ethereum/eip')
plt.close(fig)

print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
