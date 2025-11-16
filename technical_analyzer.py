import pandas as pd
import numpy as np

# --- وظائف حساب المؤشرات الفنية ---

def calculate_rsi(df, period=14):
    """حساب مؤشر القوة النسبية (RSI)."""
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(df, fast_period=12, slow_period=26, signal_period=9):
    """حساب مؤشر الماكد (MACD)."""
    fast_ema = df['close'].ewm(span=fast_period, adjust=False).mean()
    slow_ema = df['close'].ewm(span=slow_period, adjust=False).mean()
    macd = fast_ema - slow_ema
    signal_line = macd.ewm(span=signal_period, adjust=False).mean()
    return macd, signal_line

def calculate_psar(df, iaf=0.02, maxaf=0.2):
    """حساب مؤشر Parabolic SAR."""
    length = len(df)
    high = df['high']
    low = df['low']
    close = df['close']

    psar = close.copy()
    psarbull = [None] * length
    psarbear = [None] * length
    bull = True
    af = iaf
    ep = low[0]
    hp = high[0]
    lp = low[0]

    for i in range(2, length):
        if bull:
            psar[i] = psar[i - 1] + af * (hp - psar[i - 1])
        else:
            psar[i] = psar[i - 1] + af * (lp - psar[i - 1])

        reverse = False

        if bull:
            if low[i] < psar[i]:
                bull = False
                reverse = True
                psar[i] = hp
                lp = low[i]
                af = iaf
        else:
            if high[i] > psar[i]:
                bull = True
                reverse = True
                psar[i] = lp
                hp = high[i]
                af = iaf

        if not reverse:
            if bull:
                if high[i] > hp:
                    hp = high[i]
                    af = min(af + iaf, maxaf)
                if low[i - 1] < psar[i]:
                    psar[i] = low[i - 1]
                if low[i - 2] < psar[i]:
                    psar[i] = low[i - 2]
            else:
                if low[i] < lp:
                    lp = low[i]
                    af = min(af + iaf, maxaf)
                if high[i - 1] > psar[i]:
                    psar[i] = high[i - 1]
                if high[i - 2] > psar[i]:
                    psar[i] = high[i - 2]

        if bull:
            psarbull[i] = psar[i]
        else:
            psarbear[i] = psar[i]

    return pd.Series(psarbull, index=df.index), pd.Series(psarbear, index=df.index)

# --- دالة التحليل الرئيسية ---

def analyze_data(df):
    """
    تحليل بيانات السوق للعثور على إشارة شراء محددة.
    """
    if df is None or len(df) < 26:  # MACD يحتاج على الأقل 26 نقطة
        return False

    # حساب المؤشرات الفنية
    df['RSI_14'] = calculate_rsi(df)
    df['MACD_12_26_9'], df['MACDs_12_26_9'] = calculate_macd(df)
    df['PSARl_0.02_0.2'], df['PSARs_0.02_0.2'] = calculate_psar(df)

    # تنظيف قيم NaN الناتجة عن حساب المؤشرات
    df.dropna(inplace=True)
    if df.empty or len(df) < 2:
        return False

    # الحصول على آخر شمعتين للتحقق من التقاطعات
    last_candle = df.iloc[-1]
    prev_candle = df.iloc[-2]

    # --- الشرط الأول: مؤشر Parabolic SAR ---
    sar_threshold = 0.001  # 0.1%
    sar_close = False
    if pd.notna(last_candle['PSARl_0.02_0.2']) and last_candle['PSARl_0.02_0.2'] < last_candle['low']:
        if abs(last_candle['low'] - last_candle['PSARl_0.02_0.2']) / last_candle['close'] < sar_threshold:
            sar_close = True
    elif pd.notna(last_candle['PSARs_0.02_0.2']) and last_candle['PSARs_0.02_0.2'] > last_candle['high']:
        if abs(last_candle['high'] - last_candle['PSARs_0.02_0.2']) / last_candle['close'] < sar_threshold:
            sar_close = True

    # --- الشرط الثاني: مؤشر القوة النسبية (RSI) ---
    rsi_under_50 = last_candle['RSI_14'] < 50

    # --- الشرط الثالث: مؤشر الماكد (MACD) ---
    macd_crossed_up = (prev_candle['MACD_12_26_9'] <= prev_candle['MACDs_12_26_9'] and
                       last_candle['MACD_12_26_9'] > last_candle['MACDs_12_26_9'])
    macd_above_zero = last_candle['MACD_12_26_9'] > 0 and last_candle['MACDs_12_26_9'] > 0
    macd_signal = macd_crossed_up and macd_above_zero

    # التحقق النهائي: يجب أن تكون جميع الشروط صحيحة
    if sar_close and rsi_under_50 and macd_signal:
        return True

    return False
