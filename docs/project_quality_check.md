# Project Quality Check

This document summarizes the current consistency and quality status of the BIST Banking Analytics project.

## 1. Documentation Consistency

The main documentation files are:

* `README.md`
* `docs/methodology.md`
* `docs/data_dictionary.md`
* `docs/initial_findings.md`

The documentation uses consistent terminology for macroeconomic variables and model specifications.

The project uses the term **CBRT weighted average funding cost** instead of policy rate for the EVDS series `TP.APIFON4`.

This is important because `TP.APIFON4` is used as an operational funding condition indicator and should not be interpreted as the official one-week repo policy rate.

## 2. Main Dataset Consistency

The project uses the following main datasets:

* `data/raw/stock_prices_raw.csv`
* `data/processed/stock_prices_weekly.csv`
* `data/raw/macro_raw.csv`
* `data/processed/macro_weekly.csv`
* `data/processed/stock_macro_weekly.csv`

The stock data and macroeconomic data are aligned to weekly frequency.

Weekly stock returns are used as the dependent variable in macro sensitivity models.

## 3. Macro Variable Consistency

The macro variables used in the project are:

| Variable       | Description                        |
| -------------- | ---------------------------------- |
| `usd_try`      | USD/TRY buying exchange rate       |
| `eur_try`      | EUR/TRY buying exchange rate       |
| `cpi_index`    | Consumer Price Index               |
| `funding_cost` | CBRT weighted average funding cost |

Derived variables:

| Variable                   | Description                                             |
| -------------------------- | ------------------------------------------------------- |
| `usd_try_weekly_change`    | Weekly percentage change in USD/TRY                     |
| `eur_try_weekly_change`    | Weekly percentage change in EUR/TRY                     |
| `cpi_index_weekly_change`  | Weekly percentage change in CPI after weekly alignment  |
| `cpi_index_yoy_change`     | CPI year-over-year change                               |
| `funding_cost_weekly_diff` | Weekly difference in CBRT weighted average funding cost |

## 4. Macro Model Consistency

The macro sensitivity analysis uses four model specifications:

| Model                       | Description                                                              |
| --------------------------- | ------------------------------------------------------------------------ |
| `core_usd_model`            | USD/TRY weekly change and CPI YoY change                                 |
| `core_eur_model`            | EUR/TRY weekly change and CPI YoY change                                 |
| `funding_cost_level_model`  | USD/TRY weekly change, CPI YoY change and funding cost level             |
| `funding_cost_change_model` | USD/TRY weekly change, CPI YoY change and weekly funding cost difference |

These models are designed for statistical association and sensitivity analysis, not causal inference.

## 5. Dashboard Consistency

The Streamlit dashboard includes the following pages:

* Market Overview
* Stock Comparison
* Risk Metrics
* Risk Scores
* Macro Sensitivity

The Macro Sensitivity page uses the revised funding cost terminology and reads the updated macro regression output files.

## 6. Current Known Issues

The dashboard is functional, but visual design improvements are still planned.

Known improvement areas:

* Risk score chart color mapping
* Positive/negative correlation color distinction
* Regression significance highlighting
* Better KPI formatting
* Optional beta metric restoration if beta output is added later

These are presentation-level improvements and do not block the current analytical workflow.

## 7. Interpretation Rules

The project follows these interpretation rules:

* Correlation does not imply causality.
* Regression outputs show statistical association, not causal effects.
* CPI is originally monthly and aligned to weekly frequency.
* CBRT weighted average funding cost is not the official one-week repo policy rate.
* The dashboard and model outputs should not be interpreted as investment advice.

## 8. Current Project Status

The project currently includes:

* Market data collection
* Weekly preprocessing
* Risk metric calculation
* Risk scoring
* TCMB EVDS macro data integration
* Stock-macro merged dataset
* Macro correlation analysis
* Macro regression models
* Streamlit dashboard
* GitHub version control

The project is ready for the next development phase: model diagnostics and analytical refinement.
