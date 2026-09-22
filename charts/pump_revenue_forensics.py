"""
PUMP Revenue Forensics — 6 Exhibits
Four Pillars design theme
Data: pump_chart_datapoints.xlsx
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch
from pathlib import Path
from config import (
    create_figure, apply_style, save_chart,
    COLORS, SERIES_COLORS, AXIS_CONFIG, GRID_CONFIG,
    POSITIVE_COLOR, NEGATIVE_COLOR,
    gradient_rounded_bar, area_glow, endpoint_dot,
    setup_font, DPI, DEFAULT_FIGSIZE,
)

OUTPUT_DIR = 'outputs/charts/pump/revenue'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# pump.fun brand colors
PUMP_GREEN = '#86efac'       # brand primary
PUMP_GREEN_DARK = '#1fd978'  # positive
ACCENT_CYAN = '#86efac'      # replaced with brand green
EVENT_RED = '#ff6467'        # negative red
AMBER = '#facc15'            # yellow-400
TEXT_COLOR = '#a1a1aa'        # text tertiary
GRID_COLOR = '#38383f'       # border-low

# Override Four Pillars config colors with pump.fun brand
COLORS['text'] = '#fafafa'
COLORS['text_secondary'] = TEXT_COLOR
COLORS['grid'] = GRID_COLOR
POSITIVE_COLOR = '#1fd978'   # pump.fun positive green

# Load data
xlsx = pd.ExcelFile('outputs/data/pump_chart_datapoints.xlsx')


# ============================================================
# Exhibit 1: Three Sources Table (styled figure)
# ============================================================
def draw_ex1_table():
    setup_font()
    fig, ax = plt.subplots(figsize=(10.67, 3.2), dpi=DPI)
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    headers = ['Source', 'Type', 'Period', 'Value', 'Method']
    rows = [
        ['DeFiLlama', 'Protocol Revenue', "Jul 15 '25 - Feb 21 '26", '$300,041,880', 'On-chain adapter'],
        ['fees.pump.fun', 'Cumulative Buyback', "Jul 15 '25 - Feb 21 '26", '$300,178,162', 'Self-reported'],
        ['Dune (adam_tech)', 'Solana-only Revenue', 'Ongoing', '68-69% of DL', 'On-chain indexer'],
    ]
    disc_row = ['Discrepancy', '', '', '$136,282', '0.045%']

    col_widths = [0.20, 0.20, 0.22, 0.20, 0.18]
    y_start = 0.85
    row_h = 0.15
    x_starts = [0.02]
    for w in col_widths[:-1]:
        x_starts.append(x_starts[-1] + w)

    # Header
    for j, h in enumerate(headers):
        ax.text(x_starts[j] + col_widths[j] / 2, y_start, h,
                fontsize=10, fontweight='bold', color=COLORS['text_secondary'],
                ha='center', va='center', transform=ax.transAxes)

    # Header line
    ax.plot([0.02, 0.98], [y_start - row_h * 0.45] * 2,
            color=COLORS['grid'], alpha=0.4, linewidth=0.8,
            transform=ax.transAxes, clip_on=False)

    # Data rows
    for i, row in enumerate(rows):
        y = y_start - (i + 1) * row_h
        for j, val in enumerate(row):
            color = COLORS['text'] if j in [0] else COLORS['text_secondary']
            if j == 3:
                color = ACCENT_CYAN
            weight = 'bold' if j in [0, 3] else 'normal'
            ax.text(x_starts[j] + col_widths[j] / 2, y, val,
                    fontsize=10, fontweight=weight, color=color,
                    ha='center', va='center', transform=ax.transAxes)

        ax.plot([0.02, 0.98], [y - row_h * 0.45] * 2,
                color=COLORS['grid'], alpha=0.2, linewidth=0.5,
                transform=ax.transAxes, clip_on=False)

    # Discrepancy row
    y_disc = y_start - 4 * row_h
    for j, val in enumerate(disc_row):
        if not val:
            continue
        color = COLORS['text_secondary']
        weight = 'normal'
        if j == 3:
            color = POSITIVE_COLOR
            weight = 'bold'
        if j == 0:
            weight = 'bold'
        ax.text(x_starts[j] + col_widths[j] / 2, y_disc, val,
                fontsize=10, fontweight=weight, color=color,
                ha='center', va='center', transform=ax.transAxes)

    fig.tight_layout()
    return fig


# ============================================================
# Exhibit 3: Fee-to-Revenue Ratio (Line)
# ============================================================
def draw_ex3_fee_rev_ratio():
    df = pd.read_excel(xlsx, sheet_name='Ex3_Fee_Rev_Ratio')
    df = df.dropna(subset=['Date'])
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])

    # Weekly average for smoother line (like JSX data)
    df['Ratio (7d Avg)'] = pd.to_numeric(df['Ratio (7d Avg)'], errors='coerce')
    df = df.dropna(subset=['Ratio (7d Avg)'])
    df_weekly = df.set_index('Date').resample('W-Mon').mean(numeric_only=True).reset_index()
    df_weekly = df_weekly.dropna(subset=['Ratio (7d Avg)'])

    fig, ax = create_figure('line')
    ax.set_facecolor('none')

    x = np.arange(len(df_weekly))
    y = df_weekly['Ratio (7d Avg)'].values.astype(float)
    dates = df_weekly['Date']

    # Area glow
    area_glow(ax, x, y, color=PUMP_GREEN, n_layers=50, max_alpha=0.18, power=2.5)

    # Main line
    ax.plot(x, y, color=PUMP_GREEN, linewidth=2, zorder=4)

    # Endpoint dot
    endpoint_dot(ax, x[-1], y[-1], color=PUMP_GREEN, size=40)

    # Event reference lines
    events = [
        ('2025-03-20', 'PumpSwap'),
        ('2025-05-13', 'Creator Rev'),
        ('2025-09-02', 'Ascend'),
    ]
    for date_str, label in events:
        event_date = pd.Timestamp(date_str)
        # Find nearest weekly index
        diffs = abs(dates - event_date)
        idx = diffs.argmin()
        ax.axvline(x=idx, color='#e4e4e7', linestyle='--', linewidth=0.8, alpha=0.45, zorder=3)
        ax.text(idx, 1.13, label, fontsize=8, fontweight='bold',
                color='#e4e4e7', alpha=0.7, ha='center', va='bottom',
                clip_on=False)

    # Y axis
    ax.set_ylim(0.3, 1.15)
    ax.yaxis.set_major_locator(mticker.FixedLocator([0.3, 0.5, 0.7, 0.9, 1.1]))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f'))

    # X axis - show ~6 ticks
    n = len(df_weekly)
    tick_indices = np.linspace(0, n - 1, 6, dtype=int)
    ax.set_xticks(tick_indices)
    ax.set_xticklabels([dates.iloc[i].strftime('%b %Y') for i in tick_indices])

    ax.set_xlim(-1, n)

    apply_style(fig, ax, 'line')
    return fig


# ============================================================
# Exhibit 4: Streak Distribution (Bar + Geometric overlay)
# ============================================================
def draw_ex4_streaks():
    df = pd.read_excel(xlsx, sheet_name='Ex4_Streaks')
    df = df.dropna(subset=['Streak Length (days)'])
    df = df.head(6)

    fig, ax = create_figure('bar')

    x = np.arange(len(df))
    observed = df['Observed Count'].values
    expected = df['Expected (Geometric)'].values
    width = 0.45

    # Flat bars
    colors = [ACCENT_CYAN] * len(x)
    alphas = [max(0.95 - i * 0.12, 0.4) for i in range(len(x))]
    bars = ax.bar(x, observed, width, color=colors, zorder=3)
    for bar, a in zip(bars, alphas):
        bar.set_alpha(a)

    # X axis (no rotation for single digits)
    ax.set_xticks(x)
    ax.set_xticklabels(df['Streak Length (days)'].astype(int).astype(str), rotation=0, ha='center')
    ax.set_xlim(-0.6, len(x) - 0.4)

    # Y axis
    ax.set_ylim(0, max(observed) * 1.15)
    ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5))

    apply_style(fig, ax, 'bar')
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha='center')
    fig.tight_layout()
    return fig


# ============================================================
# Exhibit 5: Last Digit Distribution (Bar + 10% reference)
# ============================================================
def draw_ex5_digits():
    df = pd.read_excel(xlsx, sheet_name='Ex5_Digits')
    df = df.dropna(subset=['Last Digit'])
    df = df.head(10)

    fig, ax = create_figure('bar')

    x = np.arange(len(df))
    pcts = df['Observed %'].values
    digits = df['Last Digit'].astype(int).values
    width = 0.5

    # Flat bars, digit 0 highlighted
    colors = [AMBER if d == 0 else ACCENT_CYAN for d in digits]
    ax.bar(x, pcts, width, color=colors, alpha=0.85, zorder=3)

    # 10% reference line
    ax.axhline(y=10, color=POSITIVE_COLOR, linestyle='--', linewidth=1, alpha=0.7, zorder=3)
    ax.text(len(x) - 0.5, 10.3, 'Uniform = 10%', fontsize=9, fontweight='bold',
            color=POSITIVE_COLOR, ha='right', va='bottom')

    # X axis
    ax.set_xticks(x)
    ax.set_xticklabels([str(d) for d in digits], rotation=0, ha='center')
    ax.set_xlim(-0.6, len(x) - 0.4)

    # Y axis
    ax.set_ylim(0, 14)
    ax.yaxis.set_major_locator(mticker.FixedLocator([0, 4, 8, 12]))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%g%%'))

    apply_style(fig, ax, 'bar')
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha='center')
    fig.tight_layout()
    return fig


# ============================================================
# Exhibit 6: Weekend Effect (Bar + reference lines)
# ============================================================
def draw_ex6_weekend():
    df = pd.read_excel(xlsx, sheet_name='Ex6_Weekend')
    df = df.dropna(subset=['Day'])
    df = df.head(7)

    fig, ax = create_figure('bar')

    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    x = np.arange(len(df))
    avgs = df['Avg Daily Fees (USD)'].values / 1e6  # Convert to $M
    is_weekend = [d == 'Yes' for d in df['Weekend?']]
    width = 0.55

    colors = [AMBER if w else ACCENT_CYAN for w in is_weekend]
    alphas_list = [0.75 if w else 0.9 for w in is_weekend]
    bars = ax.bar(x, avgs, width, color=colors, zorder=3)
    for bar, a in zip(bars, alphas_list):
        bar.set_alpha(a)

    # Reference lines
    weekday_avg = 2.141
    weekend_avg = 1.806
    ax.axhline(y=weekday_avg, color=ACCENT_CYAN, linestyle='--', linewidth=1, alpha=0.6, zorder=3)
    ax.text(len(x) - 0.3, weekday_avg + 0.04, f'Weekday ${weekday_avg:.2f}M',
            fontsize=9, fontweight='bold', color=ACCENT_CYAN, ha='right', va='bottom')

    ax.axhline(y=weekend_avg, color=AMBER, linestyle='--', linewidth=1, alpha=0.6, zorder=3)
    ax.text(len(x) - 0.3, weekend_avg + 0.04, f'Weekend ${weekend_avg:.2f}M',
            fontsize=9, fontweight='bold', color=AMBER, ha='right', va='bottom')

    # X axis
    ax.set_xticks(x)
    ax.set_xticklabels(days)
    ax.set_xlim(-0.6, len(x) - 0.4)

    # Y axis
    ax.set_ylim(1.4, 2.5)
    ax.yaxis.set_major_locator(mticker.FixedLocator([1.4, 1.7, 2.0, 2.3]))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%.1fM'))

    apply_style(fig, ax, 'bar')
    return fig


# ============================================================
# Exhibit 7: Autocorrelation Decay (Dot-line)
# ============================================================
def draw_ex7_autocorrelation():
    df = pd.read_excel(xlsx, sheet_name='Ex7_Autocorrelation')
    df = df.dropna(subset=['Lag (days)'])
    df = df.head(5)

    fig, ax = create_figure('line')

    df['Autocorrelation'] = pd.to_numeric(df['Autocorrelation'], errors='coerce')
    df = df.dropna(subset=['Autocorrelation'])
    x = np.arange(len(df)).astype(float)
    y = df['Autocorrelation'].values.astype(float)
    labels = ['1d', '2d', '3d', '7d', '14d']

    # Line
    ax.plot(x, y, color=PUMP_GREEN, linewidth=2.5, zorder=4)

    # Area glow
    area_glow(ax, x, y, color=PUMP_GREEN, n_layers=40, max_alpha=0.15, power=2.5)

    # Dots
    ax.scatter(x, y, color=PUMP_GREEN, s=70, zorder=5, edgecolors='none')

    # Value labels on dots
    for i, (xi, yi) in enumerate(zip(x, y)):
        ax.text(xi, yi + 0.03, f'{yi:.3f}', fontsize=10, fontweight='bold',
                color=COLORS['text'], ha='center', va='bottom')

    # Random reference
    ax.axhline(y=0, color=COLORS['grid'], linestyle='--', linewidth=1, alpha=0.4, zorder=2)
    ax.text(len(x) - 0.3, 0.03, 'Random ≈ 0.00', fontsize=9, fontweight='bold',
            color=COLORS['text_secondary'], ha='right', va='bottom')

    # X axis
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    # Y axis
    ax.set_ylim(-0.05, 1.0)
    ax.yaxis.set_major_locator(mticker.FixedLocator([0, 0.25, 0.50, 0.75, 1.0]))

    apply_style(fig, ax, 'line')
    return fig


# ============================================================
# Generate all
# ============================================================
if __name__ == '__main__':
    charts = [
        ('pump_ex1_three_sources', draw_ex1_table),
        ('pump_ex3_fee_rev_ratio', draw_ex3_fee_rev_ratio),
        ('pump_ex4_streaks', draw_ex4_streaks),
        ('pump_ex5_digits', draw_ex5_digits),
        ('pump_ex6_weekend', draw_ex6_weekend),
        ('pump_ex7_autocorrelation', draw_ex7_autocorrelation),
    ]

    for name, func in charts:
        print(f'Drawing {name}...')
        fig = func()
        png_path, svg_path = save_chart(fig, name, output_dir=OUTPUT_DIR)
        print(f'  → {png_path}')
        plt.close(fig)

    print('\nAll 6 exhibits generated.')
