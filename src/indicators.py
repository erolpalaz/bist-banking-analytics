import pandas as pd


def calculate_moving_average(data: pd.DataFrame, window: int, price_col: str = "Adj_Close") -> pd.Series:
    """Calculate moving average."""
    return data[price_col].rolling(window=window).mean()


def calculate_rsi(data: pd.DataFrame, window: int = 14, price_col: str = "Adj_Close") -> pd.Series:
    """Calculate Relative Strength Index."""
    delta = data[price_col].diff()

    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_macd(
    data: pd.DataFrame,
    price_col: str = "Adj_Close",
    short_window: int = 12,
    long_window: int = 26,
    signal_window: int = 9
) -> pd.DataFrame:
    """Calculate MACD and signal line."""
    short_ema = data[price_col].ewm(span=short_window, adjust=False).mean()
    long_ema = data[price_col].ewm(span=long_window, adjust=False).mean()

    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_window, adjust=False).mean()

    return pd.DataFrame({
        "macd": macd,
        "macd_signal": signal,
        "macd_histogram": macd - signal
    })
