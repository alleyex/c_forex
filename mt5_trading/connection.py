"""
MT5 交易平台的連接管理
此模組負責處理與 MetaTrader 5 交易平台的連接、認證和斷開連接等操作。
"""

import MetaTrader5 as mt5
import json
import os
from typing import Optional
from mt5_trading.utils import setup_logger

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
            credentials_file (str): 憑證檔案的路徑，預設為 "credential.json"
        """
        self._is_connected = False  # 連接狀態標記
        self.logger = setup_logger('MT5Connection')
        self.logger.info("初始化 MT5Connection")
        
        # 取得當前目錄的路徑，用於定位憑證檔案
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.credentials_path = os.path.join(current_dir, credentials_file)
        self._load_credentials(self.credentials_path)
        
    def _load_credentials(self, file: str) -> None:
        """
        從 JSON 檔案載入 MT5 登入憑證
        
        Args:
            file (str): 憑證檔案的路徑
            
        Raises:
            FileNotFoundError: 當找不到憑證檔案時
            ValueError: 當憑證檔案格式錯誤或缺少必要欄位時
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
        
        Raises:
            ConnectionError: 當連接失敗時
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
        此方法會確保所有資源都被正確釋放
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
        
        Returns:
            bool: 如果連接正常則返回 True，否則返回 False
        """
        return self._is_connected and mt5.terminal_info() is not None
            
    def __enter__(self):
        """
        支援 with 語句的上下文管理器入口
        自動建立連接
        
        Returns:
            MT5Connection: 當前實例
        """
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        支援 with 語句的上下文管理器出口
        自動斷開連接
        
        Args:
            exc_type: 異常類型
            exc_val: 異常值
            exc_tb: 異常追蹤
        """
        self.disconnect() 

if __name__ == "__main__":
    """
    測試程式碼
    用於測試 MT5Connection 類別的基本功能
    """
    try:
        # 使用 with 語句自動管理連接
        with MT5Connection() as mt5_conn:
            print("MT5 連接狀態:", mt5_conn.is_connected)
            
            # 測試斷開連接
            mt5_conn.disconnect()
            print("斷開連接後狀態:", mt5_conn.is_connected)
            
            # 測試重新連接
            mt5_conn.connect()
            print("重新連接後狀態:", mt5_conn.is_connected)
            
    except Exception as e:
        print(f"測試過程中發生錯誤: {str(e)}") 