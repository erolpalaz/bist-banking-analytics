# Initial Findings

This document summarizes the first results of the BIST Banking Analytics project.

## Dataset

The project uses weekly historical market data for selected BIST banking stocks and BIST 100 benchmark index. The initial analysis period starts from 2018.

Analyzed banking stocks:

- AKBNK.IS
- GARAN.IS
- HALKB.IS
- ISCTR.IS
- VAKBN.IS
- YKBNK.IS

Benchmark:

- XU100.IS

## First Risk-Return Findings

Based on weekly historical data, GARAN.IS stands out with the highest annualized return and the highest Sharpe ratio among the selected banking stocks.

VAKBN.IS has the highest annualized volatility and the highest risk score, indicating a more volatile historical risk profile.

AKBNK.IS has the highest beta against BIST 100, suggesting that it has shown the strongest sensitivity to broad market movements within the selected banking stock universe.

HALKB.IS shows one of the weakest performance profiles based on the current scoring framework.

## Risk Scoring Interpretation

The first version of the risk scoring system uses:

- Annualized volatility
- Absolute maximum drawdown
- Beta against BIST 100

Higher risk score indicates higher historical market risk.

The performance score uses:

- Annualized return
- Sharpe ratio
- Drawdown resilience

Higher performance score indicates a stronger historical risk-adjusted profile.

## Important Note

These results are based on historical data and are intended for educational and analytical purposes only. They should not be interpreted as investment advice.