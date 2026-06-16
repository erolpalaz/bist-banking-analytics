from pathlib import Path

import pandas as pd

from src.utils import get_project_root, ensure_directory


def merge_stock_and_macro_data(
    stock_filename: str = "stock_prices_weekly.csv",
    macro_filename: str = "macro_weekly.csv",
    output_filename: str = "stock_macro_weekly.csv"
) -> Path:
    """
    Merge weekly stock data with weekly macroeconomic variables.
    """
    root = get_project_root()

    stock_path = root / "data" / "processed" / stock_filename
    macro_path = root / "data" / "processed" / macro_filename
    output_dir = ensure_directory(root / "data" / "processed")
    output_path = output_dir / output_filename

    if not stock_path.exists():
        raise FileNotFoundError(f"Stock weekly file not found: {stock_path}")

    if not macro_path.exists():
        raise FileNotFoundError(f"Macro weekly file not found: {macro_path}")

    stock = pd.read_csv(stock_path)
    macro = pd.read_csv(macro_path)

    stock["Date"] = pd.to_datetime(stock["Date"])
    macro["Date"] = pd.to_datetime(macro["Date"])

    merged = stock.merge(macro, on="Date", how="left")

    merged = merged.sort_values(["Ticker", "Date"])

    merged.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"Merged stock-macro data saved to: {output_path}")
    print(f"Rows: {len(merged)}")
    print(f"Columns: {merged.columns.tolist()}")

    return output_path


if __name__ == "__main__":
    merge_stock_and_macro_data()