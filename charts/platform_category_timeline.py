import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import setup_font, COLORS, DPI, GRID_CONFIG

# =============================================================================
# Data
# =============================================================================
print("Loading data...")
df = pd.read_csv('outputs/data/kalshi_polymarket_merged.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['month'] = df['timestamp'].dt.to_period('M')

theme_map = {
    'Sports': 'Sports',
    'Politics': 'Politics',
    'Economics': 'Macro',
    'Crypto': 'Crypto',
    'Culture': 'Culture',
    'STEM': 'Other',
    'Financials': 'Macro',
}
df['theme'] = df['category'].map(theme_map).fillna('Other')

START = pd.Period('2024-01', 'M')
END = pd.Period('2026-02', 'M')

# Monthly aggregation
monthly = df.groupby(['month', 'source', 'theme'])['open_interest_usd'].sum().reset_index()
monthly = monthly[(monthly['month'] >= START) & (monthly['month'] <= END)]
monthly['date'] = monthly['month'].dt.to_timestamp()

output_dir = 'outputs/charts/prediction_markets'
Path(output_dir).mkdir(parents=True, exist_ok=True)

theme_colors = {
    'Sports':     '#91cc75',
    'Politics':   '#5470c6',
    'Macro':      '#73c0de',
    'Crypto':     '#f7931a',
    'Culture':    '#ea7ccc',
    'Other':      '#666666',
}

# Stack order (bottom to top)
STACK_ORDER = ['Other', 'Culture', 'Crypto', 'Macro', 'Politics', 'Sports']

def make_pct_chart(platform, filename):
    setup_font()

    pdf = monthly[monthly['source'] == platform].copy()
    pivot = pdf.groupby(['date', 'theme'])['open_interest_usd'].sum().unstack(fill_value=0)

    # Convert to percentages
    row_totals = pivot.sum(axis=1)
    pct = pivot.div(row_totals, axis=0) * 100
    pct = pct.fillna(0)

    # Ensure all columns exist
    for col in STACK_ORDER:
        if col not in pct.columns:
            pct[col] = 0

    fig, ax = plt.subplots(figsize=(1297/DPI, 518/DPI), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    # Platform label (top-left)
    ax.text(0.01, 0.97, platform, transform=ax.transAxes,
            fontsize=18, fontweight='bold', color=COLORS['text_secondary'],
            va='top', ha='left', alpha=0.6, zorder=10)

    # Stacked bar (100%)
    bar_width = 20  # days
    bottom = np.zeros(len(pct))
    for col in STACK_ORDER:
        vals = pct[col].values
        color = theme_colors.get(col, '#666666')
        ax.bar(pct.index, vals, bottom=bottom, width=bar_width,
               color=color, alpha=0.85, edgecolor='#1a1a1a', linewidth=0.3)
        bottom += vals

    latest = pct.iloc[-1]

    # Y-axis
    y_ticks = [0, 25, 50, 75, 100]
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f'{v}%' for v in y_ticks],
                       fontsize=13, fontweight='bold', color=COLORS['text_secondary'])
    ax.tick_params(axis='y', length=0, pad=12)
    ax.set_ylim(0, 100)

    # X-axis
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
    ax.tick_params(axis='x', labelsize=11, pad=8, length=0, colors=COLORS['text_secondary'])
    plt.setp(ax.xaxis.get_majorticklabels(), fontweight='bold', ha='right', rotation=45)
    ax.set_xlim(pct.index.min() - pd.Timedelta(days=15), pct.index.max() + pd.Timedelta(days=15))

    # Grid
    ax.grid(True, axis='y',
            color=GRID_CONFIG['color'], alpha=GRID_CONFIG['alpha'],
            linestyle=GRID_CONFIG['linestyle'], linewidth=GRID_CONFIG['linewidth'])
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.tight_layout()
    fig.savefig(f'{output_dir}/{filename}.png', dpi=DPI,
                facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)
    fig.savefig(f'{output_dir}/{filename}.svg', format='svg',
                facecolor='none', edgecolor='none', bbox_inches='tight', transparent=True)

    # Resize to exact 1297x518
    from PIL import Image
    img = Image.open(f'{output_dir}/{filename}.png')
    img = img.resize((1297, 518), Image.LANCZOS)
    img.save(f'{output_dir}/{filename}.png')
    plt.close(fig)

    print(f"\n{platform} category share (Feb 2026):")
    for col in reversed(STACK_ORDER):
        if latest[col] > 1:
            print(f"  {col}: {latest[col]:.1f}%")

make_pct_chart('Kalshi', 'kalshi_categories_pct')
print("Chart 1 saved: Kalshi Category Share")

make_pct_chart('Polymarket', 'polymarket_categories_pct')
print("Chart 2 saved: Polymarket Category Share")
