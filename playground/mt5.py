"""
MetaTrader 5 (MT5) 交易平台連接模組

使用範例：
    with MT5Manager() as mt5:
        if mt5.is_connected:
            # 進行 MT5 操作
            pass
"""

import MetaTrader5 as mt5
import json

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

# 使用範例
if __name__ == "__main__":
    try:
        with MT5Manager() as mt5_manager:
            if mt5_manager.is_connected:
                print("成功連接到 MT5")
                # 在這裡可以進行其他 MT5 操作
    except Exception as e:
        print(f"錯誤: {str(e)}")
