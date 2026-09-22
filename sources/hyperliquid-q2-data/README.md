# Hyperliquid Q2 2026 Data Archive

Raw-data archive backing the HRC 2Q26 quarterly report. Captured 2026-07-16 (KST) via
network-level interception — every file is the byte-for-byte JSON the sites' own APIs
served; nothing was re-typed or transformed. Integrity: every manifest entry carries
`sha256`, `bytes`, `url`, and `fetched_at_utc`.

## Layout

```
asxn/                    hyperscreener.asxn.xyz (ASXN Hyperliquid dashboard)
  raw/                   401 JSON files, ~260 MB
  manifest.json          404 entries: url, params, status, sha256, timestamp
  live_requests.json     every request the site made during page visits (per route)
hleco/                   hl.eco (House of all Hyperliquid)
  raw/                   71 JSON files, ~23 MB (REST endpoints + third-party sources)
  streams/               22 SSE feeds, raw frames (captured 2026-07-16 via real-browser
                         session after Turnstile auth; base64+MessagePack inside SSE)
  streams_decoded/       the same 22 feeds decoded to plain JSON (0 decode errors)
  manifest.json          entries for raw + decoded, same schema
  live_requests.json     per-route request log
  feeds.json             the 22 SSE feed names hl.eco serves
```

## What's inside (ASXN) — the report-critical series

- `INCOME_STATEMENT__daily/monthly` — full income statement since 2025-08-17 with
  ASXN's methodology notes embedded (perp/spot/HIP-3 fees, HyperEVM gas, builder fees,
  auction proceeds, priority fees, HLP cost, net income).
- `HL_BUYBACKS`, `ASSISTANCE_FUND_HOLDINGS`, `AF_BUYBACK_METRICS`, `BUYBACK_REVENUES`,
  `REVENUE_METRICS`, `AVERAGE_DAILY_BURN`, `HYPE_PRICE` — complete AF/buyback history
  (daily since 2025-03; all-time revenue $1.0223B at capture).
- `PRIORITY_FEES_DAILY__all_1d` + summary/by-coin/by-wallet — daily since launch
  2026-04-13, split order (write) vs gossip (read).
- `HIP3_*` — daily volume/OI/liquidations/traders/trades/funding, by-asset, by-deployer
  pies, categories (current + historical), percentage-of-total (volume and OI bases).
- `OUTCOME_*` (HIP-4) — aggregate metrics/daily series, by-question and by-outcome
  aggregates, plus per-market timeseries for all 50 question markets.
- `TREASURY_*` — DAT holdings/transactions/m-NAV/HYPE-per-share; ETF list, holdings,
  flows, price, volume (all 9 tracked ETPs).
- `BUILDER_*` — all-time metrics, table, volume/fees/users charts (site maximum = 90d
  granular + all-time stacked).
- `HYPER_EVM_*` — fees, token metrics, DEX volumes (by asset/type), stablecoin supply
  chart+table, transfer/DEX volume, liquid staking (holders/supply/ratio), gas spenders.
- CEX comparison (`FUTURE_/SPOT_/OPEN_INTEREST_*`), cloudfront full-history series
  (volume, OI, users, inflows, liquidations, trades, HLP PnL), staking/validators
  (metrics, largest stakers, unstaking queue, emissions, jailing, proposal share),
  network (block times, TPS, tx/op types), auctions (HL auctions, analytics, period
  analysis, revenue proportion), liquidations (node summary/daily/symbols), risk
  metrics, vaults + leaderboard (stats-data.hyperliquid.xyz), spot ecosystem, DEX
  metrics, DAU, market data.
- `LIVE__*` / `LIVEPOST__*` — exact replays of every additional call the pages made
  live, including official `api.hyperliquid.xyz /info` POSTs (meta, contexts, candles).

## What's inside (hl.eco)

- `api.hl.eco__api_hypedexer_fills_aggregated__…` — AF daily buyback fills from TGE
  window (independent source; cross-validates ASXN, see Verification).
- `purr-stock`, `hyperion-stock`, `spcx-stock` — PURR/HYPD candles + SpaceX market data.
- `ht/*` — HYPE cohort analytics (Fish→Whale segments), top positions, stop/TP books.
- `search/index`, `search/concepts` — hl.eco's own catalog of every tab/chart entity.
- `projects` — the 244-project ecosystem directory.
- Third-party sources the site aggregates, replayed raw: DeFiLlama protocol TVLs +
  Hyperliquid stablecoin chart, coins.llama price charts, CoinGecko (Kinetiq,
  HyperLend), Binance BTC depth, Kinetiq buyback fills (rpc.km.xyz), HyperLend API,
  Project X subgraph (Goldsky), Sevenseas vault stats, Nest APIs, on-chain eth_call
  supply reads (LST totalSupply), official HL /info POSTs.

```
external/                Public-source gap fillers (added after coverage audit)
  raw/                   DeFiLlama: HL spot-orderbook volume (full history), daily
                         fees/revenue/holders-revenue, HyperEVM chain TVL; BTC daily
                         price 990d + HYPE daily price 594d (coins.llama, chunked);
                         HIP-4 daily merged May 3 2026 → capture (in asxn/raw)
  manifest.json          same schema
```

## QoQ / YoY coverage (audited 2026-07-16)

Series depth confirmed by reading every key file's date range:

- Back to Jun 2023 (full YoY+): perp volume, OI, DAU, inflows, new users, trades,
  liquidations, HLP PnL (cloudfront); CEX futures-volume share (Aug 2023); TVL.
- Back to Oct–Dec 2024: income statement (gross fees / revenue / holders_revenue /
  earnings, monthly+daily), staking metrics, emissions, HYPE price (TGE via hl.eco
  candles + coins.llama).
- Back to Feb–Jun 2025: all HyperEVM series (chain launch Feb 18 2025), AF buybacks
  daily (Mar 2025), DAT holdings/mNAV (Jun 2025).
- Structural (series as old as the feature): HIP-3 (Oct 2025), CEX OI-share (Oct 2025),
  priority fees (Apr 13 2026), HIP-4 (May 2026), ETFs (May 2026).
- Segment caveat: ASXN's perp/spot/HIP-3 fee split starts 2025-08-17; 2Q25 segment
  split must come from the HRC Annual Report's own income statement (standard
  prior-published-report comparative).

## Stream feeds (hl.eco, decoded highlights)

- `hype-etf-flows` — daily net flows / $ volume / units+NAV per fund (BHYP, HYPG,
  THYP) 2026-05-12 → 2026-07-15, cumulative net inflows $337.8M, 5.15M HYPE held,
  leveraged fund (TXXH) snapshot; source chain documented in-feed (issuer primaries,
  farside backup). SUPERSEDES ASXN's TREASURY_ETFS_FLOWS (which ended Jun 26).
- `real-inflation` — full net-supply model: emission vs burn per year, burn mechanism
  split (AF 45.86M HYPE ≈ $3.01B ≈ 97.4% of all burn), staked, reserve runway,
  buyback VWAP, scenarios. Feeds the report's Supply & Float section directly.
- `hl-revenue` / `hl-revenue-grains` / `fees` / `burns` — hl.eco's revenue stack
  (gross fees, HIP-3 by dex, deployer shares, builder fees).
- `hip3-history` / `hip3-oi-history` / `hip3-overview` / `hip3-auction` /
  `hip3-stats` — HIP-3 daily volume/OI by deployer + auction history.
- `hip4-growth`, `pf-history`/`pf-markets-history`/`pf-wallets` (priority fees),
  `spot-auctions`, `tt-users`, `twaps`, `hype-holders`, `hypedexer-*`,
  `gossip-priority`.

## Items that must be refreshed/added manually at writing time

1. Team unlock claims vs entitlement — Jae will provide the exact data
   (Unlocks.app + Discord announcements basis, as in 1Q26 report).
2. All point-in-time snapshots (market data, cohorts, depth) — re-capture at quarter
   -close basis if quoted as of Jun 30. ETF flows now covered through Jul 15 via
   the hype-etf-flows feed; re-pull near publication for the final days.

## Verification (2026-07-16)

Automated pass (`verify_archive.py`, kept in session scratchpad; report below):

1. Income statement June total revenue matches page render ($70.92M) — PASS
2. ETF holdings BHYP 2.10M / THYP 416.8K HYPE match page render — PASS
3. kHYPE supply 16.71M matches page render — PASS
4. Stablecoin table USDC $5.73B / USDH $20.8M matches page render — PASS
5. CEX comparison HL OI $11.14B matches page render — PASS
6. PURR holdings 17.6M HYPE matches page render — PASS
7. Cross-source AF buybacks, ASXN vs hl.eco independent fills: 297/307 overlapping
   days within 5% notional; Q2 2026 totals $141.11M vs $139.56M (1.1% apart) — PASS
   ⚠ Note: press claims of "$283M Q2 buybacks" (Crypto Briefing, Jul 3) do NOT match
   either primary source. Use the primary series.

## Known gaps / caveats

- ~~hl.eco SSE streams pending~~ RESOLVED 2026-07-16: all 22 feeds captured through
  the user's real Chrome session (Turnstile-authed) and decoded to JSON with zero
  errors. See `streams/` (raw SSE) + `streams_decoded/`.
- ASXN manifest not-ok entries are documented probes, not data gaps: legacy/dead
  constants that no live page calls (staking-data, validator-summaries, consensus-*,
  token-distribution, top-100-depositors, largest-user-deposits, liquidations/
  time-series), parameter-validation rejects (builder days>90 — site max is 90d;
  DAU days>365; income-statement weekly granularity unsupported), and the site's own
  /verify challenge POSTs. Live-page parity was confirmed per route via
  `live_requests.json`.
- Point-in-time tables (market-data/latest, cohorts, order books, depth) reflect the
  capture timestamp — treat as "as of 2026-07-16", not quarter-end.
- ASXN income-statement series starts 2025-08-17 (their fees_start_date) and uses
  gross-fee methodology; it is NOT the same series as "holder revenue" used in the
  1Q26 HRC report. Bridge the two explicitly before printing either.
- Per-wallet lookup tools (ASXN /profile, hl.eco /explorer, /mlm) and per-token spot
  holder drill-downs are interactive lookups, not dashboard series; out of scope.
