import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from matplotlib.ticker import MaxNLocator
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, setup_font, COLORS, DPI

mpl.rcParams['axes.unicode_minus'] = False

KRW_TO_USD = 1000.0

# =============================================================================
# 데이터 로드
# =============================================================================
upbit_ts = pd.read_csv('outputs/data/upbit_2025_daily.csv', parse_dates=['Date'])
bithumb_ts = pd.read_csv('outputs/data/bithumb_2025_daily.csv', parse_dates=['Date'])
upbit_tokens = pd.read_csv('outputs/data/upbit_2025_listings.csv')
bithumb_tokens = pd.read_csv('outputs/data/bithumb_2025_listings.csv')

output_dir = 'outputs/charts/korean_exchange'
Path(output_dir).mkdir(parents=True, exist_ok=True)


def make_chart(ts_df, tokens_df, exchange_name, filename):
    setup_font()
    fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=150)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    dates = ts_df['Date'].values
    cap_usd = ts_df['Capital Deployed (KRW)'].values / KRW_TO_USD
    val_usd = ts_df['Portfolio Value (KRW)'].values / KRW_TO_USD
    rois = ts_df['ROI (%)'].values

    x_pos = np.arange(len(dates))

    # Area fills
    ax.fill_between(x_pos, 0, cap_usd, color='#9a60b4', alpha=0.35, zorder=2)
    ax.plot(x_pos, cap_usd, color='#9a60b4', linewidth=1.5, alpha=0.9, zorder=3)

    ax.fill_between(x_pos, 0, val_usd, color='#fac858', alpha=0.45, zorder=4)
    ax.plot(x_pos, val_usd, color='#fac858', linewidth=1.5, alpha=0.9, zorder=5)

    # Left Y-axis ($)
    max_y = max(cap_usd) * 1.15
    ax.set_ylim(0, max_y)

    def usd_fmt(x, pos):
        if x >= 1000:
            return f'${x/1000:.0f}k'
        return f'${x:.0f}'
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(usd_fmt))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=5))

    # X-axis (bimonthly)
    month_ticks = []
    month_labels = []
    prev = None
    for i, d in enumerate(pd.to_datetime(dates)):
        ym = (d.year, d.month)
        if prev is None or ym != prev:
            if d.month % 2 == 1:
                month_ticks.append(i)
                month_labels.append(d.strftime('%b %Y'))
            prev = ym
    ax.set_xticks(month_ticks)
    ax.set_xticklabels(month_labels)
    ax.set_xlim(-0.5, len(dates) - 0.5)

    # Style
    apply_style(fig, ax, 'area')
    ax.tick_params(axis='y', labelsize=18, length=0, pad=15)
    ax.tick_params(axis='x', labelsize=12, length=0, pad=10, rotation=45)
    plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
    ax.grid(True, axis='y', color='#404040', alpha=0.8, linestyle=(0, (3.7, 1.6)), linewidth=1.0)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Right Y-axis (ROI %)
    ax2 = ax.twinx()
    ax2.plot(x_pos, rois, color='#73c0de', linewidth=1.2, alpha=0.85, zorder=6)
    ax2.set_facecolor('none')

    roi_min, roi_max = min(rois), max(rois)
    margin = (roi_max - roi_min) * 0.1
    ax2.set_ylim(roi_min - margin, roi_max + margin)
    ax2.yaxis.set_major_locator(MaxNLocator(nbins=5))

    def roi_fmt(x, pos):
        return f'{x:.0f}%'
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(roi_fmt))
    ax2.tick_params(axis='y', labelsize=14, length=0, pad=10, colors='#73c0de')
    for spine in ax2.spines.values():
        spine.set_visible(False)

    # Align grid ticks (left axis grid only)
    ax2.grid(False)

    fig.savefig(f'{output_dir}/{filename}.png', dpi=DPI, facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
    fig.savefig(f'{output_dir}/{filename}.svg', format='svg', facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
    plt.close(fig)
    print(f"Saved: {output_dir}/{filename}.png")

    # Stats
    active = tokens_df[tokens_df['Status'] == 'Active']
    n_tokens = len(active)
    total_cap = active['Invested (KRW)'].astype(float).sum() / KRW_TO_USD
    total_val = active['Current Value (KRW)'].astype(float).sum() / KRW_TO_USD
    final_roi = rois[-1]
    per_dollar = total_val / total_cap if total_cap > 0 else 0

    print(f"\n--- {exchange_name} ---")
    print(f"Tokens (active): {n_tokens}")
    print(f"Capital deployed: ${total_cap:,.0f}")
    print(f"Current value: ${total_val:,.0f}")
    print(f"ROI: {final_roi:+.1f}%")
    print(f"Per $1 invested: ${per_dollar:.2f}")

    # Top/Bottom
    active_sorted = active.sort_values('ROI (%)', ascending=False)
    print(f"\nTop 3:")
    for _, r in active_sorted.head(3).iterrows():
        print(f"  {r['Ticker']} ({r['Name']}): {r['ROI (%)']:+.1f}%")
    print(f"Bottom 3:")
    for _, r in active_sorted.tail(3).iterrows():
        print(f"  {r['Ticker']} ({r['Name']}): {r['ROI (%)']:+.1f}%")

    return n_tokens, total_cap, total_val, final_roi, per_dollar


# =============================================================================
# Chart 1: Upbit
# =============================================================================
print("=" * 50)
u_n, u_cap, u_val, u_roi, u_pd = make_chart(upbit_ts, upbit_tokens, 'Upbit', 'upbit_2025_listings')

# =============================================================================
# Chart 2: Bithumb
# =============================================================================
print("\n" + "=" * 50)
b_n, b_cap, b_val, b_roi, b_pd = make_chart(bithumb_ts, bithumb_tokens, 'Bithumb', 'bithumb_2025_listings')
