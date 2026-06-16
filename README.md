# BIST Banking Analytics

BIST Banking Analytics is a Python-based financial analytics project that analyzes selected BIST banking stocks using market data, risk metrics, macroeconomic indicators, regression-based macro sensitivity models, model diagnostics, robust inference and an interactive Streamlit dashboard.

The project focuses on the relationship between Turkish banking stocks and macroeconomic variables such as USD/TRY, EUR/TRY, CPI and CBRT weighted average funding cost.

The main objective is to create a structured, reproducible and portfolio-ready analytics project for banking sector analysis.

## Project Scope

The project analyzes selected BIST banking stocks and compares them with the BIST 100 benchmark.

Selected banking stocks:

| Ticker   | Bank               |
| -------- | ------------------ |
| AKBNK.IS | Akbank             |
| GARAN.IS | Garanti BBVA       |
| HALKB.IS | Halkbank           |
| ISCTR.IS | İş Bankası C       |
| VAKBN.IS | VakıfBank          |
| YKBNK.IS | Yapı Kredi Bankası |

Benchmark:

| Ticker   | Description    |
| -------- | -------------- |
| XU100.IS | BIST 100 Index |

## Project Objectives

The project is designed to answer the following analytical questions:

* How did selected BIST banking stocks perform over time?
* Which banking stocks show higher volatility and downside risk?
* Which stocks have stronger risk-adjusted performance?
* How are weekly banking stock returns associated with macroeconomic variables?
* Which macro variables appear more stable in regression-based sensitivity analysis?
* Do the macro regression models show multicollinearity, heteroskedasticity or residual normality issues?
* How do robust standard errors affect statistical inference?
* How can the results be presented in an interactive dashboard?

## Main Features

The project includes the following components:

* Yahoo Finance market data collection
* Weekly stock price transformation
* Weekly return calculation
* Risk metric calculation
* Risk score and performance score generation
* TCMB EVDS macroeconomic data integration
* Stock-macro merged panel dataset
* Macro correlation analysis
* OLS macro regression models
* Model diagnostics
* VIF analysis
* HC3 robust standard errors
* Robust regression summaries
* Streamlit dashboard
* Project documentation

## Data Sources

### Market Data

Market data is downloaded from Yahoo Finance using the `yfinance` Python package.

The raw market data includes:

* Open
* High
* Low
* Close
* Adjusted Close
* Volume

### Macroeconomic Data

Macroeconomic data is collected from TCMB EVDS.

The macro variables used in the project are:

| Variable     | EVDS Series Code | Description                        |
| ------------ | ---------------- | ---------------------------------- |
| usd_try      | TP.DK.USD.A.YTL  | USD/TRY buying exchange rate       |
| eur_try      | TP.DK.EUR.A.YTL  | EUR/TRY buying exchange rate       |
| cpi_index    | TP.FE.OKTG01     | Consumer Price Index               |
| funding_cost | TP.APIFON4       | CBRT weighted average funding cost |

Important note:

The CBRT weighted average funding cost is not interpreted as the official one-week repo policy rate. It is used as an operational monetary and funding condition indicator.

## Project Structure

```text
bist-banking-analytics/
├── config/
│   ├── macro_series.json
│   └── tickers.json
├── dashboard/
│   └── app.py
├── data/
│   ├── external/
│   │   └── .gitkeep
│   ├── processed/
│   │   └── .gitkeep
│   └── raw/
│       └── .gitkeep
├── docs/
│   ├── data_dictionary.md
│   ├── initial_findings.md
│   ├── methodology.md
│   └── project_quality_check.md
├── notebooks/
│   ├── 01_data_collection.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda_risk_analysis.ipynb
│   ├── 04_macro_sensitivity.ipynb
│   ├── 05_modeling.ipynb
│   └── 06_scoring_system.ipynb
├── outputs/
│   └── .gitkeep
├── reports/
│   └── figures/
│       └── .gitkeep
├── src/
│   ├── data_loader.py
│   ├── export_outputs.py
│   ├── indicators.py
│   ├── macro_analysis.py
│   ├── macro_loader.py
│   ├── merge_macro.py
│   ├── model_diagnostics.py
│   ├── preprocessing.py
│   ├── risk_metrics.py
│   ├── robust_macro_regression.py
│   ├── scoring.py
│   └── utils.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Installation

Clone the repository:

```bash
git clone https://github.com/erolpalaz/bist-banking-analytics.git
cd bist-banking-analytics
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment on Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

Install requirements:

```bash
pip install -r requirements.txt
```

## EVDS API Key Setup

The project uses TCMB EVDS data. Therefore, an EVDS API key is required for macroeconomic data collection.

Create a `.env` file in the project root:

```text
EVDS_API_KEY=your_evds_api_key_here
```

The `.env` file is ignored by Git and should not be committed.

## How to Run the Full Pipeline

Run the scripts in the following order:

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

## Pipeline Explanation

### 1. Market Data Collection

```bash
python -m src.data_loader
```

This script downloads historical market data for selected BIST banking stocks and the BIST 100 benchmark.

Main output:

```text
data/raw/stock_prices_raw.csv
```

### 2. Weekly Preprocessing

```bash
python -m src.preprocessing
```

This script converts daily stock data to weekly frequency and calculates weekly returns.

Main output:

```text
data/processed/stock_prices_weekly.csv
```

### 3. Risk Metrics and Risk Scores

```bash
python -m src.export_outputs
```

This script calculates risk metrics, performance metrics, risk scores and summary tables.

Main outputs:

```text
outputs/risk_metrics.csv
outputs/risk_scores.csv
outputs/summary_tables.xlsx
```

### 4. Macro Data Collection

```bash
python -m src.macro_loader
```

This script downloads macroeconomic variables from TCMB EVDS and transforms them into weekly frequency.

Main outputs:

```text
data/raw/macro_raw.csv
data/processed/macro_weekly.csv
```

### 5. Stock-Macro Dataset Merge

```bash
python -m src.merge_macro
```

This script merges weekly stock data with weekly macroeconomic data.

Main output:

```text
data/processed/stock_macro_weekly.csv
```

### 6. Macro Sensitivity Analysis

```bash
python -m src.macro_analysis
```

This script calculates macro correlations and OLS macro regression results.

Main outputs:

```text
outputs/macro_correlation_all_variables.csv
outputs/macro_model_summary.csv
outputs/funding_cost_change_summary.csv
outputs/macro_regression_core_usd_model.csv
outputs/macro_regression_core_eur_model.csv
outputs/macro_regression_funding_cost_level_model.csv
outputs/macro_regression_funding_cost_change_model.csv
```

### 7. Model Diagnostics

```bash
python -m src.model_diagnostics
```

This script evaluates macro regression models using basic diagnostic tests.

The diagnostic framework includes:

* Adjusted R-squared
* F-test p-value
* Durbin-Watson statistic
* Breusch-Pagan test
* Jarque-Bera test
* Variance Inflation Factor

Main outputs:

```text
outputs/macro_model_diagnostics.csv
outputs/macro_vif_results.csv
```

### 8. Robust Macro Regression

```bash
python -m src.robust_macro_regression
```

This script estimates macro regression models using HC3 robust standard errors.

The coefficient estimates remain based on OLS, but standard errors, t-statistics, p-values and confidence intervals are adjusted for heteroskedasticity concerns.

Main outputs:

```text
outputs/robust_macro_regression_core_usd_model.csv
outputs/robust_macro_regression_core_eur_model.csv
outputs/robust_macro_regression_funding_cost_level_model.csv
outputs/robust_macro_regression_funding_cost_change_model.csv
outputs/robust_macro_regression_all_models.csv
outputs/robust_macro_regression_summary.csv
```

### 9. Streamlit Dashboard

```bash
streamlit run dashboard/app.py
```

This command launches the interactive dashboard.

## Dashboard Pages

The dashboard includes the following pages:

| Page              | Description                                                 |
| ----------------- | ----------------------------------------------------------- |
| Market Overview   | General overview of selected stocks and benchmark           |
| Stock Comparison  | Stock-level comparison using price, return and volume data  |
| Risk Metrics      | Risk and performance metrics                                |
| Risk Scores       | Composite risk and performance scores                       |
| Macro Sensitivity | Macro correlation and OLS regression results                |
| Model Diagnostics | Regression diagnostics and VIF results                      |
| Robust Results    | HC3 robust regression summaries and detailed robust outputs |

## Main Analytical Methods

## Weekly Return Calculation

Weekly returns are calculated from weekly adjusted close or close prices.

General formula:

```text
weekly_return = current_week_price / previous_week_price - 1
```

The first weekly return observation for each ticker is missing because there is no previous week for comparison.

## Risk Metrics

The project calculates:

* Mean weekly return
* Annualized return
* Weekly volatility
* Annualized volatility
* Maximum drawdown
* Sharpe ratio
* Number of observations

## Risk Scoring

The project creates comparative risk and performance scores.

The risk score is designed to summarize relative risk across selected banking stocks.

The performance score is designed to summarize relative return and risk-adjusted performance.

The scoring system is relative to the selected stock universe.

## Macro Correlation Analysis

The macro correlation analysis calculates Pearson correlations between weekly stock returns and selected macroeconomic variables.

Macro variables included:

* `usd_try_weekly_change`
* `eur_try_weekly_change`
* `cpi_index_weekly_change`
* `cpi_index_yoy_change`
* `funding_cost`
* `funding_cost_weekly_diff`

Correlation results should be interpreted as descriptive association, not causality.

## Macro Regression Models

The dependent variable in all macro regression models is:

```text
weekly_return
```

The project uses four macro sensitivity model specifications.

### Core USD Model

Variables:

```text
usd_try_weekly_change
cpi_index_yoy_change
```

### Core EUR Model

Variables:

```text
eur_try_weekly_change
cpi_index_yoy_change
```

### Funding Cost Level Model

Variables:

```text
usd_try_weekly_change
cpi_index_yoy_change
funding_cost
```

### Funding Cost Change Model

Variables:

```text
usd_try_weekly_change
cpi_index_yoy_change
funding_cost_weekly_diff
```

The models are estimated separately for each selected banking stock.

The BIST 100 benchmark is excluded from bank-level macro regression outputs.

## Model Diagnostics

The project applies model diagnostics to evaluate the reliability of macro regression results.

The diagnostic framework includes:

| Diagnostic Test           | Purpose                                                                |
| ------------------------- | ---------------------------------------------------------------------- |
| Adjusted R-squared        | Measures explanatory power after adjusting for the number of variables |
| F-test p-value            | Evaluates overall model significance                                   |
| Durbin-Watson statistic   | Checks possible residual autocorrelation                               |
| Breusch-Pagan test        | Checks possible heteroskedasticity                                     |
| Jarque-Bera test          | Checks residual normality                                              |
| Variance Inflation Factor | Checks multicollinearity among explanatory variables                   |

The diagnostic results show that the macro sensitivity models have relatively low explanatory power. This is expected because weekly stock returns are influenced by many factors beyond a limited set of macroeconomic variables.

The VIF results do not indicate a multicollinearity concern. This supports the decision to estimate USD/TRY and EUR/TRY models separately.

The Breusch-Pagan and Jarque-Bera results suggest that heteroskedasticity and non-normal residuals may be present in several model specifications. These issues are common in financial return data.

## Robust Inference

Because heteroskedasticity may be present in financial return data, the project also estimates macro sensitivity models using HC3 robust standard errors.

The robust regression framework keeps the OLS coefficient estimates but adjusts:

* Standard errors
* t-statistics
* p-values
* Confidence intervals

The robust results are used to evaluate whether the statistical significance of macro variables remains stable after correcting standard errors.

## Initial Findings

The initial findings suggest that selected BIST banking stocks differ meaningfully in terms of return, volatility, drawdown risk and risk-adjusted performance.

The macro correlation results suggest that USD/TRY and EUR/TRY weekly changes generally have negative relationships with banking stock returns.

The OLS regression results indicate that USD/TRY weekly changes are negatively associated with several banking stock returns.

The CPI YoY variable appears statistically relevant in several model specifications.

The model diagnostics show that explanatory power is limited, which is expected for weekly financial return models with a small set of macro variables.

The VIF results do not indicate a meaningful multicollinearity problem.

The robust regression results show that `cpi_index_yoy_change` remains the most stable macro variable across banking stocks and model specifications.

In several robust model specifications, `cpi_index_yoy_change` is statistically significant at the 5% level and is the strongest variable by absolute robust t-value in most model-stock combinations.

The USD/TRY weekly change variable appears significant mainly for AKBNK.IS and GARAN.IS at the 10% level in selected specifications.

The EUR/TRY weekly change variable provides a weaker signal and appears significant mainly for GARAN.IS at the 10% level.

The funding cost level and funding cost change variables do not consistently appear as statistically significant explanatory variables in the robust results.

HALKB.IS shows weaker macro sensitivity compared to the other selected banking stocks.

## Important Interpretation Notes

The project follows these interpretation rules:

* Correlation does not imply causality.
* Regression outputs show statistical association, not causal effects.
* CPI is originally monthly and aligned to weekly frequency.
* CPI should be interpreted as an inflation environment or inflation regime indicator.
* CBRT weighted average funding cost is not the official one-week repo policy rate.
* Funding cost is used as an operational monetary and funding condition indicator.
* Robust standard errors improve statistical inference under possible heteroskedasticity.
* The dashboard and model outputs should not be interpreted as investment advice.

## Generated Files and Git Policy

The project does not commit generated data and output files to GitHub.

The following files are intentionally ignored:

```text
data/raw/*.csv
data/processed/*.csv
outputs/*.csv
outputs/*.xlsx
.env
```

The repository keeps `.gitkeep` files to preserve empty folder structure.

This keeps the GitHub repository clean while allowing users to reproduce outputs by running the pipeline scripts.

## Documentation

Additional documentation is available in the `docs/` folder:

| File                          | Description                                       |
| ----------------------------- | ------------------------------------------------- |
| docs/methodology.md           | Explains the methodological framework             |
| docs/data_dictionary.md       | Defines datasets, variables and output files      |
| docs/initial_findings.md      | Summarizes initial analytical findings            |
| docs/project_quality_check.md | Summarizes project consistency and quality checks |

## Requirements

Main Python packages used in the project:

* pandas
* numpy
* yfinance
* matplotlib
* plotly
* streamlit
* scikit-learn
* statsmodels
* openpyxl
* python-dotenv
* requests

Install all dependencies with:

```bash
pip install -r requirements.txt
```

## Reproducibility Checklist

To reproduce the project:

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install requirements.
4. Create a `.env` file with the EVDS API key.
5. Run the full pipeline in the correct order.
6. Launch the dashboard.

Full execution order:

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

## Future Improvements

Possible future improvements include:

* Rolling-window correlation analysis
* Rolling beta analysis
* Forecasting models
* Bank-level financial ratio integration
* Residual visualization
* Model comparison dashboard
* More advanced risk scoring
* Streamlit Cloud deployment
* Automated report generation
* Sector-level comparison with non-bank BIST stocks

## Disclaimer

This project is developed for educational, analytical and portfolio presentation purposes.

It does not provide investment advice.

All results should be interpreted as exploratory statistical analysis.
