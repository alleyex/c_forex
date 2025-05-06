"""
MT5 交易平台的歷史數據管理模組

此模組提供以下主要功能：
1. 歷史數據的獲取和管理
2. 即時報價數據的獲取
3. 數據格式轉換和處理

主要類別：
- HistoryData: 用於存儲單筆歷史數據的資料類別
- MT5History: 提供與 MT5 平台交互的歷史數據管理功能
"""

import MetaTrader5 as mt5
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
import pandas as pd
import os
import sys

from ..utils import setup_logger
from .connection import MT5Connection

@dataclass
class HistoryData:
    """
    歷史數據信息類別
    
    用於存儲單筆歷史數據的資料結構，包含以下欄位：
    - time: 時間戳記
    - open: 開盤價
    - high: 最高價
    - low: 最低價
    - close: 收盤價
    - volume: 成交量
    - spread: 點差
    """
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    spread: int

class MT5History:
    """
    MT5 歷史數據管理類別
    
    提供與 MT5 平台交互的歷史數據管理功能，包括：
    1. 獲取歷史K線數據
    2. 獲取即時報價數據
    3. 數據格式轉換和處理
    
    使用範例：
    >>> history = MT5History(connection)
    >>> df = history.get_historical_data("EURUSD", "H1")
    """
    
    def __init__(self, connection):
        """
        初始化 MT5 歷史數據管理器
        
        Args:
            connection: MT5Connection 實例，用於與 MT5 平台建立連接
        """
        self.connection = connection
        self.logger = setup_logger('MT5History')
        self.logger.info("初始化 MT5History")
        
    def get_historical_data(
        self,
        symbol: str,
        timeframe: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        count: Optional[int] = None
    ) -> pd.DataFrame:
        """
        獲取歷史K線數據
        
        此方法可以通過以下三種方式獲取數據：
        1. 指定時間範圍（start_time 和 end_time）
        2. 指定數量（count）
        3. 不指定任何參數，獲取最近的 1000 筆數據
        
        Args:
            symbol (str): 交易品種，例如 "EURUSD", "GBPUSD" 等
            timeframe (str): 時間週期，支援以下值：
                - 'M1': 1分鐘
                - 'M5': 5分鐘
                - 'M15': 15分鐘
                - 'M30': 30分鐘
                - 'H1': 1小時
                - 'H4': 4小時
                - 'D1': 日線
                - 'W1': 週線
                - 'MN1': 月線
            start_time (datetime, optional): 開始時間
            end_time (datetime, optional): 結束時間
            count (int, optional): 獲取數量
            
        Returns:
            pd.DataFrame: 包含以下欄位的歷史數據：
                - time: 時間戳記
                - open: 開盤價
                - high: 最高價
                - low: 最低價
                - close: 收盤價
                - volume: 成交量
                - spread: 點差
                
        Raises:
            ConnectionError: MT5 未連接時拋出
            ValueError: 交易品種不存在或時間週期不支援時拋出
        """
        if not self.connection.is_connected:
            self.logger.error("MT5 未連接")
            raise ConnectionError("MT5 未連接")
            
        try:
            # 檢查交易品種
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                self.logger.error(f"交易品種 {symbol} 不存在")
                raise ValueError(f"交易品種 {symbol} 不存在")
                
            # 轉換時間週期
            timeframe_map = {
                'M1': mt5.TIMEFRAME_M1,
                'M5': mt5.TIMEFRAME_M5,
                'M15': mt5.TIMEFRAME_M15,
                'M30': mt5.TIMEFRAME_M30,
                'H1': mt5.TIMEFRAME_H1,
                'H4': mt5.TIMEFRAME_H4,
                'D1': mt5.TIMEFRAME_D1,
                'W1': mt5.TIMEFRAME_W1,
                'MN1': mt5.TIMEFRAME_MN1
            }
            
            if timeframe not in timeframe_map:
                self.logger.error(f"不支援的時間週期: {timeframe}")
                raise ValueError(f"不支援的時間週期: {timeframe}")
                
            # 獲取歷史數據
            rates = mt5.copy_rates_range(
                symbol,
                timeframe_map[timeframe],
                start_time or datetime(1970, 1, 1),
                end_time or datetime.now()
            ) if start_time or end_time else mt5.copy_rates_from_pos(
                symbol,
                timeframe_map[timeframe],
                0,
                count or 1000
            )
            
            if rates is None:
                error = mt5.last_error()
                self.logger.error(f"無法獲取歷史數據: {error}")
                raise ValueError(f"無法獲取歷史數據: {error}")
                
            # 轉換為 DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            return df
        except Exception as e:
            self.logger.error(f"獲取歷史數據時發生錯誤: {str(e)}")
            raise ValueError(f"獲取歷史數據時發生錯誤: {str(e)}")
            
    def get_ticks(
        self,
        symbol: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        count: Optional[int] = None
    ) -> pd.DataFrame:
        """
        獲取即時報價數據
        
        此方法可以通過以下三種方式獲取數據：
        1. 指定時間範圍（start_time 和 end_time）
        2. 指定數量（count）
        3. 不指定任何參數，獲取最近的 1000 筆數據
        
        Args:
            symbol (str): 交易品種，例如 "EURUSD", "GBPUSD" 等
            start_time (datetime, optional): 開始時間
            end_time (datetime, optional): 結束時間
            count (int, optional): 獲取數量
            
        Returns:
            pd.DataFrame: 包含以下欄位的即時報價數據：
                - time: 時間戳記
                - bid: 買入價
                - ask: 賣出價
                - volume: 成交量
                
        Raises:
            ConnectionError: MT5 未連接時拋出
            ValueError: 交易品種不存在或獲取數據失敗時拋出
        """
        if not self.connection.is_connected:
            self.logger.error("MT5 未連接")
            raise ConnectionError("MT5 未連接")
            
        try:
            # 檢查交易品種
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                self.logger.error(f"交易品種 {symbol} 不存在")
                raise ValueError(f"交易品種 {symbol} 不存在")
                
            # 獲取即時報價
            ticks = mt5.copy_ticks_range(
                symbol,
                start_time or datetime(1970, 1, 1),
                end_time or datetime.now(),
                mt5.COPY_TICKS_ALL
            ) if start_time or end_time else mt5.copy_ticks_from(
                symbol,
                0,
                count or 1000,
                mt5.COPY_TICKS_ALL
            )
            
            if ticks is None:
                error = mt5.last_error()
                self.logger.error(f"無法獲取即時報價: {error}")
                raise ValueError(f"無法獲取即時報價: {error}")
                
            # 轉換為 DataFrame
            df = pd.DataFrame(ticks)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            return df
        except Exception as e:
            self.logger.error(f"獲取即時報價時發生錯誤: {str(e)}")
            raise ValueError(f"獲取即時報價時發生錯誤: {str(e)}")

if __name__ == "__main__":
    """
    模組測試程式
    
    此部分用於測試模組的主要功能：
    1. 測試歷史數據獲取
    2. 測試即時報價獲取
    3. 測試錯誤處理
    """
    from datetime import datetime, timedelta
    from mt5_trading.connection import MT5Connection
    
    # 建立 MT5 連接
    connection = MT5Connection()
    connection.connect()
    
    # 建立歷史數據管理器
    history = MT5History(connection)
    
    try:
        # 測試獲取歷史數據
        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)
        
        # 獲取 EURUSD 的 H1 歷史數據
        df = history.get_historical_data(
            symbol="EURUSD",
            timeframe="H1",
            start_time=start_time,
            end_time=end_time
        )
        
        print(f"獲取到 {len(df)} 筆歷史數據")
        print("\n前 5 筆數據:")
        print(df.head())
        
        # 測試獲取即時報價
        ticks = history.get_ticks(
            symbol="EURUSD",
            count=10
        )
        
        print(f"\n獲取到 {len(ticks)} 筆即時報價")
        print("\n前 5 筆報價:")
        print(ticks.head())
        
    except Exception as e:
        print(f"測試過程中發生錯誤: {str(e)}")
    finally:
        # 關閉連接
        connection.disconnect() 