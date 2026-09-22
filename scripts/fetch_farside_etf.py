"""
Scrape Farside BTC Spot ETF daily flows.
URL: https://farside.co.uk/bitcoin-etf-flow-all-data/
Output: outputs/data/farside_btc_etf_flow.csv
"""
from pathlib import Path
from io import StringIO
from playwright.sync_api import sync_playwright
import pandas as pd
import re

OUT = Path('outputs/data/farside_btc_etf_flow.csv')


def parse_value(s):
    if s is None:
        return None
    s = str(s).strip()
    if s in ('', '-', '—', '–'):
        return 0.0
    neg = False
    if s.startswith('(') and s.endswith(')'):
        neg = True
        s = s[1:-1]
    s = s.replace(',', '').replace('$', '').strip()
    try:
        v = float(s)
    except ValueError:
        return None
    return -v if neg else v


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0)')
        page = ctx.new_page()
        page.goto('https://farside.co.uk/bitcoin-etf-flow-all-data/', wait_until='domcontentloaded', timeout=60000)
        page.wait_for_selector('table', timeout=30000)

        # Pull the first data table
        tables = page.locator('table').all()
        target = None
        for t in tables:
            text = t.inner_text()
            if 'IBIT' in text and 'Date' in text:
                target = t
                break
        if not target:
            raise SystemExit('No Farside ETF table found')

        html = target.evaluate('el => el.outerHTML')
        browser.close()

    dfs = pd.read_html(StringIO(html))
    df = dfs[0]
    # Sometimes multiindex headers — flatten
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[-1] if isinstance(c, tuple) else c for c in df.columns]
    # Drop trailing summary rows
    df = df[df['Date'].astype(str).str.match(r'\d{1,2} \w+ \d{4}', na=False) | df['Date'].astype(str).str.match(r'\d{4}-\d{2}-\d{2}', na=False)]
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    # Convert all non-Date columns
    for col in df.columns:
        if col != 'Date':
            df[col] = df[col].map(parse_value)
    df = df.sort_values('Date').reset_index(drop=True)
    df.to_csv(OUT, index=False)
    print(f'  wrote {len(df)} rows to {OUT}')
    print(df.tail(3).to_string())


if __name__ == '__main__':
    main()
