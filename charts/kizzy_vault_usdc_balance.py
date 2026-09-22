import sys

import matplotlib

matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append('.claude/skills/design/four-pillars')
from config import apply_style, create_figure, save_chart

# =============================================================================
# Data
# =============================================================================
df = pd.read_csv('sources/figure18_kizzy_vault_usdc_balance.csv',
                 parse_dates=['date'])
d = df[df['vault_usdc_balance'].notna()]
bal_k = d['vault_usdc_balance'] / 1e3

COLOR_KIZZY = '#7C3AED'  # Kizzy 세트 바이올렛

# =============================================================================
# Chart: Vault USDC 잔고 line + light area fill
# =============================================================================
fig, ax = create_figure('area')

ax.plot(d['date'], bal_k, color=COLOR_KIZZY, linewidth=2.5, zorder=4)
ax.fill_between(d['date'], bal_k, color=COLOR_KIZZY, alpha=0.12,
                linewidth=0, zorder=2)

# Y axis: $0K~$100K, $25K 간격 (최종 $101.5K)
ax.set_yticks([0, 25, 50, 75, 100])
ax.set_yticklabels(['$0K', '$25K', '$50K', '$75K', '$100K'])
ax.set_ylim(0, 105)

# X axis (데이터 시작 12/15라 Jan부터 격월 틱)
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 3, 5, 7]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.set_xlim(d['date'].min(), d['date'].max())

apply_style(fig, ax, 'area')
ax.tick_params(axis='y', labelsize=16)
ax.tick_params(axis='x', labelsize=14)

png, svg = save_chart(fig, 'kizzy_vault_usdc_balance',
                      'outputs/charts/kizzy/vault')
plt.close(fig)
print(png)
