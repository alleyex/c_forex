import os
import pandas as pd
import numpy as np
from .feature_engineering import FeatureEngineering

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

    def prepare_sequence_data(self, data: pd.DataFrame, window_size: int, features: int) -> np.ndarray:
        """
        將原始資料轉換成 (樣本數, window_size, features) 的格式，用於序列模型（例如 LSTM）。

        Args:
            data (pd.DataFrame): 輸入的資料，每個欄位包含序列型態的 list。
            window_size (int): 每個樣本的時間步長。
            features (int): 每個時間步的特徵數。

        Returns:
            np.ndarray: 轉換後的資料，形狀為 (樣本數, window_size, features)。
        """

        # 將所有欄位（每列是 list）先各自堆疊成 numpy array
        stacked_data = np.concatenate([np.stack(data[col].values) for col in data.columns], axis=1)

        # 將堆疊後的資料 reshape 成 (樣本數, window_size, features)
        reshaped_data = stacked_data.reshape(stacked_data.shape[0], window_size, features)

        # 顯示 reshape 後的資料形狀（方便 debug）
        print(f"Reshaped Data: {reshaped_data.shape}")

        return reshaped_data.astype('float32')