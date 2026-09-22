"""
Scrape Farside HYPE ETF daily flows.
URL: https://farside.co.uk/hyp/
Output: outputs/data/farside_hype_etf_flow.csv
Columns: date, BHYP, THYP, total
"""
import re
from pathlib import Path
from playwright.sync_api import sync_playwright
import pandas as pd

OUT = Path('outputs/data/farside_hype_etf_flow.csv')


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
        browser = p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled'],
        )
        ctx = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15',
            viewport={'width': 1440, 'height': 900},
            locale='en-US',
        )
        page = ctx.new_page()
        page.goto('https://farside.co.uk/hyp/', wait_until='domcontentloaded', timeout=60000)
        # Wait for Cloudflare to clear and the data table (class="etf") to load
        html = None
        for _ in range(30):
            page.wait_for_timeout(2000)
            content = page.content()
            if '<table class="etf">' in content and 'THYP' in content and 'May 2026' in content:
                html = content
                break
        if html is None:
            raise SystemExit('Could not retrieve Farside HYPE ETF page')
        browser.close()

    # Extract the etf data table
    m = re.search(r'<table class="etf">.*?</table>', html, re.DOTALL)
    if not m:
        raise SystemExit('No etf table in fetched HTML')
    table_html = m.group(0)

    # Parse rows manually — header is multi-row so we hard-code column order
    rows = []
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL):
        cells = re.findall(r'<td[^>]*>(.*?)</td>', tr, re.DOTALL)
        if len(cells) != 4:
            continue
        # Strip HTML tags inside each cell
        texts = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
        date_str = texts[0]
        # Date format: "12 May 2026"
        try:
            d = pd.to_datetime(date_str, format='%d %b %Y')
        except Exception:
            continue
        bhyp = parse_value(texts[1])
        thyp = parse_value(texts[2])
        total = parse_value(texts[3])
        rows.append({'date': d, 'BHYP': bhyp, 'THYP': thyp, 'total': total})

    if not rows:
        raise SystemExit('No data rows parsed')

    df = pd.DataFrame(rows).sort_values('date').reset_index(drop=True)
    df.to_csv(OUT, index=False, date_format='%Y-%m-%d')
    print(f'  wrote {len(df)} rows to {OUT}')
    print(df.tail(10).to_string())


if __name__ == '__main__':
    main()
