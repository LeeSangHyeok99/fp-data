# E2. All three Q2 pre-IPO markets ran the same 100x funding step at conversion; risk limits were sized per name

Only the risk settings differ across the three markets: how much open interest the venue would carry, and how far it let the price travel from its own oracle in one move. Funding is identical on all three, and so is the contract, a cash-settled linear perpetual with 5x maximum leverage on isolated margin.

| Market | Company | OI cap | Initial reference | Discovery bound | Launch date (UTC) | Conversion date (UTC) | Funding multiplier, pre / post conversion |
|---|---|---|---|---|---|---|---|
| CBRS | Cerebras | $100M | $175 | ±25% | 2026-05-01 | 2026-05-14 | 0.005x / 0.5x |
| QNT | Quantinuum | $20M | $75 | ±25% | 2026-05-28 | 2026-06-04 | 0.005x / 0.5x |
| SPCX | SpaceX | $150M | $150 | ±20% | 2026-05-17 | 2026-06-12 | 0.005x / 0.5x |

Data as of 2026-07-24, parameters as configured at launch, all dates UTC | Source: Trade[XYZ] pre-IPO perpetuals documentation (docs.trade.xyz); Nasdaq tape for the listing dates.
