import sys
import os
from datetime import datetime, timedelta
import pandas as pd

# 添加父目錄到系統路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.mt5_trading.connection import MT5Connection
from utils.mt5_trading.history import MT5History

def get_eurusd_1m_data(count=10000):
    """
    獲取指定數量的最新 EUR/USD 1分鐘數據
    
    Args:
        count (int): 要獲取的數據筆數，預設為 10000 筆
    """
    # 初始化 MT5 連接
    connection = MT5Connection()
    try:
        connection.connect()
    except Exception as e:
        print(f"MT5 連接失敗: {str(e)}")
        return None
    
    # 創建歷史數據管理器
    history = MT5History(connection)
    
    # 獲取數據（從現在開始往回獲取指定數量的數據）
    df = history.get_historical_data(
        symbol="EURUSD",
        timeframe="M1",
        count=count
    )
    
    # 關閉 MT5 連接
    connection.disconnect()
    
    return df

if __name__ == "__main__":
    # 獲取最新的 99000 筆數據
    df = get_eurusd_1m_data(count=99000)
    
    if df is not None:
        # 顯示數據
        print(f"獲取到 {len(df)} 筆 EUR/USD 1分鐘數據")
        print("\n數據時間範圍：")
        print(f"開始時間：{df.index.min()}")
        print(f"結束時間：{df.index.max()}")
        print("\n前 5 筆數據（最早的數據）：")
        print(df.head())
        print("\n最後 5 筆數據（最新的數據）：")
        print(df.tail())
        
        # 計算數據統計
        print("\n數據統計：")
        print("平均價格：", df['close'].mean())
        print("最高價格：", df['high'].max())
        print("最低價格：", df['low'].min())
        print("總成交量：", df['tick_volume'].sum())
        
        # 保存數據到 CSV 文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"data/eurusd_1m_{timestamp}.csv"
        os.makedirs("data", exist_ok=True)
        df.to_csv(output_file)
        print(f"\n數據已保存到 {output_file}")
    else:
        print("獲取數據失敗")
