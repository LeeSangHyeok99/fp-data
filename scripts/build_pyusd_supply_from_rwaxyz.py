"""
Build PYUSD monthly supply CSV from rwa.xyz CSV export.
Replaces the DefiLlama-based aggregation.
"""
import pandas as pd

src = '/Users/ijaheun/Desktop/rwa-xyz-stablecoins-market-caps.csv'
df = pd.read_csv(src)
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values('Date').reset_index(drop=True)
for c in ['Ethereum', 'Solana', 'Stellar', 'Arbitrum']:
    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

# Daily output
daily = df[['Date', 'Ethereum', 'Solana', 'Arbitrum', 'Stellar']].copy()
daily['Total'] = daily[['Ethereum', 'Solana', 'Arbitrum', 'Stellar']].sum(axis=1)
daily.rename(columns={'Date': 'date'}, inplace=True)
daily.to_csv('/Users/ijaheun/Desktop/Project/data/outputs/data/pyusd_supply_by_chain_daily.csv', index=False)

# Monthly: last day of each month
monthly = df.set_index('Date').resample('ME').last().reset_index()
monthly['period'] = monthly['Date'].dt.strftime('%Y-%m')
monthly = monthly[['period', 'Ethereum', 'Solana', 'Arbitrum', 'Stellar']]
monthly['Total'] = monthly[['Ethereum', 'Solana', 'Arbitrum', 'Stellar']].sum(axis=1)
monthly.to_csv('/Users/ijaheun/Desktop/Project/data/outputs/data/pyusd_supply_by_chain_monthly.csv', index=False)

print('Daily rows:', len(daily))
print('Monthly rows:', len(monthly))
print()
print('Latest 6 months:')
print(monthly.tail(6).to_string(index=False))
