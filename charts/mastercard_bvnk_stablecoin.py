"""
Mastercard-BVNK Acquisition + Stablecoin Market Overview
Four Pillars design theme
Data: rwa.xyz (Mar 18, 2026)
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path
from config import (
    create_figure, apply_style, save_chart,
    COLORS, SERIES_COLORS, AXIS_CONFIG,
    setup_font, DPI, DEFAULT_FIGSIZE,
)

OUTPUT_DIR = 'outputs/charts/stablecoin/market'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


# ============================================================
# Chart 1: Stablecoin Market Cap by Platform (Horizontal Bar)
# ============================================================
def draw_market_share():
    fig, ax = create_figure('bar')

    platforms = ['Tether', 'Circle', 'Binance', 'Sky', 'Ethena', 'Paxos', 'BitGo', 'MakerDAO', 'Others']
    values = [174.3, 75.7, 9.3, 7.7, 6.9, 5.5, 4.5, 3.6, 12.84]  # $B

    # Brand colors
    bar_colors = [
        '#26a17b',  # Tether green
        '#2775ca',  # Circle blue
        '#f0b90b',  # Binance yellow
        '#6c63ff',  # Sky purple
        '#1e1e1e',  # Ethena dark
        '#00845d',  # Paxos green
        '#3073f0',  # BitGo blue
        '#f5ac37',  # MakerDAO orange
        '#4a4a4a',  # Others gray
    ]

    y = np.arange(len(platforms))
    bars = ax.barh(y, values, height=0.6, color=bar_colors, alpha=0.9, zorder=3)

    # Value labels
    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height() / 2,
                f'${val:.1f}B', fontsize=10, fontweight='bold',
                color=COLORS['text'], va='center', ha='left')

    ax.set_yticks(y)
    ax.set_yticklabels(platforms)
    ax.invert_yaxis()
    ax.set_xlim(0, 200)
    ax.xaxis.set_major_locator(mticker.FixedLocator([0, 50, 100, 150, 200]))
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('$%gB'))

    apply_style(fig, ax, 'bar')
    # Override x-tick rotation
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha='center')
    fig.tight_layout()
    return fig


# ============================================================
# Chart 2: TradFi Stablecoin Deals (Horizontal Bar)
# ============================================================
def draw_tradfi_deals():
    fig, ax = create_figure('bar')

    deals = [
        'Mastercard → BVNK\n(Mar 2026)',
        'Stripe → Bridge\n(Feb 2025)',
    ]
    values = [1.8, 1.1]
    bar_colors = ['#eb001b', '#635bff']  # Mastercard red, Stripe purple

    y = np.arange(len(deals))
    bars = ax.barh(y, values, height=0.45, color=bar_colors, alpha=0.9, zorder=3)

    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 0.03, bar.get_y() + bar.get_height() / 2,
                f'${val:.1f}B', fontsize=14, fontweight='bold',
                color=COLORS['text'], va='center', ha='left')

    ax.set_yticks(y)
    ax.set_yticklabels(deals, fontsize=11)
    ax.invert_yaxis()
    ax.set_xlim(0, 2.5)
    ax.xaxis.set_major_locator(mticker.FixedLocator([0, 0.5, 1.0, 1.5, 2.0]))
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('$%.1fB'))

    apply_style(fig, ax, 'bar')
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha='center')
    fig.tight_layout()
    return fig


# ============================================================
# Chart 3: Stablecoin Market Cap by Network (Horizontal Bar)
# ============================================================
def draw_network_share():
    fig, ax = create_figure('bar')

    networks = ['Ethereum', 'TRON', 'Solana', 'BNB Chain', 'Arbitrum', 'Base']
    values = [167.2, 85.8, 14.9, 12.8, 7.6, 4.5]
    bar_colors = [
        '#627eea',  # Ethereum
        '#ff0013',  # TRON
        '#9945ff',  # Solana
        '#f0b90b',  # BNB
        '#28a0f0',  # Arbitrum
        '#0052ff',  # Base
    ]

    y = np.arange(len(networks))
    bars = ax.barh(y, values, height=0.55, color=bar_colors, alpha=0.9, zorder=3)

    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height() / 2,
                f'${val:.1f}B', fontsize=10, fontweight='bold',
                color=COLORS['text'], va='center', ha='left')

    ax.set_yticks(y)
    ax.set_yticklabels(networks)
    ax.invert_yaxis()
    ax.set_xlim(0, 195)
    ax.xaxis.set_major_locator(mticker.FixedLocator([0, 50, 100, 150]))
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('$%gB'))

    apply_style(fig, ax, 'bar')
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha='center')
    fig.tight_layout()
    return fig


# ============================================================
# Generate all
# ============================================================
if __name__ == '__main__':
    charts = [
        ('stablecoin_market_share_by_platform', draw_market_share),
        ('tradfi_stablecoin_deals', draw_tradfi_deals),
        ('stablecoin_market_cap_by_network', draw_network_share),
    ]

    for name, func in charts:
        print(f'Drawing {name}...')
        fig = func()
        png_path, svg_path = save_chart(fig, name, output_dir=OUTPUT_DIR)
        print(f'  → {png_path}')
        plt.close(fig)

    print('\nAll charts generated.')
