"""Preview helper: render the HRC chart on a solid dark canvas for visual QA."""
import sys
sys.path.insert(0, '.claude/skills/design/hrc')
sys.path.insert(0, 'charts')

import matplotlib.pyplot as plt
from single_name_equity_volume_hrc import draw_chart

fig = draw_chart()
fig.patch.set_alpha(1)
fig.patch.set_facecolor('#0a3a34')
fig.savefig(
    'outputs/charts/hyperliquid/hip3/single_name_equity_volume_hrc_preview.png',
    dpi=150, facecolor='#0a3a34', edgecolor='none', bbox_inches='tight',
)
plt.close(fig)
print('Preview saved.')
