# Initial Findings

This document summarizes the initial analytical findings of the BIST Banking Analytics project.

The analysis is based on weekly data for selected BIST banking stocks and macroeconomic indicators obtained from TCMB EVDS. The findings are descriptive and should not be interpreted as investment advice or causal evidence.

## 1. Market Performance Overview

The weekly market analysis shows that selected BIST banking stocks exhibit different risk-return profiles over the sample period.

Based on the initial risk and performance outputs, GARAN.IS stands out as one of the strongest stocks in terms of annualized return and Sharpe ratio. This suggests that GARAN.IS provided a relatively better return per unit of risk compared to other banking stocks in the selected universe.

VAKBN.IS shows a higher risk profile, mainly due to its relatively higher volatility and risk score. This indicates that VAKBN.IS experienced stronger price fluctuations compared to other banking stocks in the sample.

The normalized price chart in the dashboard helps compare stock performance on a common base value of 100. This makes it easier to compare cumulative performance across stocks with different price levels.

## 2. Risk Metrics Findings

The risk metrics module evaluates each banking stock using return, volatility, drawdown and risk-adjusted performance indicators.

The key interpretation is that banking stocks do not carry the same level of risk even though they belong to the same sector. Some stocks show stronger return performance, while others show higher volatility and drawdown risk.

Maximum drawdown is especially important because it measures the largest historical loss from a peak to a trough. A high drawdown indicates that the stock experienced a deeper loss during the sample period.

Sharpe ratio is used to evaluate risk-adjusted performance. A higher Sharpe ratio indicates that the stock generated more return relative to its volatility.

## 3. Risk Score Findings

The risk scoring system provides a comparative ranking of banking stocks based on selected risk components.

The risk score combines multiple risk indicators into a single score. This makes it easier to compare stocks using a simplified risk classification framework.

The initial dashboard results suggest that VAKBN.IS has one of the highest risk scores, while GARAN.IS has one of the lower risk scores among the selected banking stocks.

This result is consistent with the general interpretation that GARAN.IS shows a stronger risk-adjusted performance profile, while VAKBN.IS shows a more volatile risk profile.

## 4. Macro Data Integration Findings

The project successfully integrates macroeconomic data from TCMB EVDS and aligns it with weekly stock return data.

The macro variables used in the analysis are:

* USD/TRY buying exchange rate
* EUR/TRY buying exchange rate
* CPI index
* CBRT weighted average funding cost

Exchange rates and funding cost data are transformed into weekly frequency using the last available observation of each week. CPI is a monthly variable and is forward-filled to weekly frequency.

The final merged dataset includes stock market variables and macroeconomic indicators in a single weekly panel structure.

## 5. Macro Correlation Findings

The macro correlation analysis shows the statistical association between weekly banking stock returns and macroeconomic variables.

The initial results suggest that USD/TRY weekly changes generally have a negative correlation with banking stock returns. This means that during weeks when USD/TRY increased, banking stock returns tended to be weaker.

EUR/TRY weekly changes also show a generally negative relationship with banking stock returns, although the strength of the relationship differs across stocks.

CPI-related variables show weak but generally positive correlations with banking stock returns. However, these correlations should be interpreted carefully because CPI is originally a monthly variable and represents an inflation environment rather than a weekly inflation shock.

The funding cost variable is interpreted as an operational monetary and funding condition indicator. It should not be interpreted as the official one-week repo policy rate.

## 6. Regression Model Findings

The macro sensitivity analysis includes four model specifications:

1. Core USD Model
2. Core EUR Model
3. Funding Cost Level Model
4. Funding Cost Change Model

The Core USD Model uses USD/TRY weekly change and CPI year-over-year change. Initial regression results show that USD/TRY weekly change has a negative coefficient for several banking stocks. This supports the descriptive finding that banking stock returns tend to weaken during weeks of TRY depreciation.

CPI year-over-year change appears statistically relevant in several model specifications. This suggests that the inflation regime has a measurable relationship with banking stock returns in the sample period.

The Funding Cost Level Model uses the level of CBRT weighted average funding cost as a funding environment variable. The Funding Cost Change Model uses weekly changes in the funding cost variable.

Initial results indicate that funding cost variables do not consistently show strong statistical significance across all banking stocks. This suggests that short-term weekly return movements may be more directly associated with exchange rate changes and inflation regime variables than with weekly changes in funding cost.

## 7. Methodological Notes

The results should be interpreted as statistical association and macro sensitivity, not as causal effects.

Important limitations:

* Correlation does not imply causation.
* Regression coefficients show conditional statistical relationships, not direct economic causality.
* CPI is monthly and aligned to weekly frequency through forward filling.
* CBRT weighted average funding cost is not the official one-week repo policy rate.
* Weekly stock returns may be affected by many other factors that are not included in the current model.
* The current models are designed for exploratory analysis and portfolio presentation, not investment decision-making.

## 8. Overall Interpretation

The initial findings suggest that selected BIST banking stocks are sensitive to macroeconomic conditions, especially exchange rate movements and inflation regime indicators.

GARAN.IS appears to show stronger risk-adjusted performance, while VAKBN.IS appears to carry a higher risk profile. USD/TRY weekly changes generally show a negative relationship with banking stock returns. CPI year-over-year change appears relevant in several regression specifications.

These findings provide a strong analytical foundation for further development of the project. Future improvements may include model diagnostics, multicollinearity checks, rolling-window analysis, forecasting models and more advanced dashboard visualizations.
