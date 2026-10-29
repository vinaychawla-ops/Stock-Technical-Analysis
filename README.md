# Stock Technical Analysis Screener

A Python CLI that pulls Yahoo Finance history for a list of tickers, computes technical indicators with `pandas_ta`, and writes BUY / SELL / HOLD signals with a plain-English reason to a timestamped CSV.

## What it does

For each ticker it:

1. Downloads 1 year of daily OHLCV bars (auto-adjusted) from Yahoo Finance.
2. Dumps the raw bars to `source_data/` for auditing and replay.
3. Computes RSI(14), SMA(50), SMA(200), and MACD(12, 26, 9).
4. Evaluates the latest bar against the rules below, using MACD as a confirmation filter.
5. Appends one row per ticker to `output/ta_stocks_<YYYYMMDD_HHMMSS>.csv`.

### Key features

- Batched fetch: one `yfinance` call for the whole ticker list
- MACD state filter — RSI/SMA and MACD must agree before a BUY or SELL is emitted
- Every signal carries a machine-checkable `Reason` string
- Raw source data preserved alongside results
- Tickers via command-line arguments, with a default watchlist
- Pure CSV output — no database, no service, no state

## Requirements

- **Python 3.12 or newer.** `pandas-ta` 0.4.71b0 declares `Requires-Python >=3.12`; this repo's venv runs 3.14.4.
- `pip`

Dependencies in `requirements.txt`:

| Package | Role |
|---|---|
| `yfinance` | Yahoo Finance downloads |
| `pandas` | DataFrames |
| `pandas-ta` | RSI / SMA / MACD (0.4.x fork, which pins `numba==0.61.2`) |
| `numba` | JIT backend for `pandas-ta` |
| `tqdm` | Progress bars |

`numba` and `tqdm` are listed explicitly because `pandas-ta` needs them; you do not import them directly.

## Installation

```powershell
cd test-stock-ta-opencode
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On macOS/Linux the activation line is `source venv/bin/activate`.

## Usage

Default watchlist (`AAPL`, `MSFT`, `NVDA`, `TSLA`):

```powershell
.\venv\Scripts\python.exe main.py
```

Any other tickers, space-separated:

```powershell
.\venv\Scripts\python.exe main.py GOOGL AMZN META
.\venv\Scripts\python.exe main.py JPM BAC GS MS
```

Output:

```
Saved screener results to output\ta_stocks_20261029_124829.csv
```

There is no argument parser. Every token after `main.py` is treated as a ticker, so flags such as `--help` will be sent to Yahoo Finance as symbols.

### Sample output

Real run from this project (AAPL and MSFT):

```csv
Ticker,Signal,Reason,RSI,SMA_50,SMA_200,MACD,MACD_Signal
AAPL,HOLD,"RSI 62.3 neutral (30-70), MACD bullish",62.26,332.39,295.85,4.14,4.08
MSFT,HOLD,"RSI 50.9 neutral (30-70), MACD bearish",50.94,511.98,436.5,5.38,7.53
```

## Signal rules

| Condition | MACD state | Result |
|---|---|---|
| RSI < 30 AND Close > SMA 200 | Bullish (MACD > Signal) | **BUY** |
| RSI < 30 AND Close > SMA 200 | Bearish (MACD < Signal) | HOLD — filter blocked |
| RSI > 70 | Bearish (MACD < Signal) | **SELL** |
| RSI > 70 | Bullish (MACD > Signal) | HOLD — filter blocked |
| RSI 30–70 (neutral) | Any | HOLD |

SELL deliberately omits a trend condition; only BUY requires price above the 200-day SMA. The asymmetry is intentional, not a bug.

## Indicators

| Indicator | Parameters | Interpretation |
|---|---|---|
| RSI | 14 periods | `< 30` oversold, `> 70` overbought, else neutral |
| SMA 50 | 50 sessions | Short-term trend |
| SMA 200 | 200 sessions | Long-term trend; used as the BUY trend gate |
| MACD | 12 / 26 / 9 | `MACD > MACD_Signal` is bullish; otherwise bearish |

Bollinger Bands and volume confirmation are **not** implemented. `Volume` is downloaded and stored but no rule reads it.

## Output files

| Path | Contents |
|---|---|
| `output/ta_stocks_<YYYYMMDD_HHMMSS>.csv` | One row per ticker with signal and indicator values |
| `source_data/<TICKER>_<YYYYMMDD_HHMMSS>.csv` | Raw OHLCV, dividends, splits for replay |

### Output columns

| Column | Description |
|---|---|
| Ticker | Stock symbol |
| Signal | BUY / SELL / HOLD |
| Reason | Plain-English explanation including MACD state |
| RSI | 14-day Relative Strength Index |
| SMA_50 | 50-day Simple Moving Average |
| SMA_200 | 200-day Simple Moving Average |
| MACD | MACD line value |
| MACD_Signal | MACD signal line value |

Both directories accumulate files across runs and are not gitignored. Prune them when the history stops being useful.

To also capture the console output:

```powershell
.\venv\Scripts\python.exe main.py > run.log
```

## Project structure

```
test-stock-ta-opencode/
├── main.py                  # Entry point: fetch -> indicators -> signal -> CSV
├── screener_logic.py        # calculate_indicators() and generate_signal()
├── requirements.txt
├── README.md
├── AGENTS.md                # Rules and verified behavior for AI agents
├── .gitignore
├── .opencode/
│   ├── skills/
│   │   └── stock-ta-screener/
│   │       └── SKILL.md     # Agent workflow for this screener
│   ├── package.json         # Declares @opencode-ai/plugin (gitignored)
│   └── node_modules/        # JS deps above, not part of the Python app (gitignored)
├── tools/
│   ├── data_fetcher.py      # fetch_market_data(), source_data/ writer
│   └── logger.py            # log_signal() -> trade_history.csv (unused)
├── source_data/             # Raw Yahoo Finance CSV dumps
└── output/                  # Timestamped signal CSVs
```

`tools/logger.py` is not wired into the pipeline. Its header is fixed to `Timestamp, Ticker, Signal, RSI`, so passing it a full result row raises `ValueError: dict contains fields not in fieldnames`.

## How the code fits together

```
main.run_screener(tickers)
  └─ tools.data_fetcher.fetch_market_data(tickers)   # 1 batched yfinance call, writes source_data/
  └─ for each ticker:
       screener_logic.calculate_indicators(df)       # adds RSI/SMA/MACD columns, then df.dropna()
       screener_logic.generate_signal(latest_row)    # applies the rule table, returns (signal, reason)
main.save_results_to_csv(results)                    # writes output/ta_stocks_<ts>.csv
```

### Configuration

Tunables are function defaults, not CLI flags:

| Setting | Location | Default |
|---|---|---|
| History window | `tools/data_fetcher.py` `period` | `"1y"` |
| Source data on/off | `tools/data_fetcher.py` `save_source_data` | `True` |
| Source directory | `tools/data_fetcher.py` `source_dir` | `"source_data"` |
| Output directory | `main.py` `save_results_to_csv(output_dir=...)` | `"output"` |

## Limitations

- **One year is a tight window.** SMA(200) needs 200 sessions and `calculate_indicators` drops every row containing a NaN, so a 1-year fetch leaves roughly 50 usable rows. Pass a longer `period` if you need more history.
- **Short or empty history crashes.** Fewer than ~200 usable rows drops to an empty frame and `df.iloc[-1]` raises `IndexError: single positional indexer is out-of-bounds`.
- **Invalid tickers crash.** `ta.macd()` returns `None` for an empty frame, producing `TypeError: 'NoneType' object is not subscriptable` at `screener_logic.py:9`. There is no per-ticker error handling yet.
- **One bad ticker sinks the run.** All tickers share a single download and a single loop; any failure aborts the whole batch before the CSV is written.
- **No tests, no linter, no CI.** Verification means running the CLI and reading the CSV.

## Troubleshooting

### `ModuleNotFoundError: No module named 'yfinance'`

You are not in the venv. Activate it, or call `.\venv\Scripts\python.exe` explicitly.

### `TypeError: 'NoneType' object is not subscriptable` at `screener_logic.py:9`

Yahoo returned no data for at least one symbol. Check the ticker spelling and confirm the download warning above the traceback. Remove the bad symbol and rerun.

### `IndexError: single positional indexer is out-of-bounds`

The ticker has too little history to compute SMA(200). Use a longer `period`, or drop the ticker.

### `ValueError: dict contains fields not in fieldnames`

You called `tools.logger.log_signal()` with a full screener row. That helper only accepts `Timestamp`, `Ticker`, `Signal`, and `RSI`, and `main.py` does not use it.

### Download warnings or empty results

Yahoo Finance rate-limits and occasionally returns partial data. Wait a minute and retry; screening many tickers in a tight loop makes this more likely.

## Disclaimer

This tool is for educational and informational purposes only. It is not financial advice. Technical indicators describe past prices; they do not predict future returns. Do your own research and consult a licensed financial advisor before making investment decisions.

## License

Provided as-is for educational purposes.

## Contributing

Ideas that fit the existing design:

- Per-ticker error handling so one bad symbol does not abort the batch
- A `--period` / `--output` CLI flag instead of editing defaults
- Bollinger Bands and volume confirmation, wired into the rule table and the `Reason` string
- Backtesting against the archived `source_data/` files
- JSON export alongside CSV
