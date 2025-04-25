import os
import pandas as pd

class FeatureEngineering:
    def __init__(self) -> None:
        pass

    def create_indicators(self, df):
        df["price_change"] = df.close - df.open
    
        print(f"Feature Engineering: {df.shape}")
            
        return df

class DataPreprocessing:
    def __init__(self) -> None:
        pass

    def load_csv(self, file_path):
        """
        如果檔案存在則載入 CSV 檔案，否則回傳 None。
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


