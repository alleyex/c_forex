import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from typing import Optional, Tuple, Dict
from utils.utils import setup_logger, get_project_root
import logging


class DataQualityChecker:
    """數據質量檢查器類別"""
    
    def __init__(self):
        self.logger = setup_logger('DataQualityChecker')

    def check_missing_values(self, df: pd.DataFrame) -> pd.Series:
        """檢查數據框中的缺漏值"""
        missing_values = df.isnull().sum()
        self.logger.info("缺漏值統計:\n%s", missing_values)
        return missing_values

    def check_outliers(self, df: pd.DataFrame) -> Dict[str, Tuple[int, float, float]]:
        """使用 IQR 方法檢查數值型欄位的異常值"""
        outlier_stats = {}
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]
            
            outlier_stats[col] = (len(outliers), outliers.min() if len(outliers) > 0 else None, 
                                outliers.max() if len(outliers) > 0 else None)
            
            self.logger.info("%s 的異常值數量: %d", col, len(outliers))
            if len(outliers) > 0:
                self.logger.info("異常值範圍: %f 到 %f", outliers.min(), outliers.max())
        
        return outlier_stats

    def check_time_series_continuity(self, df: pd.DataFrame) -> Optional[pd.Series]:
        """檢查時間序列的連續性"""
        if not isinstance(df.index, pd.DatetimeIndex):
            self.logger.warning("警告：數據框的索引不是日期時間類型")
            return None
            
        time_diff = df.index.to_series().diff()
        gaps = time_diff[time_diff > pd.Timedelta(minutes=1)]
        
        if len(gaps) > 0:
            self.logger.info("發現 %d 個時間間隔", len(gaps))
            self.logger.info("最大的時間間隔: %s", gaps.max())
        else:
            self.logger.info("時間序列是連續的")
            
        return gaps


class SpreadProcessor:
    """Spread 數據處理器類別"""
    
    def __init__(self, plots_dir: str):
        self.logger = setup_logger('SpreadProcessor')
        self.plots_dir = plots_dir

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """處理 spread 數據"""
        self.logger.info("開始處理 spread 數據")
        
        try:
            df_processed = df.copy()
            original_stats = df['spread'].describe()
            self.logger.info("原始 spread 統計量:\n%s", original_stats)
            
            # 使用 IQR 方法標記異常值
            df_processed['is_spread_outlier_iqr'] = self._mark_iqr_outliers(df['spread'])
            
            # 使用固定閾值標記異常值
            df_processed['is_spread_outlier_threshold'] = (df['spread'] > 10).astype(int)
            
            # 計算異常值比例
            self._log_outlier_ratios(df_processed)
            
            # 繪製分布圖
            self._plot_distribution(df, df_processed)
            
            return df_processed
            
        except Exception as e:
            self.logger.error("處理 spread 數據時發生錯誤: %s", str(e))
            raise

    def _mark_iqr_outliers(self, series: pd.Series) -> pd.Series:
        """使用 IQR 方法標記異常值"""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return ((series < lower_bound) | (series > upper_bound)).astype(int)

    def _log_outlier_ratios(self, df: pd.DataFrame) -> None:
        """記錄異常值比例"""
        iqr_outlier_ratio = df['is_spread_outlier_iqr'].mean() * 100
        threshold_outlier_ratio = df['is_spread_outlier_threshold'].mean() * 100
        
        self.logger.info("IQR method outlier ratio: %.2f%%", iqr_outlier_ratio)
        self.logger.info("Fixed threshold method outlier ratio: %.2f%%", threshold_outlier_ratio)

    def _plot_distribution(self, df: pd.DataFrame, df_processed: pd.DataFrame) -> None:
        """繪製 spread 分布圖"""
        plt.figure(figsize=(15, 5))
        
        plt.subplot(1, 3, 1)
        plt.hist(df['spread'], bins=50, alpha=0.7)
        plt.title('Original Spread Distribution')
        plt.xlabel('Spread')
        plt.ylabel('Frequency')
        
        plt.subplot(1, 3, 2)
        plt.hist(df['spread'][df_processed['is_spread_outlier_iqr'] == 0], bins=50, alpha=0.7, color='green')
        plt.hist(df['spread'][df_processed['is_spread_outlier_iqr'] == 1], bins=50, alpha=0.7, color='red')
        plt.title('IQR Method Outlier Detection')
        plt.xlabel('Spread')
        plt.ylabel('Frequency')
        
        plt.subplot(1, 3, 3)
        plt.hist(df['spread'][df_processed['is_spread_outlier_threshold'] == 0], bins=50, alpha=0.7, color='green')
        plt.hist(df['spread'][df_processed['is_spread_outlier_threshold'] == 1], bins=50, alpha=0.7, color='red')
        plt.title('Threshold Method Outlier Detection')
        plt.xlabel('Spread')
        plt.ylabel('Frequency')
        
        plt.tight_layout()
        output_file = os.path.join(self.plots_dir, 'spread_distribution.png')
        plt.savefig(output_file)
        self.logger.info("已生成分布圖: %s", output_file)
        plt.close()


class TickVolumeProcessor:
    """Tick Volume 數據處理器類別"""
    
    def __init__(self, plots_dir: str):
        self.logger = setup_logger('TickVolumeProcessor')
        self.plots_dir = plots_dir

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """處理 tick_volume 數據"""
        self.logger.info("開始處理 tick_volume 數據")
        
        try:
            df_processed = df.copy()
            original_stats = df['tick_volume'].describe()
            self.logger.info("原始 tick_volume 統計量:\n%s", original_stats)
            
            # 進行對數轉換
            df_processed['tick_volume_log'] = np.log1p(df['tick_volume'])
            
            # 標記異常值
            df_processed['is_tick_volume_outlier'] = self._mark_outliers(df_processed['tick_volume_log'])
            
            # 計算異常值比例
            outlier_ratio = df_processed['is_tick_volume_outlier'].mean() * 100
            self.logger.info("異常值比例: %.2f%%", outlier_ratio)
            
            # 繪製分布圖
            self._plot_distribution(df, df_processed)
            
            return df_processed
            
        except Exception as e:
            self.logger.error("處理 tick_volume 數據時發生錯誤: %s", str(e))
            raise

    def _mark_outliers(self, series: pd.Series) -> pd.Series:
        """使用 IQR 方法標記異常值"""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return ((series < lower_bound) | (series > upper_bound)).astype(int)

    def _plot_distribution(self, df: pd.DataFrame, df_processed: pd.DataFrame) -> None:
        """繪製 tick_volume 分布圖"""
        plt.figure(figsize=(12, 6))
        
        plt.subplot(1, 2, 1)
        plt.hist(df['tick_volume'], bins=50, alpha=0.7)
        plt.title('Original Tick Volume Distribution')
        plt.xlabel('Tick Volume')
        plt.ylabel('Frequency')
        
        plt.subplot(1, 2, 2)
        plt.hist(df_processed['tick_volume_log'], bins=50, alpha=0.7)
        plt.title('Log-Transformed Tick Volume Distribution')
        plt.xlabel('log(Tick Volume + 1)')
        plt.ylabel('Frequency')
        
        plt.tight_layout()
        output_file = os.path.join(self.plots_dir, 'tick_volume_distribution.png')
        plt.savefig(output_file)
        self.logger.info("已生成分布圖: %s", output_file)
        plt.close()


class DataProcessor:
    """數據處理主類別"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.logger = setup_logger('DataProcessor')
        self.quality_checker = DataQualityChecker()
        self.plots_dir = os.path.join(data_dir, 'plots')
        os.makedirs(self.plots_dir, exist_ok=True)
        
        # 初始化處理器
        self.spread_processor = SpreadProcessor(self.plots_dir)
        self.tick_volume_processor = TickVolumeProcessor(self.plots_dir)

    def process_spread(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        處理 spread 數據
        
        Args:
            df (pd.DataFrame): 原始數據框
        Returns:
            pd.DataFrame: 處理後的數據框
        """
        return self.spread_processor.process(df)

    def process_tick_volume(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        處理 tick_volume 數據
        
        Args:
            df (pd.DataFrame): 原始數據框
        Returns:
            pd.DataFrame: 處理後的數據框
        """
        return self.tick_volume_processor.process(df)

    def check_data_quality(self, df: pd.DataFrame) -> None:
        """
        檢查數據質量
        
        Args:
            df (pd.DataFrame): 要檢查的數據框
        """
        self.logger.info("開始數據質量檢查")
        
        try:
            # 檢查缺漏值
            self.logger.info("1. 缺漏值檢查:")
            self.quality_checker.check_missing_values(df)
            
            # 檢查異常值
            self.logger.info("2. 異常值檢查:")
            self.quality_checker.check_outliers(df)
            
            # 檢查時間序列連續性
            self.logger.info("3. 時間序列連續性檢查:")
            self.quality_checker.check_time_series_continuity(df)
                
        except Exception as e:
            self.logger.error("數據質量檢查時發生錯誤: %s", str(e))
            raise 

    def process_price_changes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        計算相對價格變動和波動率
        
        Args:
            df (pd.DataFrame): 原始數據框
            
        Returns:
            pd.DataFrame: 添加了相對價格變動和波動率的數據框
        """
        self.logger.info("開始處理相對價格變動和波動率")
        
        try:
            df_processed = df.copy()
            
            # 計算相對價格變動
            df_processed['price_change_pct'] = df['close'].pct_change()
            df_processed['price_change_pct_abs'] = df_processed['price_change_pct'].abs()
            
            # 計算波動率（使用20個週期的滾動標準差）
            df_processed['volatility'] = df_processed['price_change_pct'].rolling(window=20).std()
            
            # 計算標準化價格（使用波動率標準化）
            df_processed['normalized_price'] = (df['close'] - df['close'].rolling(window=20).mean()) / df_processed['volatility']
            
            # 計算價格變動的移動平均
            df_processed['price_change_ma'] = df_processed['price_change_pct'].rolling(window=20).mean()
            
            # 計算價格變動的波動率
            df_processed['price_change_volatility'] = df_processed['price_change_pct'].rolling(window=20).std()
            
            # 記錄統計資訊
            self._log_price_statistics(df_processed)
            
            # 繪製分布圖
            self._plot_price_distributions(df_processed)
            
            return df_processed
            
        except Exception as e:
            self.logger.error(f"處理相對價格變動時發生錯誤: {str(e)}")
            raise
            
    def _log_price_statistics(self, df: pd.DataFrame) -> None:
        """記錄價格變動的統計資訊"""
        stats = {
            'price_change_pct': df['price_change_pct'].describe(),
            'volatility': df['volatility'].describe(),
            'normalized_price': df['normalized_price'].describe()
        }
        
        for name, stat in stats.items():
            self.logger.info(f"{name} 統計量:\n{stat}")
            
    def _plot_price_distributions(self, df: pd.DataFrame) -> None:
        """繪製價格變動的分布圖"""
        plt.figure(figsize=(15, 10))
        
        # 價格變動百分比分布
        plt.subplot(2, 2, 1)
        plt.hist(df['price_change_pct'].dropna(), bins=50, alpha=0.7)
        plt.title('Price Change Percentage Distribution')
        plt.xlabel('Price Change Percentage')
        plt.ylabel('Frequency')
        
        # 波動率分布
        plt.subplot(2, 2, 2)
        plt.hist(df['volatility'].dropna(), bins=50, alpha=0.7)
        plt.title('Volatility Distribution')
        plt.xlabel('Volatility')
        plt.ylabel('Frequency')
        
        # 標準化價格分布
        plt.subplot(2, 2, 3)
        plt.hist(df['normalized_price'].dropna(), bins=50, alpha=0.7)
        plt.title('Normalized Price Distribution')
        plt.xlabel('Normalized Price')
        plt.ylabel('Frequency')
        
        # 價格變動的移動平均
        plt.subplot(2, 2, 4)
        plt.plot(df.index, df['price_change_ma'], label='Moving Average')
        plt.plot(df.index, df['price_change_pct'], label='Actual Change', alpha=0.3)
        plt.title('Price Change Moving Average')
        plt.xlabel('Time')
        plt.ylabel('Price Change')
        plt.legend()
        
        plt.tight_layout()
        output_file = os.path.join(self.plots_dir, 'price_distributions.png')
        plt.savefig(output_file)
        self.logger.info(f"已生成價格分布圖: {output_file}")
        plt.close() 