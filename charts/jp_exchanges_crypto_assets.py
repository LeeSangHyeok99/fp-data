"""
Japanese crypto exchanges by number of crypto-assets handled — bar chart
Source: provided data (27 JFSA-registered exchanges)
Style: four-pillars, transparent BG, no title/legend/source.
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from config import setup_font, save_chart, GRID_CONFIG, AXIS_CONFIG, COLORS

setup_font()

BLUE = '#2f6fd0'

# ----------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------
data = [
    ('Binance Japan', 65), ('OKCoin Japan', 51), ('BitTrade', 49),
    ('SBI VC Trade', 47), ('bitbank', 44), ('bitFlyer', 39),
    ('Coincheck', 38), ('GMO Coin', 27), ('Zaif', 26), ('MERCURY', 25),
    ('FINX JCrypto', 18), ('Custodiem', 16), ('Rakuten Wallet', 14),
    ('Crypto Garage', 9), ('LINE Xenesis', 9), ('Btc Box', 7),
    ('S.BLOX', 6), ('BACKSEAT Exchange', 5), ('OSL Japan', 5),
    ('Digital Asset Markets', 4), ('Gaia', 3), ('Mercoin', 3),
    ('Tokyo Hash', 2), ('COINHUB', 1), ('Gate Japan', 1),
    ('MONEY PARTNERS', 1), ('Coinbase', 0),
]
df = pd.DataFrame(data, columns=['exchange', 'crypto_assets_handled'])
df.insert(0, 'rank', range(1, len(df) + 1))
df.to_csv('outputs/data/jp_exchanges_crypto_assets.csv', index=False)

x = np.arange(len(df))

# ----------------------------------------------------------------------
# Figure
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(13, 5.8), dpi=150)
ax.bar(x, df['crypto_assets_handled'], width=0.78, color=BLUE, zorder=3)

ax.set_ylim(0, 68)
ax.yaxis.set_major_locator(MultipleLocator(20))   # 0,20,40,60
ax.set_xticks(x)
ax.set_xticklabels(df['exchange'])
ax.set_xlim(-0.7, len(df) - 0.3)

# four-pillars styling
fig.patch.set_alpha(0)
ax.set_facecolor('none')
ax.grid(True, axis='y', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(axis='y', labelsize=AXIS_CONFIG['y_tick']['fontsize'],
               pad=AXIS_CONFIG['y_tick']['pad'], length=0,
               colors=AXIS_CONFIG['y_tick']['color'])
ax.tick_params(axis='x', labelsize=11, pad=8, rotation=90,
               colors=AXIS_CONFIG['x_tick']['color'])
plt.setp(ax.xaxis.get_majorticklabels(), ha='center', va='top')
fig.tight_layout()

png, svg = save_chart(fig, 'jp_exchanges_crypto_assets',
                      'outputs/charts/macro/exchanges')
plt.close(fig)
print('saved:', png)
print('exchanges:', len(df), '| max', df['crypto_assets_handled'].max(),
      '| median', int(df['crypto_assets_handled'].median()))
