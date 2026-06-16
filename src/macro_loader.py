from pathlib import Path
from datetime import datetime
from urllib.parse import urlencode
import os
import time

import pandas as pd
import requests
from dotenv import load_dotenv

from src.utils import get_project_root, load_json, ensure_directory


EVDS_ENDPOINTS = [
    "https://evds3.tcmb.gov.tr/service/evds/",
    "https://evds3.tcmb.gov.tr/igmevdsms-dis/",
    "https://evds2.tcmb.gov.tr/service/evds/"
]


def get_evds_api_key() -> str:
    """Read EVDS API key from .env file."""
    load_dotenv()
    api_key = os.getenv("EVDS_API_KEY")

    if not api_key:
        raise ValueError(
            "EVDS_API_KEY not found. Create a .env file and add:\n"
            "EVDS_API_KEY=your_api_key"
        )

    return api_key


def get_today_evds_format() -> str:
    """Return today's date in EVDS format: DD-MM-YYYY."""
    return datetime.today().strftime("%d-%m-%Y")


def load_macro_config(config_path: str | Path | None = None) -> dict:
    """Load macro series configuration."""
    root = get_project_root()

    if config_path is None:
        config_path = root / "config" / "macro_series.json"

    return load_json(config_path)


def evds_date_ranges(start_date: str, end_date: str) -> list[tuple[str, str]]:
    """
    Split long EVDS request into yearly date ranges.

    Date format: DD-MM-YYYY
    """
    start = datetime.strptime(start_date, "%d-%m-%Y")
    end = datetime.strptime(end_date, "%d-%m-%Y")

    ranges = []
    current_start = start

    while current_start <= end:
        current_end = datetime(current_start.year, 12, 31)

        if current_end > end:
            current_end = end

        ranges.append(
            (
                current_start.strftime("%d-%m-%Y"),
                current_end.strftime("%d-%m-%Y")
            )
        )

        current_start = datetime(current_start.year + 1, 1, 1)

    return ranges


def parse_evds_date(series: pd.Series) -> pd.Series:
    """Parse EVDS date column safely."""
    parsed = pd.to_datetime(series, dayfirst=True, errors="coerce")

    if parsed.isna().mean() > 0.5:
        parsed = pd.to_datetime(series, errors="coerce")

    return parsed


def fetch_evds_series_single_request(
    variable_name: str,
    series_code: str,
    start_date: str,
    end_date: str,
    api_key: str
) -> pd.DataFrame:
    """
    Fetch one EVDS series for a limited date range.

    This version tries multiple EVDS endpoint and URL formats.
    """
    params = {
        "series": series_code,
        "startDate": start_date,
        "endDate": end_date,
        "type": "json"
    }

    headers = {
        "key": api_key,
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    endpoints = [
        "https://evds3.tcmb.gov.tr/igmevdsms-dis/",
        "https://evds2.tcmb.gov.tr/service/evds/",
        "https://evds3.tcmb.gov.tr/service/evds/"
    ]

    last_error = None

    for endpoint in endpoints:
        encoded_params = urlencode(params)

        candidate_urls = [
            f"{endpoint}{encoded_params}",
            f"{endpoint}?{encoded_params}"
        ]

        for url in candidate_urls:
            try:
                response = requests.get(
                    url=url,
                    headers=headers,
                    timeout=30
                )

                preview = response.text[:300].replace("\n", " ")

                if response.status_code != 200:
                    last_error = (
                        f"URL: {url} | "
                        f"HTTP {response.status_code} | "
                        f"Preview: {preview}"
                    )
                    continue

                try:
                    data = response.json()
                except Exception:
                    last_error = (
                        f"URL: {url} | "
                        f"Response was not JSON | "
                        f"Preview: {preview}"
                    )
                    continue

                if "items" not in data:
                    last_error = (
                        f"URL: {url} | "
                        f"'items' key not found | "
                        f"Keys: {list(data.keys())}"
                    )
                    continue

                items = data["items"]

                if not items:
                    return pd.DataFrame(
                        columns=["Date", "variable", "value", "series_code"]
                    )

                df = pd.DataFrame(items)

                date_col = None
                for candidate in ["Tarih", "Date", "DATE", "date"]:
                    if candidate in df.columns:
                        date_col = candidate
                        break

                if date_col is None:
                    raise ValueError(
                        f"Date column not found. Columns: {df.columns.tolist()}"
                    )

                value_candidates = [
                    col for col in df.columns
                    if col != date_col and col.lower() not in ["unix_time"]
                ]

                if not value_candidates:
                    raise ValueError(
                        f"Value column not found. Columns: {df.columns.tolist()}"
                    )

                value_col = value_candidates[0]

                result = df[[date_col, value_col]].copy()
                result.columns = ["Date", "value"]

                result["Date"] = parse_evds_date(result["Date"])

                result["value"] = (
                    result["value"]
                    .astype(str)
                    .str.replace(",", ".", regex=False)
                    .replace(["null", "None", "", "nan"], pd.NA)
                )

                result["value"] = pd.to_numeric(result["value"], errors="coerce")
                result["variable"] = variable_name
                result["series_code"] = series_code

                result = result.dropna(subset=["Date", "value"])
                result = result[["Date", "variable", "value", "series_code"]]

                return result

            except Exception as error:
                last_error = f"URL: {url} | Error: {error}"
                continue

    raise RuntimeError(
        f"Failed single request for {variable_name} ({series_code}) "
        f"{start_date} - {end_date}. Last error: {last_error}"
    )


def fetch_evds_series(
    variable_name: str,
    series_code: str,
    start_date: str,
    end_date: str,
    api_key: str
) -> pd.DataFrame:
    """
    Fetch one EVDS series by splitting long date range into yearly chunks.
    """
    date_ranges = evds_date_ranges(start_date, end_date)
    frames = []

    for chunk_start, chunk_end in date_ranges:
        try:
            chunk = fetch_evds_series_single_request(
                variable_name=variable_name,
                series_code=series_code,
                start_date=chunk_start,
                end_date=chunk_end,
                api_key=api_key
            )

            if not chunk.empty:
                frames.append(chunk)

            print(
                f"{variable_name} | {series_code} | "
                f"{chunk_start} - {chunk_end} | rows: {len(chunk)}"
            )

            time.sleep(0.2)

        except Exception as error:
            print(
                f"Chunk failed: {variable_name} | {series_code} | "
                f"{chunk_start} - {chunk_end} | {error}"
            )

    if not frames:
        raise RuntimeError(
            f"No data returned for {variable_name} ({series_code}) "
            f"between {start_date} and {end_date}."
        )

    result = pd.concat(frames, ignore_index=True)
    result = result.drop_duplicates(subset=["Date", "variable", "series_code"])
    result = result.sort_values("Date")

    print(
        f"Downloaded {variable_name}: {series_code} | "
        f"min: {result['Date'].min().date()} | "
        f"max: {result['Date'].max().date()} | "
        f"rows: {len(result)}"
    )

    return result


def download_macro_data(output_filename: str = "macro_raw.csv") -> Path:
    """Download all configured macro series and save raw long-format data."""
    root = get_project_root()
    config = load_macro_config()
    api_key = get_evds_api_key()

    start_date = config.get("start_date", "01-01-2018")
    end_date = get_today_evds_format()

    frames = []
    failed = []

    for variable_name, info in config["series"].items():
        series_code = info["code"]

        try:
            df = fetch_evds_series(
                variable_name=variable_name,
                series_code=series_code,
                start_date=start_date,
                end_date=end_date,
                api_key=api_key
            )
            frames.append(df)

        except Exception as error:
            print(f"FAILED {variable_name} ({series_code}): {error}")
            failed.append(
                {
                    "variable": variable_name,
                    "series_code": series_code,
                    "error": str(error)
                }
            )

    if not frames:
        raise RuntimeError("No macro series could be downloaded.")

    macro_raw = pd.concat(frames, ignore_index=True)
    macro_raw = macro_raw.drop_duplicates(subset=["Date", "variable", "series_code"])
    macro_raw = macro_raw.sort_values(["variable", "Date"])

    output_dir = ensure_directory(root / "data" / "raw")
    output_path = output_dir / output_filename

    macro_raw.to_csv(output_path, index=False, encoding="utf-8-sig")

    if failed:
        failed_path = output_dir / "macro_failed_series.csv"
        pd.DataFrame(failed).to_csv(failed_path, index=False, encoding="utf-8-sig")
        print(f"Failed series saved to: {failed_path}")

    print(f"Macro raw data saved to: {output_path}")
    return output_path


def process_macro_data(
    input_filename: str = "macro_raw.csv",
    output_filename: str = "macro_weekly.csv"
) -> Path:
    """
    Convert raw macro data into weekly wide-format dataset.
    """
    root = get_project_root()

    input_path = root / "data" / "raw" / input_filename
    output_dir = ensure_directory(root / "data" / "processed")
    output_path = output_dir / output_filename

    if not input_path.exists():
        raise FileNotFoundError(f"Macro raw file not found: {input_path}")

    macro_raw = pd.read_csv(input_path)
    macro_raw["Date"] = pd.to_datetime(macro_raw["Date"])

    wide = macro_raw.pivot_table(
        index="Date",
        columns="variable",
        values="value",
        aggfunc="last"
    ).sort_index()

    weekly = wide.resample("W-FRI").last()
    weekly = weekly.ffill()

    if "usd_try" in weekly.columns:
        weekly["usd_try_weekly_change"] = weekly["usd_try"].pct_change()

    if "eur_try" in weekly.columns:
        weekly["eur_try_weekly_change"] = weekly["eur_try"].pct_change()

    if "funding_cost" in weekly.columns:
        weekly["funding_cost_weekly_diff"] = weekly["funding_cost"].diff()

    if "cpi_index" in weekly.columns:
        weekly["cpi_index_weekly_change"] = weekly["cpi_index"].pct_change()
        weekly["cpi_index_yoy_change"] = weekly["cpi_index"].pct_change(52)

    weekly = weekly.reset_index()
    weekly.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"Macro weekly data saved to: {output_path}")
    return output_path


def run_macro_pipeline():
    """Run full macro data pipeline."""
    download_macro_data()
    process_macro_data()


if __name__ == "__main__":
    run_macro_pipeline()