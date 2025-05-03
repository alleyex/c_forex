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
            df (pandas.DataFrame): 包含金融數據的數據框，必須包含以下列：
                - 'close': 收盤價
                - 'open': 開盤價
                - 'high': 最高價
                - 'low': 最低價
                - 'volume': 成交量（可選）
            
        返回:
            pandas.DataFrame: 添加了技術指標的數據框，包含以下新增列：
                - 'price_change': 收盤價與開盤價的差值
                - 'sma_20': 20日簡單移動平均線
                - 'sma_50': 50日簡單移動平均線
                - 'ema_12': 12日指數移動平均線
                - 'ema_26': 26日指數移動平均線
                - 'rsi_14': 14日相對強弱指標
                - 'macd_diff': MACD線
                - 'macd_signal': MACD信號線
                - 'macd_hist': MACD直方圖
            
        說明:
            - 價格變動（price_change）: 反映單根K線的價格變動幅度
            - 移動平均線（SMA/EMA）: 用於判斷趨勢方向和支撐壓力位
            - RSI: 用於判斷超買超賣情況，範圍在0-100之間
            - MACD: 用於判斷趨勢變化和動量強度
        """
        # 計算收盤價與開盤價的差值，表示價格變動
        df["price_change"] = df.close - df.open
        
        # 計算移動平均線
        df["sma_20"] = self.sma(df.close, 20)  # 20日簡單移動平均線
        df["sma_50"] = self.sma(df.close, 50)  # 50日簡單移動平均線
        df["ema_12"] = self.ema(df.close, 12)  # 12日指數移動平均線
        df["ema_26"] = self.ema(df.close, 26)  # 26日指數移動平均線
        
        # 計算RSI指標
        df["rsi_14"] = self.rsi(df.close, 14)  # 14日相對強弱指標
        
        # 計算MACD指標
        macd_diff, macd_signal, macd_hist = self.macd(df.close)  # 使用預設參數
        df["macd_diff"] = macd_diff
        df["macd_signal"] = macd_signal
        df["macd_hist"] = macd_hist
    
        print(f"Feature Engineering: {df.shape}")
            
        return df
    
    def sma(self, data, window):
        """
        計算簡單移動平均線（Simple Moving Average, SMA）
        
        參數:
            data (pandas.Series): 輸入的數據序列，通常是價格數據（如收盤價）
            window (int): 計算 SMA 的窗口大小（時間週期）
            
        返回:
            pandas.Series: 計算出的 SMA 序列
            
        說明:
            - SMA 是最基本的技術分析指標之一
            - 計算方法是取指定窗口大小內所有數據的平均值
            - 常用於判斷趨勢方向、尋找支撐壓力位
            - 與 EMA 相比，SMA 對價格變動的反應較慢，但較為平滑
        """
        return data.rolling(window).mean()
    
    def ema(self, data, window):
        """
        計算指數移動平均線（Exponential Moving Average, EMA）
        
        參數:
            data (pandas.Series): 輸入的數據序列，通常是價格數據（如收盤價）
            window (int): 計算 EMA 的窗口大小（時間週期）
            
        返回:
            pandas.Series: 計算出的 EMA 序列
            
        說明:
            - EMA 是一種技術分析指標，給予較新的數據更高的權重
            - 與簡單移動平均線（SMA）相比，EMA 對價格變動的反應更快
            - 常用於判斷趨勢方向、尋找支撐壓力位，以及產生交易信號
            - adjust=False 表示使用簡單的指數加權計算方式
        """
        return data.ewm(span=window, adjust=False).mean()
    
    def rsi(self, data, window):
        """
        計算相對強弱指標（Relative Strength Index, RSI）
        
        參數:
            data (pandas.Series): 輸入的數據序列，通常是價格數據（如收盤價）
            window (int): 計算 RSI 的窗口大小（時間週期）
            
        返回:
            pandas.Series: 計算出的 RSI 序列，數值範圍在 0-100 之間
            
        說明:
            - RSI 是一種動量指標，用於衡量價格變動的速度和幅度
            - 計算步驟：
                1. 計算價格變動（delta）
                2. 分別計算上漲和下跌的平均值（gain 和 loss）
                3. 計算相對強度（RS = gain / loss）
                4. RSI = 100 - 100 / (1 + RS)
            - 常用於：
                - 判斷超買（RSI > 70）和超賣（RSI < 30）情況
                - 尋找背離信號
                - 確認趨勢強度
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window).mean()   
        loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
        rs = gain / loss
        return 100 - 100 / (1 + rs)
    
    def macd(self, data, short_window=12, long_window=26, signal_window=9):
        """
        計算移動平均收斂發散指標（Moving Average Convergence Divergence, MACD）
        
        參數:
            data (pandas.Series): 輸入的價格數據序列（通常是收盤價）
            short_window (int): 短期 EMA 的週期，預設為 12
            long_window (int): 長期 EMA 的週期，預設為 26
            signal_window (int): 信號線的週期，預設為 9
            
        返回:
            tuple: (MACD 線, 信號線, 直方圖)
                - MACD 線 = 短期 EMA - 長期 EMA
                - 信號線 = MACD 線的 EMA
                - 直方圖 = MACD 線 - 信號線
            
        說明:
            - MACD 是一種趨勢跟蹤的動量指標
            - 計算步驟：
                1. 計算短期和長期的指數移動平均線（EMA）
                2. MACD 線 = 短期 EMA - 長期 EMA
                3. 信號線 = MACD 線的 EMA
                4. 直方圖 = MACD 線 - 信號線
            - 常用於：
                - 判斷趨勢方向（MACD 線在信號線上方為多頭，下方為空頭）
                - 尋找金叉（MACD 線向上穿越信號線）和死叉（MACD 線向下穿越信號線）
                - 判斷背離（價格與 MACD 的背離）
        """
        # 計算短期和長期的指數移動平均線
        short_ema = self.ema(data, short_window)
        long_ema = self.ema(data, long_window)
        
        # 計算 MACD 線（短期 EMA 與長期 EMA 的差值）
        macd_diff = short_ema - long_ema
        
        # 計算信號線（MACD 線的 EMA）
        macd_signal = self.ema(macd_diff, signal_window)
        
        # 計算 MACD 直方圖（MACD 線與信號線的差值）
        macd_hist = macd_diff - macd_signal
        
        return macd_diff, macd_signal, macd_hist
    
 
        

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
  
        # 對 RSI 指標進行標準化處理
        # RSI 原始值範圍在 0-100 之間，除以 100 將其轉換為 0-1 範圍
        # 這樣可以與其他標準化後的指標保持一致的數值範圍
        for col in ["rsi_14"]:
            df[f"scaled_{col}"] = np.round((df[col] / 100), 6)

        # 對 MACD 指標進行標準化處理
        # MACD 指標包含三個主要部分：
        # 1. MACD 線：快速 EMA 與慢速 EMA 的差值
        # 2. 信號線：MACD 線的 EMA
        # 3. MACD 直方圖：MACD 線與信號線的差值
        # 這些指標的原始值範圍可能差異很大，因此需要分別進行標準化
        # 使用 np.round 將數值四捨五入到小數點後 6 位，以保持數據精度
        for col in ["macd_diff", "macd_signal", "macd_hist"]:
            df[f"scaled_{col}"] = np.round(df[[col]], 6)

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

        return reshaped_data.astype('float32')