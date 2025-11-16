import pandas as pd
import pandas_ta as ta

def analyze_data(df):
    """
    تحليل بيانات السوق للعثور على إشارة شراء محددة.

    Args:
        df (pd.DataFrame): إطار بيانات يحتوي على بيانات OHLCV.

    Returns:
        bool: True إذا تم استيفاء شروط إشارة الشراء، وإلا False.
    """
    if df is None or len(df) < 2:
        return False

    # حساب المؤشرات الفنية باستخدام pandas_ta
    df.ta.psar(append=True)
    df.ta.rsi(append=True)
    df.ta.macd(append=True)

    # تنظيف قيم NaN
    df.dropna(inplace=True)
    if df.empty:
        return False

    # الحصول على آخر شمعتين للتحقق من التقاطعات
    last_candle = df.iloc[-1]
    prev_candle = df.iloc[-2]

    # --- الشرط الأول: مؤشر Parabolic SAR ---
    # السعر يقترب من قيمة SAR.
    sar_threshold = 0.001  # 0.1%
    sar_close = False
    if last_candle['PSARl_0.02_0.2'] < last_candle['low']:
        if abs(last_candle['low'] - last_candle['PSARl_0.02_0.2']) / last_candle['close'] < sar_threshold:
            sar_close = True
    elif last_candle['PSARs_0.02_0.2'] > last_candle['high']:
        if abs(last_candle['high'] - last_candle['PSARs_0.02_0.2']) / last_candle['close'] < sar_threshold:
            sar_close = True

    # --- الشرط الثاني: مؤشر القوة النسبية (RSI) ---
    rsi_under_50 = last_candle['RSI_14'] < 50

    # --- الشرط الثالث: مؤشر الماكد (MACD) ---
    # خط MACD يتقاطع فوق خط الإشارة، وكلاهما فوق الصفر.
    macd_crossed_up = (prev_candle['MACD_12_26_9'] <= prev_candle['MACDs_12_26_9'] and
                       last_candle['MACD_12_26_9'] > last_candle['MACDs_12_26_9'])
    macd_above_zero = last_candle['MACD_12_26_9'] > 0 and last_candle['MACDs_12_26_9'] > 0

    macd_signal = macd_crossed_up and macd_above_zero

    # التحقق النهائي: يجب أن تكون جميع الشروط صحيحة
    if sar_close and rsi_under_50 and macd_signal:
        return True

    return False
