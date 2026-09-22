import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, '.claude/skills/design/four-pillars')
from config import setup_font, COLORS, DPI

setup_font()

output_dir = 'outputs/charts/wallet/share'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# =============================================================================
# Data (from image)
# =============================================================================
kr_data = {
    'MetaMask': 68,
    'OKX': 25,
    'Others': 7,
}

global_data = {
    'MetaMask': 50,
    'OKX': 18,
    'Dynamic': 18,
    'Rabby': 7,
    'Others': 7,
}

color_map = {
    'MetaMask': '#e2723a',
    'OKX': '#6b7280',
    'Dynamic': '#6366f1',
    'Rabby': '#a78bfa',
    'Others': '#9ca3af',
}

# =============================================================================
# Chart
# =============================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.67, 5.5), dpi=DPI)
fig.patch.set_alpha(0)

def make_donut(ax, data, colors):
    labels = list(data.keys())
    values = list(data.values())
    cols = [colors[k] for k in labels]
    total = sum(values)

    wedges, _ = ax.pie(
        values,
        colors=cols,
        startangle=90,
        counterclock=False,
        wedgeprops={'width': 0.38, 'edgecolor': '#ffffff', 'linewidth': 2.5},
    )

    # Label each wedge
    angle_start = 90
    for i, (val, wedge) in enumerate(zip(values, wedges)):
        pct = val / total * 100
        mid_angle = angle_start - (val / total * 360) / 2
        angle_rad = np.radians(mid_angle)

        if pct >= 15:
            # Large segments: label on the wedge
            r = 0.81
            x = r * np.cos(angle_rad)
            y = r * np.sin(angle_rad)
            ax.text(x, y, f'{labels[i]}\n{int(pct)}%',
                    ha='center', va='center',
                    fontsize=12, fontweight='bold',
                    color='#ffffff')
        else:
            # Small segments: label outside with leader line
            r_mid = 0.81
            r_out = 1.22

            # Adjust ha based on angle
            deg = mid_angle % 360
            if 90 < deg < 270:
                ha = 'right'
            else:
                ha = 'left'
            if 45 < deg < 135 or 225 < deg < 315:
                ha = 'center'

            x_out = r_out * np.cos(angle_rad)
            y_out = r_out * np.sin(angle_rad)

            ax.text(x_out, y_out, f'{labels[i]} {int(pct)}%',
                    ha=ha, va='center',
                    fontsize=9, fontweight='bold',
                    color=COLORS['text'])

            # Leader line
            x_in = r_mid * np.cos(angle_rad)
            y_in = r_mid * np.sin(angle_rad)
            x_line = 1.08 * np.cos(angle_rad)
            y_line = 1.08 * np.sin(angle_rad)
            ax.plot([x_in, x_line], [y_in, y_line],
                    color='#ffffff', linewidth=0.7, alpha=0.5)

        angle_start -= val / total * 360

    ax.set_facecolor('none')

# Left: South Korea
make_donut(ax1, kr_data, color_map)

# Right: Global
make_donut(ax2, global_data, color_map)

fig.tight_layout(pad=2)

for fmt in ['png', 'svg']:
    fig.savefig(
        f'{output_dir}/wallet_share_donut.{fmt}',
        dpi=DPI,
        facecolor='none',
        edgecolor='none',
        bbox_inches='tight',
        format=fmt if fmt == 'svg' else None,
    )
plt.close()

print(f'Done: wallet_share_donut (png + svg)')
print(f'Output: {output_dir}/')
