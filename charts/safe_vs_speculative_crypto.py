"""
Safe Assets Outpace Speculative Assets in Crypto
Tokenized US Treasury vs. DeFi TVL & Total Crypto Market Cap, 2023-01-01 ~ now
Four Pillars design theme

3개 시리즈의 y축 range가 3자리수 차이나므로 두 가지 표현을 모두 출력한다.
  _indexed  2023-01-01 = 100 리베이스, 로그 축 1개 (상대 성장률 비교)
  _dual     듀얼 축. 왼쪽 $B (Treasury + DeFi TVL), 오른쪽 $T (Total Market Cap)

Data:
  Tokenized US Treasury  sources/rwa-xyz-treasury-market-caps.csv (app.rwa.xyz/treasuries)
  DeFi TVL               api.llama.fi/v2/historicalChainTvl
  Total Crypto Mcap      api.coinmarketcap.com global-metrics historical
"""

import sys
sys.path.insert(0, '.claude/skills/design/four-pillars')

import time
import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from pathlib import Path
from config import COLORS, apply_style, setup_font, save_chart

RWA_SRC = 'sources/rwa-xyz-treasury-market-caps.csv'  # app.rwa.xyz/treasuries 익스포트
CACHE = Path('outputs/data/safe_vs_speculative.csv')
OUTPUT_DIR = 'outputs/charts/rwa/market'
START_DATE = '2023-01-01'

C_TREASURY = '#fc8452'   # 오렌지
C_TVL = '#5470c6'        # 블루
C_MCAP = '#9aa0a6'       # 미디엄 그레이 (어두운 배경에서도 보이게)
TICK_FONTSIZE = 16       # x/y 축 공통
SMOOTH_DAYS = 14         # 일별 노이즈만 걷어내는 중심 이동평균


def load() -> pd.DataFrame:
    if CACHE.exists():
        df = pd.read_csv(CACHE, parse_dates=['date'])
        return df

    rwa = pd.read_csv(RWA_SRC)
    rwa['date'] = pd.to_datetime(rwa['Date'])
    funds = rwa.drop(columns=['Timestamp', 'Date', 'Measure', 'date'])
    rwa['treasury'] = funds.apply(pd.to_numeric, errors='coerce').sum(axis=1) / 1e9
    rwa = rwa[['date', 'treasury']]

    r = requests.get('https://api.llama.fi/v2/historicalChainTvl', timeout=60)
    r.raise_for_status()
    tvl = pd.DataFrame(r.json())
    tvl['date'] = pd.to_datetime(tvl['date'], unit='s').dt.normalize()
    tvl['tvl'] = tvl['tvl'] / 1e9
    tvl = tvl[['date', 'tvl']]

    end = int(time.time())
    start = int(pd.Timestamp(START_DATE).timestamp()) - 7 * 86400
    url = ('https://api.coinmarketcap.com/data-api/v3/global-metrics/quotes/historical'
           f'?format=chart&interval=1d&timeStart={start}&timeEnd={end}')
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=60)
    r.raise_for_status()
    mcap = pd.DataFrame([
        {'date': pd.to_datetime(q['timestamp']).tz_localize(None).normalize(),
         'mcap': q['quote'][0]['totalMarketCap'] / 1e12}
        for q in r.json()['data']['quotes']
    ])

    df = rwa.merge(tvl, on='date').merge(mcap, on='date')
    df = df[df['date'] >= START_DATE].sort_values('date').reset_index(drop=True)
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CACHE, index=False)
    return df


df = load()
assert len(df) > 1200, f'unexpected row count: {len(df)}'
assert df['mcap'].max() < 4.5, f'mcap exceeds right axis: {df["mcap"].max()}'
assert df[['treasury', 'tvl']].max().max() < 180, 'left axis range too small'


def sm(series: pd.Series) -> pd.Series:
    """중심 7일 이동평균. 양 끝은 min_periods=1로 잘리지 않게 둔다."""
    return series.rolling(SMOOTH_DAYS, center=True, min_periods=1).mean()


def _finish(fig, ax, ax2=None):
    apply_style(fig, ax, 'line')
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.tick_params(axis='x', labelsize=TICK_FONTSIZE)
    ax.tick_params(axis='y', labelsize=TICK_FONTSIZE)
    if ax2 is not None:
        for spine in ax2.spines.values():
            spine.set_visible(False)
        ax2.tick_params(axis='y', labelsize=TICK_FONTSIZE, length=0, pad=15,
                        colors=COLORS['text_secondary'])
        ax2.set_facecolor('none')
    fig.tight_layout()


def draw_dual(figsize=(10.67, 4.67)):
    """왼쪽 $B (Treasury, DeFi TVL) / 오른쪽 $T (Total Market Cap)."""
    setup_font()
    fig, ax = plt.subplots(figsize=figsize, dpi=150)
    ax2 = ax.twinx()

    d = df['date']
    ax2.plot(d, sm(df['mcap']), color=C_MCAP, linewidth=2.0, zorder=2)
    ax.plot(d, sm(df['tvl']), color=C_TVL, linewidth=2.2, zorder=3)
    ax.plot(d, sm(df['treasury']), color=C_TREASURY, linewidth=2.2, zorder=4)

    ax.set_xlim(d.iloc[0], d.iloc[-1])
    # 좌/우 틱 5개, 축 상단 여백 비율을 동일(40/180 == 1/4.5)하게 맞춰 그리드 정렬
    ax.set_ylim(0, 180)
    ax.yaxis.set_major_locator(mticker.FixedLocator([0, 40, 80, 120, 160]))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%gB'))
    ax2.set_ylim(0, 4.5)
    ax2.yaxis.set_major_locator(mticker.FixedLocator([0, 1, 2, 3, 4]))
    ax2.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%gT'))

    _finish(fig, ax, ax2)
    return fig


def draw_indexed(figsize=(10.67, 4.67)):
    """2023-01-01 = 100 리베이스, 로그 축."""
    setup_font()
    fig, ax = plt.subplots(figsize=figsize, dpi=150)

    d = df['date']
    for col, color in (('mcap', C_MCAP), ('tvl', C_TVL), ('treasury', C_TREASURY)):
        ax.plot(d, sm(df[col] / df[col].iloc[0] * 100), color=color,
                linewidth=2.2, zorder=3)

    ax.set_xlim(d.iloc[0], d.iloc[-1])
    ax.set_yscale('log')
    ax.set_ylim(50, 50000)
    ax.yaxis.set_major_locator(mticker.FixedLocator([100, 1000, 10000]))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v:,.0f}'))
    ax.yaxis.set_minor_locator(mticker.NullLocator())

    _finish(fig, ax)
    return fig


if __name__ == '__main__':
    first, last = df.iloc[0], df.iloc[-1]
    print(f'{first["date"].date()} ~ {last["date"].date()}  ({len(df)} rows)')
    for col, unit in (('treasury', 'B'), ('tvl', 'B'), ('mcap', 'T')):
        print(f'  {col:9s} ${first[col]:.3f}{unit} -> ${last[col]:.2f}{unit}'
              f'  ({last[col] / first[col]:.1f}x)')

    for name, fn in (('safe_vs_speculative_dual', draw_dual),
                     ('safe_vs_speculative_indexed', draw_indexed)):
        fig = fn()
        png, svg = save_chart(fig, name, output_dir=OUTPUT_DIR)
        print(f'  -> {png}')
        plt.close(fig)
