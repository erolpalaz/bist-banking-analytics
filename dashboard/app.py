import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.risk_metrics import summarize_risk_metrics
from src.scoring import calculate_risk_scores


st.set_page_config(
    page_title="BIST Banking Analytics",
    page_icon="📊",
    layout="wide"
)


def format_percent(value):
    """Format decimal numbers as percentage."""
    if pd.isna(value):
        return "-"
    return f"{value:.2%}"


def load_data():
    processed_path = PROJECT_ROOT / "data" / "processed" / "stock_prices_weekly.csv"

    if not processed_path.exists():
        st.warning(
            "Processed weekly data not found. Run the following commands first:\n\n"
            "`python -m src.data_loader`\n\n"
            "`python -m src.preprocessing`"
        )
        st.stop()

    df = pd.read_csv(processed_path)
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def create_normalized_price(data, price_col="Adj_Close"):
    """Create normalized price index where first observation equals 100."""
    df = data.copy()

    if price_col not in df.columns:
        price_col = "Close"

    df = df.sort_values(["Ticker", "Date"])

    df["normalized_price"] = df.groupby("Ticker")[price_col].transform(
        lambda x: 100 * x / x.iloc[0]
    )

    return df


def prepare_display_metrics(metrics):
    """Prepare risk metrics table for better dashboard display."""
    display = metrics.copy()

    display["annualized_return"] = display["annualized_return"].apply(format_percent)
    display["weekly_volatility"] = display["weekly_volatility"].apply(format_percent)
    display["annualized_volatility"] = display["annualized_volatility"].apply(format_percent)
    display["max_drawdown"] = display["max_drawdown"].apply(format_percent)
    display["beta_to_bist100"] = display["beta_to_bist100"].round(3)
    display["sharpe_ratio"] = display["sharpe_ratio"].round(3)

    return display


def prepare_display_scores(scores):
    """Prepare score table for better dashboard display."""
    display_cols = [
        "Ticker",
        "risk_score",
        "performance_score",
        "risk_class",
        "annualized_return",
        "annualized_volatility",
        "max_drawdown",
        "beta_to_bist100",
        "sharpe_ratio"
    ]

    display = scores[display_cols].copy()

    display["risk_score"] = display["risk_score"].round(2)
    display["performance_score"] = display["performance_score"].round(2)
    display["annualized_return"] = display["annualized_return"].apply(format_percent)
    display["annualized_volatility"] = display["annualized_volatility"].apply(format_percent)
    display["max_drawdown"] = display["max_drawdown"].apply(format_percent)
    display["beta_to_bist100"] = display["beta_to_bist100"].round(3)
    display["sharpe_ratio"] = display["sharpe_ratio"].round(3)

    return display


st.title("BIST Banking Analytics")
st.caption("Educational financial analytics dashboard. Not investment advice.")

data = load_data()
data = create_normalized_price(data)

tickers = sorted(data["Ticker"].unique().tolist())
bank_tickers = [t for t in tickers if t != "XU100.IS"]

metrics = summarize_risk_metrics(data)
scores = calculate_risk_scores(metrics)

page = st.sidebar.radio(
    "Select Page",
    [
        "Market Overview",
        "Stock Comparison",
        "Risk Metrics",
        "Risk Scores"
    ]
)


if page == "Market Overview":
    st.header("Market Overview")

    selected = st.multiselect(
        "Select tickers",
        options=tickers,
        default=bank_tickers[:3]
    )

    filtered = data[data["Ticker"].isin(selected)]

    st.subheader("Normalized Price Performance")
    st.caption("Base value = 100 at the first available observation for each ticker.")

    fig_normalized = px.line(
        filtered,
        x="Date",
        y="normalized_price",
        color="Ticker",
        title="Normalized Weekly Price Comparison"
    )
    st.plotly_chart(fig_normalized, use_container_width=True)

    st.subheader("Actual Adjusted Closing Prices")

    fig_price = px.line(
        filtered,
        x="Date",
        y="Adj_Close" if "Adj_Close" in filtered.columns else "Close",
        color="Ticker",
        title="Weekly Adjusted Close Price"
    )
    st.plotly_chart(fig_price, use_container_width=True)


elif page == "Stock Comparison":
    st.header("Stock Comparison")

    selected = st.multiselect(
        "Select banking stocks",
        options=bank_tickers,
        default=bank_tickers[:2]
    )

    filtered = data[data["Ticker"].isin(selected)]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Normalized Price")
        fig_norm = px.line(
            filtered,
            x="Date",
            y="normalized_price",
            color="Ticker",
            title="Normalized Price Comparison"
        )
        st.plotly_chart(fig_norm, use_container_width=True)

    with col2:
        st.subheader("Weekly Returns")
        fig_return = px.line(
            filtered,
            x="Date",
            y="weekly_return",
            color="Ticker",
            title="Weekly Returns"
        )
        st.plotly_chart(fig_return, use_container_width=True)

    st.subheader("Selected Stock Risk Metrics")
    selected_metrics = metrics[metrics["Ticker"].isin(selected)]
    st.dataframe(
        prepare_display_metrics(selected_metrics),
        use_container_width=True,
        hide_index=True
    )


elif page == "Risk Metrics":
    st.header("Risk Metrics")

    best_return = metrics.loc[metrics["annualized_return"].idxmax()]
    highest_vol = metrics.loc[metrics["annualized_volatility"].idxmax()]
    best_sharpe = metrics.loc[metrics["sharpe_ratio"].idxmax()]
    highest_beta = metrics.loc[metrics["beta_to_bist100"].idxmax()]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Highest Annualized Return",
        best_return["Ticker"],
        format_percent(best_return["annualized_return"])
    )

    col2.metric(
        "Highest Volatility",
        highest_vol["Ticker"],
        format_percent(highest_vol["annualized_volatility"])
    )

    col3.metric(
        "Highest Sharpe Ratio",
        best_sharpe["Ticker"],
        round(best_sharpe["sharpe_ratio"], 3)
    )

    col4.metric(
        "Highest Beta",
        highest_beta["Ticker"],
        round(highest_beta["beta_to_bist100"], 3)
    )

    st.subheader("Risk Metrics Table")
    st.dataframe(
        prepare_display_metrics(metrics),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Annualized Volatility")
    fig_vol = px.bar(
        metrics.sort_values("annualized_volatility", ascending=False),
        x="Ticker",
        y="annualized_volatility",
        title="Annualized Volatility by Banking Stock"
    )
    st.plotly_chart(fig_vol, use_container_width=True)

    st.subheader("Maximum Drawdown")
    fig_dd = px.bar(
        metrics.sort_values("max_drawdown"),
        x="Ticker",
        y="max_drawdown",
        title="Maximum Drawdown by Banking Stock"
    )
    st.plotly_chart(fig_dd, use_container_width=True)

    st.subheader("Beta to BIST 100")
    fig_beta = px.bar(
        metrics.sort_values("beta_to_bist100", ascending=False),
        x="Ticker",
        y="beta_to_bist100",
        title="Beta to BIST 100"
    )
    st.plotly_chart(fig_beta, use_container_width=True)


elif page == "Risk Scores":
    st.header("Risk Scores")

    lowest_risk = scores.loc[scores["risk_score"].idxmin()]
    highest_risk = scores.loc[scores["risk_score"].idxmax()]
    best_performance = scores.loc[scores["performance_score"].idxmax()]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Lowest Risk Score",
        lowest_risk["Ticker"],
        round(lowest_risk["risk_score"], 2)
    )

    col2.metric(
        "Highest Risk Score",
        highest_risk["Ticker"],
        round(highest_risk["risk_score"], 2)
    )

    col3.metric(
        "Highest Performance Score",
        best_performance["Ticker"],
        round(best_performance["performance_score"], 2)
    )

    st.subheader("Risk and Performance Score Table")
    st.dataframe(
        prepare_display_scores(scores),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Risk Score by Banking Stock")
    risk_color_map = {
    "Low Risk": "green",
    "Medium Risk": "orange",
    "High Risk": "red"
}

    fig_risk = px.bar(
        scores.sort_values("risk_score", ascending=False),
        x="Ticker",
        y="risk_score",
        color="risk_class",
        color_discrete_map=risk_color_map,
        title="Risk Score by Banking Stock"
    )
    st.plotly_chart(fig_risk, use_container_width=True)

    st.subheader("Performance Score by Banking Stock")
    fig_perf = px.bar(
        scores.sort_values("performance_score", ascending=False),
        x="Ticker",
        y="performance_score",
        title="Performance Score by Banking Stock"
    )
    st.plotly_chart(fig_perf, use_container_width=True)