"""ch7 e74: HIP-3 volume share at five dated milestones.

Every reading is a single day, never a monthly average, because Dreamcash
settled nothing until June 30 and Felix took its last fill on June 20. The
runner-up strip is what the chart is about, so it keeps the red the wind-downs
carry elsewhere in the chapter.
"""
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import to_rgb

sys.path.append('charts')
from tradexyz_ch7_palette import (  # noqa: E402
    DATA, DPI, NOTE, POINT, DIM, RED, base_axes, save, setup_font)


def draw_chart():
    setup_font()
    df = pd.read_csv(DATA / 'e74_concentration_data.csv', parse_dates=['date'])
    df['note'] = df['note'].str.replace(
        r'\b([a-z])', lambda m: m.group(1).upper(), regex=True
    ).str.replace('Km', 'km', regex=False)  # km is a namespace, not a word
    df['runner_name'] = df['runner_name'].replace({'cash': 'Dreamcash'})
    xyz = df['xyz'] * 100
    runner = df['runner'] * 100
    rest = df['rest'] * 100

    fig, ax = plt.subplots(figsize=(12.6, 6.4), dpi=DPI)
    fig.patch.set_alpha(0)
    base_axes(ax)

    x = range(len(df))
    w = 0.56
    for i in x:
        bottom = 0.0
        for series, colour in ((xyz, POINT), (runner, RED), (rest, DIM)):
            grad = np.ones((256, 1, 4))
            grad[:, :, :3] = to_rgb(colour)
            grad[:, :, 3] = np.linspace(1.0, 0.72, 256).reshape(-1, 1)
            ax.imshow(grad, extent=(i - w / 2, i + w / 2, bottom,
                                    bottom + series[i]), origin='upper',
                      aspect='auto', interpolation='bilinear', zorder=3)
            bottom += series[i]

    for i, r in df.iterrows():
        ax.text(i, 46, f'{xyz[i]:.1f}%', fontsize=17, color='#1a1a1a',
                ha='center', va='center', zorder=5)
        ax.text(i, 112, f"{int(r['ns'])} Namespaces Live", fontsize=12,
                color=NOTE, ha='center', va='center', zorder=5)
        # the runner-up strip gets thinner than its own label, so the label
        # always sits above the bar rather than inside the strip
        ax.text(i, 102.5, f"{r['runner_name']} {runner[i]:.1f}%",
                fontsize=12.5, color=RED, ha='center', va='bottom', zorder=5)

    key = [('Trade[XYZ]', POINT, 0.05), ('Runner-Up', RED, 1.05),
           ('All Other Deployers', DIM, 2.05)]
    for label, c, kx in key:
        ax.text(kx - 0.42, -0.26, label, fontsize=12.5, color=c, ha='left',
                va='center', zorder=5, transform=ax.get_xaxis_transform())

    ax.set_ylim(0, 120)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])
    ax.set_xlim(-0.55, len(df) - 0.45)
    ax.set_xticks(list(x))
    ax.set_xticklabels(
        [f"{d.strftime('%b %-d')}\n{n}" for d, n in zip(df['date'], df['note'])],
        fontsize=12.5, linespacing=1.5)
    ax.tick_params(axis='x', pad=10)

    fig.tight_layout()
    return fig


if __name__ == '__main__':
    save(draw_chart(), 'e74_concentration')
