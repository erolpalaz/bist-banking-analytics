import pandas as pd
import statsmodels.api as sm

from src.utils import get_project_root, ensure_directory
from src.macro_analysis import MODEL_SPECS, load_stock_macro_data


ROBUST_COV_TYPE = "HC3"


def run_robust_regression_for_ticker(
    data: pd.DataFrame,
    ticker: str,
    model_name: str,
    features: list[str]
) -> dict:
    """
    Run OLS regression with HC3 robust standard errors.

    The coefficient estimates are the same as OLS, but standard errors,
    t-statistics and p-values are adjusted for heteroskedasticity.
    """
    group = data[data["Ticker"] == ticker].copy()

    required_cols = ["weekly_return"] + features
    group = group[required_cols].dropna()

    if group.shape[0] < 30:
        return {
            "model_name": model_name,
            "Ticker": ticker,
            "status": "insufficient_observations",
            "observations": group.shape[0],
            "robust_cov_type": ROBUST_COV_TYPE
        }

    y = group["weekly_return"]
    X = group[features]
    X = sm.add_constant(X)

    ols_model = sm.OLS(y, X).fit()
    robust_model = ols_model.get_robustcov_results(cov_type=ROBUST_COV_TYPE)

    variable_names = X.columns.tolist()

    robust_params = pd.Series(robust_model.params, index=variable_names)
    robust_bse = pd.Series(robust_model.bse, index=variable_names)
    robust_tvalues = pd.Series(robust_model.tvalues, index=variable_names)
    robust_pvalues = pd.Series(robust_model.pvalues, index=variable_names)

    conf_int = pd.DataFrame(
        robust_model.conf_int(),
        index=variable_names,
        columns=["ci_lower", "ci_upper"]
    )

    result = {
        "model_name": model_name,
        "Ticker": ticker,
        "status": "success",
        "observations": int(ols_model.nobs),
        "robust_cov_type": ROBUST_COV_TYPE,
        "r_squared": ols_model.rsquared,
        "adj_r_squared": ols_model.rsquared_adj,
        "ols_f_pvalue": ols_model.f_pvalue
    }

    for variable in variable_names:
        result[f"{variable}_coef"] = robust_params.get(variable)
        result[f"{variable}_robust_std_error"] = robust_bse.get(variable)
        result[f"{variable}_robust_tvalue"] = robust_tvalues.get(variable)
        result[f"{variable}_robust_pvalue"] = robust_pvalues.get(variable)
        result[f"{variable}_robust_ci_lower"] = conf_int.loc[variable, "ci_lower"]
        result[f"{variable}_robust_ci_upper"] = conf_int.loc[variable, "ci_upper"]

    return result


def create_robust_results_for_model(
    data: pd.DataFrame,
    model_name: str,
    features: list[str]
) -> pd.DataFrame:
    """Run robust regression for all banking tickers for one model."""
    results = []

    bank_tickers = sorted([
        ticker for ticker in data["Ticker"].unique()
        if ticker != "XU100.IS"
    ])

    for ticker in bank_tickers:
        result = run_robust_regression_for_ticker(
            data=data,
            ticker=ticker,
            model_name=model_name,
            features=features
        )
        results.append(result)

    return pd.DataFrame(results)


def get_significant_variables(
    row: pd.Series,
    features: list[str],
    alpha: float
) -> str:
    """Return variables that are significant at selected alpha level."""
    significant = []

    for feature in features:
        pvalue_col = f"{feature}_robust_pvalue"

        if pvalue_col in row.index:
            pvalue = row[pvalue_col]

            if pd.notna(pvalue) and pvalue < alpha:
                significant.append(feature)

    if not significant:
        return "none"

    return ", ".join(significant)


def get_strongest_variable_by_tvalue(
    row: pd.Series,
    features: list[str]
) -> str:
    """Return variable with the highest absolute robust t-value."""
    tvalues = {}

    for feature in features:
        tvalue_col = f"{feature}_robust_tvalue"

        if tvalue_col in row.index:
            tvalue = row[tvalue_col]

            if pd.notna(tvalue):
                tvalues[feature] = abs(tvalue)

    if not tvalues:
        return "not_available"

    return max(tvalues, key=tvalues.get)


def create_robust_summary(
    combined_results: pd.DataFrame
) -> pd.DataFrame:
    """
    Create compact robust regression summary.

    This summary is easier to read than full coefficient output files.
    """
    summary_rows = []

    for model_name, spec in MODEL_SPECS.items():
        features = spec["features"]

        model_rows = combined_results[
            combined_results["model_name"] == model_name
        ].copy()

        for _, row in model_rows.iterrows():
            if row.get("status") != "success":
                summary_rows.append({
                    "model_name": model_name,
                    "Ticker": row.get("Ticker"),
                    "status": row.get("status"),
                    "observations": row.get("observations"),
                    "robust_cov_type": row.get("robust_cov_type"),
                    "r_squared": None,
                    "adj_r_squared": None,
                    "significant_5pct_variables": "not_available",
                    "significant_10pct_variables": "not_available",
                    "strongest_variable_by_abs_tvalue": "not_available"
                })
                continue

            significant_5 = get_significant_variables(
                row=row,
                features=features,
                alpha=0.05
            )

            significant_10 = get_significant_variables(
                row=row,
                features=features,
                alpha=0.10
            )

            strongest_variable = get_strongest_variable_by_tvalue(
                row=row,
                features=features
            )

            summary_rows.append({
                "model_name": model_name,
                "Ticker": row.get("Ticker"),
                "status": row.get("status"),
                "observations": row.get("observations"),
                "robust_cov_type": row.get("robust_cov_type"),
                "r_squared": row.get("r_squared"),
                "adj_r_squared": row.get("adj_r_squared"),
                "significant_5pct_variables": significant_5,
                "significant_10pct_variables": significant_10,
                "strongest_variable_by_abs_tvalue": strongest_variable
            })

    return pd.DataFrame(summary_rows)


def run_robust_macro_regressions():
    """
    Run robust macro regressions for all model specifications.

    Outputs:
    - One robust regression result file per model
    - One combined robust regression summary file
    """
    root = get_project_root()
    output_dir = ensure_directory(root / "outputs")

    data = load_stock_macro_data()

    all_results = []

    for model_name, spec in MODEL_SPECS.items():
        features = spec["features"]

        model_results = create_robust_results_for_model(
            data=data,
            model_name=model_name,
            features=features
        )

        output_path = output_dir / f"robust_macro_regression_{model_name}.csv"
        model_results.to_csv(output_path, index=False, encoding="utf-8-sig")

        print(f"Robust regression results saved to: {output_path}")

        all_results.append(model_results)

    combined_results = pd.concat(all_results, ignore_index=True)

    combined_path = output_dir / "robust_macro_regression_all_models.csv"
    combined_results.to_csv(combined_path, index=False, encoding="utf-8-sig")

    summary = create_robust_summary(combined_results)

    summary_path = output_dir / "robust_macro_regression_summary.csv"
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")

    print(f"Combined robust results saved to: {combined_path}")
    print(f"Robust regression summary saved to: {summary_path}")

    print("\nRobust regression summary:")
    print(summary.head(30))


if __name__ == "__main__":
    run_robust_macro_regressions()