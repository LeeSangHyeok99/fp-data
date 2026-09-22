import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/hrc')
from config import setup_font, COLORS, DPI, GRID_CONFIG

output_dir = 'outputs/charts/hyperliquid/metrics'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# =============================================================================
# Data from PDF Table 11 (March 2026) + Table 12
# =============================================================================
exchanges = ['Hyperliquid', 'Binance', 'Bybit', 'Coinbase', 'Kraken']

# OI in billions
total_oi = [5.85, 15.0, 7.5, 2.0, 1.4]
btc_oi =   [1.7, 7.2, 3.5, 1.0, 0.65]
eth_oi =   [0.85, 3.5, 1.7, 0.45, 0.30]
sol_oi =   [0.35, 1.5, 0.75, 0.15, 0.12]

# HL vs CEX ratio
hl_ratio = [None, 39, 78, 293, 418]  # %

# Slippage for $1M market order (BTC-PERP, lower = better)
slippage_1m_btc = [0.008, 0.02, 0.015, 0.04, 0.06]  # %

# BTC spread
btc_spread = [1.0, 5.50, 3.0, 8.0, 12.0]  # USD

# Colors
EX_COLORS = {
    'Hyperliquid': '#50e3c2',
    'Binance': '#F0B90B',
    'Bybit': '#f7a600',
    'Coinbase': '#0052FF',
    'Kraken': '#7B61FF',
}

setup_font()

# =============================================================================
# Chart 1: Total Perp OI Horizontal Bar
# =============================================================================
fig, ax = plt.subplots(figsize=(10.67, 4.0), dpi=DPI)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

# Sort by OI descending for horizontal bar (ascending for barh)
order = np.argsort(total_oi)  # ascending
sorted_ex = [exchanges[i] for i in order]
sorted_oi = [total_oi[i] for i in order]
sorted_colors = [EX_COLORS[e] for e in sorted_ex]

bars = ax.barh(range(len(sorted_ex)), sorted_oi, height=0.6,
               color=sorted_colors, alpha=0.85, zorder=3)

# Value labels + HL ratio
for i, (ex, oi) in enumerate(zip(sorted_ex, sorted_oi)):
    # Value label
    ax.text(oi + 0.2, i, f'${oi:.1f}B',
            va='center', ha='left',
            fontsize=15, fontweight='bold',
            color=COLORS['text'])

    # HL ratio for CEXs
    idx = exchanges.index(ex)
    if hl_ratio[idx] is not None:
        ratio = hl_ratio[idx]
        if ratio < 100:
            ratio_text = f'HL = {ratio}%'
            ratio_color = COLORS['text_secondary']
        else:
            ratio_text = f'HL = {ratio}%'
            ratio_color = '#50e3c2'
        ax.text(oi + 0.2, i - 0.25, ratio_text,
                va='top', ha='left',
                fontsize=11, fontweight='bold',
                color=ratio_color, alpha=0.8)

# Y axis
ax.set_yticks(range(len(sorted_ex)))
ax.set_yticklabels(sorted_ex,
                    fontsize=18, fontweight='bold',
                    color=COLORS['text'])

# X axis
x_ticks = np.arange(0, 20, 5)
ax.set_xticks(x_ticks)
ax.set_xticklabels([f'${int(v)}B' for v in x_ticks],
                    fontsize=16, fontweight='bold',
                    color=COLORS['text_secondary'])
ax.set_xlim(0, 18)

# Grid
ax.grid(True, axis='x',
        color=GRID_CONFIG['color'],
        alpha=GRID_CONFIG['alpha'],
        linestyle=GRID_CONFIG['linestyle'],
        linewidth=GRID_CONFIG['linewidth'])
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

ax.tick_params(axis='y', length=0, pad=10)
ax.tick_params(axis='x', length=6, width=1, colors=COLORS['text_secondary'])

fig.tight_layout()

for fmt in ['png', 'svg']:
    fig.savefig(
        f'{output_dir}/hl_vs_cex_total_oi.{fmt}',
        dpi=DPI, facecolor='none', edgecolor='none',
        bbox_inches='tight', transparent=True,
        format=fmt if fmt == 'svg' else None,
    )
plt.close()

# =============================================================================
# Chart 2: BTC/ETH/SOL OI Grouped Bar
# =============================================================================
fig2, ax2 = plt.subplots(figsize=(10.67, 4.67), dpi=DPI)
fig2.patch.set_alpha(0)
ax2.set_facecolor('none')

assets = ['BTC', 'ETH', 'SOL']
asset_data = {
    'BTC': btc_oi,
    'ETH': eth_oi,
    'SOL': sol_oi,
}

x = np.arange(len(exchanges))
n_assets = len(assets)
bar_width = 0.22
offsets = np.arange(n_assets) - (n_assets - 1) / 2

ASSET_COLORS = ['#f97316', '#627eea', '#9945ff']  # BTC orange, ETH blue, SOL purple

for j, (asset, color) in enumerate(zip(assets, ASSET_COLORS)):
    vals = asset_data[asset]
    bars = ax2.bar(x + offsets[j] * bar_width, vals, bar_width,
                   color=color, alpha=0.85, zorder=3)
    # Value labels on top
    for i, v in enumerate(vals):
        if v >= 1:
            label = f'${v:.1f}B'
        else:
            label = f'${int(v*1000)}M'
        ax2.text(x[i] + offsets[j] * bar_width, v + 0.08, label,
                 ha='center', va='bottom',
                 fontsize=9, fontweight='bold',
                 color=color, alpha=0.9)

# X axis
ax2.set_xticks(x)
ax2.set_xticklabels(exchanges,
                     fontsize=16, fontweight='bold',
                     color=COLORS['text'])

# Y axis
y_ticks = np.arange(0, 10, 2)
ax2.set_yticks(y_ticks)
ax2.set_yticklabels([f'${int(v)}B' for v in y_ticks],
                     fontsize=18, fontweight='bold',
                     color=COLORS['text_secondary'])
ax2.set_ylim(0, 9)

# Grid
ax2.grid(True, axis='y',
         color=GRID_CONFIG['color'],
         alpha=GRID_CONFIG['alpha'],
         linestyle=GRID_CONFIG['linestyle'],
         linewidth=GRID_CONFIG['linewidth'])
ax2.set_axisbelow(True)

for spine in ax2.spines.values():
    spine.set_visible(False)

ax2.tick_params(axis='x', length=0, pad=10)
ax2.tick_params(axis='y', length=0)

fig2.tight_layout()

for fmt in ['png', 'svg']:
    fig2.savefig(
        f'{output_dir}/hl_vs_cex_asset_oi.{fmt}',
        dpi=DPI, facecolor='none', edgecolor='none',
        bbox_inches='tight', transparent=True,
        format=fmt if fmt == 'svg' else None,
    )
plt.close()

# =============================================================================
# Chart 3: BTC Slippage + Spread Comparison (horizontal bar, lower = better)
# =============================================================================
fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(10.67, 3.5), dpi=DPI,
                                    gridspec_kw={'width_ratios': [1, 1]})
fig3.patch.set_alpha(0)

for ax_sub in [ax3a, ax3b]:
    ax_sub.set_facecolor('none')
    for spine in ax_sub.spines.values():
        spine.set_visible(False)

# Left: BTC Spread
order_spread = np.argsort(btc_spread)  # ascending (best first)
sorted_ex_s = [exchanges[i] for i in order_spread]
sorted_spread = [btc_spread[i] for i in order_spread]
sorted_colors_s = [EX_COLORS[e] for e in sorted_ex_s]

ax3a.barh(range(len(sorted_ex_s)), sorted_spread, height=0.55,
          color=sorted_colors_s, alpha=0.85, zorder=3)

for i, (ex, val) in enumerate(zip(sorted_ex_s, sorted_spread)):
    ax3a.text(val + 0.2, i, f'${val:.2f}' if val < 2 else f'${val:.1f}',
              va='center', ha='left',
              fontsize=13, fontweight='bold',
              color=COLORS['text'])

ax3a.set_yticks(range(len(sorted_ex_s)))
ax3a.set_yticklabels(sorted_ex_s, fontsize=14, fontweight='bold', color=COLORS['text'])
ax3a.set_xlim(0, 16)
ax3a.set_xticks([0, 5, 10, 15])
ax3a.set_xticklabels(['$0', '$5', '$10', '$15'],
                      fontsize=12, fontweight='bold', color=COLORS['text_secondary'])
ax3a.grid(True, axis='x', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
          linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax3a.set_axisbelow(True)
ax3a.tick_params(axis='y', length=0, pad=8)
ax3a.tick_params(axis='x', length=4, width=1, colors=COLORS['text_secondary'])
ax3a.set_title('BTC Spread', fontsize=16, fontweight='bold',
               color=COLORS['text'], pad=12)

# Right: $1M Slippage
order_slip = np.argsort(slippage_1m_btc)
sorted_ex_sl = [exchanges[i] for i in order_slip]
sorted_slip = [slippage_1m_btc[i] for i in order_slip]
sorted_colors_sl = [EX_COLORS[e] for e in sorted_ex_sl]

ax3b.barh(range(len(sorted_ex_sl)), sorted_slip, height=0.55,
          color=sorted_colors_sl, alpha=0.85, zorder=3)

for i, (ex, val) in enumerate(zip(sorted_ex_sl, sorted_slip)):
    ax3b.text(val + 0.001, i, f'{val:.3f}%',
              va='center', ha='left',
              fontsize=13, fontweight='bold',
              color=COLORS['text'])

ax3b.set_yticks(range(len(sorted_ex_sl)))
ax3b.set_yticklabels(sorted_ex_sl, fontsize=14, fontweight='bold', color=COLORS['text'])
ax3b.set_xlim(0, 0.08)
ax3b.set_xticks([0, 0.02, 0.04, 0.06])
ax3b.set_xticklabels(['0%', '0.02%', '0.04%', '0.06%'],
                      fontsize=12, fontweight='bold', color=COLORS['text_secondary'])
ax3b.grid(True, axis='x', color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
          linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
ax3b.set_axisbelow(True)
ax3b.tick_params(axis='y', length=0, pad=8)
ax3b.tick_params(axis='x', length=4, width=1, colors=COLORS['text_secondary'])
ax3b.set_title('BTC $1M Slippage', fontsize=16, fontweight='bold',
               color=COLORS['text'], pad=12)

fig3.tight_layout()

for fmt in ['png', 'svg']:
    fig3.savefig(
        f'{output_dir}/hl_vs_cex_liquidity.{fmt}',
        dpi=DPI, facecolor='none', edgecolor='none',
        bbox_inches='tight', transparent=True,
        format=fmt if fmt == 'svg' else None,
    )
plt.close()

print('Done: hl_vs_cex_total_oi, hl_vs_cex_asset_oi, hl_vs_cex_liquidity')
print(f'\nHL Total OI: $5.85B (39% of Binance, 293% of Coinbase)')
print(f'HL BTC Spread: $1 (Binance $5.50, 5.5x tighter)')
print(f'HL $1M Slippage: 0.008% (Binance 0.02%, 2.5x better)')
