"""Payment Scan monthly volume history by project (4pillars research dashboard).

Data: sources/paymentscan_volume_by_project.json
      (RSC payload of https://research.4pillars.io/en/data/payment, 2026-08-10)
Colors: the dashboard's own per-project gradient stops.
"""
import json
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, save_chart, AXIS_CONFIG

SRC = 'sources/paymentscan_volume_by_project.json'
OTHERS_COLOR = '#787b86'

# Named series in dashboard stack order (bottom to top), with its brand colors
PROJECTS = [
    ('RedotPay', '#E63B3B'),
    ('KAST', '#00E5BD'),
    ('EtherFi', '#C4B5FD'),
    ('Karta', '#6366F1'),
    ('Plasma One', '#02FF8A'),
]

WIDTH = 0.72
ALPHA_TOP, ALPHA_BOTTOM = 0.95, 0.5  # dashboard gradient stops


def gradient_segment(ax, xc, y0, h, color):
    """Bar segment filled with a vertical alpha ramp (dim at the bottom)."""
    if h <= 0:
        return
    rgb = matplotlib.colors.to_rgb(color)
    grad = np.empty((256, 1, 4))
    grad[:, 0, :3] = rgb
    grad[:, 0, 3] = np.linspace(ALPHA_BOTTOM, ALPHA_TOP, 256)
    ax.imshow(grad, aspect='auto', origin='lower', interpolation='bilinear',
              extent=[xc - WIDTH / 2, xc + WIDTH / 2, y0, y0 + h], zorder=2)


rows = json.load(open(SRC))
labels = [r['date'] for r in rows]
x = np.arange(len(rows))

named = {p: np.array([r.get(p, 0) / 1e6 for r in rows]) for p, _ in PROJECTS}
others = np.array([r['total'] / 1e6 for r in rows]) - sum(named.values())

fig, ax = create_figure('bar')
bottom = np.zeros(len(rows))
for name, color in PROJECTS + [('Others', OTHERS_COLOR)]:
    v = named.get(name, others)
    for xi, y0, h in zip(x, bottom, v):
        gradient_segment(ax, xi, y0, h, color)
    bottom += v

ax.set_xlim(-0.7, len(rows) - 0.3)
ax.set_ylim(0, 1200)
ax.set_yticks([0, 300, 600, 900, 1200])
ax.set_yticklabels([f'${v}M' for v in [0, 300, 600, 900, 1200]])

ticks = [i for i, d in enumerate(labels) if d.endswith(('-01', '-07'))]
ax.set_xticks(ticks)
ax.set_xticklabels([f"{'Jan' if labels[i].endswith('-01') else 'Jul'} {labels[i][:4]}"
                    for i in ticks])

apply_style(fig, ax, 'bar')
ax.tick_params(axis='y', labelsize=AXIS_CONFIG['y_tick']['fontsize'] - 4)
ax.tick_params(axis='x', labelsize=AXIS_CONFIG['x_tick']['fontsize'] - 4)
fig.tight_layout()

png, svg = save_chart(fig, 'paymentscan_volume_by_project',
                      'outputs/charts/payment/volume')
plt.close(fig)

last = rows[-1]
print(f"{last['date']}  total ${last['total']/1e6:.1f}M")
for name, _ in PROJECTS:
    print(f"  {name:12} ${named[name][-1]:7.1f}M  {named[name][-1]/(last['total']/1e6)*100:5.1f}%")
print(f"  {'Others':12} ${others[-1]:7.1f}M  {others[-1]/(last['total']/1e6)*100:5.1f}%")
print(png, svg, sep='\n')
