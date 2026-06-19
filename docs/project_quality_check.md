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

## 5. Model Diagnostics Consistency

The project includes model diagnostics for macro sensitivity models.

The diagnostic outputs are:

* `outputs/macro_model_diagnostics.csv`
* `outputs/macro_vif_results.csv`

The diagnostic framework includes:

* Adjusted R-squared
* F-test p-value
* Durbin-Watson statistic
* Breusch-Pagan test
* Jarque-Bera test
* Variance Inflation Factor

The VIF results do not indicate a meaningful multicollinearity problem.

The diagnostic results indicate that low explanatory power, heteroskedasticity and non-normal residuals may be present in several model specifications.

These findings are expected for weekly financial return models.

## 6. Robust Inference Consistency

The project includes robust macro regression outputs using HC3 robust standard errors.

The robust output files are:

* `outputs/robust_macro_regression_core_usd_model.csv`
* `outputs/robust_macro_regression_core_eur_model.csv`
* `outputs/robust_macro_regression_funding_cost_level_model.csv`
* `outputs/robust_macro_regression_funding_cost_change_model.csv`
* `outputs/robust_macro_regression_all_models.csv`
* `outputs/robust_macro_regression_summary.csv`

The robust results show that `cpi_index_yoy_change` is the most stable macro variable across many model-stock combinations.

Funding cost variables do not consistently appear as statistically significant short-term return drivers.

## 7. Rolling Analysis Consistency

The project now includes 52-week rolling macro sensitivity analysis.

The rolling analysis evaluates whether the relationship between weekly banking stock returns and macroeconomic variables is stable over time.

The main rolling analysis files are:

* `src/rolling_analysis.py`
* `outputs/rolling_macro_correlation.csv`
* `outputs/rolling_macro_correlation_summary.csv`

The dashboard includes a dedicated `Rolling Macro Sensitivity` page.

The rolling analysis confirms that USD/TRY weekly change has the most stable negative relationship with selected BIST banking stock returns.

The rolling outputs are generated files and should not be committed to GitHub.

## 8. Dashboard Consistency

The Streamlit dashboard includes the following pages:

* Market Overview
* Stock Comparison
* Risk Metrics
* Risk Scores
* Macro Sensitivity
* Model Diagnostics
* Robust Results
* Rolling Macro Sensitivity

The Macro Sensitivity page uses the revised funding cost terminology and reads the updated macro regression output files.

The Model Diagnostics page uses diagnostic and VIF output files.

The Robust Results page uses HC3 robust regression output files.

The Rolling Macro Sensitivity page uses rolling correlation output files.

The Rolling Macro Sensitivity page has been refined with additional interpretation features.

The page now includes:

* KPI cards for average rolling correlation, latest rolling correlation, mostly negative relationships and time-varying relationships
* Automated insight text based on the selected macro variable and ticker filters
* Relationship stability overview
* A zero-correlation reference line on rolling correlation charts
* Latest rolling correlation chart with relationship stability classification
* Interpretation notes
* Raw rolling correlation data inside an expandable section

This improves dashboard readability and supports portfolio presentation quality.

## 9. Current Known Issues

The dashboard is functional, but visual design improvements are still planned.

Known improvement areas:

* Risk score chart color mapping
* Positive/negative correlation color distinction
* Regression significance highlighting
* Better KPI formatting
* Rolling correlation chart simplification when many variables are selected
* Optional beta metric restoration if beta output is added later

These are presentation-level improvements and do not block the current analytical workflow.

## 10. Interpretation Rules

The project follows these interpretation rules:

* Correlation does not imply causality.
* Regression outputs show statistical association, not causal effects.
* Rolling correlation shows time-varying association, not causality.
* CPI is originally monthly and aligned to weekly frequency.
* CBRT weighted average funding cost is not the official one-week repo policy rate.
* The dashboard and model outputs should not be interpreted as investment advice.

## 11. Git and Output File Policy

The project intentionally does not commit generated data and output files.

Ignored files include:

* `data/raw/*.csv`
* `data/processed/*.csv`
* `outputs/*.csv`
* `outputs/*.xlsx`
* `.env`

The repository keeps `.gitkeep` files to preserve folder structure.

This keeps the GitHub repository clean while allowing users to reproduce all outputs by running the pipeline.

## 12. Current Project Status

The project currently includes:

* Market data collection
* Weekly preprocessing
* Risk metric calculation
* Risk scoring
* TCMB EVDS macro data integration
* Stock-macro merged dataset
* Macro correlation analysis
* Macro regression models
* Model diagnostics
* VIF analysis
* HC3 robust macro regression
* Rolling macro sensitivity analysis
* Refined rolling macro sensitivity dashboard
* Streamlit dashboard
* GitHub version control
* Project documentation

The project is ready for the next development phase: advanced visual refinement, rolling analysis interpretation and optional forecasting extensions.
