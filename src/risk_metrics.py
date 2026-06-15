import numpy as np
import pandas as pd


def calculate_max_drawdown(price_series: pd.Series) -> float:
    """Calculate maximum drawdown from a price series."""
    cumulative_max = price_series.cummax()
    drawdown = price_series / cumulative_max - 1
    return drawdown.min()


def calculate_beta(
    stock_returns: pd.Series,
    benchmark_returns: pd.Series
) -> float:
    """Calculate beta against benchmark returns."""
    aligned = pd.concat([stock_returns, benchmark_returns], axis=1).dropna()
    if aligned.shape[0] < 2:
        return np.nan

    stock = aligned.iloc[:, 0]
    benchmark = aligned.iloc[:, 1]

    benchmark_var = np.var(benchmark, ddof=1)
    if benchmark_var == 0:
        return np.nan

    covariance = np.cov(stock, benchmark, ddof=1)[0, 1]
    return covariance / benchmark_var


def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 52
) -> float:
    """
    Calculate annualized Sharpe ratio.

    risk_free_rate should be given in annual decimal form.
    Example: 0.35 for 35%.
    """
    returns = returns.dropna()
    if returns.std() == 0 or len(returns) == 0:
        return np.nan

    periodic_rf = risk_free_rate / periods_per_year
    excess_returns = returns - periodic_rf
    return np.sqrt(periods_per_year) * excess_returns.mean() / returns.std()


def summarize_risk_metrics(
    weekly_data: pd.DataFrame,
    benchmark_ticker: str = "XU100.IS",
    price_col: str = "Adj_Close",
    return_col: str = "weekly_return"
) -> pd.DataFrame:
    """Create risk-return summary table for each stock."""
    df = weekly_data.copy()
    df["Date"] = pd.to_datetime(df["Date"])

    benchmark = df[df["Ticker"] == benchmark_ticker][["Date", return_col]]
    benchmark = benchmark.rename(columns={return_col: "benchmark_return"})

    results = []

    for ticker, group in df[df["Ticker"] != benchmark_ticker].groupby("Ticker"):
        group = group.sort_values("Date")
        merged = group.merge(benchmark, on="Date", how="left")

        returns = merged[return_col]

        metrics = {
            "Ticker": ticker,
            "mean_weekly_return": returns.mean(),
            "annualized_return": returns.mean() * 52,
            "weekly_volatility": returns.std(),
            "annualized_volatility": returns.std() * np.sqrt(52),
            "max_drawdown": calculate_max_drawdown(merged[price_col]),
            "beta_to_bist100": calculate_beta(merged[return_col], merged["benchmark_return"]),
            "sharpe_ratio": calculate_sharpe_ratio(returns),
            "observations": returns.dropna().shape[0]
        }

        results.append(metrics)

    return pd.DataFrame(results)
