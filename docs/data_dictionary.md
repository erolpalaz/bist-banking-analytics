# Data Dictionary

## Market Data

| Column | Description |
|---|---|
| Date | Observation date |
| Ticker | Stock or index symbol |
| Open | Opening price |
| High | Highest price |
| Low | Lowest price |
| Close | Closing price |
| Adj_Close | Adjusted closing price |
| Volume | Trading volume |
| daily_return | Daily percentage return |
| weekly_return | Weekly percentage return |

## Risk Metrics

| Metric | Description |
|---|---|
| mean_weekly_return | Average weekly return |
| annualized_return | Mean weekly return multiplied by 52 |
| weekly_volatility | Standard deviation of weekly returns |
| annualized_volatility | Weekly volatility annualized by sqrt(52) |
| max_drawdown | Largest historical peak-to-trough decline |
| beta_to_bist100 | Sensitivity to BIST 100 weekly returns |
| sharpe_ratio | Annualized risk-adjusted return metric |
