from pathlib import Path
import pandas as pd
import yfinance as yf

from src.utils import get_project_root, load_json, ensure_directory


def load_ticker_config(config_path: str | Path | None = None) -> dict:
    """Load ticker configuration."""
    root = get_project_root()
    if config_path is None:
        config_path = root / "config" / "tickers.json"
    return load_json(config_path)


def flatten_yfinance_columns(data: pd.DataFrame) -> pd.DataFrame:
    """
    Flatten possible MultiIndex columns returned by yfinance.

    yfinance may return columns like:
    ('Close', 'AKBNK.IS') or ('AKBNK.IS', 'Close')
    This function converts them into simple columns:
    Close, High, Low, Open, Volume, Adj Close
    """
    df = data.copy()

    expected_cols = {
        "Open",
        "High",
        "Low",
        "Close",
        "Adj Close",
        "Adj_Close",
        "Volume",
        "Date",
        "Datetime"
    }

    if isinstance(df.columns, pd.MultiIndex):
        new_cols = []

        for col in df.columns:
            parts = [
                str(part)
                for part in col
                if part is not None and str(part) not in ["", "nan", "NaN"]
            ]

            chosen_col = None

            for part in parts:
                if part in expected_cols:
                    chosen_col = part
                    break

            if chosen_col is None:
                chosen_col = parts[0] if parts else ""

            new_cols.append(chosen_col)

        df.columns = new_cols
    else:
        df.columns = [str(col) for col in df.columns]

    return df


def standardize_market_columns(data: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Standardize yfinance output into a clean long-format dataframe."""
    df = flatten_yfinance_columns(data)

    df = df.reset_index()

    df.columns = [str(col).replace(" ", "_") for col in df.columns]

    rename_map = {
        "Adj_Close": "Adj_Close",
        "Adj_Close_": "Adj_Close",
        "Adj_Close.": "Adj_Close",
        "Datetime": "Date",
        "index": "Date"
    }

    df = df.rename(columns=rename_map)

    if "Adj_Close" not in df.columns and "Close" in df.columns:
        df["Adj_Close"] = df["Close"]

    if "Date" not in df.columns:
        possible_date_cols = [
            col for col in df.columns
            if "date" in col.lower() or "datetime" in col.lower()
        ]

        if possible_date_cols:
            df = df.rename(columns={possible_date_cols[0]: "Date"})
        else:
            raise ValueError(
                f"Date column could not be detected for {ticker}. "
                f"Available columns: {df.columns.tolist()}"
            )

    df["Ticker"] = ticker

    required_cols = [
        "Date",
        "Ticker",
        "Open",
        "High",
        "Low",
        "Close",
        "Adj_Close",
        "Volume"
    ]

    for col in required_cols:
        if col not in df.columns:
            df[col] = pd.NA

    df = df[required_cols]

    return df


def download_yfinance_data(
    tickers: list[str],
    start: str = "2018-01-01",
    end: str | None = None,
    interval: str = "1d"
) -> pd.DataFrame:
    """
    Download historical market data from Yahoo Finance using yfinance.

    Safer version:
    - Downloads tickers one by one
    - Avoids database lock errors
    - Standardizes columns
    - Produces long-format data
    """
    frames = []
    failed_tickers = []

    for ticker in tickers:
        try:
            print(f"Downloading: {ticker}")

            raw = yf.download(
                tickers=ticker,
                start=start,
                end=end,
                interval=interval,
                auto_adjust=False,
                progress=False,
                threads=False
            )

            if raw.empty:
                print(f"Warning: No data returned for {ticker}")
                failed_tickers.append(ticker)
                continue

            clean = standardize_market_columns(raw, ticker)
            frames.append(clean)

        except Exception as error:
            print(f"Failed download for {ticker}: {error}")
            failed_tickers.append(ticker)

    if not frames:
        raise ValueError("No data returned. Check ticker symbols or internet connection.")

    data = pd.concat(frames, ignore_index=True)

    if failed_tickers:
        print(f"Failed tickers: {failed_tickers}")
    else:
        print("All tickers downloaded successfully.")

    return data


def save_raw_market_data(output_filename: str = "stock_prices_raw.csv") -> Path:
    """Download initial stock and benchmark data and save to data/raw."""
    root = get_project_root()
    config = load_ticker_config()

    banking_tickers = list(config["banking_stocks"].keys())
    benchmark_tickers = list(config["benchmark"].keys())
    tickers = banking_tickers + benchmark_tickers

    data = download_yfinance_data(
        tickers=tickers,
        start=config.get("start_date", "2018-01-01")
    )

    output_dir = ensure_directory(root / "data" / "raw")
    output_path = output_dir / output_filename

    data.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"Raw market data saved to: {output_path}")

    return output_path


if __name__ == "__main__":
    save_raw_market_data()