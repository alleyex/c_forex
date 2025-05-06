import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import MetaTrader5 as mt5
import numpy as np
import warnings

# 添加父目錄到系統路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.mt5_trading.connection import MT5Connection
from utils.mt5_trading.history import MT5History
from utils.utils import setup_logger
from utils.data_processing import check_data_quality, process_tick_volume, process_spread

def get_data():
    """
    從 MT5 獲取 EUR/USD 的歷史數據
    """
    # 初始化 MT5
    if not mt5.initialize():
        print("初始化 MT5 失敗")
        mt5.shutdown()
        return None
    
    # 設置時間範圍
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # 獲取 EUR/USD 的歷史數據
    rates = mt5.copy_rates_range("EURUSD", mt5.TIMEFRAME_M1, start_date, end_date)
    
    # 關閉 MT5
    mt5.shutdown()
    
    if rates is None:
        print("獲取數據失敗")
        return None
    
    # 轉換為 DataFrame
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    
    return df

def calculate_technical_indicators(df):
    """
    使用 pandas 計算技術指標
    """
    # 計算 EMA
    df['ema_fast'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=26, adjust=False).mean()
    
    # 計算 MACD
    df['macd'] = df['ema_fast'] - df['ema_slow']
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    
    # 計算 RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # 計算布林通道
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    df['bb_std'] = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + 2 * df['bb_std']
    df['bb_lower'] = df['bb_middle'] - 2 * df['bb_std']
    
    # 計算 ATR
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    df['atr'] = true_range.rolling(window=14).mean()
    
    return df

def main():
    # 創建數據目錄
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    
    # 獲取數據
    df = get_data()
    if df is None:
        return
    
    # 保存原始數據
    raw_data_path = os.path.join(data_dir, 'raw_data.csv')
    df.to_csv(raw_data_path)
    print(f"\n已保存原始數據到: {raw_data_path}")
    
    # 檢查數據質量
    check_data_quality(df)
    
    # 處理 spread 異常值
    df = process_spread(df, data_dir)
    
    # 處理 tick_volume 異常值
    df = process_tick_volume(df, data_dir)
    
    # 計算技術指標
    df = calculate_technical_indicators(df)
    
    # 自創特徵：EMA 差距
    df["ema_gap"] = df["ema_fast"] - df["ema_slow"]

    # 選擇使用的特徵欄位
    selected_features = [
        'open', 'high', 'low', 'close', 'tick_volume_log',
        'is_tick_volume_outlier', 'is_spread_outlier_threshold',
        'ema_fast', 'ema_slow', 'ema_gap',
        'rsi', 'macd', 'macd_signal',
        'bb_middle', 'bb_upper', 'bb_lower',
        'atr'
    ]

    # 去除 NaN（技術指標開頭幾筆資料可能為空）
    df.dropna(subset=selected_features, inplace=True)
    
    # 保存處理後的數據
    processed_data_path = os.path.join(data_dir, 'processed_data.csv')
    df.to_csv(processed_data_path)
    print(f"\n已保存處理後的數據到: {processed_data_path}")

if __name__ == "__main__":
    main()
    
    
    