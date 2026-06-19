from pathlib import Path

import pandas as pd

from src.utils import get_project_root, ensure_directory


ROLLING_WINDOW = 52

MACRO_VARIABLES = [
    "usd_try_weekly_change",
    "eur_try_weekly_change",
    "cpi_index_yoy_change",
    "funding_cost",
    "funding_cost_weekly_diff",
]


def load_stock_macro_data() -> pd.DataFrame:
    """Load merged weekly stock and macro dataset."""
    root = get_project_root()
    path = root / "data" / "processed" / "stock_macro_weekly.csv"

    if not path.exists():
        raise FileNotFoundError(
            f"Required file not found: {path}. "
            "Run python -m src.merge_macro first."
        )

    data = pd.read_csv(path, parse_dates=["Date"])
    return data


def calculate_rolling_correlations(
    data: pd.DataFrame,
    window: int = ROLLING_WINDOW
) -> pd.DataFrame:
    """
    Calculate rolling correlations between weekly stock returns and macro variables.

    Each result represents the rolling correlation for one ticker, one date
    and one macroeconomic variable.
    """
    rows = []

    required_base_cols = ["Date", "Ticker", "weekly_return"]

    for col in required_base_cols:
        if col not in data.columns:
            raise ValueError(f"Required column missing: {col}")

    available_macro_vars = [
        var for var in MACRO_VARIABLES
        if var in data.columns
    ]

    if not available_macro_vars:
        raise ValueError("No macro variables found in stock_macro_weekly.csv")

    bank_tickers = sorted([
        ticker for ticker in data["Ticker"].dropna().unique()
        if ticker != "XU100.IS"
    ])

    for ticker in bank_tickers:
        ticker_data = (
            data[data["Ticker"] == ticker]
            .sort_values("Date")
            .copy()
        )

        for macro_var in available_macro_vars:
            temp = ticker_data[
                ["Date", "Ticker", "weekly_return", macro_var]
            ].dropna()

            if temp.shape[0] < window:
                continue

            rolling_corr = (
                temp["weekly_return"]
                .rolling(window=window)
                .corr(temp[macro_var])
            )

            result = temp[["Date", "Ticker"]].copy()
            result["macro_variable"] = macro_var
            result["rolling_window"] = window
            result["rolling_correlation"] = rolling_corr

            result = result.dropna(subset=["rolling_correlation"])

            rows.append(result)

    if not rows:
        return pd.DataFrame(
            columns=[
                "Date",
                "Ticker",
                "macro_variable",
                "rolling_window",
                "rolling_correlation"
            ]
        )

    return pd.concat(rows, ignore_index=True)


def create_rolling_correlation_summary(
    rolling_df: pd.DataFrame
) -> pd.DataFrame:
    """Create summary statistics for rolling correlations."""
    if rolling_df.empty:
        return pd.DataFrame()

    summary = (
        rolling_df
        .groupby(["Ticker", "macro_variable"], as_index=False)
        .agg(
            observations=("rolling_correlation", "count"),
            mean_rolling_correlation=("rolling_correlation", "mean"),
            median_rolling_correlation=("rolling_correlation", "median"),
            min_rolling_correlation=("rolling_correlation", "min"),
            max_rolling_correlation=("rolling_correlation", "max"),
            latest_date=("Date", "max")
        )
    )

    latest_values = (
        rolling_df
        .sort_values("Date")
        .groupby(["Ticker", "macro_variable"], as_index=False)
        .tail(1)
        [["Ticker", "macro_variable", "rolling_correlation"]]
        .rename(columns={"rolling_correlation": "latest_rolling_correlation"})
    )

    positive_share = (
        rolling_df
        .assign(is_positive=lambda df: df["rolling_correlation"] > 0)
        .groupby(["Ticker", "macro_variable"], as_index=False)
        .agg(
            positive_correlation_share=("is_positive", "mean")
        )
    )

    summary = summary.merge(
        latest_values,
        on=["Ticker", "macro_variable"],
        how="left"
    )

    summary = summary.merge(
        positive_share,
        on=["Ticker", "macro_variable"],
        how="left"
    )

    summary["relationship_stability"] = summary["positive_correlation_share"].apply(
        classify_relationship_stability
    )

    return summary


def classify_relationship_stability(value: float) -> str:
    """
    Classify whether the rolling relationship is mostly positive,
    mostly negative or unstable.
    """
    if pd.isna(value):
        return "not_available"

    if value >= 0.75:
        return "mostly_positive"

    if value <= 0.25:
        return "mostly_negative"

    return "unstable_or_time_varying"


def run_rolling_analysis():
    """Run rolling macro sensitivity analysis."""
    root = get_project_root()
    output_dir = ensure_directory(root / "outputs")

    data = load_stock_macro_data()

    rolling_df = calculate_rolling_correlations(
        data=data,
        window=ROLLING_WINDOW
    )

    rolling_output_path = output_dir / "rolling_macro_correlation.csv"
    rolling_df.to_csv(
        rolling_output_path,
        index=False,
        encoding="utf-8-sig"
    )

    summary_df = create_rolling_correlation_summary(rolling_df)

    summary_output_path = output_dir / "rolling_macro_correlation_summary.csv"
    summary_df.to_csv(
        summary_output_path,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Rolling macro correlation saved to: {rolling_output_path}")
    print(f"Rolling macro correlation summary saved to: {summary_output_path}")

    print("\nRolling correlation summary:")
    if summary_df.empty:
        print("No rolling correlation summary generated.")
    else:
        print(summary_df.head(30))


if __name__ == "__main__":
    run_rolling_analysis()