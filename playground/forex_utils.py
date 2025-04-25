import os
import pandas as pd
import numpy as np

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
    
    def feature_scaling(self, df):      
        # 定義價格欄位
        price_cols = ['open', 'high', 'low', 'close'] 
        
        # 對每個價格欄位進行 min-max 標準化
        for col in price_cols:
            col_max = df[col].max()
            col_min = df[col].min()
            
            # 如果最大值與最小值不同，則進行 min-max 標準化
            if col_max != col_min:
                df[f"scaled_{col}"] = np.round((df[col] - col_min) / (col_max - col_min), 6)
            else:
                # 如果最大值與最小值相同，則設定為 0（避免除以 0）
                df[f"scaled_{col}"] = 0  

        # 計算價格變動百分比：(收盤價 - 開盤價) / 開盤價 * 100
        df["price_change_percent"] = np.round((df.close - df.open) / df.open, 6) * 100

        # 處理缺失值（可以選擇填補而非刪除，視情況而定）
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)

        # 輸出資料處理後的形狀
        print(f"feature_scaling    : {df.shape}")

        # 返回處理過的資料
        return df
    

    def create_features(self, df):
        """
        將處理過的數據轉換為機器學習模型可用的特徵和標籤格式。
        
        參數:
            df (pandas.DataFrame): 包含縮放後特徵的數據框
            
        返回:
            tuple: (特徵和標籤的數據框, 特徵數量)
        """
        # 找出所有縮放後的特徵列
        feature_columns = [col for col in df.columns if col.startswith('scaled_')]
        
        # 檢查是否有特徵列
        if not feature_columns:
            print("警告：沒有找到縮放後的特徵列")
            return pd.DataFrame(), 0
        
        # 創建特徵和標籤的數據框
        ml_data = pd.DataFrame()
        
        # 將特徵列轉換為列表格式
        ml_data["features"] = df[feature_columns].values.tolist()
        
        # 使用 price_change_percent 作為標籤
        ml_data["target"] = df["price_change_percent"]
        
        # 計算特徵數量
        feature_count = len(feature_columns)
        
        # 輸出數據形狀和特徵數量
        print(f"Features & Lables  : {ml_data.shape}      Number of Features:  {feature_count}")       
        
        return ml_data, feature_count

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


