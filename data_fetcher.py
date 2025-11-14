import ccxt
import pandas as pd

def get_data(symbol, timeframe):
    """
    Fetches historical candlestick data from Binance.

    Args:
        symbol (str): The trading pair symbol (e.g., 'BTC/USDT').
        timeframe (str): The timeframe for the data (e.g., '1h', '4h').

    Returns:
        pandas.DataFrame: A DataFrame containing the OHLCV data, or None if an error occurs.
    """
    try:
        exchange = ccxt.okx()
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
        if ohlcv:
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
    except ccxt.NetworkError as e:
        print(f"Network error while fetching data for {symbol} on {timeframe}: {e}")
    except ccxt.ExchangeError as e:
        print(f"Exchange error while fetching data for {symbol} on {timeframe}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while fetching data for {symbol} on {timeframe}: {e}")

    return None

if __name__ == '__main__':
    # Example usage for testing
    symbol_to_test = 'BTC/USDT'
    timeframe_to_test = '1h'
    data = get_data(symbol_to_test, timeframe_to_test)

    if data is not None and not data.empty:
        print(f"Successfully fetched data for {symbol_to_test} on {timeframe_to_test}:")
        print(data.head())
        print("\nData columns and types:")
        print(data.info())
    else:
        print(f"Failed to fetch data for {symbol_to_test} on {timeframe_to_test}.")
