from pathlib import Path

import pandas as pd
import statsmodels.api as sm

from src.utils import get_project_root, ensure_directory


CORRELATION_VARIABLES = [
    "usd_try_weekly_change",
    "eur_try_weekly_change",
    "cpi_index_weekly_change",
    "cpi_index_yoy_change",
    "funding_cost",
    "funding_cost_weekly_diff"
]


MODEL_SPECS = {
    "core_usd_model": {
        "description": "Core macro model using USD/TRY weekly change and CPI YoY change.",
        "features": [
            "usd_try_weekly_change",
            "cpi_index_yoy_change"
        ]
    },
    "core_eur_model": {
        "description": "Alternative core macro model using EUR/TRY weekly change and CPI YoY change.",
        "features": [
            "eur_try_weekly_change",
            "cpi_index_yoy_change"
        ]
    },
    "funding_cost_level_model": {
        "description": "Funding cost regime model using CBRT weighted average funding cost level.",
        "features": [
            "usd_try_weekly_change",
            "cpi_index_yoy_change",
            "funding_cost"
        ]
    },
    "funding_cost_change_model": {
        "description": "Funding cost change model using weekly changes in CBRT weighted average funding cost.",
        "features": [
            "usd_try_weekly_change",
            "cpi_index_yoy_change",
            "funding_cost_weekly_diff"
        ]
    }
}


def load_stock_macro_data() -> pd.DataFrame:
    """Load merged weekly stock and macro dataset."""
    root = get_project_root()
    path = root / "data" / "processed" / "stock_macro_weekly.csv"

    if not path.exists():
        raise FileNotFoundError(
            "stock_macro_weekly.csv not found. Run first:\n"
            "python -m src.macro_loader\n"
            "python -m src.merge_macro"
        )

    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"])

    return df


def validate_columns(data: pd.DataFrame, columns: list[str]) -> None:
    """Check whether required columns exist."""
    missing = [col for col in columns if col not in data.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def create_correlation_table(data: pd.DataFrame) -> Path:
    """
    Calculate correlation between weekly stock returns and macro variables.

    This table is descriptive. It should be interpreted as statistical association,
    not causality.
    """
    root = get_project_root()
    output_dir = ensure_directory(root / "outputs")
    output_path = output_dir / "macro_correlation_all_variables.csv"

    required_cols = ["Ticker", "weekly_return"] + CORRELATION_VARIABLES
    validate_columns(data, required_cols)

    results = []

    for ticker, group in data.groupby("Ticker"):
        for macro_var in CORRELATION_VARIABLES:
            temp = group[["weekly_return", macro_var]].dropna()

            if temp.empty:
                continue

            corr = temp["weekly_return"].corr(temp[macro_var])

            results.append({
                "Ticker": ticker,
                "macro_variable": macro_var,
                "correlation": corr,
                "observations": temp.shape[0]
            })

    result_df = pd.DataFrame(results)
    result_df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"Correlation table saved to: {output_path}")

    return output_path


def run_regression_for_ticker(
    data: pd.DataFrame,
    ticker: str,
    model_name: str,
    features: list[str]
) -> dict:
    """
    Run OLS regression for one ticker.

    weekly_return = constant + selected macro variables
    """
    group = data[data["Ticker"] == ticker].copy()

    required_cols = ["weekly_return"] + features
    group = group[required_cols].dropna()

    if group.shape[0] < 30:
        return {
            "model_name": model_name,
            "Ticker": ticker,
            "status": "insufficient_observations",
            "observations": group.shape[0]
        }

    y = group["weekly_return"]
    X = group[features]
    X = sm.add_constant(X)

    model = sm.OLS(y, X).fit()

    result = {
        "model_name": model_name,
        "Ticker": ticker,
        "status": "success",
        "observations": int(model.nobs),
        "r_squared": model.rsquared,
        "adj_r_squared": model.rsquared_adj,
        "f_pvalue": model.f_pvalue
    }

    for variable in ["const"] + features:
        result[f"{variable}_coef"] = model.params.get(variable)
        result[f"{variable}_pvalue"] = model.pvalues.get(variable)

    return result


def create_regression_results(
    data: pd.DataFrame,
    model_name: str,
    features: list[str]
) -> Path:
    """Run selected macro model for all bank tickers."""
    root = get_project_root()
    output_dir = ensure_directory(root / "outputs")
    output_path = output_dir / f"macro_regression_{model_name}.csv"

    validate_columns(data, ["Ticker", "weekly_return"] + features)

    results = []

    for ticker in sorted(data["Ticker"].unique()):
        if ticker == "XU100.IS":
            continue

        result = run_regression_for_ticker(
            data=data,
            ticker=ticker,
            model_name=model_name,
            features=features
        )
        results.append(result)

    result_df = pd.DataFrame(results)
    result_df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"Regression results saved to: {output_path}")

    return output_path


def create_model_summary() -> Path:
    """Create a model specification summary file."""
    root = get_project_root()
    output_dir = ensure_directory(root / "outputs")
    output_path = output_dir / "macro_model_summary.csv"

    rows = []

    for model_name, spec in MODEL_SPECS.items():
        rows.append({
            "model_name": model_name,
            "description": spec["description"],
            "features": ", ".join(spec["features"]),
            "dependent_variable": "weekly_return",
            "interpretation_note": (
                "Results indicate statistical association/sensitivity, not causality."
            )
        })

    summary = pd.DataFrame(rows)
    summary.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"Model summary saved to: {output_path}")

    return output_path


def create_funding_cost_change_summary(data: pd.DataFrame) -> Path:
    """
    Summarize how often the CBRT weighted average funding cost changes
    in the weekly dataset.

    This is not the official policy rate. It is an operational funding cost
    indicator and may change more frequently.
    """
    root = get_project_root()
    output_dir = ensure_directory(root / "outputs")
    output_path = output_dir / "funding_cost_change_summary.csv"

    validate_columns(data, ["Date", "funding_cost", "funding_cost_weekly_diff"])

    macro_by_date = (
        data[["Date", "funding_cost", "funding_cost_weekly_diff"]]
        .drop_duplicates(subset=["Date"])
        .sort_values("Date")
        .dropna(subset=["funding_cost_weekly_diff"])
    )

    total_weeks = macro_by_date.shape[0]
    change_weeks = (
        macro_by_date["funding_cost_weekly_diff"].abs() > 1e-12
    ).sum()

    no_change_weeks = total_weeks - change_weeks

    event_summary = pd.DataFrame([
        {
            "total_weeks": total_weeks,
            "funding_cost_change_weeks": int(change_weeks),
            "no_change_weeks": int(no_change_weeks),
            "funding_cost_change_week_ratio": (
                change_weeks / total_weeks if total_weeks else None
            ),
            "interpretation": (
                "funding_cost_weekly_diff measures weekly changes in CBRT weighted "
                "average funding cost. It is not the official one-week repo policy rate."
            )
        }
    ])

    event_summary.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"Funding cost change summary saved to: {output_path}")

    return output_path


def run_macro_analysis():
    """
    Run revised macro sensitivity analysis.

    Model logic:
    1. Correlation table: descriptive association with all macro variables.
    2. Core USD model: exchange rate + inflation regime.
    3. Core EUR model: alternative exchange rate specification.
    4. Funding cost level model: monetary/funding cost environment.
    5. Funding cost change model: weekly funding cost changes.
    """
    data = load_stock_macro_data()

    validate_columns(
        data,
        ["Date", "Ticker", "weekly_return"] + CORRELATION_VARIABLES
    )

    print(f"Loaded merged dataset rows: {len(data)}")
    print(f"Date range: {data['Date'].min().date()} - {data['Date'].max().date()}")

    create_correlation_table(data)
    create_model_summary()
    create_funding_cost_change_summary(data)

    for model_name, spec in MODEL_SPECS.items():
        create_regression_results(
            data=data,
            model_name=model_name,
            features=spec["features"]
        )


if __name__ == "__main__":
    run_macro_analysis()