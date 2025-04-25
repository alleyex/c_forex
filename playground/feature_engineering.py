import os
import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Optional, Union
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FeatureEngineering:
    """
    用於外匯數據特徵工程的類。
    
    該類提供了多種技術指標的計算方法，以及數據預處理和特徵工程的功能。
    主要用於準備機器學習模型的輸入數據。
    """
    
    def __init__(self, config: Optional[Dict] = None) -> None:
        """
        初始化 FeatureEngineering 類。
        
        Args:
            config: 配置字典，包含各種參數設置
        """
        # 默認配置
        self.config = {
            'window_size': 8,
            'price_cols': ['open', 'high', 'low', 'close', 'wma_5', 'wma_10', 'upper_band', 'lower_band'],
            'volume_cols': ['tick_volume', 'atr_14'],
            'percent_cols': ['rsi_7', 'k_14', 'd_3', 'bias_5'],
            'macd_cols': ['macd_line_12', 'macd_signal_12', 'macd_histogram_12'],
            'macd_params': {'short_window': 12, 'long_window': 26, 'signal_window': 9},
            'rsi_window': 7,
            'kd_period': 14,
            'bias_window': 5,
            'bollinger_params': {'window': 20, 'num_std': 2},
            'atr_window': 14
        }
        
        # 更新配置
        if config:
            self.config.update(config)
            
        logger.info("FeatureEngineering 初始化完成")

    def prepare_data_pipeline(self, df: pd.DataFrame, window_size: Optional[int] = None) -> Tuple[np.ndarray, int]:
        """
        準備數據管道，用於預測。
        
        Args:
            df: 輸入的 DataFrame
            window_size: 窗口大小，如果為 None 則使用配置中的值
            
        Returns:
            Tuple[np.ndarray, int]: 處理後的數據和特徵數量
        """
        if window_size is None:
            window_size = self.config['window_size']
            
        logger.info(f"開始數據管道處理，窗口大小: {window_size}")
        
        df = self.create_indicators(df)
        df = self.feature_scaling(df)
         
        df, feature_size = self.create_features(df)
        df = self.windowed(df, window_size)
        df.drop(columns=["y"], inplace=True)

        reshaped_df = self.process_data(df, window_size, feature_size)

        logger.info(f"數據管道處理完成，輸出形狀: {reshaped_df.shape}")
        return reshaped_df, feature_size
    
    def prepare_data_pipeline_for_training(self, df: pd.DataFrame, window_size: Optional[int] = None) -> Tuple[np.ndarray, int]:
        """
        準備數據管道，用於訓練。
        
        Args:
            df: 輸入的 DataFrame
            window_size: 窗口大小，如果為 None 則使用配置中的值
            
        Returns:
            Tuple[np.ndarray, int]: 處理後的數據和特徵數量
        """
        if window_size is None:
            window_size = self.config['window_size']
            
        logger.info(f"開始訓練數據管道處理，窗口大小: {window_size}")
        
        df = self.create_indicators(df)
        df = self.feature_scaling(df)
         
        df, feature_size = self.create_features(df)
        df = self.windowed(df, window_size)

        reshaped_df = self.process_data(df, window_size, feature_size)

        logger.info(f"訓練數據管道處理完成，輸出形狀: {reshaped_df.shape}")
        return reshaped_df, feature_size
        
    def create_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        創建技術指標。
        
        Args:
            df: 輸入的 DataFrame
            
        Returns:
            pd.DataFrame: 添加了技術指標的 DataFrame
        """
        logger.info("開始創建技術指標")
        
        # 確保輸入 DataFrame 包含必要的列
        required_columns = ['open', 'high', 'low', 'close']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"輸入 DataFrame 缺少必要的列: {col}")
        
        # 計算價格變動
        df["balance"] = df.close - df.open
        
        # 計算移動平均線
        df["wma_5"] = self.wma(df.close, 5)
        df["wma_10"] = self.wma(df.close, 10)
        
        # 計算 MACD
        macd_params = self.config['macd_params']
        df["macd_line_12"], df["macd_signal_12"], df["macd_histogram_12"] = self.macd(
            df.close, 
            macd_params['short_window'], 
            macd_params['long_window'], 
            macd_params['signal_window']
        )
        
        # 計算 RSI
        df["rsi_7"] = self.rsi(df.close, self.config['rsi_window'])
        
        # 計算 KD
        df["k_14"], df["d_3"] = self.kd(df, self.config['kd_period'])
        
        # 計算乖離率
        df["bias_5"] = self.bias(df.close, self.config['bias_window'])
        
        # 計算布林通道
        bollinger_params = self.config['bollinger_params']
        df["upper_band"], df["lower_band"] = self.bollinger_bands(
            df.close, 
            bollinger_params['window'], 
            bollinger_params['num_std']
        )
        
        # 計算 ATR
        df["atr_14"] = self.atr(df, self.config['atr_window'])
    
        logger.info(f"技術指標創建完成，DataFrame 形狀: {df.shape}")
        return df

    def sma(self, data: pd.Series, window: int) -> pd.Series:
        """
        計算簡單移動平均線 (Simple Moving Average)。
        
        Args:
            data: 輸入數據
            window: 窗口大小
            
        Returns:
            pd.Series: 計算結果
        """
        return data.rolling(window).mean()
  
    def ema(self, data: pd.Series, period: int) -> pd.Series:
        """
        計算指數移動平均線 (Exponential Moving Average)。
        
        Args:
            data: 輸入數據
            period: 週期
            
        Returns:
            pd.Series: 計算結果
        """
        return data.ewm(span=period, adjust=False).mean()  

    def wma(self, data: pd.Series, window: int) -> pd.Series:
        """
        計算加權移動平均線 (Weighted Moving Average)。
        
        Args:
            data: 輸入數據
            window: 窗口大小
            
        Returns:
            pd.Series: 計算結果
        """
        weights = np.arange(1, window + 1)
        wma = data.rolling(window).apply(lambda prices: np.dot(prices, weights) / weights.sum(), raw=True)
        return wma
    
    def macd(self, data: pd.Series, short_window: int = 12, long_window: int = 26, signal_window: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        計算 MACD 指標 (Moving Average Convergence Divergence)。
        
        Args:
            data: 輸入數據
            short_window: 短期窗口
            long_window: 長期窗口
            signal_window: 信號窗口
            
        Returns:
            Tuple[pd.Series, pd.Series, pd.Series]: MACD 線、信號線和柱狀圖
        """
        short_ema = self.ema(data, short_window)
        long_ema = self.ema(data, long_window)
        macd_line = short_ema - long_ema
        signal_line = self.ema(macd_line, signal_window)
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    def rsi(self, data: pd.Series, window: int = 14) -> pd.Series:
        """
        計算相對強弱指標 (Relative Strength Index)。
        
        Args:
            data: 輸入數據
            window: 窗口大小
            
        Returns:
            pd.Series: RSI 值
        """
        delta = data.diff()  # 計算每個週期的變動量
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()  # 計算平均增益
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()  # 計算平均損失
        
        # 處理除零錯誤
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)  # 填充 NaN 值為中性值 50

    def kd(self, df: pd.DataFrame, period: int = 14) -> Tuple[pd.Series, pd.Series]:
        """
        計算 KD 指標 (Stochastic Oscillator)。
        
        Args:
            df: 輸入 DataFrame
            period: 週期
            
        Returns:
            Tuple[pd.Series, pd.Series]: K 值和 D 值
        """
        low = df.low.rolling(window=period).min()  # 取週期內最低價
        high = df.high.rolling(window=period).max()  # 取週期內最高價
        
        # 處理除零錯誤
        denominator = (high - low).replace(0, np.nan)
        k = 100 * ((df.close - low) / denominator)  # 計算 K 值
        k = k.fillna(50)  # 填充 NaN 值為中性值 50
        
        d = k.rolling(window=3).mean()  # 計算 D 值，為 K 值的3週期移動平均
        return k, d
        
    def bias(self, data: pd.Series, window: int) -> pd.Series:
        """
        計算乖離率 (Bias)。
        
        Args:
            data: 輸入數據
            window: 窗口大小
            
        Returns:
            pd.Series: 乖離率值
        """
        ma = self.sma(data, window)
        # 處理除零錯誤
        return ((data - ma) / ma.replace(0, np.nan)) * 100
    
    def bollinger_bands(self, data: pd.Series, window: int = 20, num_std: int = 2) -> Tuple[pd.Series, pd.Series]:
        """
        計算布林通道 (Bollinger Bands)。
        
        Args:
            data: 輸入數據
            window: 窗口大小
            num_std: 標準差倍數
            
        Returns:
            Tuple[pd.Series, pd.Series]: 上軌和下軌
        """
        mean = data.rolling(window=window).mean()
        std = data.rolling(window=window).std()
        upper_band = mean + (std * num_std)
        lower_band = mean - (std * num_std)
        return upper_band, lower_band
    
    def atr(self, df: pd.DataFrame, window: int = 14) -> pd.Series:
        """
        計算平均真實範圍 (Average True Range)。
        
        Args:
            df: 輸入 DataFrame
            window: 窗口大小
            
        Returns:
            pd.Series: ATR 值
        """
        # 計算真實範圍 (True Range, TR)
        tr = np.maximum(
            df.high - df.low, 
            np.maximum(
                abs(df.high - df.close.shift(1)), 
                abs(df.low - df.close.shift(1))
            )
        )
        atr = tr.rolling(window=window, min_periods=1).mean()
        return atr
    
    def feature_scaling(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        特徵縮放。
        
        Args:
            df: 輸入 DataFrame
            
        Returns:
            pd.DataFrame: 縮放後的 DataFrame
        """
        logger.info("開始特徵縮放")
        
        # 價格縮放
        max_val = df[['open', 'high', 'low', 'close']].max().max()
        min_val = df[['open', 'high', 'low', 'close']].min().min()
        
        price_cols = self.config['price_cols']
        for col in price_cols:
            if col in df.columns:
                if max_val != min_val:
                    df[f"scaled_{col}"] = np.round((df[col] - min_val) / (max_val - min_val), 6)
                else:
                    df[f"scaled_{col}"] = 0
            else:
                logger.warning(f"列 {col} 不存在於 DataFrame 中")

        # 交易量縮放
        volume_cols = self.config['volume_cols']
        for col in volume_cols:
            if col in df.columns:
                col_max = df[col].max()
                col_min = df[col].min()
                if col_max != col_min:
                    df[f"scaled_{col}"] = np.round((df[col] - col_min) / (col_max - col_min), 6)
                else:
                    df[f"scaled_{col}"] = 0
            else:
                logger.warning(f"列 {col} 不存在於 DataFrame 中")

        # 百分比縮放
        percent_cols = self.config['percent_cols']
        for col in percent_cols:
            if col in df.columns:
                df[f"scaled_{col}"] = np.round(df[col] / 100, 6)
            else:
                logger.warning(f"列 {col} 不存在於 DataFrame 中")

        # MACD 縮放
        macd_cols = self.config['macd_cols']
        for col in macd_cols:
            if col in df.columns:
                df[f"scaled_{col}"] = np.round(df[col], 6)
            else:
                logger.warning(f"列 {col} 不存在於 DataFrame 中")

        # 計算價格變動百分比
        df["range"] = np.round((df.close - df.open) / df.open.replace(0, np.nan), 6) * 100
        df["range"] = df["range"].fillna(0)

        # 清理 NaN 值
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)

        logger.info(f"特徵縮放完成，DataFrame 形狀: {df.shape}")
        return df
        
    def create_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
        """
        創建特徵和標籤。
        
        Args:
            df: 輸入 DataFrame
            
        Returns:
            Tuple[pd.DataFrame, int]: 特徵和標籤的 DataFrame 以及特徵數量
        """
        logger.info("開始創建特徵和標籤")
        
        scaled_columns = [col for col in df.columns if col.startswith('scaled_')]
        if not scaled_columns:
            raise ValueError("沒有找到縮放後的特徵列")
            
        xy_df = pd.DataFrame()
        xy_df["X"] = df[scaled_columns].values.tolist()
        xy_df["y"] = df.apply(lambda row: row.range, axis=1)
        
        if not xy_df.empty:
            features = len(xy_df.X.values[0])
        else:
            logger.error("DataFrame 為空")
            raise ValueError("DataFrame 為空")

        logger.info(f"特徵和標籤創建完成，DataFrame 形狀: {xy_df.shape}，特徵數量: {features}")
        return xy_df, features
    
    def windowed(self, df: pd.DataFrame, window_size: int) -> pd.DataFrame:
        """
        創建窗口化的數據。
        
        Args:
            df: 輸入 DataFrame
            window_size: 窗口大小
            
        Returns:
            pd.DataFrame: 窗口化後的 DataFrame
        """
        logger.info(f"開始創建窗口化數據，窗口大小: {window_size}")
        
        win_df = pd.DataFrame()

        for i in reversed(range(window_size)):
            win_df[f"x_{i}"] = df.X.shift(i)   

        win_df["y"] = df["y"][-win_df.shape[0]:].shift(-1) 
        if pd.isna(win_df.loc[win_df.index[-1], 'y']):
            win_df.loc[win_df.index[-1], 'y'] = 0 
             
        win_df.dropna(inplace=True)
        win_df.reset_index(drop=True, inplace=True)
            
        logger.info(f"窗口化數據創建完成，DataFrame 形狀: {win_df.shape}")
        return win_df
    
    def process_data(self, data: pd.DataFrame, window_size: int, features: int) -> np.ndarray:
        """
        處理數據，將其重塑為適合深度學習的形狀。
        
        Args:
            data: 輸入 DataFrame
            window_size: 窗口大小
            features: 特徵數量
            
        Returns:
            np.ndarray: 重塑後的數據
        """
        logger.info("開始處理數據")
        
        stacked_data = np.concatenate([np.stack(data[col].values) for col in data.columns], axis=1)
        reshaped_data = stacked_data.reshape(stacked_data.shape[0], window_size, features)
        
        logger.info(f"數據處理完成，輸出形狀: {reshaped_data.shape}")
        return reshaped_data


if __name__ == "__main__":
    # 示例用法
    from DataCollection import DataCollection
    
    # 初始化
    server = DataCollection()
    feature_engineering = FeatureEngineering()
    
    # 獲取數據
    raw_data = server.get_market_data()
    
    # 處理數據
    df, feature_size = feature_engineering.prepare_data_pipeline(raw_data)
    
    print(f"處理後的數據形狀: {df.shape}")
    print(f"特徵數量: {feature_size}") 