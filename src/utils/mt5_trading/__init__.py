"""
MT5 交易平台相關功能模組

此包提供了與 MetaTrader 5 交易平台交互的所有必要功能，包括：
- 連接管理
- 歷史數據獲取
- 帳戶信息查詢
- 交易操作
"""

from .connection import MT5Connection
from .history import MT5History
from .account import MT5Account
from .positions import MT5Positions

__all__ = ['MT5Connection', 'MT5History', 'MT5Account', 'MT5Positions'] 