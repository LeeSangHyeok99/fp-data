"""Daily xyz liquidation notional from the ASXN HIP-3 API.

The API sits behind a challenge, so the request is made from a browser page on
hyperscreener.asxn.xyz, which holds the clearance cookie.

Output: outputs/data/tradexyz_daily_liquidations_q2.csv (date, liquidated_usd)
"""
import csv
from playwright.sync_api import sync_playwright

START, END = '2026-04-01T00:00:00', '2026-07-01T00:00:00'
URL = ('https://api-hyperliquid.asxn.xyz/api/meta/hip3/liquidations-chart'
       f'?timeframe=all&dex=xyz&start_time={START}&end_time={END}')
OUT = 'outputs/data/tradexyz_daily_liquidations_q2.csv'

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://hyperscreener.asxn.xyz/home', wait_until='domcontentloaded')
    data = page.evaluate(
        """async (url) => (await (await fetch(url, {credentials: 'include'})).json())""",
        URL)
    browser.close()

rows = [(d['date'], (d.get('dex_volumes') or {}).get('xyz', 0))
        for d in data['chart_data']]
with open(OUT, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['date', 'liquidated_usd'])
    w.writerows(rows)
print(len(rows), 'rows ->', OUT)
