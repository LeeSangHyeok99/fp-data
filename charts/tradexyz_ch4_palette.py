"""Shared colours for the Trade[XYZ] ch4 HRC redraws.

Text/structure roles follow the HRC dark spec; venue series keep the reference
hues (brightened for a dark ground) except Trade[XYZ], which takes the point
colour.
"""
TITLE = '#D9D9D9'   # headline text
BODY = '#9CA3AF'    # sub-title and body text
NOTE = '#6D6D6D'    # source / date / note text
POINT = '#F9BD29'   # point colour

# the three Q2 pre-IPO markets, keeping the reference hues (blue / green / gold)
MARKET_COLORS = {
    'CBRS': '#5B7FD4',
    'SPCX': '#2FB894',
    'QNT': '#F9BD29',
}

# every event gets its own vertical dashed line, coloured by whose event it is
EVENT_COLORS = {
    'offering': '#9CA3AF',  # S-1/A, range hike, upsize, guidance, press reports
    'pricing': '#E0574B',   # the print itself: priced, first trade, opening cross
    'nasdaq': '#D9D9D9',    # the listing venue opening / the perp converting
}
EVENT_LINE = dict(linewidth=1.3, linestyle=(0, (6, 4)), alpha=1.0, zorder=2)

# readable ink for a label that sits on top of that venue's own fill
VENUE_INK = {
    'trade.xyz': '#5C4300',
    'binance': '#5C2606',
    'okx': '#22262B',
}

VENUE_COLORS = {
    'trade.xyz': POINT,
    'Trade[XYZ]': POINT,
    'binance': '#E07B39',
    'Binance': '#E07B39',
    'okx': '#A8AEB6',
    'OKX': '#A8AEB6',
    'aster': '#A97BD6',
    'Aster': '#A97BD6',
    'lighter': '#5C7CE0',
    'Lighter': '#5C7CE0',
    'ventuals': '#E0574B',
    'Ventuals': '#E0574B',
}
