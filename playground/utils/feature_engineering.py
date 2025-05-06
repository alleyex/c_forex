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
        """
        return data.rolling(window).mean()
    
    def ema(self, data, window):
        """
        計算指數移動平均線（Exponential Moving Average, EMA）
        """
        return data.ewm(span=window, adjust=False).mean()
    
    def rsi(self, data, window):
        """
        計算相對強弱指標（Relative Strength Index, RSI）
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window).mean()   
        loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
        rs = gain / loss
        return 100 - 100 / (1 + rs)
    
    def macd(self, data, short_window=12, long_window=26, signal_window=9):
        """
        計算移動平均收斂發散指標（Moving Average Convergence Divergence, MACD）
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
        對價格欄位進行 Min-Max 標準化，並計算價格變動百分比。
        """
        # 定義價格欄位
        price_cols = ['open', 'high', 'low', 'close']

        # 對每個價格欄位進行 min-max 標準化
        for col in price_cols:
            col_max = df[col].max()
            col_min = df[col].min()

            if col_max != col_min:
                df[f"scaled_{col}"] = np.round((df[col] - col_min) / (col_max - col_min), 6)
            else:
                df[f"scaled_{col}"] = 0

        # 計算價格變動百分比
        df["scaled_price_change_percent"] = np.round((df.close - df.open) / df.open, 6) * 100
  
        # 對 RSI 指標進行標準化處理
        for col in ["rsi_14"]:
            df[f"scaled_{col}"] = np.round((df[col] / 100), 6)

        # 對 MACD 指標進行標準化處理
        for col in ["macd_diff", "macd_signal", "macd_hist"]:
            df[f"scaled_{col}"] = np.round(df[[col]], 6)

        # 處理缺失值
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)

        print(f"feature_scaling    : {df.shape}")

        return df

    def windowed(self, df: pd.DataFrame, window_size: int) -> pd.DataFrame:
        """
        將時間序列資料轉換為以窗口大小為基準的資料。
        """
        win_df = pd.DataFrame()

        for i in reversed(range(window_size)):
            win_df[f"x_{i}"] = df.X.shift(i)

        win_df["y"] = df["y"][-win_df.shape[0]:].shift(-1)

        if pd.isna(win_df.loc[win_df.index[-1], 'y']):
            win_df.loc[win_df.index[-1], 'y'] = 0

        win_df.dropna(inplace=True)
        win_df.reset_index(drop=True, inplace=True)

        print(f"windowed Size = {window_size}  : {win_df.shape}")

        return win_df

    def create_features(self, df):
        """
        將處理過的數據轉換為機器學習模型可用的特徵和標籤格式。
        """
        feature_columns = [col for col in df.columns if col.startswith('scaled_')]
        
        if not feature_columns:
            print("警告：沒有找到縮放後的特徵列")
            return pd.DataFrame(), 0
        
        ml_data = pd.DataFrame()
        ml_data["X"] = df[feature_columns].values.tolist()
        ml_data["y"] = df["scaled_close"].shift(-1)
        
        feature_count = len(feature_columns)
        
        print(f"Features & Lables  : {ml_data.shape}      Number of Features:  {feature_count}")       
        
        return ml_data, feature_count 