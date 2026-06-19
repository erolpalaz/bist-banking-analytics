from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="BIST Banking Analytics",
    page_icon="📊",
    layout="wide"
)


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = ROOT_DIR / "outputs"


PATHS = {
    "stock_weekly": PROCESSED_DIR / "stock_prices_weekly.csv",
    "stock_macro_weekly": PROCESSED_DIR / "stock_macro_weekly.csv",
    "risk_metrics": OUTPUTS_DIR / "risk_metrics.csv",
    "risk_scores": OUTPUTS_DIR / "risk_scores.csv",
    "macro_correlation": OUTPUTS_DIR / "macro_correlation_all_variables.csv",
    "macro_model_summary": OUTPUTS_DIR / "macro_model_summary.csv",
    "macro_model_diagnostics": OUTPUTS_DIR / "macro_model_diagnostics.csv",
    "macro_vif_results": OUTPUTS_DIR / "macro_vif_results.csv",
    "robust_summary": OUTPUTS_DIR / "robust_macro_regression_summary.csv",
    "robust_all_models": OUTPUTS_DIR / "robust_macro_regression_all_models.csv",
    "rolling_macro_correlation": OUTPUTS_DIR / "rolling_macro_correlation.csv",
    "rolling_macro_correlation_summary": OUTPUTS_DIR / "rolling_macro_correlation_summary.csv",
}


REGRESSION_FILE_MAP = {
    "core_usd_model": OUTPUTS_DIR / "macro_regression_core_usd_model.csv",
    "core_eur_model": OUTPUTS_DIR / "macro_regression_core_eur_model.csv",
    "funding_cost_level_model": OUTPUTS_DIR / "macro_regression_funding_cost_level_model.csv",
    "funding_cost_change_model": OUTPUTS_DIR / "macro_regression_funding_cost_change_model.csv",
}


ROBUST_FILE_MAP = {
    "core_usd_model": OUTPUTS_DIR / "robust_macro_regression_core_usd_model.csv",
    "core_eur_model": OUTPUTS_DIR / "robust_macro_regression_core_eur_model.csv",
    "funding_cost_level_model": OUTPUTS_DIR / "robust_macro_regression_funding_cost_level_model.csv",
    "funding_cost_change_model": OUTPUTS_DIR / "robust_macro_regression_funding_cost_change_model.csv",
}


def file_is_available(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


@st.cache_data
def load_csv(path: Path, parse_dates: list[str] | None = None) -> pd.DataFrame:
    if not file_is_available(path):
        return pd.DataFrame()

    try:
        return pd.read_csv(path, parse_dates=parse_dates)
    except Exception:
        return pd.DataFrame()


def show_missing_file_warning(path: Path, command: str | None = None):
    st.warning(f"Required file is missing or empty: `{path}`")

    if command:
        st.code(command, language="bash")


def get_available_columns(df: pd.DataFrame, columns: list[str]) -> list[str]:
    available = []
    seen = set()

    for col in columns:
        if col in df.columns and col not in seen:
            available.append(col)
            seen.add(col)

    return available


def format_percentage(value):
    if pd.isna(value):
        return ""

    return f"{value:.2%}"


def format_decimal(value):
    if pd.isna(value):
        return ""

    return f"{value:.4f}"


def clean_warning_text(value):
    if pd.isna(value):
        return "not_available"

    return str(value).replace(";", "; ")


def split_diagnostic_warnings(warning_series: pd.Series) -> pd.DataFrame:
    """
    Split combined diagnostic warning strings into individual warning counts.
    """
    warning_items = []

    for warning_text in warning_series.fillna("not_available"):
        parts = str(warning_text).split(";")

        for part in parts:
            cleaned = part.strip()

            if cleaned:
                warning_items.append(cleaned)

    if not warning_items:
        return pd.DataFrame(columns=["diagnostic_warning", "count"])

    warning_counts = (
        pd.Series(warning_items)
        .value_counts()
        .reset_index()
    )

    warning_counts.columns = ["diagnostic_warning", "count"]

    return warning_counts


def create_cumulative_return_table(stock_weekly: pd.DataFrame) -> pd.DataFrame:
    if stock_weekly.empty or "weekly_return" not in stock_weekly.columns:
        return pd.DataFrame()

    df = stock_weekly[["Date", "Ticker", "weekly_return"]].copy()
    df = df.dropna(subset=["Date", "Ticker", "weekly_return"])

    returns = df.pivot_table(
        index="Date",
        columns="Ticker",
        values="weekly_return",
        aggfunc="mean"
    ).sort_index()

    cumulative = (1 + returns.fillna(0)).cumprod() - 1
    cumulative = cumulative.reset_index()

    return cumulative


def page_market_overview():
    st.title("Market Overview")

    stock_weekly = load_csv(PATHS["stock_weekly"], parse_dates=["Date"])
    risk_metrics = load_csv(PATHS["risk_metrics"])

    if stock_weekly.empty:
        show_missing_file_warning(
            PATHS["stock_weekly"],
            "python -m src.data_loader\npython -m src.preprocessing"
        )
        return

    st.markdown(
        """
        This page provides a general overview of selected BIST banking stocks and the BIST 100 benchmark.
        """
    )

    tickers = sorted(stock_weekly["Ticker"].dropna().unique().tolist())

    selected_tickers = st.multiselect(
        "Select tickers",
        options=tickers,
        default=tickers
    )

    filtered = stock_weekly[stock_weekly["Ticker"].isin(selected_tickers)].copy()

    cumulative = create_cumulative_return_table(filtered)

    if not cumulative.empty:
        cumulative_long = cumulative.melt(
            id_vars="Date",
            var_name="Ticker",
            value_name="Cumulative Return"
        )

        fig = px.line(
            cumulative_long,
            x="Date",
            y="Cumulative Return",
            color="Ticker",
            title="Cumulative Weekly Return"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Latest Weekly Data")

    display_cols = get_available_columns(
        filtered,
        ["Date", "Ticker", "Open", "High", "Low", "Close", "Adj_Close", "Volume", "weekly_return"]
    )

    st.dataframe(
        filtered[display_cols].sort_values(["Date", "Ticker"], ascending=[False, True]).head(50),
        use_container_width=True
    )

    if not risk_metrics.empty:
        st.subheader("Risk Metrics Snapshot")

        st.dataframe(risk_metrics, use_container_width=True)


def page_stock_comparison():
    st.title("Stock Comparison")

    stock_weekly = load_csv(PATHS["stock_weekly"], parse_dates=["Date"])

    if stock_weekly.empty:
        show_missing_file_warning(
            PATHS["stock_weekly"],
            "python -m src.data_loader\npython -m src.preprocessing"
        )
        return

    tickers = sorted(stock_weekly["Ticker"].dropna().unique().tolist())

    selected_tickers = st.multiselect(
        "Select stocks to compare",
        options=tickers,
        default=[ticker for ticker in tickers if ticker != "XU100.IS"][:4]
    )

    filtered = stock_weekly[stock_weekly["Ticker"].isin(selected_tickers)].copy()

    metric_options = get_available_columns(
        filtered,
        ["Close", "Adj_Close", "weekly_return", "Volume"]
    )

    selected_metric = st.selectbox(
        "Select comparison metric",
        options=metric_options
    )

    fig = px.line(
        filtered,
        x="Date",
        y=selected_metric,
        color="Ticker",
        title=f"{selected_metric} Comparison"
    )

    st.plotly_chart(fig, use_container_width=True)

    cumulative = create_cumulative_return_table(filtered)

    if not cumulative.empty:
        cumulative_long = cumulative.melt(
            id_vars="Date",
            var_name="Ticker",
            value_name="Cumulative Return"
        )

        fig_cum = px.line(
            cumulative_long,
            x="Date",
            y="Cumulative Return",
            color="Ticker",
            title="Cumulative Return Comparison"
        )

        st.plotly_chart(fig_cum, use_container_width=True)


def page_risk_metrics():
    st.title("Risk Metrics")

    risk_metrics = load_csv(PATHS["risk_metrics"])

    if risk_metrics.empty:
        show_missing_file_warning(
            PATHS["risk_metrics"],
            "python -m src.export_outputs"
        )
        return

    st.markdown(
        """
        This page presents risk and performance metrics for selected BIST banking stocks.
        """
    )

    st.dataframe(risk_metrics, use_container_width=True)

    chart_cols = get_available_columns(
        risk_metrics,
        [
            "annualized_return",
            "annualized_volatility",
            "max_drawdown",
            "sharpe_ratio",
            "beta"
        ]
    )

    if chart_cols:
        selected_metric = st.selectbox(
            "Select risk metric",
            options=chart_cols
        )

        fig = px.bar(
            risk_metrics.sort_values(selected_metric),
            x="Ticker",
            y=selected_metric,
            title=f"{selected_metric} by Ticker"
        )

        st.plotly_chart(fig, use_container_width=True)


def page_risk_scores():
    st.title("Risk Scores")

    risk_scores = load_csv(PATHS["risk_scores"])

    if risk_scores.empty:
        show_missing_file_warning(
            PATHS["risk_scores"],
            "python -m src.export_outputs"
        )
        return

    st.markdown(
        """
        This page presents composite risk and performance scores.
        """
    )

    st.dataframe(risk_scores, use_container_width=True)

    if "risk_score" in risk_scores.columns:
        color_col = "risk_category" if "risk_category" in risk_scores.columns else None

        fig_risk = px.bar(
            risk_scores.sort_values("risk_score", ascending=False),
            x="Ticker",
            y="risk_score",
            color=color_col,
            title="Risk Score by Ticker"
        )

        st.plotly_chart(fig_risk, use_container_width=True)

    if "performance_score" in risk_scores.columns:
        fig_perf = px.bar(
            risk_scores.sort_values("performance_score", ascending=False),
            x="Ticker",
            y="performance_score",
            title="Performance Score by Ticker"
        )

        st.plotly_chart(fig_perf, use_container_width=True)


def page_macro_sensitivity():
    st.title("Macro Sensitivity")

    correlation = load_csv(PATHS["macro_correlation"])
    model_summary = load_csv(PATHS["macro_model_summary"])

    if correlation.empty:
        show_missing_file_warning(
            PATHS["macro_correlation"],
            "python -m src.macro_loader\npython -m src.merge_macro\npython -m src.macro_analysis"
        )
        return

    st.markdown(
        """
        This page presents macro correlation and OLS macro regression results.
        """
    )

    st.subheader("Macro Correlation Results")

    tickers = sorted(correlation["Ticker"].dropna().unique().tolist())
    macro_vars = sorted(correlation["macro_variable"].dropna().unique().tolist())

    selected_tickers = st.multiselect(
        "Select tickers",
        options=tickers,
        default=tickers
    )

    selected_macro_vars = st.multiselect(
        "Select macro variables",
        options=macro_vars,
        default=macro_vars
    )

    corr_filtered = correlation[
        correlation["Ticker"].isin(selected_tickers)
        & correlation["macro_variable"].isin(selected_macro_vars)
    ].copy()

    if not corr_filtered.empty:
        fig_corr = px.bar(
            corr_filtered,
            x="Ticker",
            y="correlation",
            color="macro_variable",
            barmode="group",
            title="Correlation Between Weekly Returns and Macro Variables"
        )

        st.plotly_chart(fig_corr, use_container_width=True)

        st.dataframe(corr_filtered, use_container_width=True)

    st.subheader("Macro Model Specifications")

    if not model_summary.empty:
        st.dataframe(model_summary, use_container_width=True)

    st.subheader("OLS Regression Results")

    available_models = [
        model_name for model_name, path in REGRESSION_FILE_MAP.items()
        if file_is_available(path)
    ]

    if not available_models:
        st.warning("No OLS regression output files found.")
        return

    selected_model = st.selectbox(
        "Select OLS model",
        options=available_models
    )

    regression_df = load_csv(REGRESSION_FILE_MAP[selected_model])

    if regression_df.empty:
        st.warning("Selected regression result file could not be loaded.")
        return

    st.dataframe(regression_df, use_container_width=True)

    coefficient_cols = [
        col for col in regression_df.columns
        if col.endswith("_coef") and not col.startswith("const")
    ]

    coefficient_rows = []

    for _, row in regression_df.iterrows():
        for coef_col in coefficient_cols:
            variable = coef_col.replace("_coef", "")
            pvalue_col = f"{variable}_pvalue"

            coefficient_rows.append(
                {
                    "Ticker": row.get("Ticker"),
                    "variable": variable,
                    "coefficient": row.get(coef_col),
                    "pvalue": row.get(pvalue_col)
                }
            )

    coef_df = pd.DataFrame(coefficient_rows)

    if not coef_df.empty:
        fig_coef = px.bar(
            coef_df,
            x="Ticker",
            y="coefficient",
            color="variable",
            barmode="group",
            title=f"OLS Coefficients - {selected_model}"
        )

        st.plotly_chart(fig_coef, use_container_width=True)

        st.dataframe(coef_df, use_container_width=True)


def page_model_diagnostics():
    st.title("Model Diagnostics")

    diagnostics = load_csv(PATHS["macro_model_diagnostics"])
    vif_results = load_csv(PATHS["macro_vif_results"])

    if diagnostics.empty:
        show_missing_file_warning(
            PATHS["macro_model_diagnostics"],
            "python -m src.model_diagnostics"
        )
        return

    st.markdown(
        """
        This page evaluates macro regression models using diagnostic tests such as
        adjusted R-squared, F-test p-values, Durbin-Watson, Breusch-Pagan,
        Jarque-Bera and VIF.
        """
    )

    models = sorted(diagnostics["model_name"].dropna().unique().tolist())
    tickers = sorted(diagnostics["Ticker"].dropna().unique().tolist())

    col1, col2 = st.columns(2)

    with col1:
        selected_models = st.multiselect(
            "Select models",
            options=models,
            default=models
        )

    with col2:
        selected_tickers = st.multiselect(
            "Select tickers",
            options=tickers,
            default=tickers
        )

    filtered = diagnostics[
        diagnostics["model_name"].isin(selected_models)
        & diagnostics["Ticker"].isin(selected_tickers)
    ].copy()

    if filtered.empty:
        st.warning("No diagnostic results found for the selected filters.")
        return

    avg_adj_r2 = filtered["adj_r_squared"].mean() if "adj_r_squared" in filtered.columns else np.nan
    max_vif = filtered["max_vif"].max() if "max_vif" in filtered.columns else np.nan

    warning_count = 0

    if "diagnostic_warnings" in filtered.columns:
        warning_count = filtered[
            filtered["diagnostic_warnings"].fillna("") != "no_major_warning"
        ].shape[0]

    kpi1, kpi2, kpi3 = st.columns(3)

    with kpi1:
        st.metric("Average Adjusted R²", format_decimal(avg_adj_r2))

    with kpi2:
        st.metric("Maximum VIF", format_decimal(max_vif))

    with kpi3:
        st.metric("Models with Warnings", warning_count)

    st.subheader("Adjusted R-squared by Model and Ticker")

    if "adj_r_squared" in filtered.columns:
        fig_adj = px.bar(
            filtered,
            x="Ticker",
            y="adj_r_squared",
            color="model_name",
            barmode="group",
            title="Adjusted R-squared"
        )

        st.plotly_chart(fig_adj, use_container_width=True)

    st.subheader("Durbin-Watson Statistics")

    if "durbin_watson" in filtered.columns:
        fig_dw = px.bar(
            filtered,
            x="Ticker",
            y="durbin_watson",
            color="model_name",
            barmode="group",
            title="Durbin-Watson by Model"
        )

        st.plotly_chart(fig_dw, use_container_width=True)

    st.subheader("Diagnostic Warning Summary")

    if "diagnostic_warnings" in filtered.columns:
        warning_df = filtered.copy()
        warning_df["diagnostic_warnings"] = warning_df["diagnostic_warnings"].apply(clean_warning_text)

        warning_counts = split_diagnostic_warnings(warning_df["diagnostic_warnings"])

        if not warning_counts.empty:
            fig_warn = px.bar(
                warning_counts,
                x="diagnostic_warning",
                y="count",
                title="Diagnostic Warning Counts"
            )

            st.plotly_chart(fig_warn, use_container_width=True)

            st.dataframe(warning_counts, use_container_width=True)
        else:
            st.info("No diagnostic warnings available.")

    st.subheader("Diagnostics Table")

    display_cols = get_available_columns(
        filtered,
        [
            "model_name",
            "Ticker",
            "status",
            "observations",
            "r_squared",
            "adj_r_squared",
            "f_pvalue",
            "f_test_interpretation",
            "durbin_watson",
            "durbin_watson_interpretation",
            "breusch_pagan_pvalue",
            "breusch_pagan_interpretation",
            "jarque_bera_pvalue",
            "jarque_bera_interpretation",
            "max_vif",
            "mean_vif",
            "diagnostic_warnings"
        ]
    )

    st.dataframe(filtered[display_cols], use_container_width=True)

    st.subheader("VIF Results")

    if vif_results.empty:
        show_missing_file_warning(
            PATHS["macro_vif_results"],
            "python -m src.model_diagnostics"
        )
    else:
        vif_filtered = vif_results[
            vif_results["model_name"].isin(selected_models)
            & vif_results["Ticker"].isin(selected_tickers)
        ].copy()

        if not vif_filtered.empty:
            vif_chart_df = (
                vif_filtered
                .groupby(["model_name", "variable"], as_index=False)
                .agg(
                    max_vif=("vif", "max"),
                    mean_vif=("vif", "mean")
                )
            )

            fig_vif = px.bar(
                vif_chart_df,
                x="variable",
                y="max_vif",
                color="model_name",
                barmode="group",
                title="Maximum VIF by Variable and Model"
            )

            st.plotly_chart(fig_vif, use_container_width=True)

            st.markdown(
                """
                VIF values are aggregated using the maximum VIF across selected tickers.
                This prevents repeated ticker-level VIF rows from being visually summed in the chart.
                """
            )

            st.subheader("Aggregated VIF Table")

            st.dataframe(vif_chart_df, use_container_width=True)

            st.subheader("Ticker-level VIF Table")

            st.dataframe(vif_filtered, use_container_width=True)


def page_robust_results():
    st.title("Robust Results")

    robust_summary = load_csv(PATHS["robust_summary"])
    robust_all = load_csv(PATHS["robust_all_models"])

    if robust_summary.empty:
        show_missing_file_warning(
            PATHS["robust_summary"],
            "python -m src.robust_macro_regression"
        )
        return

    st.markdown(
        """
        This page presents macro regression results estimated with HC3 robust standard errors.
        Robust standard errors improve inference when heteroskedasticity may be present.
        """
    )

    models = sorted(robust_summary["model_name"].dropna().unique().tolist())
    tickers = sorted(robust_summary["Ticker"].dropna().unique().tolist())

    col1, col2 = st.columns(2)

    with col1:
        selected_models = st.multiselect(
            "Select models",
            options=models,
            default=models
        )

    with col2:
        selected_tickers = st.multiselect(
            "Select tickers",
            options=tickers,
            default=tickers
        )

    filtered_summary = robust_summary[
        robust_summary["model_name"].isin(selected_models)
        & robust_summary["Ticker"].isin(selected_tickers)
    ].copy()

    if filtered_summary.empty:
        st.warning("No robust regression results found for selected filters.")
        return

    st.subheader("Robust Inference Summary")

    st.dataframe(filtered_summary, use_container_width=True)

    st.subheader("Significant Variables at 5% Level")

    if "significant_5pct_variables" in filtered_summary.columns:
        sig5_counts = (
            filtered_summary["significant_5pct_variables"]
            .fillna("not_available")
            .value_counts()
            .reset_index()
        )

        sig5_counts.columns = ["significant_5pct_variables", "count"]

        fig_sig5 = px.bar(
            sig5_counts,
            x="significant_5pct_variables",
            y="count",
            title="5% Robust Significance Summary"
        )

        st.plotly_chart(fig_sig5, use_container_width=True)

    st.subheader("Strongest Variable by Absolute Robust t-value")

    if "strongest_variable_by_abs_tvalue" in filtered_summary.columns:
        strongest_counts = (
            filtered_summary["strongest_variable_by_abs_tvalue"]
            .fillna("not_available")
            .value_counts()
            .reset_index()
        )

        strongest_counts.columns = ["strongest_variable_by_abs_tvalue", "count"]

        fig_strongest = px.bar(
            strongest_counts,
            x="strongest_variable_by_abs_tvalue",
            y="count",
            title="Most Frequent Strongest Variable"
        )

        st.plotly_chart(fig_strongest, use_container_width=True)

    st.subheader("Detailed Robust Regression Results")

    available_models = [
        model_name for model_name, path in ROBUST_FILE_MAP.items()
        if file_is_available(path)
    ]

    if not available_models:
        st.warning("No detailed robust regression output files found.")
        return

    selected_model = st.selectbox(
        "Select detailed robust model",
        options=available_models
    )

    detailed = load_csv(ROBUST_FILE_MAP[selected_model])

    if detailed.empty:
        st.warning("Selected robust result file could not be loaded.")
        return

    detailed_tickers = sorted(detailed["Ticker"].dropna().unique().tolist())

    selected_detail_tickers = st.multiselect(
        "Select tickers for detailed robust output",
        options=detailed_tickers,
        default=detailed_tickers
    )

    detailed_filtered = detailed[detailed["Ticker"].isin(selected_detail_tickers)].copy()

    st.dataframe(detailed_filtered, use_container_width=True)

    variable_rows = []

    coef_cols = [
        col for col in detailed_filtered.columns
        if col.endswith("_coef") and not col.startswith("const")
    ]

    for _, row in detailed_filtered.iterrows():
        for coef_col in coef_cols:
            variable = coef_col.replace("_coef", "")
            robust_p_col = f"{variable}_robust_pvalue"
            robust_t_col = f"{variable}_robust_tvalue"
            robust_se_col = f"{variable}_robust_std_error"
            ci_lower_col = f"{variable}_robust_ci_lower"
            ci_upper_col = f"{variable}_robust_ci_upper"

            variable_rows.append(
                {
                    "Ticker": row.get("Ticker"),
                    "variable": variable,
                    "coefficient": row.get(coef_col),
                    "robust_std_error": row.get(robust_se_col),
                    "robust_tvalue": row.get(robust_t_col),
                    "robust_pvalue": row.get(robust_p_col),
                    "robust_ci_lower": row.get(ci_lower_col),
                    "robust_ci_upper": row.get(ci_upper_col)
                }
            )

    robust_coef_df = pd.DataFrame(variable_rows)

    if not robust_coef_df.empty:
        fig_robust_coef = px.bar(
            robust_coef_df,
            x="Ticker",
            y="coefficient",
            color="variable",
            barmode="group",
            title=f"Robust Coefficients - {selected_model}"
        )

        st.plotly_chart(fig_robust_coef, use_container_width=True)

        st.dataframe(robust_coef_df, use_container_width=True)


def page_rolling_macro_sensitivity():
    st.title("Rolling Macro Sensitivity")

    rolling_df = load_csv(PATHS["rolling_macro_correlation"], parse_dates=["Date"])
    summary_df = load_csv(PATHS["rolling_macro_correlation_summary"], parse_dates=["latest_date"])

    if rolling_df.empty or summary_df.empty:
        show_missing_file_warning(
            PATHS["rolling_macro_correlation"],
            "python -m src.rolling_analysis"
        )
        return

    st.markdown(
        """
        This page analyzes whether the relationship between weekly banking stock returns
        and macroeconomic variables changes over time.

        Rolling correlations are calculated using a 52-week window.
        """
    )

    tickers = sorted(rolling_df["Ticker"].dropna().unique().tolist())
    macro_vars = sorted(rolling_df["macro_variable"].dropna().unique().tolist())

    col1, col2 = st.columns(2)

    with col1:
        selected_tickers = st.multiselect(
            "Select tickers",
            options=tickers,
            default=tickers
        )

    with col2:
        selected_macro_vars = st.multiselect(
            "Select macro variables",
            options=macro_vars,
            default=["usd_try_weekly_change"] if "usd_try_weekly_change" in macro_vars else macro_vars[:1]
        )

    filtered = rolling_df[
        rolling_df["Ticker"].isin(selected_tickers)
        & rolling_df["macro_variable"].isin(selected_macro_vars)
    ].copy()

    summary_filtered = summary_df[
        summary_df["Ticker"].isin(selected_tickers)
        & summary_df["macro_variable"].isin(selected_macro_vars)
    ].copy()

    if filtered.empty:
        st.warning("No rolling correlation data found for selected filters.")
        return

    latest_mean = (
        summary_filtered["latest_rolling_correlation"].mean()
        if "latest_rolling_correlation" in summary_filtered.columns and not summary_filtered.empty
        else np.nan
    )

    mean_corr = (
        summary_filtered["mean_rolling_correlation"].mean()
        if "mean_rolling_correlation" in summary_filtered.columns and not summary_filtered.empty
        else np.nan
    )

    mostly_negative_count = 0

    if "relationship_stability" in summary_filtered.columns:
        mostly_negative_count = summary_filtered[
            summary_filtered["relationship_stability"] == "mostly_negative"
        ].shape[0]

    kpi1, kpi2, kpi3 = st.columns(3)

    with kpi1:
        st.metric("Average Rolling Correlation", format_decimal(mean_corr))

    with kpi2:
        st.metric("Latest Rolling Correlation", format_decimal(latest_mean))

    with kpi3:
        st.metric("Mostly Negative Relations", mostly_negative_count)

    st.subheader("Rolling Correlation Over Time")

    fig_line = px.line(
        filtered,
        x="Date",
        y="rolling_correlation",
        color="Ticker",
        line_dash="macro_variable",
        title="52-Week Rolling Correlation"
    )

    st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("Latest Rolling Correlation")

    if not summary_filtered.empty and "latest_rolling_correlation" in summary_filtered.columns:
        fig_latest = px.bar(
            summary_filtered.sort_values("latest_rolling_correlation"),
            x="Ticker",
            y="latest_rolling_correlation",
            color="macro_variable",
            barmode="group",
            title="Latest Rolling Correlation by Ticker"
        )

        st.plotly_chart(fig_latest, use_container_width=True)

    st.subheader("Relationship Stability Summary")

    if not summary_filtered.empty and "relationship_stability" in summary_filtered.columns:
        stability_counts = (
            summary_filtered["relationship_stability"]
            .value_counts()
            .reset_index()
        )

        stability_counts.columns = ["relationship_stability", "count"]

        fig_stability = px.bar(
            stability_counts,
            x="relationship_stability",
            y="count",
            title="Relationship Stability Counts"
        )

        st.plotly_chart(fig_stability, use_container_width=True)

        st.dataframe(stability_counts, use_container_width=True)

    st.subheader("Rolling Correlation Summary Table")

    summary_display_cols = get_available_columns(
        summary_filtered,
        [
            "Ticker",
            "macro_variable",
            "observations",
            "mean_rolling_correlation",
            "median_rolling_correlation",
            "min_rolling_correlation",
            "max_rolling_correlation",
            "latest_date",
            "latest_rolling_correlation",
            "positive_correlation_share",
            "relationship_stability"
        ]
    )

    st.dataframe(
        summary_filtered[summary_display_cols].sort_values(
            ["macro_variable", "Ticker"]
        ),
        use_container_width=True
    )

    st.subheader("Rolling Correlation Raw Data")

    raw_display_cols = get_available_columns(
        filtered,
        [
            "Date",
            "Ticker",
            "macro_variable",
            "rolling_window",
            "rolling_correlation"
        ]
    )

    st.dataframe(
        filtered[raw_display_cols].sort_values(["Date", "Ticker"], ascending=[False, True]).head(500),
        use_container_width=True
    )


def show_sidebar():
    st.sidebar.title("BIST Banking Analytics")

    pages = [
        "Market Overview",
        "Stock Comparison",
        "Risk Metrics",
        "Risk Scores",
        "Macro Sensitivity",
        "Model Diagnostics",
        "Robust Results",
        "Rolling Macro Sensitivity",
    ]

    selected_page = st.sidebar.radio("Navigation", pages)

    st.sidebar.markdown("---")

    st.sidebar.markdown(
        """
        **Project Scope**

        BIST banking stock analytics with risk metrics, macro sensitivity analysis,
        model diagnostics, robust inference and rolling macro sensitivity.
        """
    )

    return selected_page


def main():
    selected_page = show_sidebar()

    if selected_page == "Market Overview":
        page_market_overview()

    elif selected_page == "Stock Comparison":
        page_stock_comparison()

    elif selected_page == "Risk Metrics":
        page_risk_metrics()

    elif selected_page == "Risk Scores":
        page_risk_scores()

    elif selected_page == "Macro Sensitivity":
        page_macro_sensitivity()

    elif selected_page == "Model Diagnostics":
        page_model_diagnostics()

    elif selected_page == "Robust Results":
        page_robust_results()

    elif selected_page == "Rolling Macro Sensitivity":
        page_rolling_macro_sensitivity()


if __name__ == "__main__":
    main()