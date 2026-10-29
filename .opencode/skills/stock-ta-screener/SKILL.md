---
name: stock-ta-screener
description: Screens stocks using Yahoo Finance data and applies technical indicators (RSI, SMA, MACD) to generate BUY/SELL/HOLD signals with plain-English reasons. Use when the user requests a list of stocks meeting specific technical criteria.
---

# Stock Screener Skill

## Objective
Identify stocks that meet specific technical criteria by fetching historical data from Yahoo Finance, calculating indicators, and filtering based on predefined rules with a MACD state filter.

## Workflow
1. **Ticker Retrieval:** Accept tickers as command-line arguments. If none provided, default to `["AAPL", "MSFT", "NVDA", "TSLA"]`.
2. **Data Fetching:** For each ticker, use `yfinance` to fetch 1 year of historical OHLCV data and save raw CSVs to `source_data/`.
3. **Indicator Calculation:** Use `pandas_ta` to compute:
   - **RSI (14-day):** Overbought (>70) or oversold (<30) conditions.
   - **SMA (50 & 200-day):** Short-term and long-term trend.
   - **MACD (12, 26, 9):** MACD line and signal line — state comparison used as a filter.
4. **Filtering:** Apply the signal rules requiring both RSI/SMA and MACD state to agree (see Signal Rules below).
5. **Report Generation:** Output a timestamped CSV file under `output/` with columns: Ticker, Signal, Reason, RSI, SMA_50, SMA_200, MACD, MACD_Signal.

## Signal Rules
- **BUY**: RSI < 30 AND Close > SMA 200 AND MACD > MACD_Signal (bullish)
- **SELL**: RSI > 70 AND MACD < MACD_Signal (bearish)
- **HOLD**: Otherwise — includes cases where RSI/SMA triggers but MACD disagrees (filter blocked) or RSI is neutral

## Output CSV Columns
| Column | Description |
|---|---|
| Ticker | Stock symbol |
| Signal | BUY / SELL / HOLD |
| Reason | Plain-English explanation (e.g., "RSI 25.0 oversold, price above 200-SMA, MACD bullish") |
| RSI | 14-day Relative Strength Index |
| SMA_50 | 50-day Simple Moving Average |
| SMA_200 | 200-day Simple Moving Average |
| MACD | MACD line value |
| MACD_Signal | MACD signal line value |

## Technical Constraints
- **Data Integrity:** Always drop NaN rows after indicator calculation. Insufficient data returns an error rather than a guess.
- **Adjusted Prices:** `yfinance` auto-adjusts prices by default.
- **Safety:** Do not provide financial advice. Clearly label the output for informational purposes only.

## Examples
*   **User Prompt:** "Run the screener for GOOGL, AMZN, META."
*   **Action:** `python main.py GOOGL AMZN META`
*   **User Prompt:** "Screen the default stocks."
*   **Action:** `python main.py`