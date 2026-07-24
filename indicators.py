import pandas as pd
import numpy as np

def calculate_rsi(df, period=14):
    """
    Calculates the Wilder's Relative Strength Index (RSI).
    """
    if len(df) < period + 1:
        df['RSI'] = 50.0
        return df
    
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).copy()
    loss = (-delta.where(delta < 0, 0)).copy()

    # Exponentially Weighted Moving Average for gains/losses (Wilder's style)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period).mean()

    rs = avg_gain / (avg_loss + 1e-10)
    df['RSI'] = 100 - (100 / (1 + rs))
    df['RSI'] = df['RSI'].fillna(50.0)
    return df

def calculate_ichimoku(df, n1=9, n2=26, n3=52):
    """
    Calculates the Ichimoku Kinko Hyo components:
    - Tenkan-sen (Conversion Line)
    - Kijun-sen (Base Line)
    - Senkou Span A (Leading Span A) - projected 26 periods ahead
    - Senkou Span B (Leading Span B) - projected 26 periods ahead
    - Chikou Span (Lagging Span) - projected 26 periods back
    """
    if len(df) < n3:
        # Fallback empty structures if there's not enough data
        df['tenkan_sen'] = df['close']
        df['kijun_sen'] = df['close']
        df['senkou_span_a'] = df['close']
        df['senkou_span_b'] = df['close']
        df['chikou_span'] = df['close']
        return df

    # Tenkan-sen (Conversion Line): (9-period high + 9-period low) / 2
    period9_high = df['high'].rolling(window=n1).max()
    period9_low = df['low'].rolling(window=n1).min()
    df['tenkan_sen'] = (period9_high + period9_low) / 2

    # Kijun-sen (Base Line): (26-period high + 26-period low) / 2
    period26_high = df['high'].rolling(window=n2).max()
    period26_low = df['low'].rolling(window=n2).min()
    df['kijun_sen'] = (period26_high + period26_low) / 2

    # Senkou Span A (Leading Span A): (Conversion Line + Base Line) / 2
    # Shifted 26 periods forward
    df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(n2)

    # Senkou Span B (Leading Span B): (52-period high + 52-period low) / 2
    # Shifted 26 periods forward
    period52_high = df['high'].rolling(window=n3).max()
    period52_low = df['low'].rolling(window=n3).min()
    df['senkou_span_b'] = ((period52_high + period52_low) / 2).shift(n2)

    # Chikou Span (Lagging Span): Close shifted 26 periods backward
    df['chikou_span'] = df['close'].shift(-n2)

    return df

def calculate_moving_averages(df, ma_short=20, ma_medium=50, ma_long=200):
    """
    Calculates Exponential Moving Averages (EMA) for 20, 50, and 200 periods.
    """
    df[f'EMA_{ma_short}'] = df['close'].ewm(span=ma_short, adjust=False).mean()
    df[f'EMA_{ma_medium}'] = df['close'].ewm(span=ma_medium, adjust=False).mean()
    df[f'EMA_{ma_long}'] = df['close'].ewm(span=ma_long, adjust=False).mean()
    
    # Simple Moving Averages (optional backup)
    df[f'SMA_{ma_short}'] = df['close'].rolling(window=ma_short).mean().fillna(df['close'])
    df[f'SMA_{ma_medium}'] = df['close'].rolling(window=ma_medium).mean().fillna(df['close'])
    df[f'SMA_{ma_long}'] = df['close'].rolling(window=ma_long).mean().fillna(df['close'])
    
    return df

def process_all_indicators(df, config):
    """
    Applies all specified indicators to the dataframe.
    """
    df = calculate_rsi(df, period=config.get("rsi_period", 14))
    df = calculate_ichimoku(df, 
                            n1=config.get("ichimoku_tenkan", 9), 
                            n2=config.get("ichimoku_kijun", 26), 
                            n3=config.get("ichimoku_senkou_b", 52))
    df = calculate_moving_averages(df, 
                                   ma_short=config.get("ma_short", 20), 
                                   ma_medium=config.get("ma_medium", 50), 
                                   ma_long=config.get("ma_long", 200))
    return df
