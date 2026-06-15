from pathlib import Path

import pandas as pd

from src.utils import get_project_root, ensure_directory
from src.risk_metrics import summarize_risk_metrics
from src.scoring import calculate_risk_scores


def export_project_outputs():
    """
    Export risk metrics, risk scores, and summary tables.
    """
    root = get_project_root()

    processed_path = root / "data" / "processed" / "stock_prices_weekly.csv"
    output_dir = ensure_directory(root / "outputs")

    if not processed_path.exists():
        raise FileNotFoundError(
            "Processed data not found. Run first:\n"
            "python -m src.data_loader\n"
            "python -m src.preprocessing"
        )

    data = pd.read_csv(processed_path)
    data["Date"] = pd.to_datetime(data["Date"])

    risk_metrics = summarize_risk_metrics(data)
    risk_scores = calculate_risk_scores(risk_metrics)

    risk_metrics_path = output_dir / "risk_metrics.csv"
    risk_scores_path = output_dir / "risk_scores.csv"
    excel_path = output_dir / "summary_tables.xlsx"

    risk_metrics.to_csv(risk_metrics_path, index=False, encoding="utf-8-sig")
    risk_scores.to_csv(risk_scores_path, index=False, encoding="utf-8-sig")

    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        risk_metrics.to_excel(writer, sheet_name="Risk Metrics", index=False)
        risk_scores.to_excel(writer, sheet_name="Risk Scores", index=False)

    print(f"Risk metrics saved to: {risk_metrics_path}")
    print(f"Risk scores saved to: {risk_scores_path}")
    print(f"Excel summary saved to: {excel_path}")


if __name__ == "__main__":
    export_project_outputs()