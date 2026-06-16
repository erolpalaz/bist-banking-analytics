from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"


STOCK_WEEKLY_PATH = PROCESSED_DIR / "stock_prices_weekly.csv"
STOCK_MACRO_PATH = PROCESSED_DIR / "stock_macro_weekly.csv"

RISK_METRICS_PATH = OUTPUTS_DIR / "risk_metrics.csv"
RISK_SCORES_PATH = OUTPUTS_DIR / "risk_scores.csv"

MACRO_CORR_PATH = OUTPUTS_DIR / "macro_correlation_all_variables.csv"
MACRO_MODEL_SUMMARY_PATH = OUTPUTS_DIR / "macro_model_summary.csv"
FUNDING_SUMMARY_PATH = OUTPUTS_DIR / "funding_cost_change_summary.csv"

CORE_USD_PATH = OUTPUTS_DIR / "macro_regression_core_usd_model.csv"
CORE_EUR_PATH = OUTPUTS_DIR / "macro_regression_core_eur_model.csv"
FUNDING_LEVEL_PATH = OUTPUTS_DIR / "macro_regression_funding_cost_level_model.csv"
FUNDING_CHANGE_PATH = OUTPUTS_DIR / "macro_regression_funding_cost_change_model.csv"


# --------------------------------------------------
# Streamlit config
# --------------------------------------------------

st.set_page_config(
    page_title="BIST Banking Analytics",
    page_icon="📊",
    layout="wide"
)


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

@st.cache_data
def load_csv(path: Path) -> pd.DataFrame:
    """Load CSV file with Date parsing when available."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    df = pd.read_csv(path)

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])

    return df


def load_optional_csv(path: Path) -> pd.DataFrame | None:
    """Load CSV if it exists, otherwise return None."""
    if not path.exists():
        return None

    df = pd.read_csv(path)

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])

    return df


def format_percentage(value):
    """Format decimal values as percentage."""
    if pd.isna(value):
        return "-"

    return f"{value:.2%}"


def format_number(value, digits=4):
    """Format numeric values safely."""
    if pd.isna(value):
        return "-"

    return f"{value:.{digits}f}"


def get_price_column(df: pd.DataFrame) -> str:
    """Choose adjusted close if available, otherwise close."""
    if "Adj_Close" in df.columns:
        return "Adj_Close"

    if "Close" in df.columns:
        return "Close"

    raise ValueError("Neither Adj_Close nor Close column found.")


def normalize_price_series(series: pd.Series) -> pd.Series:
    """Normalize a price series to base 100."""
    clean_series = series.dropna()

    if clean_series.empty:
        return pd.Series(index=series.index, dtype="float64")

    base_value = clean_series.iloc[0]

    if base_value == 0:
        return pd.Series(index=series.index, dtype="float64")

    return series / base_value * 100


def add_normalized_price(df: pd.DataFrame) -> pd.DataFrame:
    """Create normalized price index with base 100."""
    price_col = get_price_column(df)

    result = df.copy()
    result = result.sort_values(["Ticker", "Date"])

    result["normalized_price"] = result.groupby("Ticker")[price_col].transform(
        normalize_price_series
    )

    return result


def display_missing_file_warning(files: list[Path], command: str):
    """Show missing file warning."""
    missing = [path.name for path in files if not path.exists()]

    if missing:
        st.warning(
            "Required output files are missing.\n\n"
            f"Missing files: {missing}\n\n"
            "Run this command in terminal:\n\n"
            f"`{command}`"
        )
        st.stop()


def make_display_table(df: pd.DataFrame) -> pd.DataFrame:
    """Round numeric columns for cleaner display and remove duplicate columns."""
    result = df.copy()

    # Prevent duplicate-column errors in pandas/Streamlit display
    result = result.loc[:, ~result.columns.duplicated()].copy()

    for col in result.columns:
        if pd.api.types.is_numeric_dtype(result[col]):
            result[col] = result[col].round(4)

    return result


def get_available_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Return the first available column from a candidate list."""
    for col in candidates:
        if col in df.columns:
            return col

    return None


def show_unavailable_metric(column_name: str):
    """Show metric placeholder when a required column is unavailable."""
    st.metric(column_name, "Not Available", "Check output file")


# --------------------------------------------------
# Load main data
# --------------------------------------------------

try:
    stock_data = load_csv(STOCK_WEEKLY_PATH)
except FileNotFoundError:
    st.error(
        "Weekly stock data not found. Run:\n\n"
        "`python -m src.data_loader`\n\n"
        "`python -m src.preprocessing`"
    )
    st.stop()


risk_metrics = load_optional_csv(RISK_METRICS_PATH)
risk_scores = load_optional_csv(RISK_SCORES_PATH)

stock_data = add_normalized_price(stock_data)

all_tickers = sorted(stock_data["Ticker"].unique())
bank_tickers = [ticker for ticker in all_tickers if ticker != "XU100.IS"]


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.title("BIST Banking Analytics")

page = st.sidebar.selectbox(
    "Select Page",
    [
        "Market Overview",
        "Stock Comparison",
        "Risk Metrics",
        "Risk Scores",
        "Macro Sensitivity"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("BIST Banking Analytics Dashboard")


# --------------------------------------------------
# Page 1: Market Overview
# --------------------------------------------------

if page == "Market Overview":
    st.title("BIST Banking Analytics Dashboard")
    st.caption(
        "Weekly market performance, risk metrics and macro sensitivity analysis "
        "for selected BIST banking stocks."
    )

    if risk_metrics is not None and not risk_metrics.empty:
        bank_metrics = risk_metrics[risk_metrics["Ticker"] != "XU100.IS"].copy()

        return_col = get_available_column(
            bank_metrics,
            ["annualized_return", "annual_return", "ann_return"]
        )

        volatility_col = get_available_column(
            bank_metrics,
            ["annualized_volatility", "annual_volatility", "ann_volatility"]
        )

        sharpe_col = get_available_column(
            bank_metrics,
            ["sharpe_ratio", "sharpe"]
        )

        beta_col = get_available_column(
            bank_metrics,
            ["beta", "market_beta", "beta_to_bist100", "bist100_beta", "benchmark_beta"]
        )

        col1, col2, col3, col4 = st.columns(4)

        if return_col is not None:
            highest_return = bank_metrics.loc[bank_metrics[return_col].idxmax()]
            col1.metric(
                "Highest Annualized Return",
                highest_return["Ticker"],
                format_percentage(highest_return[return_col])
            )
        else:
            col1.metric("Highest Annualized Return", "Not Available", "Check risk metrics")

        if volatility_col is not None:
            highest_volatility = bank_metrics.loc[bank_metrics[volatility_col].idxmax()]
            col2.metric(
                "Highest Volatility",
                highest_volatility["Ticker"],
                format_percentage(highest_volatility[volatility_col])
            )
        else:
            col2.metric("Highest Volatility", "Not Available", "Check risk metrics")

        if sharpe_col is not None:
            highest_sharpe = bank_metrics.loc[bank_metrics[sharpe_col].idxmax()]
            col3.metric(
                "Highest Sharpe Ratio",
                highest_sharpe["Ticker"],
                format_number(highest_sharpe[sharpe_col], 2)
            )
        else:
            col3.metric("Highest Sharpe Ratio", "Not Available", "Check risk metrics")

        if beta_col is not None:
            highest_beta = bank_metrics.loc[bank_metrics[beta_col].idxmax()]
            col4.metric(
                "Highest Beta",
                highest_beta["Ticker"],
                format_number(highest_beta[beta_col], 2)
            )
        else:
            col4.metric("Highest Beta", "Not Available", "Beta column missing")

    else:
        st.info(
            "Risk metrics file is not available yet. Run `python -m src.export_outputs` "
            "to show KPI cards."
        )

    st.subheader("Normalized Price Performance")

    selected_tickers = st.multiselect(
        "Select tickers",
        options=all_tickers,
        default=bank_tickers
    )

    filtered = stock_data[stock_data["Ticker"].isin(selected_tickers)].copy()

    if filtered.empty:
        st.warning("Please select at least one ticker.")
        st.stop()

    fig = px.line(
        filtered,
        x="Date",
        y="normalized_price",
        color="Ticker",
        title="Normalized Price Index - Base 100"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Weekly Return Distribution")

    return_data = filtered.dropna(subset=["weekly_return"]).copy()

    fig_return = px.box(
        return_data,
        x="Ticker",
        y="weekly_return",
        title="Weekly Return Distribution by Ticker"
    )

    st.plotly_chart(fig_return, use_container_width=True)


# --------------------------------------------------
# Page 2: Stock Comparison
# --------------------------------------------------

elif page == "Stock Comparison":
    st.title("Stock Comparison")

    selected_tickers = st.multiselect(
        "Select tickers to compare",
        options=all_tickers,
        default=bank_tickers[:3]
    )

    if not selected_tickers:
        st.warning("Please select at least one ticker.")
        st.stop()

    filtered = stock_data[stock_data["Ticker"].isin(selected_tickers)].copy()

    st.subheader("Normalized Price Comparison")

    fig = px.line(
        filtered,
        x="Date",
        y="normalized_price",
        color="Ticker",
        title="Normalized Price Index - Base 100"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Return Statistics")

    summary = (
        filtered
        .groupby("Ticker")
        .agg(
            start_date=("Date", "min"),
            end_date=("Date", "max"),
            mean_weekly_return=("weekly_return", "mean"),
            weekly_volatility=("weekly_return", "std"),
            observations=("weekly_return", "count")
        )
        .reset_index()
    )

    st.dataframe(
        make_display_table(summary),
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# Page 3: Risk Metrics
# --------------------------------------------------

elif page == "Risk Metrics":
    st.title("Risk Metrics")

    display_missing_file_warning(
        files=[RISK_METRICS_PATH],
        command="python -m src.export_outputs"
    )

    risk_metrics = load_csv(RISK_METRICS_PATH)

    bank_metrics = risk_metrics[risk_metrics["Ticker"] != "XU100.IS"].copy()

    st.subheader("Risk Metrics Table")

    st.dataframe(
        make_display_table(bank_metrics),
        use_container_width=True,
        hide_index=True
    )

    volatility_col = get_available_column(
        bank_metrics,
        ["annualized_volatility", "annual_volatility", "ann_volatility"]
    )

    drawdown_col = get_available_column(
        bank_metrics,
        ["max_drawdown", "maximum_drawdown", "drawdown"]
    )

    beta_col = get_available_column(
        bank_metrics,
        ["beta", "market_beta", "beta_to_bist100", "bist100_beta", "benchmark_beta"]
    )

    if volatility_col is not None:
        st.subheader("Annualized Volatility")

        fig_vol = px.bar(
            bank_metrics.sort_values(volatility_col, ascending=False),
            x="Ticker",
            y=volatility_col,
            title="Annualized Volatility by Ticker"
        )

        st.plotly_chart(fig_vol, use_container_width=True)
    else:
        st.info("Annualized volatility column was not found in risk_metrics.csv.")

    if drawdown_col is not None:
        st.subheader("Maximum Drawdown")

        fig_dd = px.bar(
            bank_metrics.sort_values(drawdown_col),
            x="Ticker",
            y=drawdown_col,
            title="Maximum Drawdown by Ticker"
        )

        st.plotly_chart(fig_dd, use_container_width=True)
    else:
        st.info("Maximum drawdown column was not found in risk_metrics.csv.")

    st.subheader("Beta to BIST 100")

    if beta_col is not None:
        fig_beta = px.bar(
            bank_metrics.sort_values(beta_col, ascending=False),
            x="Ticker",
            y=beta_col,
            title="Beta to BIST 100"
        )

        st.plotly_chart(fig_beta, use_container_width=True)
    else:
        st.info(
            "Beta column was not found in risk_metrics.csv. "
            "The dashboard will continue without the beta chart. "
            "To restore beta analysis, check `src/risk_metrics.py` and run "
            "`python -m src.export_outputs` again."
        )


# --------------------------------------------------
# Page 4: Risk Scores
# --------------------------------------------------

elif page == "Risk Scores":
    st.title("Risk Scores")

    display_missing_file_warning(
        files=[RISK_SCORES_PATH],
        command="python -m src.export_outputs"
    )

    risk_scores = load_csv(RISK_SCORES_PATH)

    bank_scores = risk_scores[risk_scores["Ticker"] != "XU100.IS"].copy()

    st.subheader("Risk and Performance Score Table")

    st.dataframe(
        make_display_table(bank_scores),
        use_container_width=True,
        hide_index=True
    )

    if "risk_score" in bank_scores.columns:
        st.subheader("Risk Score")

        fig_risk = px.bar(
            bank_scores.sort_values("risk_score", ascending=False),
            x="Ticker",
            y="risk_score",
            color="risk_category" if "risk_category" in bank_scores.columns else None,
            title="Risk Score by Ticker"
        )

        st.plotly_chart(fig_risk, use_container_width=True)
    else:
        st.info("risk_score column was not found in risk_scores.csv.")

    if "performance_score" in bank_scores.columns:
        st.subheader("Performance Score")

        fig_perf = px.bar(
            bank_scores.sort_values("performance_score", ascending=False),
            x="Ticker",
            y="performance_score",
            title="Performance Score by Ticker"
        )

        st.plotly_chart(fig_perf, use_container_width=True)
    else:
        st.info("performance_score column was not found in risk_scores.csv.")


# --------------------------------------------------
# Page 5: Macro Sensitivity
# --------------------------------------------------

elif page == "Macro Sensitivity":
    st.title("Macro Sensitivity Analysis")

    st.caption(
        "This page analyzes the statistical association between weekly banking stock returns "
        "and macroeconomic variables. Results indicate sensitivity/association, not causality."
    )

    required_files = [
        MACRO_CORR_PATH,
        MACRO_MODEL_SUMMARY_PATH,
        FUNDING_SUMMARY_PATH,
        CORE_USD_PATH,
        CORE_EUR_PATH,
        FUNDING_LEVEL_PATH,
        FUNDING_CHANGE_PATH
    ]

    missing_files = [path.name for path in required_files if not path.exists()]

    if missing_files:
        st.warning(
            "Macro analysis output files are missing. Run the following commands:\n\n"
            "`python -m src.macro_loader`\n\n"
            "`python -m src.merge_macro`\n\n"
            "`python -m src.macro_analysis`\n\n"
            f"Missing files: {missing_files}"
        )
        st.stop()

    corr = load_csv(MACRO_CORR_PATH)
    model_summary = load_csv(MACRO_MODEL_SUMMARY_PATH)
    funding_summary = load_csv(FUNDING_SUMMARY_PATH)

    core_usd = load_csv(CORE_USD_PATH)
    core_eur = load_csv(CORE_EUR_PATH)
    funding_level = load_csv(FUNDING_LEVEL_PATH)
    funding_change = load_csv(FUNDING_CHANGE_PATH)

    bank_corr = corr[corr["Ticker"] != "XU100.IS"].copy()

    st.subheader("Model Specifications")

    st.dataframe(
        make_display_table(model_summary),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Funding Cost Change Summary")

    col1, col2, col3, col4 = st.columns(4)

    total_weeks = int(funding_summary.loc[0, "total_weeks"])
    change_weeks = int(funding_summary.loc[0, "funding_cost_change_weeks"])
    no_change_weeks = int(funding_summary.loc[0, "no_change_weeks"])
    change_ratio = funding_summary.loc[0, "funding_cost_change_week_ratio"]

    col1.metric("Total Weeks", total_weeks)
    col2.metric("Change Weeks", change_weeks)
    col3.metric("No Change Weeks", no_change_weeks)
    col4.metric("Change Ratio", f"{change_ratio:.1%}")

    st.info(
        "Funding cost refers to CBRT weighted average funding cost, not the official one-week repo policy rate. "
        "It is used as an operational monetary/funding condition indicator."
    )

    st.subheader("Macro Correlation Analysis")

    selected_macro = st.selectbox(
        "Select macro variable",
        options=sorted(bank_corr["macro_variable"].unique())
    )

    selected_corr = (
        bank_corr[bank_corr["macro_variable"] == selected_macro]
        .sort_values("correlation")
        .copy()
    )

    fig_corr = px.bar(
        selected_corr,
        x="Ticker",
        y="correlation",
        title=f"Correlation Between Weekly Returns and {selected_macro}"
    )

    st.plotly_chart(fig_corr, use_container_width=True)

    st.dataframe(
        make_display_table(selected_corr),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Regression Results")

    regression_choice = st.selectbox(
        "Select regression model",
        options=[
            "Core USD Model",
            "Core EUR Model",
            "Funding Cost Level Model",
            "Funding Cost Change Model"
        ]
    )

    if regression_choice == "Core USD Model":
        selected_reg = core_usd.copy()
        explanation = (
            "Core USD Model uses USD/TRY weekly change and CPI YoY change. "
            "It measures basic exchange-rate and inflation-regime sensitivity."
        )

    elif regression_choice == "Core EUR Model":
        selected_reg = core_eur.copy()
        explanation = (
            "Core EUR Model uses EUR/TRY weekly change and CPI YoY change. "
            "It is an alternative exchange-rate sensitivity specification."
        )

    elif regression_choice == "Funding Cost Level Model":
        selected_reg = funding_level.copy()
        explanation = (
            "Funding Cost Level Model uses USD/TRY weekly change, CPI YoY change "
            "and CBRT weighted average funding cost level. Funding cost level is interpreted "
            "as the prevailing monetary/funding environment."
        )

    else:
        selected_reg = funding_change.copy()
        explanation = (
            "Funding Cost Change Model uses USD/TRY weekly change, CPI YoY change "
            "and weekly changes in CBRT weighted average funding cost. This captures short-term "
            "changes in funding conditions."
        )

    st.caption(explanation)

    base_display_cols = [
        "model_name",
        "Ticker",
        "observations",
        "r_squared",
        "adj_r_squared",
        "f_pvalue"
    ]

    coefficient_cols = [
        col for col in selected_reg.columns
        if (col.endswith("_coef") or col.endswith("_pvalue"))
        and col not in base_display_cols
    ]

    display_cols = [
        col for col in base_display_cols
        if col in selected_reg.columns
    ]

    display_cols = display_cols + coefficient_cols

    # Remove duplicate columns while preserving order
    display_cols = list(dict.fromkeys(display_cols))

    selected_reg_display = selected_reg.loc[:, display_cols].copy()

    st.dataframe(
        make_display_table(selected_reg_display),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Interpretation Guide")

    st.markdown(
        """
        - Negative exchange-rate coefficients suggest that banking stock returns tended to weaken during weeks of TRY depreciation.
        - CPI YoY change represents the inflation regime rather than a weekly inflation shock.
        - Funding cost level represents the monetary/funding environment.
        - Funding cost weekly difference represents short-term changes in funding conditions.
        - High p-values indicate weak statistical evidence in the selected model.
        - These results should not be interpreted as causal effects.
        """
    )