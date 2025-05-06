"""
MT5 交易平台的帳戶管理模組

此模組提供 MT5 交易平台的帳戶管理功能，包括：
- 帳戶資訊的獲取和處理
- 帳戶狀態的監控
- 帳戶相關數據的格式化輸出
"""

import sys
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import MetaTrader5 as mt5
from ..utils import setup_logger
from .connection import MT5Connection

# 添加專案根目錄到 Python 路徑，確保可以正確導入其他模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@dataclass
class AccountInfo:
    """
    帳戶信息數據類別
    
    用於封裝和處理 MT5 帳戶的相關信息，包括：
    - balance: 帳戶餘額
    - equity: 帳戶淨值
    - margin: 已用保證金
    - free_margin: 可用保證金
    - margin_level: 保證金水平
    - currency: 帳戶貨幣
    - leverage: 槓桿倍數
    """
    balance: float
    equity: float
    margin: float
    free_margin: float
    margin_level: float
    currency: str
    leverage: int
    
    @classmethod
    def from_mt5_account_info(cls, mt5_info: Any) -> 'AccountInfo':
        """
        從 MT5 帳戶信息創建 AccountInfo 實例
        
        Args:
            mt5_info: MT5 平台返回的原始帳戶信息
            
        Returns:
            AccountInfo: 封裝後的帳戶信息實例
        """
        return cls(
            balance=mt5_info.balance,
            equity=mt5_info.equity,
            margin=mt5_info.margin,
            free_margin=mt5_info.margin_free,
            margin_level=mt5_info.margin_level,
            currency=mt5_info.currency,
            leverage=mt5_info.leverage
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        將帳戶信息轉換為字典格式，方便序列化和存儲
        
        Returns:
            Dict[str, Any]: 包含所有帳戶信息的字典
        """
        return {
            'balance': self.balance,
            'equity': self.equity,
            'margin': self.margin,
            'free_margin': self.free_margin,
            'margin_level': self.margin_level,
            'currency': self.currency,
            'leverage': self.leverage
        }

class MT5Account:
    """
    MT5 帳戶管理類別
    
    Provides full account management functionality for MT5 accounts, including:
    - Connection status management
    - Account information retrieval
    - Error handling and logging
    """
    
    def __init__(self, connection: Any):
        """
        初始化 MT5 帳戶管理器
        
        Args:
            connection: MT5 連接實例，用於管理與 MT5 平台的連接狀態
        """
        self.connection = connection
        self.logger = setup_logger('MT5Account')
        self.logger.info("初始化 MT5Account")
        
    def get_account_info(self) -> AccountInfo:
        """
        獲取當前帳戶的完整信息
        
        Returns:
            AccountInfo: 封裝後的帳戶信息實例
            
        Raises:
            ConnectionError: 當 MT5 未連接時
            ValueError: 當無法獲取帳戶信息時
        """
        if not self.connection.is_connected:
            self.logger.error("MT5 未連接")
            raise ConnectionError("MT5 未連接")
            
        try:
            account_info = mt5.account_info()
            if account_info is None:
                error = mt5.last_error()
                self.logger.error(f"無法獲取帳戶信息: {error}")
                raise ValueError(f"無法獲取帳戶信息: {error}")
                
            return AccountInfo.from_mt5_account_info(account_info)
        except Exception as e:
            self.logger.error(f"獲取帳戶信息時發生錯誤: {str(e)}")
            raise ValueError(f"獲取帳戶信息時發生錯誤: {str(e)}")

def run_tests() -> None:
    """
    運行帳戶管理相關的測試
    
    This function is used to test account management functionality, including:
    - MT5 platform initialization
    - Account information retrieval
    - Data display
    """
    # 初始化 MT5
    if not mt5.initialize():
        print("MT5 初始化失敗")
        mt5.shutdown()
        sys.exit(1)
        
    try:
        # 創建模擬連接
        mock_conn = MockConnection(is_connected=True)
        
        # 創建帳戶管理器實例
        account_manager = MT5Account(mock_conn)
        
        try:
            # 測試獲取帳戶信息
            account_info = account_manager.get_account_info()
            print("帳戶信息測試成功！")
            print(f"餘額: {account_info.balance}")
            print(f"淨值: {account_info.equity}")
            print(f"保證金: {account_info.margin}")
            print(f"可用保證金: {account_info.free_margin}")
            print(f"保證金水平: {account_info.margin_level}")
            print(f"貨幣: {account_info.currency}")
            print(f"槓桿: {account_info.leverage}")
        except Exception as e:
            print(f"測試失敗: {str(e)}")
    finally:
        # 關閉 MT5 連接
        mt5.shutdown()

class MockConnection:
    """
    模擬 MT5 連接類別
    
    Used in testing environments to simulate MT5 platform connection status
    """
    def __init__(self, is_connected: bool = True):
        self.is_connected = is_connected

if __name__ == "__main__":
    run_tests() 