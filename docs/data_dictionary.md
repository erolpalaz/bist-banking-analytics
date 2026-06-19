# Data Dictionary

This document explains the main datasets, variables and output files used in the BIST Banking Analytics project.

The project uses weekly stock market data, TCMB EVDS macroeconomic data, risk metrics, scoring outputs, macro sensitivity model results, model diagnostics, robust regression outputs and rolling macro sensitivity outputs.

## 1. Raw Stock Price Data

File:

```text
data/raw/stock_prices_raw.csv
```

Description:

This file contains raw historical market data downloaded from Yahoo Finance using the `yfinance` package.

| Column | Description |
|---|---|
| Date | Trading date |
| Ticker | Stock or benchmark ticker |
| Open | Opening price |
| High | Highest price during the trading period |
| Low | Lowest price during the trading period |
| Close | Closing price |
| Adj_Close | Adjusted closing price |
| Volume | Trading volume |

Tickers used:

| Ticker | Description |
|---|---|
| AKBNK.IS | Akbank |
| GARAN.IS | Garanti BBVA |
| HALKB.IS | Halkbank |
| ISCTR.IS | İş Bankası C |
| VAKBN.IS | VakıfBank |
| YKBNK.IS | Yapı Kredi Bankası |
| XU100.IS | BIST 100 benchmark index |

## 2. Processed Weekly Stock Data

File:

```text
data/processed/stock_prices_weekly.csv
```

Description:

This file contains stock market data converted to weekly frequency.

| Column | Description |
|---|---|
| Date | Weekly date, aligned to week ending |
| Ticker | Stock or benchmark ticker |
| Open | First available opening price of the week |
| High | Highest price of the week |
| Low | Lowest price of the week |
| Close | Last available closing price of the week |
| Adj_Close | Last available adjusted closing price of the week |
| Volume | Total weekly trading volume |
| weekly_return | Weekly return calculated from adjusted close or close price |

Notes:

- Weekly return is calculated from weekly price changes.
- The first weekly return observation for each ticker is missing because there is no previous week for comparison.

## 3. Raw Macroeconomic Data

File:

```text
data/raw/macro_raw.csv
```

Description:

This file contains raw macroeconomic data downloaded from TCMB EVDS in long format.

| Column | Description |
|---|---|
| Date | Observation date |
| variable | Internal variable name used in the project |
| value | Observed macroeconomic value |
| series_code | TCMB EVDS series code |

Macro variables:

| Variable | EVDS Series Code | Description |
|---|---|---|
| usd_try | TP.DK.USD.A.YTL | USD/TRY buying exchange rate |
| eur_try | TP.DK.EUR.A.YTL | EUR/TRY buying exchange rate |
| cpi_index | TP.FE.OKTG01 | Consumer Price Index |
| funding_cost | TP.APIFON4 | CBRT weighted average funding cost |

Important note:

`funding_cost` represents the CBRT weighted average funding cost. It should not be interpreted as the official one-week repo policy rate.

## 4. Weekly Macroeconomic Data

File:

```text
data/processed/macro_weekly.csv
```

Description:

This file contains macroeconomic variables converted to weekly frequency.

| Column | Description |
|---|---|
| Date | Weekly date |
| usd_try | Weekly USD/TRY value using the last available value of the week |
| eur_try | Weekly EUR/TRY value using the last available value of the week |
| cpi_index | CPI index aligned to weekly frequency |
| funding_cost | Weekly CBRT weighted average funding cost |
| usd_try_weekly_change | Weekly percentage change in USD/TRY |
| eur_try_weekly_change | Weekly percentage change in EUR/TRY |
| funding_cost_weekly_diff | Weekly difference in CBRT weighted average funding cost |
| cpi_index_weekly_change | Weekly percentage change in CPI index after weekly alignment |
| cpi_index_yoy_change | Year-over-year percentage change in CPI index |

Notes:

- Exchange rates and funding cost are converted to weekly frequency using the last available value of each week.
- CPI is originally monthly and is forward-filled to weekly frequency.
- `cpi_index_yoy_change` requires 52 weeks of lagged data, so the first 52 weekly observations are missing.
- Weekly change variables have missing values in the first week after transformation.

## 5. Merged Stock-Macro Dataset

File:

```text
data/processed/stock_macro_weekly.csv
```

Description:

This is the main panel dataset used for macro sensitivity analysis. It combines weekly stock market data with weekly macroeconomic indicators.

| Column | Description |
|---|---|
| Date | Weekly date |
| Ticker | Stock or benchmark ticker |
| Open | Weekly opening price |
| High | Weekly high price |
| Low | Weekly low price |
| Close | Weekly closing price |
| Adj_Close | Weekly adjusted closing price |
| Volume | Weekly trading volume |
| weekly_return | Weekly stock return |
| usd_try | Weekly USD/TRY value |
| eur_try | Weekly EUR/TRY value |
| cpi_index | Weekly aligned CPI index |
| funding_cost | Weekly CBRT weighted average funding cost |
| usd_try_weekly_change | Weekly percentage change in USD/TRY |
| eur_try_weekly_change | Weekly percentage change in EUR/TRY |
| funding_cost_weekly_diff | Weekly difference in CBRT weighted average funding cost |
| cpi_index_weekly_change | Weekly percentage change in CPI index |
| cpi_index_yoy_change | Year-over-year percentage change in CPI index |

## 6. Risk Metrics Output

File:

```text
outputs/risk_metrics.csv
```

Description:

This file contains risk and performance metrics calculated for each ticker.

| Column | Description |
|---|---|
| Ticker | Stock or benchmark ticker |
| mean_weekly_return | Average weekly return |
| annualized_return | Annualized return calculated from weekly returns |
| weekly_volatility | Standard deviation of weekly returns |
| annualized_volatility | Annualized volatility calculated from weekly volatility |
| max_drawdown | Maximum historical drawdown |
| sharpe_ratio | Risk-adjusted return measure |
| observations | Number of weekly return observations |

Notes:

- Beta-related metrics may be added in later versions.
- If beta is not available, the dashboard continues without the beta chart.

## 7. Risk Scores Output

File:

```text
outputs/risk_scores.csv
```

Description:

This file contains comparative risk and performance scores for the selected banking stocks.

| Column | Description |
|---|---|
| Ticker | Banking stock ticker |
| risk_score | Composite risk score |
| performance_score | Composite performance score |
| risk_category | Risk classification if available |
| annualized_return | Annualized return used in scoring |
| annualized_volatility | Annualized volatility used in scoring |
| max_drawdown | Maximum drawdown used in scoring |
| sharpe_ratio | Sharpe ratio used in scoring |

Notes:

- The exact score components depend on the scoring methodology implemented in `src/scoring.py`.
- Higher risk scores indicate relatively higher risk.
- Higher performance scores indicate relatively stronger return and risk-adjusted performance.

## 8. Macro Correlation Output

File:

```text
outputs/macro_correlation_all_variables.csv
```

Description:

This file contains correlation results between weekly stock returns and macroeconomic variables.

| Column | Description |
|---|---|
| Ticker | Stock or benchmark ticker |
| macro_variable | Macroeconomic variable used in the correlation calculation |
| correlation | Pearson correlation between weekly return and macro variable |
| observations | Number of observations used in the calculation |

Macro variables included:

| Variable | Description |
|---|---|
| usd_try_weekly_change | Weekly percentage change in USD/TRY |
| eur_try_weekly_change | Weekly percentage change in EUR/TRY |
| cpi_index_weekly_change | Weekly percentage change in CPI index |
| cpi_index_yoy_change | CPI year-over-year change |
| funding_cost | CBRT weighted average funding cost level |
| funding_cost_weekly_diff | Weekly difference in CBRT weighted average funding cost |

Interpretation:

- Positive correlation indicates that the stock return and macro variable tended to move in the same direction.
- Negative correlation indicates that the stock return and macro variable tended to move in opposite directions.
- Correlation does not imply causality.

## 9. Macro Model Summary Output

File:

```text
outputs/macro_model_summary.csv
```

Description:

This file summarizes the macro sensitivity regression model specifications.

| Column | Description |
|---|---|
| model_name | Name of the regression model |
| description | Short explanation of the model |
| features | Independent variables used in the model |
| dependent_variable | Dependent variable of the model |
| interpretation_note | General interpretation warning |

Model specifications:

| Model | Description |
|---|---|
| core_usd_model | Uses USD/TRY weekly change and CPI YoY change |
| core_eur_model | Uses EUR/TRY weekly change and CPI YoY change |
| funding_cost_level_model | Uses USD/TRY weekly change, CPI YoY change and funding cost level |
| funding_cost_change_model | Uses USD/TRY weekly change, CPI YoY change and weekly funding cost change |

## 10. Funding Cost Change Summary

File:

```text
outputs/funding_cost_change_summary.csv
```

Description:

This file summarizes how often the CBRT weighted average funding cost changes in the weekly dataset.

| Column | Description |
|---|---|
| total_weeks | Total number of weekly observations |
| funding_cost_change_weeks | Number of weeks with a funding cost change |
| no_change_weeks | Number of weeks without a funding cost change |
| funding_cost_change_week_ratio | Ratio of weeks with funding cost changes |
| interpretation | Interpretation note for the funding cost variable |

Important note:

The funding cost variable is an operational monetary/funding condition indicator, not the official one-week repo policy rate.

## 11. Macro Regression Outputs

Files:

```text
outputs/macro_regression_core_usd_model.csv
outputs/macro_regression_core_eur_model.csv
outputs/macro_regression_funding_cost_level_model.csv
outputs/macro_regression_funding_cost_change_model.csv
```

Description:

These files contain OLS regression results for each banking stock.

Common columns:

| Column | Description |
|---|---|
| model_name | Regression model name |
| Ticker | Banking stock ticker |
| status | Regression status |
| observations | Number of observations used |
| r_squared | R-squared value |
| adj_r_squared | Adjusted R-squared value |
| f_pvalue | F-test p-value of the regression model |
| const_coef | Constant term coefficient |
| const_pvalue | Constant term p-value |

Variable-specific columns:

| Column Type | Description |
|---|---|
| variable_coef | Estimated regression coefficient for the variable |
| variable_pvalue | P-value of the estimated coefficient |

Example variable columns:

| Column | Description |
|---|---|
| usd_try_weekly_change_coef | Coefficient of USD/TRY weekly change |
| usd_try_weekly_change_pvalue | P-value of USD/TRY weekly change coefficient |
| eur_try_weekly_change_coef | Coefficient of EUR/TRY weekly change |
| eur_try_weekly_change_pvalue | P-value of EUR/TRY weekly change coefficient |
| cpi_index_yoy_change_coef | Coefficient of CPI YoY change |
| cpi_index_yoy_change_pvalue | P-value of CPI YoY change coefficient |
| funding_cost_coef | Coefficient of funding cost level |
| funding_cost_pvalue | P-value of funding cost level coefficient |
| funding_cost_weekly_diff_coef | Coefficient of weekly funding cost change |
| funding_cost_weekly_diff_pvalue | P-value of weekly funding cost change coefficient |

Interpretation:

- A negative coefficient indicates a negative statistical relationship with weekly stock returns.
- A positive coefficient indicates a positive statistical relationship with weekly stock returns.
- A lower p-value indicates stronger statistical evidence for the coefficient.
- Regression results should be interpreted as association and sensitivity, not causality.

## 12. Model Diagnostics Output

File:

```text
outputs/macro_model_diagnostics.csv
```

Description:

This file contains diagnostic test results for each macro sensitivity model and banking stock.

| Column | Description |
|---|---|
| model_name | Name of the macro sensitivity model |
| Ticker | Banking stock ticker |
| status | Model diagnostic status |
| observations | Number of observations used |
| r_squared | R-squared value |
| adj_r_squared | Adjusted R-squared value |
| f_pvalue | F-test p-value |
| f_test_interpretation | Interpretation of model-level statistical significance |
| durbin_watson | Durbin-Watson statistic |
| durbin_watson_interpretation | Residual autocorrelation interpretation |
| breusch_pagan_pvalue | Breusch-Pagan test p-value |
| breusch_pagan_interpretation | Heteroskedasticity interpretation |
| jarque_bera_pvalue | Jarque-Bera test p-value |
| jarque_bera_interpretation | Residual normality interpretation |
| residual_skewness | Skewness of model residuals |
| residual_kurtosis | Kurtosis of model residuals |
| max_vif | Maximum VIF value in the model |
| mean_vif | Average VIF value in the model |
| diagnostic_warnings | Compact warning list based on diagnostic results |

## 13. VIF Output

File:

```text
outputs/macro_vif_results.csv
```

Description:

This file contains Variance Inflation Factor results for macro regression explanatory variables.

| Column | Description |
|---|---|
| model_name | Name of the macro sensitivity model |
| Ticker | Banking stock ticker |
| variable | Explanatory variable |
| vif | Variance Inflation Factor value |
| status | VIF interpretation status |

Interpretation:

| VIF Range | Interpretation |
|---|---|
| Below 5 | Generally acceptable |
| 5 to 10 | Possible moderate multicollinearity |
| Above 10 | Possible strong multicollinearity |

## 14. Robust Macro Regression Outputs

Files:

```text
outputs/robust_macro_regression_core_usd_model.csv
outputs/robust_macro_regression_core_eur_model.csv
outputs/robust_macro_regression_funding_cost_level_model.csv
outputs/robust_macro_regression_funding_cost_change_model.csv
outputs/robust_macro_regression_all_models.csv
outputs/robust_macro_regression_summary.csv
```

Description:

These files contain macro sensitivity regression results estimated with HC3 robust standard errors.

The coefficient estimates are based on OLS, but the standard errors, t-statistics, p-values and confidence intervals are adjusted for heteroskedasticity concerns.

Common columns:

| Column | Description |
|---|---|
| model_name | Name of the macro sensitivity model |
| Ticker | Banking stock ticker |
| status | Regression status |
| observations | Number of observations used |
| robust_cov_type | Robust covariance estimator type |
| r_squared | R-squared value from the OLS model |
| adj_r_squared | Adjusted R-squared value from the OLS model |
| ols_f_pvalue | Original OLS F-test p-value |

Variable-specific columns:

| Column Type | Description |
|---|---|
| variable_coef | Estimated coefficient |
| variable_robust_std_error | HC3 robust standard error |
| variable_robust_tvalue | Robust t-statistic |
| variable_robust_pvalue | Robust p-value |
| variable_robust_ci_lower | Lower bound of robust confidence interval |
| variable_robust_ci_upper | Upper bound of robust confidence interval |

The summary file includes:

| Column | Description |
|---|---|
| significant_5pct_variables | Variables significant at the 5% level using robust p-values |
| significant_10pct_variables | Variables significant at the 10% level using robust p-values |
| strongest_variable_by_abs_tvalue | Variable with the highest absolute robust t-statistic |

## 15. Rolling Macro Correlation Outputs

Files:

```text
outputs/rolling_macro_correlation.csv
outputs/rolling_macro_correlation_summary.csv
```

Description:

These files contain 52-week rolling correlation results between weekly banking stock returns and selected macroeconomic variables.

### rolling_macro_correlation.csv

| Column | Description |
|---|---|
| Date | Rolling correlation date |
| Ticker | Banking stock ticker |
| macro_variable | Macroeconomic variable used in the rolling correlation |
| rolling_window | Rolling window length |
| rolling_correlation | Rolling correlation between weekly return and macro variable |

### rolling_macro_correlation_summary.csv

| Column | Description |
|---|---|
| Ticker | Banking stock ticker |
| macro_variable | Macroeconomic variable |
| observations | Number of rolling correlation observations |
| mean_rolling_correlation | Average rolling correlation |
| median_rolling_correlation | Median rolling correlation |
| min_rolling_correlation | Minimum rolling correlation |
| max_rolling_correlation | Maximum rolling correlation |
| latest_date | Latest rolling correlation date |
| latest_rolling_correlation | Most recent rolling correlation value |
| positive_correlation_share | Share of rolling correlations greater than zero |
| relationship_stability | Relationship stability classification |

Relationship stability classification:

| Classification | Description |
|---|---|
| mostly_positive | Relationship is positive in most rolling windows |
| mostly_negative | Relationship is negative in most rolling windows |
| unstable_or_time_varying | Relationship changes direction over time |

## 16. Dashboard Data Usage

Dashboard file:

```text
dashboard/app.py
```

The dashboard uses the following files:

| Dashboard Page | Required Files |
|---|---|
| Market Overview | `stock_prices_weekly.csv`, `risk_metrics.csv` |
| Stock Comparison | `stock_prices_weekly.csv` |
| Risk Metrics | `risk_metrics.csv` |
| Risk Scores | `risk_scores.csv` |
| Macro Sensitivity | macro correlation, model summary and regression output files |
| Model Diagnostics | `macro_model_diagnostics.csv`, `macro_vif_results.csv` |
| Robust Results | robust macro regression output files |
| Rolling Macro Sensitivity | `rolling_macro_correlation.csv`, `rolling_macro_correlation_summary.csv` |

## 17. Missing Value Notes

Expected missing values:

| Variable | Reason |
|---|---|
| weekly_return | First observation per ticker has no previous week |
| usd_try_weekly_change | First weekly macro observation has no previous week |
| eur_try_weekly_change | First weekly macro observation has no previous week |
| funding_cost_weekly_diff | First weekly macro observation has no previous week |
| cpi_index_weekly_change | First weekly macro observation has no previous week |
| cpi_index_yoy_change | Requires 52 weeks of lagged CPI data |
| rolling_correlation | First 52 rolling observations are unavailable by construction |

These missing values are expected and should not be interpreted as data errors.

## 18. General Interpretation Notes

This project is designed for educational, analytical and portfolio purposes.

Important interpretation rules:

- Correlation does not imply causality.
- Regression outputs show statistical association, not causal effects.
- Rolling correlation shows time-varying association, not causality.
- CPI is originally monthly and aligned to weekly frequency.
- Funding cost is not the official policy rate.
- The dashboard and model outputs should not be interpreted as investment advice.