import pandas as pd


def min_max_scale(series: pd.Series, reverse: bool = False) -> pd.Series:
    """Scale a series between 0 and 100."""
    min_val = series.min()
    max_val = series.max()

    if max_val == min_val:
        scaled = pd.Series([50] * len(series), index=series.index)
    else:
        scaled = 100 * (series - min_val) / (max_val - min_val)

    if reverse:
        scaled = 100 - scaled

    return scaled


def calculate_risk_scores(risk_metrics: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate transparent risk and performance scores.

    Higher risk_score = riskier.
    Higher performance_score = better historical risk-adjusted profile.
    """
    df = risk_metrics.copy()

    # Risk components: higher values are riskier except Sharpe.
    df["volatility_score"] = min_max_scale(df["annualized_volatility"], reverse=False)
    df["drawdown_score"] = min_max_scale(df["max_drawdown"].abs(), reverse=False)
    df["beta_score"] = min_max_scale(df["beta_to_bist100"].abs(), reverse=False)

    df["risk_score"] = (
        0.40 * df["volatility_score"] +
        0.35 * df["drawdown_score"] +
        0.25 * df["beta_score"]
    )

    # Performance components: higher return and Sharpe are better; lower drawdown is better.
    df["return_score"] = min_max_scale(df["annualized_return"], reverse=False)
    df["sharpe_score"] = min_max_scale(df["sharpe_ratio"], reverse=False)
    df["drawdown_resilience_score"] = min_max_scale(df["max_drawdown"].abs(), reverse=True)

    df["performance_score"] = (
        0.40 * df["return_score"] +
        0.40 * df["sharpe_score"] +
        0.20 * df["drawdown_resilience_score"]
    )

    def classify_risk(score: float) -> str:
        if score >= 70:
            return "High Risk"
        if score >= 40:
            return "Medium Risk"
        return "Low Risk"

    df["risk_class"] = df["risk_score"].apply(classify_risk)

    return df
