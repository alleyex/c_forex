import os
import pandas as pd

class FeatureEngineering:
    """
    特徵工程類別，用於處理和轉換金融數據，創建技術分析指標。
    這個類別提供各種方法來計算常用的技術指標，如移動平均線、RSI、MACD等。
    """
    def __init__(self) -> None:
        """
        初始化特徵工程類別。
        目前沒有需要初始化的參數。
        """
        pass

    def create_indicators(self, df):
        """
        為輸入的數據框創建技術分析指標。
        
        參數:
            df (pandas.DataFrame): 包含金融數據的數據框，必須包含 'close' 和 'open' 列
            
        返回:
            pandas.DataFrame: 添加了技術指標的數據框
        """
        # 計算收盤價與開盤價的差值，表示價格變動
        df["price_change"] = df.close - df.open
    
        print(f"Feature Engineering: {df.shape}")
            
        return df

class DataPreprocessing:
    """
    數據預處理類別，用於處理原始金融數據。
    提供數據載入、清洗和轉換等功能。
    """
    def __init__(self) -> None:
        """
        初始化數據預處理類別。
        目前沒有需要初始化的參數。
        """
        pass

    def load_csv(self, file_path):
        """
        如果檔案存在則載入 CSV 檔案，否則回傳 None。
        
        參數:
            file_path (str): CSV 檔案的路徑
            
        返回:
            pandas.DataFrame 或 None: 成功載入則返回數據框，失敗則返回 None
        """
        # 檢查檔案是否存在
        if os.path.isfile(file_path):
            # 使用 pandas 載入 CSV 檔案
            df = pd.read_csv(file_path)
            print(f"{file_path} 載入成功。")
            return df
        else:
            # 檔案不存在時印出提示訊息並回傳 None
            print(f"{file_path} 找不到檔案。")
            return None


