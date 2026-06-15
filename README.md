# BIST Banking Analytics

## Project Overview

BIST Banking Analytics is a Python-based financial analytics project focused on Borsa Istanbul banking stocks.  
The project analyzes historical stock prices, market risk, macroeconomic sensitivity, risk-return metrics, and creates an interactive dashboard.

This project is designed as a portfolio-ready data analytics / financial risk analytics project.

> Disclaimer: This project is for educational and analytical purposes only. It does not provide investment advice.

---

## Business Problem

How do BIST banking stocks behave under different market and macroeconomic conditions?

The project focuses on:

- Return analysis
- Volatility analysis
- Market beta
- Maximum drawdown
- Sharpe ratio
- Macro sensitivity
- Risk scoring
- Weekly return direction modeling
- Streamlit dashboard

---

## Initial Stock Universe

| Ticker | Company |
|---|---|
| AKBNK.IS | Akbank |
| GARAN.IS | Garanti BBVA |
| ISCTR.IS | Türkiye İş Bankası C |
| YKBNK.IS | Yapı Kredi |
| VAKBN.IS | Vakıfbank |
| HALKB.IS | Halkbank |

Benchmark:

| Ticker | Description |
|---|---|
| XU100.IS | BIST 100 Index |

---

## Project Structure

```text
bist-banking-analytics/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
│
├── notebooks/
│   ├── 01_data_collection.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda_risk_analysis.ipynb
│   ├── 04_macro_sensitivity.ipynb
│   ├── 05_modeling.ipynb
│   └── 06_scoring_system.ipynb
│
├── src/
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── risk_metrics.py
│   ├── indicators.py
│   ├── scoring.py
│   └── utils.py
│
├── dashboard/
│   └── app.py
│
├── config/
│   └── tickers.json
│
├── reports/
│   └── figures/
│
├── outputs/
│
├── docs/
│   ├── data_dictionary.md
│   └── methodology.md
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Roadmap

### Phase 1 — Data Collection
- Download banking stock prices
- Download BIST 100 benchmark
- Save raw data
- Validate tickers

### Phase 2 — Data Cleaning
- Standardize date columns
- Calculate daily and weekly returns
- Merge stock and benchmark data
- Handle missing values

### Phase 3 — Risk Metrics
- Volatility
- Beta
- Maximum drawdown
- Sharpe ratio
- Correlation matrix

### Phase 4 — Macro Sensitivity
- Add exchange rate, interest rate, inflation variables
- Run correlation and regression analysis
- Interpret banking-sector sensitivity

### Phase 5 — Risk Scoring
- Normalize risk metrics
- Build transparent 0-100 risk score
- Compare banks by risk profile

### Phase 6 — Modeling
- Predict next-week return direction
- Compare baseline and tree-based models
- Evaluate with financial and classification metrics

### Phase 7 — Dashboard
- Build Streamlit dashboard
- Add interactive stock comparison
- Add risk score page
- Add model results page

---

## How to Run

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Install requirements:

```bash
pip install -r requirements.txt
```

Run dashboard:

```bash
streamlit run dashboard/app.py
```

---

## Output Files

Expected project outputs:

```text
data/raw/stock_prices_raw.csv
data/processed/stock_prices_weekly.csv
outputs/risk_metrics.csv
outputs/risk_scores.csv
outputs/model_results.csv
reports/final_report.pdf
```

## Initial Results

The first version of the analysis produced the following insights:

| Finding                       | Result   |
| ----------------------------- | -------- |
| Highest annualized return     | GARAN.IS |
| Highest Sharpe ratio          | GARAN.IS |
| Highest annualized volatility | VAKBN.IS |
| Highest risk score            | VAKBN.IS |
| Lowest risk score             | GARAN.IS |
| Highest beta to BIST 100      | AKBNK.IS |

These findings are based on weekly historical data starting from 2018.

> The results are for educational and analytical purposes only and do not represent investment advice.


---

## Portfolio Value

This project demonstrates:

- Python for financial data analysis
- Time series data preparation
- Risk-return analytics
- Macroeconomic sensitivity analysis
- Scoring system design
- Machine learning classification
- Streamlit dashboard development
- Business-oriented analytical reporting
