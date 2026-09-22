"""
Build real-data CSV: DeFi total TVL (DefiLlama) vs STRC Market Cap (strc.live).

STRC market cap = shares_outstanding(t) * price(t).
  - price: STRC daily close history     -> strc.live /api/ticker-data?full=true
  - shares outstanding: IPO shares + cumulative ATM shares sold (weekly 8-K)
                                          -> strc.live /api/sec-filings
TVL: DefiLlama total historical chain TVL -> api.llama.fi/v2/historicalChainTvl

Outputs: outputs/data/tvl_vs_strc_mcap.csv  (date, tvl_b, strc_mcap_b)
"""
import json
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

RAW = Path('outputs/data/raw')
RAW.mkdir(parents=True, exist_ok=True)

IPO_SHARES = 28_010_000          # strc.live: IPO Shares 28.01M
START = datetime(2025, 8, 1)
END = datetime(2026, 6, 5)


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


# --- 1. DefiLlama total TVL ---
tvl_raw = get('https://api.llama.fi/v2/historicalChainTvl')
(RAW / 'defillama_historical_tvl.json').write_text(json.dumps(tvl_raw))
tvl_by_day = {}
for p in tvl_raw:
    d = datetime.utcfromtimestamp(p['date']).date()
    tvl_by_day[d] = p['tvl']

# --- 2. STRC price history ---
ticker = get('https://strc.live/api/ticker-data?full=true')
strc = ticker['tickers']['STRC']
price_by_day = {}
for h in strc['history']:
    d = datetime.fromisoformat(h['date'].replace('Z', '+00:00')).date()
    price_by_day[d] = h['close']
# latest close as the most recent point
lt = strc['latest']
price_by_day[datetime.fromisoformat(lt['date'].replace('Z', '+00:00')).date()] = lt['close']

# --- 3. STRC ATM share issuance (cumulative outstanding) ---
# Each weekly 8-K reports shares sold during periodStart..periodEnd. We accrue
# those shares evenly across the selling window (per day) so the cumulative
# outstanding curve ramps smoothly rather than stepping on the filing date.
sec = get('https://strc.live/api/sec-filings')
(RAW / 'strc_sec_filings.json').write_text(json.dumps(sec))
strc_filings = [f for f in sec['filings'] if f.get('ticker') == 'STRC']

daily_add = {}  # date -> shares issued that day
for f in strc_filings:
    sold = f.get('sharesSold') or 0
    if not sold:
        continue
    ps, pe = f.get('periodStart'), f.get('periodEnd')
    if ps and pe:
        d0 = datetime.strptime(ps, '%Y-%m-%d').date()
        d1 = datetime.strptime(pe, '%Y-%m-%d').date()
    else:  # fallback: 7-day window ending on filing date
        d1 = datetime.strptime(f['filedDate'], '%Y-%m-%d').date()
        d0 = d1 - timedelta(days=6)
    ndays = (d1 - d0).days + 1
    per = sold / ndays
    c = d0
    while c <= d1:
        daily_add[c] = daily_add.get(c, 0) + per
        c += timedelta(days=1)

total_atm = sum(f.get('sharesSold') or 0 for f in strc_filings)
print(f'IPO shares: {IPO_SHARES:,}  ATM total: {total_atm:,.0f}  '
      f'=> outstanding: {IPO_SHARES + total_atm:,.0f}')


def shares_outstanding(day):
    s = IPO_SHARES
    for d, add in daily_add.items():
        if d <= day:
            s += add
    return s


def ffill(by_day, day, lo=START.date()):
    """most recent value on or before `day`"""
    c = day
    while c >= lo:
        if c in by_day:
            return by_day[c]
        c -= timedelta(days=1)
    return None


# --- 4. Build daily CSV ---
rows = []
day = START
while day <= END:
    dd = day.date()
    tvl = ffill(tvl_by_day, dd)
    price = ffill(price_by_day, dd)
    if tvl is not None and price is not None:
        mcap = shares_outstanding(dd) * price
        rows.append((dd.isoformat(), tvl / 1e9, mcap / 1e9))
    day += timedelta(days=1)

out = Path('outputs/data/tvl_vs_strc_mcap.csv')
with out.open('w') as f:
    f.write('date,tvl_b,strc_mcap_b\n')
    for d, tvl_b, mcap_b in rows:
        f.write(f'{d},{tvl_b:.3f},{mcap_b:.4f}\n')

print(f'wrote {len(rows)} rows -> {out}')
print('first:', rows[0])
print('last :', rows[-1])
