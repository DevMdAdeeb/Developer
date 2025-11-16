import pandas as pd
import pandas_ta as ta

def analyze_data(df):
    """
    Analyzes the market data to find a specific buy signal.

    Args:
        df (pd.DataFrame): DataFrame with OHLCV data.

    Returns:
        bool: True if the buy signal conditions are met, False otherwise.
    """
    if df is None or len(df) < 2:
        return False

    # Calculate technical indicators using pandas_ta
    df.ta.psar(append=True)
    df.ta.rsi(append=True)
    df.ta.macd(append=True)

    # Clean up NaN values
    df.dropna(inplace=True)
    if df.empty:
        return False

    # Get the last two candles for crossover checks
    last_candle = df.iloc[-1]
    prev_candle = df.iloc[-2]

    # --- Condition 1: Parabolic SAR ---
    # The price is approaching the SAR value.
    sar_threshold = 0.001  # 0.1%
    sar_close = False
    if last_candle['PSARl_0.02_0.2'] < last_candle['low']:
        if abs(last_candle['low'] - last_candle['PSARl_0.02_0.2']) / last_candle['close'] < sar_threshold:
            sar_close = True
    elif last_candle['PSARs_0.02_0.2'] > last_candle['high']:
        if abs(last_candle['high'] - last_candle['PSARs_0.02_0.2']) / last_candle['close'] < sar_threshold:
            sar_close = True

    # --- Condition 2: RSI ---
    rsi_under_50 = last_candle['RSI_14'] < 50

    # --- Condition 3: MACD ---
    # MACD line crosses above the signal line, and both are above zero.
    macd_crossed_up = (prev_candle['MACD_12_26_9'] <= prev_candle['MACDs_12_26_9'] and
                       last_candle['MACD_12_26_9'] > last_candle['MACDs_12_26_9'])
    macd_above_zero = last_candle['MACD_12_26_9'] > 0 and last_candle['MACDs_12_26_9'] > 0

    macd_signal = macd_crossed_up and macd_above_zero

    # Final check: all conditions must be true
    if sar_close and rsi_under_50 and macd_signal:
        return True

    return False
