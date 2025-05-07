import pandas as pd
import numpy as np
from typing import Dict, Optional
from .utils import setup_logger, get_project_root

class TechnicalIndicatorCalculator:
    """
    技術指標計算器類別
    
    用於計算各種技術指標，包括：
    - EMA (指數移動平均線)
    - MACD (移動平均收斂發散指標)
    - RSI (相對強弱指標)
    - 布林通道
    - ATR (平均真實範圍)
    """
    
    # 預設配置
    DEFAULT_CONFIG = {
        'ema': {'fast': 12, 'slow': 26},
        'macd': {'signal': 9},
        'rsi': {'period': 14},
        'bollinger': {'period': 20, 'std_dev': 2},
        'atr': {'period': 14}
    }
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化技術指標計算器
        
        Parameters:
        -----------
        config : dict, optional
            配置參數，包含各指標的計算參數
        """
        self.logger = setup_logger('TechnicalIndicatorCalculator')
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config:
            self.config.update(config)
    
    def calculate_ema(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算指數移動平均線"""
        try:
            df['ema_fast'] = df['close'].ewm(span=self.config['ema']['fast'], adjust=False).mean()
            df['ema_slow'] = df['close'].ewm(span=self.config['ema']['slow'], adjust=False).mean()
            return df
        except Exception as e:
            self.logger.error(f"計算 EMA 時發生錯誤: {str(e)}")
            raise
    
    def calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算MACD指標"""
        try:
            df['macd'] = df['ema_fast'] - df['ema_slow']
            df['macd_signal'] = df['macd'].ewm(span=self.config['macd']['signal'], adjust=False).mean()
            return df
        except Exception as e:
            self.logger.error(f"計算 MACD 時發生錯誤: {str(e)}")
            raise
    
    def calculate_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算RSI指標"""
        try:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=self.config['rsi']['period']).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=self.config['rsi']['period']).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            return df
        except Exception as e:
            self.logger.error(f"計算 RSI 時發生錯誤: {str(e)}")
            raise
    
    def calculate_bollinger_bands(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算布林通道"""
        try:
            df['bb_middle'] = df['close'].rolling(window=self.config['bollinger']['period']).mean()
            df['bb_std'] = df['close'].rolling(window=self.config['bollinger']['period']).std()
            df['bb_upper'] = df['bb_middle'] + self.config['bollinger']['std_dev'] * df['bb_std']
            df['bb_lower'] = df['bb_middle'] - self.config['bollinger']['std_dev'] * df['bb_std']
            return df
        except Exception as e:
            self.logger.error(f"計算布林通道時發生錯誤: {str(e)}")
            raise
    
    def calculate_atr(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算ATR指標"""
        try:
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = np.max(ranges, axis=1)
            df['atr'] = true_range.rolling(window=self.config['atr']['period']).mean()
            return df
        except Exception as e:
            self.logger.error(f"計算 ATR 時發生錯誤: {str(e)}")
            raise
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        計算所有技術指標
        
        Parameters:
        -----------
        df : pandas.DataFrame
            包含 OHLCV 數據的 DataFrame
        
        Returns:
        --------
        pandas.DataFrame
            添加了技術指標的 DataFrame
        """
        self.logger.info("開始計算技術指標")
        
        try:
            df = self.calculate_ema(df)
            df = self.calculate_macd(df)
            df = self.calculate_rsi(df)
            df = self.calculate_bollinger_bands(df)
            df = self.calculate_atr(df)
            
            self.logger.info("技術指標計算完成")
            return df
            
        except Exception as e:
            self.logger.error(f"計算技術指標時發生錯誤: {str(e)}")
            raise 