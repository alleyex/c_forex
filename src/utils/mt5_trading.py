"""
MT5 交易平台整合模組

此模組整合了所有 MT5 交易相關的功能，包括：
1. 連接管理
2. 帳戶管理
3. 持倉管理
4. 歷史數據管理
"""

import MetaTrader5 as mt5
import json
import os
import sys
import pandas as pd
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.utils import setup_logger

# ==================== 連接管理 ====================
class MT5Connection:
    """
    MT5 連接管理類別
    此類別提供了一個完整的 MT5 連接管理解決方案，包括：
    - 憑證管理
    - 連接建立與斷開
    - 錯誤處理
    - 日誌記錄
    """
    
    def __init__(self, credentials_file: str = "credential.json"):
        """
        初始化 MT5 連接管理器
        
        Args:
            credentials_file (str): 憑證檔案的名稱，預設為 "credential.json"
        """
        self._is_connected = False  # 連接狀態標記
        self.logger = setup_logger('MT5Connection', log_dir=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')))
        self.logger.info("初始化 MT5Connection")
        
        # 取得專案根目錄的路徑
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        # 設定憑證檔案的路徑
        self.credentials_path = os.path.join(project_root, "config", credentials_file)
        self._load_credentials(self.credentials_path)
        
    def _load_credentials(self, file: str) -> None:
        """
        從 JSON 檔案載入 MT5 登入憑證
        """
        try:
            self.logger.info(f"正在載入憑證檔案: {file}")
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.login = data['login_id']      # MT5 帳號
                self.password = data['password']   # MT5 密碼
                self.server = data['server']       # MT5 伺服器
            self.logger.info("憑證載入成功")
        except FileNotFoundError:
            self.logger.error(f"找不到憑證檔案: {file}")
            raise FileNotFoundError(f"找不到憑證檔案: {file}")
        except json.JSONDecodeError:
            self.logger.error(f"憑證檔案格式錯誤: {file}")
            raise ValueError(f"憑證檔案格式錯誤: {file}")
        except KeyError as e:
            self.logger.error(f"憑證缺少必要欄位: {e}")
            raise ValueError(f"憑證缺少必要欄位: {e}")
            
    def connect(self) -> None:
        """
        建立與 MT5 平台的連接
        """
        try:
            self.logger.info("正在初始化 MT5 連接")
            if not mt5.initialize():
                error = mt5.last_error()
                self.logger.error(f"初始化失敗: {error}")
                raise ConnectionError(f"初始化失敗: {error}")
                
            self.logger.info("正在登入 MT5")
            if not mt5.login(
                login=self.login,
                password=self.password,
                server=self.server
            ):
                error = mt5.last_error()
                self.logger.error(f"登入失敗: {error}")
                raise ConnectionError(f"登入失敗: {error}")
                
            self._is_connected = True
            self.logger.info("MT5 連接成功")
        except Exception as e:
            self.logger.error(f"連接失敗: {str(e)}")
            self.disconnect()
            raise ConnectionError(f"連接失敗: {str(e)}")
            
    def disconnect(self) -> None:
        """
        安全地斷開與 MT5 平台的連接
        """
        try:
            if self._is_connected:
                self.logger.info("正在斷開 MT5 連接")
                mt5.shutdown()
                self._is_connected = False
                self.logger.info("MT5 連接已斷開")
        except Exception as e:
            self.logger.error(f"斷開連接時發生錯誤: {str(e)}")
            
    @property
    def is_connected(self) -> bool:
        """
        檢查當前是否與 MT5 平台保持連接
        """
        return self._is_connected and mt5.terminal_info() is not None
            
    def __enter__(self):
        """
        支援 with 語句的上下文管理器入口
        """
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        支援 with 語句的上下文管理器出口
        """
        self.disconnect()

# ==================== 帳戶管理 ====================
@dataclass
class AccountInfo:
    """
    帳戶信息數據類別
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
        將帳戶信息轉換為字典格式
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
    """
    
    def __init__(self, connection: Any):
        """
        初始化 MT5 帳戶管理器
        """
        self.connection = connection
        self.logger = setup_logger('MT5Account', log_dir=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')))
        self.logger.info("初始化 MT5Account")
        
    def get_account_info(self) -> AccountInfo:
        """
        獲取當前帳戶的完整信息
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

# ==================== 持倉管理 ====================
@dataclass
class PositionInfo:
    """
    持倉信息數據類別
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
    """
    
    def __init__(self, connection):
        """
        初始化 MT5 持倉管理器
        """
        self.connection = connection
        self.logger = setup_logger('MT5Positions', log_dir=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')))
        self.logger.info("初始化 MT5Positions")
        
    def get_positions(self, symbol: Optional[str] = None) -> List[PositionInfo]:
        """
        獲取持倉信息
        """
        if not self.connection.is_connected:
            self.logger.error("MT5 未連接")
            raise ConnectionError("MT5 未連接")
            
        try:
            self.logger.info(f"正在獲取持倉信息，交易品種: {symbol if symbol else '所有'}")
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
                
            self.logger.info(f"成功獲取 {len(result)} 筆持倉信息")
            return result
        except Exception as e:
            self.logger.error(f"獲取持倉信息時發生錯誤: {str(e)}")
            raise ValueError(f"獲取持倉信息時發生錯誤: {str(e)}")
            
    def close_position(self, ticket: int) -> bool:
        """
        關閉指定編號的持倉
        """
        if not self.connection.is_connected:
            self.logger.error("MT5 未連接")
            raise ConnectionError("MT5 未連接")
            
        try:
            self.logger.info(f"正在關閉持倉 {ticket}")
            position = mt5.positions_get(ticket=ticket)
            if position is None or len(position) == 0:
                error = mt5.last_error()
                self.logger.error(f"找不到持倉 {ticket}: {error}")
                return False
                
            position = position[0]
            
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
            
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                self.logger.error(f"關閉持倉失敗: {result.comment}")
                return False
                
            self.logger.info(f"成功關閉持倉 {ticket}: {result.comment}")
            return True
        except Exception as e:
            self.logger.error(f"關閉持倉時發生錯誤: {str(e)}")
            return False

# ==================== 歷史數據管理 ====================
@dataclass
class HistoryData:
    """
    歷史數據信息類別
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
    """
    
    def __init__(self, connection):
        """
        初始化 MT5 歷史數據管理器
        """
        self.connection = connection
        self.logger = setup_logger('MT5History', log_dir=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')))
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
        """
        if not self.connection.is_connected:
            self.logger.error("MT5 未連接")
            raise ConnectionError("MT5 未連接")
            
        try:
            self.logger.info(f"正在獲取 {symbol} 的歷史數據，時間週期: {timeframe}")
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                self.logger.error(f"交易品種 {symbol} 不存在")
                raise ValueError(f"交易品種 {symbol} 不存在")
                
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
                
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            self.logger.info(f"成功獲取 {len(df)} 筆歷史數據")
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
        """
        if not self.connection.is_connected:
            self.logger.error("MT5 未連接")
            raise ConnectionError("MT5 未連接")
            
        try:
            self.logger.info(f"正在獲取 {symbol} 的即時報價數據")
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                self.logger.error(f"交易品種 {symbol} 不存在")
                raise ValueError(f"交易品種 {symbol} 不存在")
                
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
                
            df = pd.DataFrame(ticks)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            self.logger.info(f"成功獲取 {len(df)} 筆即時報價數據")
            return df
        except Exception as e:
            self.logger.error(f"獲取即時報價時發生錯誤: {str(e)}")
            raise ValueError(f"獲取即時報價時發生錯誤: {str(e)}")

# ==================== 測試程式 ====================
if __name__ == "__main__":
    """
    模組測試程式
    """
    try:
        # 創建連接
        connection = MT5Connection()
        connection.connect()
        
        if not connection.is_connected:
            print("無法連接到 MT5")
            exit(1)
            
        # 測試帳戶管理
        account = MT5Account(connection)
        account_info = account.get_account_info()
        print("\n帳戶信息:")
        print(f"餘額: {account_info.balance}")
        print(f"淨值: {account_info.equity}")
        print(f"保證金: {account_info.margin}")
        print(f"可用保證金: {account_info.free_margin}")
        print(f"保證金水平: {account_info.margin_level}")
        print(f"貨幣: {account_info.currency}")
        print(f"槓桿: {account_info.leverage}")
        
        # 測試持倉管理
        positions = MT5Positions(connection)
        all_positions = positions.get_positions()
        print(f"\n當前持倉數量: {len(all_positions)}")
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
            
        # 測試歷史數據
        history = MT5History(connection)
        df = history.get_historical_data("EURUSD", "H1", count=10)
        print("\n歷史數據:")
        print(df)
        
        # 測試即時報價
        ticks = history.get_ticks("EURUSD", count=5)
        print("\n即時報價:")
        print(ticks)
        
    except Exception as e:
        print(f"測試過程中發生錯誤: {str(e)}")
    finally:
        # 斷開連接
        connection.disconnect() 