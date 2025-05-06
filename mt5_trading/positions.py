"""
MT5 交易平台的持倉管理模組

此模組提供與 MetaTrader 5 交易平台相關的持倉管理功能，
包括獲取持倉信息、關閉持倉等操作。
"""

import MetaTrader5 as mt5
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from mt5_trading.utils import setup_logger

@dataclass
class PositionInfo:
    """
    持倉信息數據類別
    
    用於存儲和表示單個持倉的詳細信息，包括：
    - ticket: 持倉的唯一識別碼
    - symbol: 交易品種代碼
    - type: 持倉類型（買入/賣出）
    - volume: 交易量
    - price: 開倉價格
    - sl: 止損價格
    - tp: 止盈價格
    - profit: 當前利潤
    - comment: 持倉註解
    - time: 開倉時間
    """
    ticket: int
    symbol: str
    type: str
    volume: float
    price: float
    sl: float
    tp: float
    profit: float
    comment: str
    time: datetime

class MT5Positions:
    """
    MT5 持倉管理類別
    
    提供與 MetaTrader 5 交易平台相關的持倉管理功能，
    包括獲取持倉信息、關閉持倉等操作。
    
    屬性:
        connection: MT5 連接實例
        logger: 日誌記錄器
    """
    
    def __init__(self, connection):
        """
        初始化 MT5 持倉管理器
        
        Args:
            connection: MT5 連接實例，用於與交易平台通信
        """
        self.connection = connection
        self.logger = setup_logger('MT5Positions')
        self.logger.info("初始化 MT5Positions")
        
    def get_positions(self, symbol: Optional[str] = None) -> List[PositionInfo]:
        """
        獲取持倉信息
        
        此方法可以獲取指定交易品種的所有持倉，或獲取所有持倉信息。
        如果獲取失敗，會拋出相應的錯誤。
        
        Args:
            symbol (str, optional): 交易品種代碼，如果為 None 則獲取所有持倉
            
        Returns:
            List[PositionInfo]: 持倉信息列表，每個元素包含一個持倉的詳細信息
            
        Raises:
            ConnectionError: 當 MT5 未連接時拋出
            ValueError: 當無法獲取持倉信息時拋出
        """
        if not self.connection.is_connected:
            self.logger.error("MT5 未連接")
            raise ConnectionError("MT5 未連接")
            
        try:
            positions = mt5.positions_get(symbol=symbol) if symbol else mt5.positions_get()
            if positions is None:
                error = mt5.last_error()
                self.logger.error(f"無法獲取持倉信息: {error}")
                raise ValueError(f"無法獲取持倉信息: {error}")
                
            result = []
            for pos in positions:
                result.append(PositionInfo(
                    ticket=pos.ticket,
                    symbol=pos.symbol,
                    type="BUY" if pos.type == mt5.POSITION_TYPE_BUY else "SELL",
                    volume=pos.volume,
                    price=pos.price_open,
                    sl=pos.sl,
                    tp=pos.tp,
                    profit=pos.profit,
                    comment=pos.comment,
                    time=datetime.fromtimestamp(pos.time)
                ))
                
            return result
        except Exception as e:
            self.logger.error(f"獲取持倉信息時發生錯誤: {str(e)}")
            raise ValueError(f"獲取持倉信息時發生錯誤: {str(e)}")
            
    def close_position(self, ticket: int) -> bool:
        """
        關閉指定編號的持倉
        
        此方法會根據持倉編號找到對應的持倉，並執行關閉操作。
        關閉操作包括：
        1. 獲取持倉信息
        2. 準備關閉請求
        3. 發送關閉請求
        4. 處理關閉結果
        
        Args:
            ticket (int): 要關閉的持倉編號
            
        Returns:
            bool: 關閉操作是否成功
            
        Raises:
            ConnectionError: 當 MT5 未連接時拋出
        """
        if not self.connection.is_connected:
            self.logger.error("MT5 未連接")
            raise ConnectionError("MT5 未連接")
            
        try:
            # 獲取持倉信息
            position = mt5.positions_get(ticket=ticket)
            if position is None or len(position) == 0:
                error = mt5.last_error()
                self.logger.error(f"找不到持倉 {ticket}: {error}")
                return False
                
            position = position[0]
            
            # 準備關閉請求
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": mt5.ORDER_TYPE_SELL if position.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                "position": ticket,
                "price": mt5.symbol_info_tick(position.symbol).bid if position.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info_tick(position.symbol).ask,
                "deviation": 10,
                "magic": position.magic,
                "comment": "Close position",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # 發送關閉請求
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                self.logger.error(f"關閉持倉失敗: {result.comment}")
                return False
                
            self.logger.info(f"關閉持倉成功: {result.comment}")
            return True
        except Exception as e:
            self.logger.error(f"關閉持倉時發生錯誤: {str(e)}")
            return False 

if __name__ == "__main__":
    """
    測試代碼
    
    此部分代碼用於測試 MT5Positions 類的功能，包括：
    1. 創建 MT5 連接
    2. 獲取所有持倉信息
    3. 顯示持倉詳細信息
    """
    from mt5_trading.connection import MT5Connection
    
    # 創建連接
    connection = MT5Connection()
    try:
        connection.connect()
        if not connection.is_connected:
            print("無法連接到 MT5")
            exit(1)
            
        # 創建持倉管理器
        positions_manager = MT5Positions(connection)
        
        # 獲取所有持倉
        all_positions = positions_manager.get_positions()
        print(f"當前持倉數量: {len(all_positions)}")
        
        # 顯示每個持倉的詳細信息
        for pos in all_positions:
            print(f"\n持倉信息:")
            print(f"編號: {pos.ticket}")
            print(f"品種: {pos.symbol}")
            print(f"類型: {pos.type}")
            print(f"數量: {pos.volume}")
            print(f"價格: {pos.price}")
            print(f"止損: {pos.sl}")
            print(f"止盈: {pos.tp}")
            print(f"利潤: {pos.profit}")
            print(f"時間: {pos.time}")
            
    except Exception as e:
        print(f"發生錯誤: {str(e)}")
    finally:
        # 斷開連接
        connection.disconnect() 