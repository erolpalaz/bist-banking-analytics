# Methodology

This document explains the methodological framework used in the BIST Banking Analytics project.

The project analyzes selected BIST banking stocks using weekly market data, financial risk metrics, macroeconomic indicators from TCMB EVDS and regression-based macro sensitivity models.

The results are designed for exploratory financial analysis, dashboard reporting and portfolio presentation. They should not be interpreted as investment advice or causal evidence.

## 1. Analytical Objective

The main objective of this project is to build a structured analytics platform for selected BIST banking stocks.

The methodology focuses on four main analytical layers:

1. Market data collection and weekly return calculation
2. Risk and performance metric calculation
3. Risk and performance scoring
4. Macroeconomic sensitivity analysis

The project is designed to answer the following questions:

* How did selected BIST banking stocks perform over time?
* Which stocks show higher volatility and drawdown risk?
* Which stocks show stronger risk-adjusted performance?
* How are weekly banking stock returns statistically associated with macroeconomic variables?
* How can market, risk and macro indicators be presented in an interactive dashboard?

## 2. Stock Market Data Methodology

Historical stock market data is downloaded from Yahoo Finance using the `yfinance` Python package.

The selected stock universe includes:

* AKBNK.IS
* GARAN.IS
* HALKB.IS
* ISCTR.IS
* VAKBN.IS
* YKBNK.IS

The BIST 100 index is used as a benchmark:

* XU100.IS

The raw data includes open, high, low, close, adjusted close and volume fields.

## 3. Weekly Frequency Transformation

The project uses weekly frequency for the main analysis.

The weekly transformation is applied because:

* It reduces short-term daily noise.
* It creates a cleaner time-series structure for comparative analysis.
* It aligns stock market data with lower-frequency macroeconomic indicators.
* It is suitable for medium-term risk and macro sensitivity analysis.

Weekly data is created using week-ending observations.

For each ticker:

* Weekly open is based on the first available opening price of the week.
* Weekly high is the maximum price of the week.
* Weekly low is the minimum price of the week.
* Weekly close is the last available closing price of the week.
* Weekly adjusted close is the last available adjusted closing price of the week.
* Weekly volume is the total trading volume of the week.

## 4. Weekly Return Calculation

Weekly returns are calculated using the adjusted close price where available. If adjusted close is unavailable, close price is used.

The general return formula is:

```text
weekly_return = current_week_price / previous_week_price - 1
```

The first weekly return observation for each ticker is missing because there is no previous week for comparison.

Weekly returns are used as the dependent variable in the macro sensitivity models.

## 5. Risk Metrics Methodology

The project calculates several risk and performance metrics for each ticker.

### 5.1 Mean Weekly Return

Mean weekly return measures the average weekly return over the sample period.

### 5.2 Annualized Return

Annualized return converts weekly return performance into an annualized measure.

The project assumes approximately 52 weeks in a year.

### 5.3 Weekly Volatility

Weekly volatility is calculated as the standard deviation of weekly returns.

It measures how much weekly returns fluctuate around their average.

### 5.4 Annualized Volatility

Annualized volatility converts weekly volatility into an annualized risk measure.

The general formula is:

```text
annualized_volatility = weekly_volatility × sqrt(52)
```

### 5.5 Maximum Drawdown

Maximum drawdown measures the largest historical decline from a previous peak to a trough.

It is used to evaluate downside risk.

A larger negative drawdown indicates that the stock experienced a deeper historical decline.

### 5.6 Sharpe Ratio

Sharpe ratio is used as a risk-adjusted performance measure.

It evaluates how much return is generated per unit of volatility.

A higher Sharpe ratio indicates stronger risk-adjusted performance.

## 6. Risk Scoring Methodology

The project creates a comparative risk scoring framework for selected banking stocks.

The risk score combines selected risk indicators into a single score.

The scoring framework is designed to make cross-stock comparison easier.

Risk score components may include:

* Annualized volatility
* Maximum drawdown
* Benchmark sensitivity metrics where available

Performance score components may include:

* Annualized return
* Sharpe ratio
* Drawdown resilience

The scoring system is relative. This means that stocks are ranked and compared within the selected stock universe.

A higher risk score indicates relatively higher risk compared to other stocks in the sample.

A higher performance score indicates relatively stronger return and risk-adjusted performance.

## 7. Macroeconomic Data Methodology

Macroeconomic data is collected from TCMB EVDS.

The project uses the following macroeconomic variables:

| Variable                           | Description                             |
| ---------------------------------- | --------------------------------------- |
| USD/TRY                            | USD/TRY buying exchange rate            |
| EUR/TRY                            | EUR/TRY buying exchange rate            |
| CPI Index                          | Consumer Price Index                    |
| CBRT Weighted Average Funding Cost | Operational funding condition indicator |

The EVDS series are configured in:

```text
config/macro_series.json
```

Raw macroeconomic data is saved in long format and then transformed into weekly wide format.

## 8. Macro Frequency Alignment

The stock data is weekly. Therefore, macroeconomic variables are also aligned to weekly frequency.

### 8.1 Exchange Rates

USD/TRY and EUR/TRY are available at high frequency.

They are converted to weekly frequency using the last available value of each week.

Weekly percentage changes are calculated as:

```text
usd_try_weekly_change = usd_try / previous_week_usd_try - 1
eur_try_weekly_change = eur_try / previous_week_eur_try - 1
```

### 8.2 CPI Index

CPI is originally a monthly variable.

To align CPI with weekly stock returns, CPI is forward-filled to weekly frequency. This means that the most recently announced CPI value remains the latest available inflation information until a new CPI value is released.

The project calculates:

```text
cpi_index_weekly_change
cpi_index_yoy_change
```

`cpi_index_yoy_change` is calculated using a 52-week lag after weekly alignment.

CPI should be interpreted as an inflation environment or inflation regime indicator, not as a true weekly inflation shock.

### 8.3 CBRT Weighted Average Funding Cost

The funding cost variable represents the CBRT weighted average funding cost.

It is not the official one-week repo policy rate.

It is used as an operational monetary and funding condition indicator.

The project uses two funding cost variables:

```text
funding_cost
funding_cost_weekly_diff
```

`funding_cost` represents the prevailing funding cost environment.

`funding_cost_weekly_diff` represents short-term weekly changes in funding conditions.

## 9. Stock-Macro Dataset Merge

The weekly stock dataset and weekly macroeconomic dataset are merged by date.

The final merged dataset is:

```text
data/processed/stock_macro_weekly.csv
```

This dataset is used for macro correlation and regression analysis.

Each row represents one ticker-week observation.

## 10. Macro Correlation Analysis

The macro correlation analysis calculates the Pearson correlation between weekly stock returns and selected macroeconomic variables.

The correlation output includes:

* Ticker
* Macro variable
* Correlation coefficient
* Number of observations

Correlation values are interpreted as follows:

* Positive correlation means the stock return and macro variable tended to move in the same direction.
* Negative correlation means the stock return and macro variable tended to move in opposite directions.
* Correlation close to zero indicates weak linear association.

Correlation does not imply causality.

## 11. Macro Regression Methodology

The macro sensitivity models use ordinary least squares regression.

The dependent variable is:

```text
weekly_return
```

The independent variables differ by model specification.

The general model form is:

```text
weekly_return = constant + macro_variables + error
```

The regression outputs include:

* Coefficients
* P-values
* R-squared
* Adjusted R-squared
* F-test p-value
* Number of observations

The models are estimated separately for each banking stock.

The BIST 100 benchmark is excluded from bank-level regression outputs.

## 12. Macro Model Specifications

The project uses four macro sensitivity model specifications.

### 12.1 Core USD Model

Variables:

```text
usd_try_weekly_change
cpi_index_yoy_change
```

Purpose:

This model evaluates the association between banking stock returns, USD/TRY weekly changes and the inflation regime.

### 12.2 Core EUR Model

Variables:

```text
eur_try_weekly_change
cpi_index_yoy_change
```

Purpose:

This model evaluates the association between banking stock returns, EUR/TRY weekly changes and the inflation regime.

### 12.3 Funding Cost Level Model

Variables:

```text
usd_try_weekly_change
cpi_index_yoy_change
funding_cost
```

Purpose:

This model evaluates the association between banking stock returns and the prevailing funding cost environment.

The funding cost level is interpreted as an operational monetary condition variable.

### 12.4 Funding Cost Change Model

Variables:

```text
usd_try_weekly_change
cpi_index_yoy_change
funding_cost_weekly_diff
```

Purpose:

This model evaluates whether weekly changes in funding conditions are statistically associated with banking stock returns.

This model should be interpreted as a short-term funding condition sensitivity model.

## 13. Interpretation of Regression Results

Regression coefficients indicate the direction and size of the statistical relationship between the dependent variable and the independent variables.

General interpretation:

* A negative coefficient indicates a negative statistical relationship.
* A positive coefficient indicates a positive statistical relationship.
* A lower p-value indicates stronger statistical evidence for the coefficient.
* A higher p-value indicates weaker statistical evidence.

R-squared measures the share of variation in weekly returns explained by the model.

Adjusted R-squared adjusts R-squared for the number of explanatory variables.

F-test p-value provides a general test of model significance.

The regression results should be interpreted as statistical association and macro sensitivity, not causality.

## 14. Model Diagnostics and Robust Inference

In addition to standard OLS regression outputs, the project applies basic diagnostic tests to evaluate the reliability of the macro sensitivity models.

The diagnostic framework includes:

| Diagnostic Test           | Purpose                                                                |
| ------------------------- | ---------------------------------------------------------------------- |
| Adjusted R-squared        | Measures explanatory power after adjusting for the number of variables |
| F-test p-value            | Evaluates overall model significance                                   |
| Durbin-Watson statistic   | Checks possible residual autocorrelation                               |
| Breusch-Pagan test        | Checks possible heteroskedasticity                                     |
| Jarque-Bera test          | Checks residual normality                                              |
| Variance Inflation Factor | Checks multicollinearity among explanatory variables                   |

The diagnostic results show that the macro sensitivity models have relatively low explanatory power. This is expected because weekly stock returns are affected by many factors beyond a limited set of macroeconomic variables.

The VIF results do not indicate a multicollinearity concern. This supports the decision to estimate USD/TRY and EUR/TRY models separately.

However, the Breusch-Pagan and Jarque-Bera results suggest that heteroskedasticity and non-normal residuals may be present in several model specifications. These issues are common in financial return data.

For this reason, the project also estimates macro sensitivity models using HC3 robust standard errors.

The robust regression framework keeps the OLS coefficient estimates but adjusts standard errors, t-statistics and p-values for heteroskedasticity concerns.

The robust inference results are used to evaluate whether the statistical significance of macro variables remains stable after correcting standard errors.

Overall, the robust results suggest that CPI year-over-year change is the most stable macro sensitivity indicator across banking stocks, while funding cost variables do not consistently appear as statistically significant short-term return drivers.

## 15. Methodological Limitations

The project has several methodological limitations.

### 15.1 No Causal Identification

The models are exploratory and descriptive.

They do not include a causal identification strategy.

Therefore, the results cannot be interpreted as causal effects.

### 15.2 Omitted Variables

Weekly banking stock returns may be affected by many variables not included in the current models, such as:

* Bank-specific financial statements
* Regulatory announcements
* Global risk appetite
* CDS premiums
* Domestic political events
* Market liquidity
* Earnings expectations
* Sector-specific news

### 15.3 Frequency Mismatch

Some macroeconomic variables are not originally weekly.

CPI is monthly and aligned to weekly frequency through forward filling.

This creates a useful weekly analytical dataset but does not turn CPI into a true weekly variable.

### 15.4 Multicollinearity Risk

USD/TRY and EUR/TRY may be highly correlated.

For this reason, the project uses separate Core USD and Core EUR model specifications.

This reduces the risk of misleading coefficient interpretation caused by multicollinearity.

### 15.5 Funding Cost Interpretation

CBRT weighted average funding cost should not be interpreted as the official one-week repo policy rate.

It is used as an operational funding condition indicator.

### 15.6 Investment Advice Limitation

The project is not designed to generate investment recommendations.

The results are for educational, analytical and portfolio presentation purposes.

## 16. Dashboard Methodology

The Streamlit dashboard presents the project outputs in an interactive format.

Dashboard pages include:

* Market Overview
* Stock Comparison
* Risk Metrics
* Risk Scores
* Macro Sensitivity

The dashboard does not calculate the full analysis from scratch. Instead, it reads processed datasets and output files generated by the project pipeline.

This makes the dashboard faster and easier to use.

## 17. Reproducibility

The project is designed to be reproducible through modular Python scripts.

The main execution order is:

```bash
python -m src.data_loader
python -m src.preprocessing
python -m src.export_outputs
python -m src.macro_loader
python -m src.merge_macro
python -m src.macro_analysis
python -m src.model_diagnostics
python -m src.robust_macro_regression
streamlit run dashboard/app.py
```

The EVDS API key must be stored in a local `.env` file and should not be committed to GitHub.

## 18. Overall Methodological Summary

The methodology combines financial time-series processing, risk measurement, scoring, macroeconomic data integration, regression-based sensitivity analysis, model diagnostics and robust inference.

The project provides a structured framework for analyzing BIST banking stocks using both market-based indicators and macroeconomic variables.

The outputs should be interpreted as descriptive and exploratory evidence.

They provide a foundation for future improvements such as:

* Rolling-window analysis
* Forecasting models
* Extended model diagnostics
* Residual visualization
* Bank-level financial ratio integration
* More advanced dashboard visualizations
