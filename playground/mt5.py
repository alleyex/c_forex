"""
MetaTrader 5 (MT5) 交易平台連接模組

使用範例：
    with MT5Manager() as mt5_manager:
        if mt5_manager.is_connected:
            # 進行 MT5 操作
            pass
"""

import MetaTrader5 as mt5
import json
import pandas as pd
from datetime import datetime, timedelta

class MT5Manager:
    """MT5 管理類別"""
    
    def __init__(self, credentials_file: str = "credential.json"):
        """初始化 MT5 管理器"""
        self._is_connected = False
        self._load_credentials(credentials_file)
        
    def _load_credentials(self, file: str) -> None:
        """載入憑證"""
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.login = data['login_id']
                self.password = data['password']
                self.server = data['server']
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到憑證檔案: {file}")
        except json.JSONDecodeError:
            raise ValueError(f"憑證檔案格式錯誤: {file}")
        except KeyError as e:
            raise ValueError(f"憑證缺少必要欄位: {e}")
            
    def connect(self) -> None:
        """建立 MT5 連接"""
        try:
            if not mt5.initialize():
                raise ConnectionError(f"初始化失敗: {mt5.last_error()}")
                
            if not mt5.login(
                login=self.login,
                password=self.password,
                server=self.server
            ):
                raise ConnectionError(f"登入失敗: {mt5.last_error()}")
                
            self._is_connected = True
        except Exception as e:
            self.disconnect()
            raise ConnectionError(f"連接失敗: {str(e)}")
            
    def disconnect(self) -> None:
        """斷開 MT5 連接"""
        try:
            if self._is_connected:
                mt5.shutdown()
                self._is_connected = False
        except Exception as e:
            print(f"斷開連接時發生錯誤: {str(e)}")
            
    @property
    def is_connected(self) -> bool:
        """檢查是否已連接"""
        return self._is_connected and mt5.terminal_info() is not None
            
    def __enter__(self):
        """進入 with 區塊時自動連接"""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """離開 with 區塊時自動斷開"""
        self.disconnect()

    def get_historical_data(self, symbol: str, timeframe: int, start_date: datetime, end_date: datetime = None) -> pd.DataFrame:
        """
        獲取歷史數據
        
        Args:
            symbol (str): 交易品種，例如 "EURUSD"
            timeframe (int): 時間週期，例如 mt5.TIMEFRAME_M1, mt5.TIMEFRAME_H1
            start_date (datetime): 開始日期
            end_date (datetime, optional): 結束日期，預設為現在
            
        Returns:
            pd.DataFrame: 包含歷史數據的 DataFrame
        """
        if not self.is_connected:
            raise ConnectionError("MT5 未連接")
            
        if end_date is None:
            end_date = datetime.now()
            
        try:
            # 檢查交易品種是否可用
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                raise ValueError(f"交易品種 {symbol} 不存在")
                
            if not symbol_info.visible:
                print(f"交易品種 {symbol} 未啟用，嘗試啟用...")
                if not mt5.symbol_select(symbol, True):
                    raise ValueError(f"無法啟用交易品種 {symbol}: {mt5.last_error()}")
            
            # 獲取歷史數據
            print(f"正在獲取 {symbol} 的歷史數據...")
            print(f"時間範圍: {start_date} 到 {end_date}")
            print(f"時間週期: {timeframe}")
            
            rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_date)
            
            if rates is None:
                error = mt5.last_error()
                print(f"MT5 錯誤代碼: {error}")
                raise ValueError(f"無法獲取 {symbol} 的歷史數據: {error}")
                
            # 轉換為 DataFrame
            df = pd.DataFrame(rates)
            
            if df.empty:
                print("警告：獲取到的數據為空")
                print("可能的原因：")
                print("1. 指定的時間範圍內沒有數據")
                print("2. 交易品種未啟用")
                print("3. 時間週期不正確")
                print("4. 帳戶權限不足")
                return df
                
            # 轉換時間戳為 datetime
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # 設置時間為索引
            df.set_index('time', inplace=True)
            
            print(f"成功獲取 {len(df)} 條數據")
            return df
            
        except Exception as e:
            raise ValueError(f"獲取歷史數據時發生錯誤: {str(e)}")

# 使用範例
if __name__ == "__main__":
    try:
        with MT5Manager() as mt5_manager:
            if mt5_manager.is_connected:
                print("成功連接到 MT5")
                
                # 獲取 EURUSD 的 1 小時歷史數據
                symbol = "EURUSD"
                timeframe = mt5.TIMEFRAME_H1
                start_date = datetime.now() - timedelta(days=7)  # 過去 7 天的數據
                
                # 打印可用的交易品種
                print("\n可用的交易品種:")
                symbols = mt5.symbols_get()
                for s in symbols[:5]:  # 只顯示前 5 個
                    print(f"- {s.name}")
                if len(symbols) > 5:
                    print(f"... 共 {len(symbols)} 個交易品種")
                
                df = mt5_manager.get_historical_data(symbol, timeframe, start_date)
                print(f"\n{symbol} 歷史數據:")
                print(df.head())
                
    except Exception as e:
        print(f"錯誤: {str(e)}")
