import pandas as pd
import statsmodels.api as sm

from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson, jarque_bera
from statsmodels.stats.diagnostic import het_breuschpagan

from src.utils import get_project_root, ensure_directory
from src.macro_analysis import MODEL_SPECS, load_stock_macro_data


def calculate_vif(data: pd.DataFrame, features: list[str], model_name: str, ticker: str) -> list[dict]:
    """
    Calculate Variance Inflation Factor for model features.

    VIF interpretation:
    - VIF < 5: generally acceptable
    - VIF >= 5: possible multicollinearity concern
    - VIF >= 10: strong multicollinearity concern
    """
    vif_rows = []

    X = data[features].dropna().copy()

    if X.shape[0] < 30 or X.shape[1] < 2:
        for feature in features:
            vif_rows.append({
                "model_name": model_name,
                "Ticker": ticker,
                "variable": feature,
                "vif": None,
                "status": "insufficient_data_or_single_feature"
            })

        return vif_rows

    X_const = sm.add_constant(X)

    for i, column in enumerate(X_const.columns):
        if column == "const":
            continue

        try:
            vif_value = variance_inflation_factor(X_const.values, i)
            status = "ok"

            if vif_value >= 10:
                status = "high_multicollinearity"
            elif vif_value >= 5:
                status = "moderate_multicollinearity"

            vif_rows.append({
                "model_name": model_name,
                "Ticker": ticker,
                "variable": column,
                "vif": vif_value,
                "status": status
            })

        except Exception as error:
            vif_rows.append({
                "model_name": model_name,
                "Ticker": ticker,
                "variable": column,
                "vif": None,
                "status": f"error: {error}"
            })

    return vif_rows


def interpret_durbin_watson(value: float) -> str:
    """Interpret Durbin-Watson statistic."""
    if pd.isna(value):
        return "not_available"

    if value < 1.5:
        return "possible_positive_autocorrelation"

    if value > 2.5:
        return "possible_negative_autocorrelation"

    return "acceptable"


def interpret_pvalue(value: float, test_name: str) -> str:
    """Interpret diagnostic p-values."""
    if pd.isna(value):
        return "not_available"

    if test_name == "breusch_pagan":
        if value < 0.05:
            return "possible_heteroskedasticity"
        return "no_strong_heteroskedasticity_evidence"

    if test_name == "jarque_bera":
        if value < 0.05:
            return "residuals_not_normal"
        return "no_strong_non_normality_evidence"

    if test_name == "f_test":
        if value < 0.05:
            return "model_statistically_significant_5pct"
        if value < 0.10:
            return "model_statistically_significant_10pct"
        return "model_not_statistically_significant"

    return "not_available"


def build_model_warning_list(
    adj_r_squared: float,
    f_pvalue: float,
    durbin_watson_stat: float,
    breusch_pagan_pvalue: float,
    jarque_bera_pvalue: float,
    max_vif: float
) -> str:
    """Create a compact warning list for model diagnostics."""
    warnings = []

    if pd.notna(adj_r_squared) and adj_r_squared < 0.02:
        warnings.append("low_explanatory_power")

    if pd.notna(f_pvalue) and f_pvalue >= 0.10:
        warnings.append("weak_overall_model_significance")

    if pd.notna(durbin_watson_stat):
        if durbin_watson_stat < 1.5:
            warnings.append("possible_positive_residual_autocorrelation")
        elif durbin_watson_stat > 2.5:
            warnings.append("possible_negative_residual_autocorrelation")

    if pd.notna(breusch_pagan_pvalue) and breusch_pagan_pvalue < 0.05:
        warnings.append("possible_heteroskedasticity")

    if pd.notna(jarque_bera_pvalue) and jarque_bera_pvalue < 0.05:
        warnings.append("residuals_not_normal")

    if pd.notna(max_vif) and max_vif >= 5:
        warnings.append("possible_multicollinearity")

    if not warnings:
        return "no_major_warning"

    return "; ".join(warnings)


def run_diagnostics_for_ticker(
    data: pd.DataFrame,
    ticker: str,
    model_name: str,
    features: list[str]
) -> tuple[dict, list[dict]]:
    """
    Run regression diagnostics for one ticker and one model.
    """
    group = data[data["Ticker"] == ticker].copy()

    required_cols = ["weekly_return"] + features
    group = group[required_cols].dropna()

    if group.shape[0] < 30:
        summary = {
            "model_name": model_name,
            "Ticker": ticker,
            "status": "insufficient_observations",
            "observations": group.shape[0]
        }

        vif_rows = []

        return summary, vif_rows

    y = group["weekly_return"]
    X = group[features]
    X_const = sm.add_constant(X)

    model = sm.OLS(y, X_const).fit()
    residuals = model.resid

    durbin_watson_stat = durbin_watson(residuals)

    try:
        jb_stat, jb_pvalue, skewness, kurtosis = jarque_bera(residuals)
    except Exception:
        jb_stat, jb_pvalue, skewness, kurtosis = None, None, None, None

    try:
        bp_stat, bp_pvalue, bp_f_stat, bp_f_pvalue = het_breuschpagan(
            residuals,
            X_const
        )
    except Exception:
        bp_stat, bp_pvalue, bp_f_stat, bp_f_pvalue = None, None, None, None

    vif_rows = calculate_vif(
        data=group,
        features=features,
        model_name=model_name,
        ticker=ticker
    )

    vif_values = [
        row["vif"] for row in vif_rows
        if row.get("vif") is not None and pd.notna(row.get("vif"))
    ]

    max_vif = max(vif_values) if vif_values else None
    mean_vif = sum(vif_values) / len(vif_values) if vif_values else None

    warning_list = build_model_warning_list(
        adj_r_squared=model.rsquared_adj,
        f_pvalue=model.f_pvalue,
        durbin_watson_stat=durbin_watson_stat,
        breusch_pagan_pvalue=bp_pvalue,
        jarque_bera_pvalue=jb_pvalue,
        max_vif=max_vif
    )

    summary = {
        "model_name": model_name,
        "Ticker": ticker,
        "status": "success",
        "observations": int(model.nobs),
        "r_squared": model.rsquared,
        "adj_r_squared": model.rsquared_adj,
        "f_pvalue": model.f_pvalue,
        "f_test_interpretation": interpret_pvalue(model.f_pvalue, "f_test"),
        "durbin_watson": durbin_watson_stat,
        "durbin_watson_interpretation": interpret_durbin_watson(durbin_watson_stat),
        "breusch_pagan_pvalue": bp_pvalue,
        "breusch_pagan_interpretation": interpret_pvalue(bp_pvalue, "breusch_pagan"),
        "jarque_bera_pvalue": jb_pvalue,
        "jarque_bera_interpretation": interpret_pvalue(jb_pvalue, "jarque_bera"),
        "residual_skewness": skewness,
        "residual_kurtosis": kurtosis,
        "max_vif": max_vif,
        "mean_vif": mean_vif,
        "diagnostic_warnings": warning_list
    }

    return summary, vif_rows


def run_model_diagnostics():
    """
    Run diagnostics for all macro sensitivity models.
    """
    root = get_project_root()
    output_dir = ensure_directory(root / "outputs")

    diagnostics_path = output_dir / "macro_model_diagnostics.csv"
    vif_path = output_dir / "macro_vif_results.csv"

    data = load_stock_macro_data()

    diagnostics_rows = []
    all_vif_rows = []

    bank_tickers = sorted([
        ticker for ticker in data["Ticker"].unique()
        if ticker != "XU100.IS"
    ])

    for model_name, spec in MODEL_SPECS.items():
        features = spec["features"]

        for ticker in bank_tickers:
            summary, vif_rows = run_diagnostics_for_ticker(
                data=data,
                ticker=ticker,
                model_name=model_name,
                features=features
            )

            diagnostics_rows.append(summary)
            all_vif_rows.extend(vif_rows)

    diagnostics_df = pd.DataFrame(diagnostics_rows)
    vif_df = pd.DataFrame(all_vif_rows)

    diagnostics_df.to_csv(diagnostics_path, index=False, encoding="utf-8-sig")
    vif_df.to_csv(vif_path, index=False, encoding="utf-8-sig")

    print(f"Model diagnostics saved to: {diagnostics_path}")
    print(f"VIF results saved to: {vif_path}")

    print("\nDiagnostics summary:")
    print(
        diagnostics_df[
            [
                "model_name",
                "Ticker",
                "adj_r_squared",
                "f_pvalue",
                "durbin_watson",
                "breusch_pagan_pvalue",
                "jarque_bera_pvalue",
                "max_vif",
                "diagnostic_warnings"
            ]
        ].head(20)
    )


if __name__ == "__main__":
    run_model_diagnostics()