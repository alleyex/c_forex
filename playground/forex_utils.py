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
        
    def feature_scaling(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        這個函數對價格欄位進行 Min-Max 標準化，並計算價格變動百分比。
        處理完後會返回一個經過標準化的資料集，並刪除缺失值。

        參數:
        - df: 包含價格資訊（如 'open', 'high', 'low', 'close'）的 DataFrame。

        回傳:
        - 返回一個新的 DataFrame，其中包括標準化後的價格欄位和價格變動百分比欄位。
        """
        
        # 定義價格欄位
        price_cols = ['open', 'high', 'low', 'close']

        # 對每個價格欄位進行 min-max 標準化
        for col in price_cols:
            col_max = df[col].max()  # 計算最大值
            col_min = df[col].min()  # 計算最小值

            # 如果最大值與最小值不同，則進行 min-max 標準化
            if col_max != col_min:
                df[f"scaled_{col}"] = np.round((df[col] - col_min) / (col_max - col_min), 6)
            else:
                # 如果最大值與最小值相同，則設定為 0（避免除以 0）
                df[f"scaled_{col}"] = 0

        # 計算價格變動百分比：(收盤價 - 開盤價) / 開盤價 * 100
        df["scaled_price_change_percent"] = np.round((df.close - df.open) / df.open, 6) * 100

        # 處理缺失值（可以選擇填補而非刪除，視情況而定）
        df.dropna(inplace=True)  # 移除含有 NaN 的行
        df.reset_index(drop=True, inplace=True)  # 重設索引

        # 輸出資料處理後的形狀以供檢查
        print(f"feature_scaling    : {df.shape}")

        # 返回處理過的資料
        return df


    def windowed(self, df: pd.DataFrame, window_size: int) -> pd.DataFrame:
        """
        這個函數將時間序列資料轉換為以窗口大小為基準的資料，並為每個窗口創建對應的特徵和標籤。

        參數:
        - df: 包含特徵（X）和目標值（y）的 DataFrame。
        - window_size: 整數，指定每個視窗的大小，即多少個時間步。

        回傳:
        - 返回一個新的 DataFrame，包含所有窗口的特徵和標籤。
        """
        
        # 創建一個空的 DataFrame 來存儲窗口資料
        win_df = pd.DataFrame()

        # 將每個時間步的資料依據窗口大小進行移動
        for i in reversed(range(window_size)):
            # 每個時間步作為一個特徵，名稱為 x_0, x_1, ..., x_(window_size-1)
            win_df[f"x_{i}"] = df.X.shift(i)

        # 計算目標值 'y'，這是資料集中的 'y' 向前移動一個時間步
        win_df["y"] = df["y"][-win_df.shape[0]:].shift(-1)

        # 處理最後一筆資料的 'y' 為 NaN 的情況，若是 NaN，則設置為 0
        if pd.isna(win_df.loc[win_df.index[-1], 'y']):
            win_df.loc[win_df.index[-1], 'y'] = 0

        # 刪除所有包含 NaN 的行
        win_df.dropna(inplace=True)

        # 重設索引
        win_df.reset_index(drop=True, inplace=True)

        # 打印窗口化後的資料形狀以供檢查
        print(f"windowed Size = {window_size}  : {win_df.shape}")

        return win_df

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
        ml_data["X"] = df[feature_columns].values.tolist()
        
        # 使用下一行的 scaled_close 作為標籤
        ml_data["y"] = df["scaled_close"].shift(-1)
        
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

        return reshaped_data