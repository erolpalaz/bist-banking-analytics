# BIST Banking Analytics

BIST Banking Analytics is a Python-based financial analytics project that analyzes selected BIST banking stocks using market data, risk metrics, macroeconomic indicators and an interactive Streamlit dashboard.

The project focuses on the relationship between Turkish banking stocks and macroeconomic variables such as USD/TRY, EUR/TRY, CPI and CBRT weighted average funding cost.

## Project Objective

The main objective of this project is to build a portfolio-ready analytics platform for BIST banking stocks.

The project includes:

* Historical stock price data collection
* Weekly return calculation
* Risk and performance metric calculation
* Risk scoring system
* TCMB EVDS macroeconomic data integration
* Stock-macro dataset merging
* Macro sensitivity analysis
* Regression-based model comparison
* Interactive Streamlit dashboard

## Stock Universe

The analysis covers selected BIST banking stocks:

* AKBNK.IS
* GARAN.IS
* HALKB.IS
* ISCTR.IS
* VAKBN.IS
* YKBNK.IS

Benchmark index:

* XU100.IS

## Data Sources

### Market Data

Market data is collected from Yahoo Finance using the `yfinance` Python package.

The raw stock data includes:

* Date
* Open
* High
* Low
* Close
* Adjusted Close
* Volume
* Ticker

The data is transformed into weekly frequency for return and risk analysis.

### Macroeconomic Data

Macroeconomic data is collected from TCMB EVDS.

The macro variables used in the project are:

| Variable                           | Description                                      |
| ---------------------------------- | ------------------------------------------------ |
| USD/TRY                            | USD/TRY buying exchange rate                     |
| EUR/TRY                            | EUR/TRY buying exchange rate                     |
| CPI Index                          | Consumer Price Index                             |
| CBRT Weighted Average Funding Cost | Operational monetary/funding condition indicator |

The CBRT weighted average funding cost is not interpreted as the official one-week repo policy rate. It is used as an operational funding condition indicator.

## Project Structure

```text
bist-banking-analytics/
├── config/
│   ├── tickers.json
│   └── macro_series.json
├── dashboard/
│   └── app.py
├── data/
│   ├── external/
│   ├── processed/
│   └── raw/
├── docs/
│   ├── data_dictionary.md
│   ├── initial_findings.md
│   └── methodology.md
├── notebooks/
│   ├── 01_data_collection.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda_risk_analysis.ipynb
│   ├── 04_macro_sensitivity.ipynb
│   ├── 05_modeling.ipynb
│   └── 06_scoring_system.ipynb
├── outputs/
├── reports/
│   └── figures/
├── src/
│   ├── data_loader.py
│   ├── export_outputs.py
│   ├── indicators.py
│   ├── macro_analysis.py
│   ├── macro_loader.py
│   ├── merge_macro.py
│   ├── preprocessing.py
│   ├── risk_metrics.py
│   ├── scoring.py
│   └── utils.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Main Features

### 1. Market Data Pipeline

The project downloads historical stock prices and converts them into weekly observations.

Main outputs:

```text
data/raw/stock_prices_raw.csv
data/processed/stock_prices_weekly.csv
```

### 2. Risk Metrics

The project calculates key financial risk and performance metrics.

Metrics include:

* Mean weekly return
* Annualized return
* Weekly volatility
* Annualized volatility
* Maximum drawdown
* Sharpe ratio
* Benchmark sensitivity metrics where available

Main output:

```text
outputs/risk_metrics.csv
```

### 3. Risk Scoring System

The project creates a comparative risk and performance scoring system for banking stocks.

Risk score components include:

* Volatility
* Maximum drawdown
* Benchmark sensitivity

Performance score components include:

* Annualized return
* Sharpe ratio
* Drawdown resilience

Main output:

```text
outputs/risk_scores.csv
```

### 4. TCMB EVDS Macro Data Integration

The project downloads macroeconomic data from TCMB EVDS using an API key.

Main outputs:

```text
data/raw/macro_raw.csv
data/processed/macro_weekly.csv
data/processed/stock_macro_weekly.csv
```

Macro variables are aligned to weekly frequency to match weekly stock returns.

Exchange rates and funding cost variables are converted to weekly frequency using the last available value of each week. CPI is monthly and forward-filled to weekly frequency.

### 5. Macro Sensitivity Analysis

The project analyzes the relationship between weekly banking stock returns and macroeconomic variables.

The analysis includes:

* Correlation analysis
* Core USD model
* Core EUR model
* Funding cost level model
* Funding cost change model

Model specifications:

| Model                     | Variables                                                         |
| ------------------------- | ----------------------------------------------------------------- |
| Core USD Model            | USD/TRY weekly change, CPI YoY change                             |
| Core EUR Model            | EUR/TRY weekly change, CPI YoY change                             |
| Funding Cost Level Model  | USD/TRY weekly change, CPI YoY change, funding cost level         |
| Funding Cost Change Model | USD/TRY weekly change, CPI YoY change, weekly funding cost change |

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

The results should be interpreted as statistical association and macro sensitivity, not as causal evidence.

### 6. Streamlit Dashboard

The dashboard includes the following pages:

* Market Overview
* Stock Comparison
* Risk Metrics
* Risk Scores
* Macro Sensitivity

Dashboard file:

```text
dashboard/app.py
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

Activate the virtual environment:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## EVDS API Key Setup

Create a `.env` file in the project root directory:

```text
EVDS_API_KEY=your_evds_api_key
```

The `.env` file is ignored by Git and should not be committed.

## How to Run the Project

### 1. Download Stock Data

```bash
python -m src.data_loader
```

### 2. Preprocess Stock Data

```bash
python -m src.preprocessing
```

### 3. Generate Risk Outputs

```bash
python -m src.export_outputs
```

### 4. Download Macro Data

```bash
python -m src.macro_loader
```

### 5. Merge Stock and Macro Data

```bash
python -m src.merge_macro
```

### 6. Run Macro Sensitivity Analysis

```bash
python -m src.macro_analysis
```

### 7. Launch Dashboard

```bash
streamlit run dashboard/app.py
```

## Initial Findings

Based on the weekly analysis period, GARAN.IS stands out with relatively strong return and Sharpe ratio performance. VAKBN.IS shows a higher risk profile due to its volatility and risk score. Macro sensitivity results suggest that USD/TRY weekly changes generally show a negative relationship with banking stock returns, while CPI YoY change appears statistically relevant in several regression specifications.

These findings are descriptive and should not be interpreted as investment advice.

## Interpretation Notes

This project is designed for analytical and educational purposes.

Important limitations:

* Results are based on historical data.
* Correlation and regression results do not prove causality.
* CPI is a monthly variable aligned to weekly frequency.
* CBRT weighted average funding cost is not the official one-week repo policy rate.
* The model outputs should not be interpreted as investment recommendations.

## Portfolio Value

This project demonstrates practical skills in:

* Python-based financial data analysis
* API-based macroeconomic data collection
* Time-series preprocessing
* Financial risk analysis
* Regression modeling
* Dashboard development with Streamlit
* Git/GitHub project management
* Financial interpretation for the banking sector

## Disclaimer

This project is for educational and analytical purposes only. It does not provide investment advice.
