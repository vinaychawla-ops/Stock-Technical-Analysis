import pandas_ta as ta

def calculate_indicators(df):
    """Adds RSI, SMA, and MACD to the dataframe using pandas_ta."""
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['SMA_50'] = ta.sma(df['Close'], length=50)
    df['SMA_200'] = ta.sma(df['Close'], length=200)
    macd_df = ta.macd(df['Close'])
    df['MACD'] = macd_df['MACD_12_26_9']
    df['MACD_Signal'] = macd_df['MACDs_12_26_9']
    df['MACD_Bullish'] = df['MACD'] > df['MACD_Signal']
    return df.dropna()

def generate_signal(row):
    """Determines Buy/Sell/Hold based on technical rules with MACD filter."""
    macd_state = "bullish" if row['MACD_Bullish'] else "bearish"

    if row['RSI'] < 30 and row['Close'] > row['SMA_200']:
        if row['MACD_Bullish']:
            return "BUY", f"RSI {row['RSI']:.1f} oversold, price above 200-SMA, MACD {macd_state}"
        return "HOLD", f"RSI {row['RSI']:.1f} oversold + price above 200-SMA but MACD {macd_state} (filter blocked)"

    if row['RSI'] > 70:
        if not row['MACD_Bullish']:
            return "SELL", f"RSI {row['RSI']:.1f} overbought, MACD {macd_state}"
        return "HOLD", f"RSI {row['RSI']:.1f} overbought but MACD {macd_state} (filter blocked)"

    return "HOLD", f"RSI {row['RSI']:.1f} neutral (30-70), MACD {macd_state}"