# Initial Findings

This document summarizes the initial analytical findings of the BIST Banking Analytics project.

The findings are based on weekly market data, risk metrics, macroeconomic indicators from TCMB EVDS, macro sensitivity regressions, model diagnostics and robust inference outputs.

The results are exploratory and should not be interpreted as investment advice or causal evidence.

## 1. Market Performance Overview

The selected BIST banking stocks show different return and risk characteristics over the sample period.

The project analyzes the following banking stocks:

* AKBNK.IS
* GARAN.IS
* HALKB.IS
* ISCTR.IS
* VAKBN.IS
* YKBNK.IS

The BIST 100 index is used as the market benchmark:

* XU100.IS

The weekly stock dataset allows comparative analysis of cumulative performance, weekly return behavior, volatility and downside risk.

Initial results suggest that selected banking stocks do not move identically over time. Some stocks display stronger cumulative performance, while others show higher volatility and deeper drawdown risk.

## 2. Risk Metrics Findings

The project calculates several risk and performance indicators for each stock.

The main risk and performance metrics include:

* Mean weekly return
* Annualized return
* Weekly volatility
* Annualized volatility
* Maximum drawdown
* Sharpe ratio
* Number of observations

The risk metrics show that banking stocks differ meaningfully in their risk-return profiles.

Higher annualized return does not always imply better risk-adjusted performance. Therefore, Sharpe ratio and maximum drawdown are important complementary indicators.

Maximum drawdown is especially useful because it captures the largest historical decline from a previous peak. This helps evaluate downside risk more directly than volatility alone.

## 3. Risk Score Findings

The project creates comparative risk and performance scores for selected banking stocks.

The risk score is designed to summarize relative risk across the selected stock universe.

The performance score is designed to summarize relative return and risk-adjusted performance.

The scoring system is relative, meaning that each stock is evaluated in comparison with the other selected banking stocks.

A higher risk score indicates relatively higher risk.

A higher performance score indicates relatively stronger performance within the selected universe.

These scores make the dashboard easier to interpret for non-technical users.

## 4. Macro Data Integration Findings

The project integrates stock market data with macroeconomic data from TCMB EVDS.

The macroeconomic variables used in the project are:

* USD/TRY buying exchange rate
* EUR/TRY buying exchange rate
* Consumer Price Index
* CBRT weighted average funding cost

The stock data and macroeconomic data are aligned to weekly frequency.

The final merged dataset is:

```text
data/processed/stock_macro_weekly.csv
```

The funding cost variable is interpreted as an operational monetary and funding condition indicator. It should not be interpreted as the official one-week repo policy rate.

This distinction is important for correct economic interpretation.

## 5. Macro Correlation Findings

The macro correlation analysis evaluates the relationship between weekly banking stock returns and macroeconomic variables.

The analysis includes the following macro variables:

* `usd_try_weekly_change`
* `eur_try_weekly_change`
* `cpi_index_weekly_change`
* `cpi_index_yoy_change`
* `funding_cost`
* `funding_cost_weekly_diff`

Initial correlation results suggest that USD/TRY weekly changes generally have a negative relationship with banking stock returns.

This indicates that exchange rate increases are often associated with weaker weekly banking stock returns.

EUR/TRY weekly changes also show generally negative relationships, although the strength of the relationship differs by ticker and model specification.

CPI-related variables show weaker but more persistent positive relationships in several cases.

Funding cost variables do not show a consistently strong correlation pattern across all selected banking stocks.

These correlation findings should be interpreted as descriptive association, not causality.

## 6. Macro Regression Findings

The project estimates four macro sensitivity regression specifications:

1. Core USD Model
2. Core EUR Model
3. Funding Cost Level Model
4. Funding Cost Change Model

The dependent variable in all models is weekly stock return.

The Core USD Model includes:

* `usd_try_weekly_change`
* `cpi_index_yoy_change`

The Core EUR Model includes:

* `eur_try_weekly_change`
* `cpi_index_yoy_change`

The Funding Cost Level Model includes:

* `usd_try_weekly_change`
* `cpi_index_yoy_change`
* `funding_cost`

The Funding Cost Change Model includes:

* `usd_try_weekly_change`
* `cpi_index_yoy_change`
* `funding_cost_weekly_diff`

Initial regression results indicate that USD/TRY weekly changes are negatively associated with several banking stock returns.

The CPI YoY variable appears statistically relevant in several model specifications.

Funding cost variables do not consistently appear as statistically significant explanatory variables for weekly banking stock returns.

This suggests that inflation regime sensitivity may be more persistent than short-term funding cost sensitivity in the current weekly model structure.

## 7. Model Diagnostics and Robust Inference Findings

The project also includes model diagnostics and robust inference checks for the macro sensitivity regressions.

The diagnostic results show that the models generally have low adjusted R-squared values. This indicates that weekly banking stock returns are only partially explained by the selected macroeconomic variables.

This result is expected because weekly stock returns are affected by many additional factors, including market sentiment, bank-specific news, financial statements, regulatory developments, liquidity conditions and global risk appetite.

The VIF results are very close to 1 across model specifications. This indicates that there is no meaningful multicollinearity problem among the explanatory variables used in the models.

The diagnostic tests also show that residual normality is not generally satisfied and that heteroskedasticity may be present in several specifications. This is common in financial return data.

For this reason, the project estimates additional robust regressions using HC3 robust standard errors.

The robust regression results show that `cpi_index_yoy_change` remains the most stable macro variable across banking stocks and model specifications.

In several models, `cpi_index_yoy_change` is statistically significant at the 5% level. It is also the strongest variable by absolute robust t-value in most model-stock combinations.

The USD/TRY weekly change variable appears significant mainly for AKBNK.IS and GARAN.IS at the 10% level in selected specifications.

The EUR/TRY weekly change variable provides a weaker signal and appears significant mainly for GARAN.IS at the 10% level.

The funding cost level and funding cost change variables do not consistently appear as statistically significant explanatory variables in the robust results.

HALKB.IS shows weaker macro sensitivity compared to the other selected banking stocks, as most robust model specifications do not produce statistically significant macro variables for this ticker.

Overall, the robust results strengthen the interpretation that inflation regime sensitivity is more stable than short-term funding cost sensitivity in the current weekly banking stock return models.

## 8. Methodological Notes

The project uses weekly data to reduce daily noise and improve alignment between stock market data and macroeconomic indicators.

CPI is originally monthly and is forward-filled to weekly frequency. Therefore, CPI should be interpreted as an inflation environment or inflation regime indicator rather than a true weekly inflation shock.

CBRT weighted average funding cost is not the official one-week repo policy rate. It is used as an operational funding condition indicator.

The macro regression models are exploratory.

The results should be interpreted as statistical association and sensitivity, not causality.

## 9. Overall Interpretation

The initial results suggest that selected BIST banking stocks are sensitive to macroeconomic conditions, but the strength of this sensitivity differs by ticker and variable.

Exchange rate changes generally show negative associations with weekly banking stock returns.

CPI YoY change appears to be the most stable macro sensitivity indicator across the current model specifications.

Funding cost variables do not consistently explain short-term weekly stock returns in the robust regression framework.

The model diagnostics show that the explanatory power of simple macro models is limited, which is expected for weekly financial return data.

The robust inference results improve the reliability of statistical interpretation by adjusting standard errors for heteroskedasticity concerns.

Overall, the project provides a useful and extensible framework for combining banking stock analytics, macroeconomic indicators, regression modeling, diagnostics and dashboard reporting.
