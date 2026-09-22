import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

import sys
sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, save_chart, COLORS, GRID_CONFIG

# ══════════════════════════════════════════════════
# Data: 501 Sources of Real-World Yield (Electric Capital, Mar 2026)
# 7 Adoption Barriers with subcategory breakdown
# ══════════════════════════════════════════════════
barriers = [
    {
        'name': 'Specialized\nOrigination',
        'total': 80,
        'subs': [
            ('Infrastructure', 21),
            ('Consumer\nLending', 20),
            ('Cat Bonds', 17),
            ('Other', 22),
        ]
    },
    {
        'name': 'Legal\nStructuring',
        'total': 77,
        'subs': [
            ('Corporate\nBonds', 24),
            ('ABS/CLOs', 19),
            ('MBS', 14),
            ('Other', 20),
        ]
    },
    {
        'name': 'Execution\nInfrastructure',
        'total': 68,
        'subs': [
            ('Carry\nStrategies', 30),
            ('Options', 20),
            ('Arbitrage', 18),
        ]
    },
    {
        'name': 'Physical-world\nIntegration',
        'total': 60,
        'subs': [
            ('Oil/Gas/\nMining', 15),
            ('Compute', 11),
            ('Real Estate', 11),
            ('Other', 23),
        ]
    },
    {
        'name': 'Cross-border\nAccess',
        'total': 55,
        'subs': [
            ('REITs', 25),
            ("Int'l Sovereign\nDebt", 11),
            ('Other', 19),
        ]
    },
    {
        'name': 'Market\nAggregation',
        'total': 43,
        'subs': [
            ('Specialty\nFinance', 20),
            ('Municipal\nBonds', 12),
            ('Other', 11),
        ]
    },
    {
        'name': 'Bespoke\nEvaluation',
        'total': 35,
        'subs': [
            ('IP Licensing', 15),
            ('Sports/Art', 14),
            ('Litigation', 6),
        ]
    },
]

# Sort descending by total
barriers.sort(key=lambda x: x['total'], reverse=False)

# ══════════════════════════════════════════════════
# Colors: subcategory segments
# ══════════════════════════════════════════════════
SUB_COLORS = [
    '#5470c6',  # blue
    '#73c0de',  # light blue
    '#91cc75',  # green
    '#fac858',  # yellow
]
OTHER_COLOR = '#3a3a3a'

# ══════════════════════════════════════════════════
# Figure
# ══════════════════════════════════════════════════
setup_font()
fig, ax = plt.subplots(figsize=(13.33, 7.33), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# ══════════════════════════════════════════════════
# Stacked horizontal bars
# ══════════════════════════════════════════════════
bar_height = 0.55
y_pos = np.arange(len(barriers))

for i, barrier in enumerate(barriers):
    left = 0
    subs = barrier['subs']

    for j, (sub_name, sub_count) in enumerate(subs):
        if sub_name == 'Other':
            color = OTHER_COLOR
        else:
            color = SUB_COLORS[j % len(SUB_COLORS)]

        bar = ax.barh(
            i, sub_count, height=bar_height,
            left=left, color=color,
            edgecolor='#141414', linewidth=0.8
        )

        # Label inside segment if wide enough
        if sub_count >= 10:
            label_x = left + sub_count / 2
            display_name = sub_name.replace('\n', ' ')
            ax.text(
                label_x, i,
                f'{display_name}\n{sub_count}',
                va='center', ha='center',
                fontsize=8.5, fontweight='bold',
                color='#ffffff' if sub_name != 'Other' else '#888888',
                linespacing=1.3,
            )
        elif sub_count >= 6:
            label_x = left + sub_count / 2
            ax.text(
                label_x, i,
                f'{sub_count}',
                va='center', ha='center',
                fontsize=8, fontweight='bold',
                color='#ffffff' if sub_name != 'Other' else '#888888',
            )

        left += sub_count

    # Total count at end of bar
    ax.text(
        barrier['total'] + 1.5, i,
        f"{barrier['total']}",
        va='center', ha='left',
        fontsize=16, fontweight='bold',
        color=COLORS['text'],
    )

# ══════════════════════════════════════════════════
# Axes
# ══════════════════════════════════════════════════
ax.set_yticks(y_pos)
ax.set_yticklabels([b['name'] for b in barriers])
ax.set_xlim(0, 95)
ax.set_xticks([0, 20, 40, 60, 80])

# ══════════════════════════════════════════════════
# Style
# ══════════════════════════════════════════════════
ax.grid(
    True, axis='x',
    color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
    linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth']
)
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

ax.tick_params(
    axis='y', labelsize=14, pad=10, length=0,
    colors=COLORS['text_secondary']
)
ax.tick_params(
    axis='x', labelsize=13, pad=10, length=0,
    colors=COLORS['text_secondary']
)

# Invert y to show largest at top
ax.invert_yaxis()

fig.tight_layout()

# ══════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════
png_path, svg_path = save_chart(
    fig, 'rwa_adoption_barriers',
    'outputs/charts/rwa/tokenization'
)
plt.close(fig)
print(f"PNG: {png_path}")
print(f"SVG: {svg_path}")
