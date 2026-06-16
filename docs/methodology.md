# Methodology

## Frequency Choice

The project starts with weekly data because daily data can be noisy and macroeconomic variables are not always available at daily frequency.

## Return Calculation

Simple returns are calculated as:

```text
Return_t = Price_t / Price_{t-1} - 1
```

## Risk Metrics

Main risk metrics:

- Volatility
- Maximum drawdown
- Beta against BIST 100
- Sharpe ratio

## Risk Score

The first version of the risk score uses:

| Component | Weight |
|---|---:|
| Annualized volatility | 40% |
| Absolute maximum drawdown | 35% |
| Absolute beta | 25% |

Higher score means higher historical risk.

## Performance Score

The first version of the performance score uses:

| Component | Weight |
|---|---:|
| Annualized return | 40% |
| Sharpe ratio | 40% |
| Drawdown resilience | 20% |

Higher score means stronger historical risk-adjusted profile.

## Important Limitation

This scoring system is not investment advice. It is a transparent analytical framework for comparing historical risk and performance.

## Current Scoring Framework

The current scoring framework is intentionally transparent and rule-based.

### Risk Score

The risk score is calculated using:

| Component | Weight |
|---|---:|
| Annualized volatility | 40% |
| Absolute maximum drawdown | 35% |
| Absolute beta to BIST 100 | 25% |

Higher risk score means higher historical risk.

### Performance Score

The performance score is calculated using:

| Component | Weight |
|---|---:|
| Annualized return | 40% |
| Sharpe ratio | 40% |
| Drawdown resilience | 20% |

Higher performance score means stronger historical risk-adjusted performance.

## Why Weekly Frequency?

Weekly frequency is preferred in the first version because:

- Daily financial data can be noisy.
- Weekly data better supports medium-term risk analysis.
- It will be easier to merge with macroeconomic variables in later phases.
- It reduces short-term market microstructure noise.

## Main Limitations

The current version has several limitations:

1. It only uses historical price data.
2. It does not yet include macroeconomic variables.
3. It does not yet include KAP disclosures or financial statement data.
4. The scoring system is rule-based and should be interpreted as an analytical comparison tool.
5. The project does not provide investment advice.

## Macro Sensitivity Methodology

The macroeconomic dataset includes USD/TRY, EUR/TRY, CPI index and CBRT weighted average funding cost variables obtained from TCMB EVDS.

All variables are aligned to weekly frequency in order to match weekly stock returns. Exchange rates and the weighted average funding cost are converted to weekly observations using the last available value of each week. CPI is a monthly variable and is forward-filled to weekly frequency because the most recently announced CPI value remains the latest available inflation information until the next monthly release.

The macro sensitivity analysis is divided into separate model specifications:

1. Core USD Model: USD/TRY weekly change and CPI year-over-year change.
2. Core EUR Model: EUR/TRY weekly change and CPI year-over-year change.
3. Funding Cost Level Model: USD/TRY weekly change, CPI year-over-year change and CBRT weighted average funding cost level.
4. Funding Cost Change Model: USD/TRY weekly change, CPI year-over-year change and weekly change in CBRT weighted average funding cost.

The CBRT weighted average funding cost is not the official one-week repo policy rate. It is used as an operational monetary policy and funding condition indicator. Therefore, its level is interpreted as the prevailing funding cost environment, while its weekly difference is interpreted as short-term changes in funding conditions.

The results should be interpreted as statistical association and macro sensitivity, not as causal evidence.


