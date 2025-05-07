import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import MetaTrader5 as mt5
 

# 添加父目錄到系統路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.mt5_trading import MT5Connection, MT5History
from utils.utils import setup_logger
from utils.data_processing import DataProcessor
from utils.technical_indicators import TechnicalIndicatorCalculator

# 設置日誌
logger = setup_logger('forex_trading')

def get_data():
    """
    從 MT5 獲取 EUR/USD 的歷史數據
    """
    logger.info("開始從 MT5 獲取數據")
    
    # 初始化 MT5 連接
    connection = MT5Connection()
    connection.connect()  # 移除 if 判斷，因為 connect() 方法內部已經有錯誤處理
    
    try:
        # 創建歷史數據處理器
        history = MT5History(connection)
        
        # 直接獲取 99000 筆歷史數據 (M1 時間週期)
        df = history.get_historical_data("EURUSD", "M5", count=99000)
        
        if df is None:
            logger.error("獲取數據失敗")
            return None
            
        logger.info(f"成功獲取 {len(df)} 筆數據")
        return df
        
    except Exception as e:
        logger.error(f"獲取數據時發生錯誤: {str(e)}")
        return None
    finally:
        connection.disconnect()

def main():
    logger.info("程式開始執行")
    
    # 創建數據目錄
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    os.makedirs(data_dir, exist_ok=True)
    logger.info(f"數據目錄已創建: {data_dir}")
    
    # 獲取數據
    df = get_data()
    if df is None:
        logger.error("無法獲取數據，程式終止")
        return
    
    # 保存原始數據
    raw_data_path = os.path.join(data_dir, 'raw_data.csv')
    df.to_csv(raw_data_path)
    logger.info(f"原始數據已保存到: {raw_data_path}")
    
    # 初始化數據處理器
    processor = DataProcessor(data_dir)
    
    # 數據處理
    df = processor.process_spread(df)
    df = processor.process_tick_volume(df)
    df = processor.process_price_changes(df)
    
    # 計算技術指標
    calculator = TechnicalIndicatorCalculator()
    df = calculator.calculate_all_indicators(df)
    
    # 檢查數據質量
    processor.check_data_quality(df)
    
    # 自創特徵：EMA 差距
    df["ema_gap"] = df["ema_fast"] - df["ema_slow"]
    logger.info("已計算 EMA 差距特徵")

    # 選擇使用的特徵欄位
    selected_features = [
        'open', 'high', 'low', 'close', 'tick_volume_log',
        'is_tick_volume_outlier', 'is_spread_outlier_threshold',
        'ema_fast', 'ema_slow', 'ema_gap',
        'rsi', 'macd', 'macd_signal',
        'bb_middle', 'bb_upper', 'bb_lower',
        'atr',
        'price_change_pct', 'volatility', 'normalized_price',
        'price_change_ma', 'price_change_volatility'
    ]

    # 去除 NaN（技術指標開頭幾筆資料可能為空）
    df.dropna(subset=selected_features, inplace=True)
    logger.info(f"去除 NaN 後剩餘 {len(df)} 筆數據")
    
    # 保存處理後的數據
    processed_data_path = os.path.join(data_dir, 'processed_data.csv')
    df.to_csv(processed_data_path)
    logger.info(f"處理後的數據已保存到: {processed_data_path}")
    logger.info("程式執行完成")

if __name__ == "__main__":
    main()
    
    
    