from pathlib import Path
import pandas as pd

from src.utils import get_project_root, ensure_directory


def clean_market_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Clean raw market data.

    Expected final columns:
    Date, Ticker, Open, High, Low, Close, Adj_Close, Volume
    """
    df = data.copy()

    df.columns = [str(col).replace(" ", "_") for col in df.columns]

    if "Adj_Close" not in df.columns and "Adj_Close_" in df.columns:
        df = df.rename(columns={"Adj_Close_": "Adj_Close"})

    if "Date" not in df.columns:
        possible_date_cols = [
            col for col in df.columns
            if "date" in col.lower() or "datetime" in col.lower()
        ]

        if possible_date_cols:
            df = df.rename(columns={possible_date_cols[0]: "Date"})
        else:
            raise ValueError(
                f"Date column not found. Available columns: {df.columns.tolist()}"
            )

    if "Adj_Close" not in df.columns and "Close" in df.columns:
        df["Adj_Close"] = df["Close"]

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    df = df.sort_values(["Ticker", "Date"])

    numeric_cols = ["Open", "High", "Low", "Close", "Adj_Close", "Volume"]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Date", "Ticker", "Close"])

    return df


def add_returns(data: pd.DataFrame, price_col: str = "Adj_Close") -> pd.DataFrame:
    """Add simple and log returns by ticker."""
    import numpy as np

    df = data.copy()

    if price_col not in df.columns:
        price_col = "Close"

    df = df.sort_values(["Ticker", "Date"])

    df["daily_return"] = df.groupby("Ticker")[price_col].pct_change()
    df["log_return"] = df.groupby("Ticker")[price_col].transform(
        lambda x: np.log(x / x.shift(1))
    )

    return df


def convert_to_weekly(data: pd.DataFrame, price_col: str = "Adj_Close") -> pd.DataFrame:
    """
    Convert daily market data to weekly frequency.

    Weekly data uses Friday close. If Friday is unavailable, it uses the last available observation of the week.
    """
    df = data.copy()
    if price_col not in df.columns:
        price_col = "Close"

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(["Ticker", "Date"])
    df = df.set_index("Date")

    weekly_frames = []

    for ticker, group in df.groupby("Ticker"):
        weekly = group.resample("W-FRI").agg({
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            price_col: "last",
            "Volume": "sum"
        })

        weekly["Ticker"] = ticker
        weekly = weekly.reset_index()
        weekly["weekly_return"] = weekly[price_col].pct_change()
        weekly_frames.append(weekly)

    weekly_data = pd.concat(weekly_frames, ignore_index=True)
    return weekly_data


def process_raw_market_data(
    input_path: str | Path | None = None,
    output_filename: str = "stock_prices_weekly.csv"
) -> Path:
    """Load raw data, clean it, calculate returns, convert to weekly, and save."""
    root = get_project_root()

    if input_path is None:
        input_path = root / "data" / "raw" / "stock_prices_raw.csv"

    raw = pd.read_csv(input_path)
    clean = clean_market_data(raw)
    clean = add_returns(clean)
    weekly = convert_to_weekly(clean)

    output_dir = ensure_directory(root / "data" / "processed")
    output_path = output_dir / output_filename
    weekly.to_csv(output_path, index=False, encoding="utf-8-sig")

    return output_path


if __name__ == "__main__":
    saved_path = process_raw_market_data()
    print(f"Processed weekly market data saved to: {saved_path}")
