import sys
from datetime import datetime
from pathlib import Path
import csv

from tools.data_fetcher import fetch_market_data
from screener_logic import calculate_indicators, generate_signal

def run_screener(tickers):
    data = fetch_market_data(tickers)
    results = []
    for ticker in tickers:
        df = data[ticker]
        df = calculate_indicators(df)
        latest = df.iloc[-1]
        signal, reason = generate_signal(latest)
        results.append({
            "Ticker": ticker,
            "Signal": signal,
            "Reason": reason,
            "RSI": round(latest['RSI'], 2),
            "SMA_50": round(latest['SMA_50'], 2),
            "SMA_200": round(latest['SMA_200'], 2),
            "MACD": round(latest['MACD'], 2),
            "MACD_Signal": round(latest['MACD_Signal'], 2),
        })
    return results


def save_results_to_csv(results, output_dir="output"):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ta_stocks_{timestamp}.csv"
    filepath = output_path / filename

    fieldnames = ["Ticker", "Signal", "Reason", "RSI", "SMA_50", "SMA_200", "MACD", "MACD_Signal"]
    with filepath.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    return filepath


if __name__ == "__main__":
    if len(sys.argv) > 1:
        my_tickers = sys.argv[1:]
    else:
        my_tickers = ["AAPL", "MSFT", "NVDA", "TSLA"]
    results = run_screener(my_tickers)
    output_file = save_results_to_csv(results)
    print(f"Saved screener results to {output_file}")