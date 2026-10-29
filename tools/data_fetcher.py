from datetime import datetime
from pathlib import Path

import yfinance as yf

def fetch_market_data(ticker_list, period="1y", save_source_data=True, source_dir="source_data"):
    """Fetches OHLCV data for multiple tickers efficiently."""
    tickers = yf.Tickers(" ".join(ticker_list))
    data = tickers.history(period=period, group_by='ticker', auto_adjust=True)

    if save_source_data:
        _save_source_data(data, ticker_list, source_dir)

    return data


def _save_source_data(data, ticker_list, source_dir):
    output_path = Path(source_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for ticker in ticker_list:
        try:
            df = data[ticker]
        except (KeyError, TypeError):
            df = data

        filename = f"{ticker}_{timestamp}.csv"
        df.to_csv(output_path / filename)