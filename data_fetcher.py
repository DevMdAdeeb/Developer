import ccxt
import pandas as pd

def get_data(symbol, timeframe):
    """
    جلب بيانات الشموع التاريخية من منصة OKX.

    Args:
        symbol (str): رمز زوج التداول (مثال: 'BTC/USDT').
        timeframe (str): الإطار الزمني للبيانات (مثال: '1h', '4h').

    Returns:
        pandas.DataFrame: إطار بيانات يحتوي على بيانات OHLCV، أو None في حالة حدوث خطأ.
    """
    try:
        exchange = ccxt.okx()
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
        if ohlcv:
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
    except ccxt.NetworkError as e:
        print(f"خطأ في الشبكة أثناء جلب البيانات لـ {symbol} على الإطار الزمني {timeframe}: {e}")
    except ccxt.ExchangeError as e:
        print(f"خطأ في المنصة أثناء جلب البيانات لـ {symbol} على الإطار الزمني {timeframe}: {e}")
    except Exception as e:
        print(f"حدث خطأ غير متوقع أثناء جلب البيانات لـ {symbol} على الإطار الزمني {timeframe}: {e}")

    return None

if __name__ == '__main__':
    # مثال للاستخدام بغرض الاختبار
    symbol_to_test = 'BTC/USDT'
    timeframe_to_test = '1h'
    data = get_data(symbol_to_test, timeframe_to_test)

    if data is not None and not data.empty:
        print(f"تم جلب البيانات بنجاح لـ {symbol_to_test} على الإطار الزمني {timeframe_to_test}:")
        print(data.head())
        print("\nأعمدة البيانات وأنواعها:")
        print(data.info())
    else:
        print(f"فشل جلب البيانات لـ {symbol_to_test} على الإطار الزمني {timeframe_to_test}.")
