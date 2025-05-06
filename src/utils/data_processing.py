import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from utils.utils import setup_logger
import logging

# 初始化全局日誌記錄器，名稱統一，檔名統一
logger = setup_logger(
    name='forex_logger',
    log_dir=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs'),
    log_file=None,  # 預設 forex_YYYYMMDD.log
    level=logging.INFO
)

def process_spread(df, output_dir):
    """
    處理 spread 的異常值：
    1. 使用 IQR 方法標記異常值
    2. 使用固定閾值（spread > 10）標記異常值
    3. 可視化處理前後的分布
    
    Args:
        df (pd.DataFrame): 原始數據框
        output_dir (str): 輸出目錄路徑
    Returns:
        pd.DataFrame: 處理後的數據框
    """
    logger.info("開始處理 spread 數據")
    
    try:
        # 創建 plots 目錄
        plots_dir = os.path.join(output_dir, 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        
        # 保存原始統計量
        logger.info("原始 spread 統計量:")
        logger.info(df['spread'].describe())
        
        # 創建新的數據框副本
        df_processed = df.copy()
        
        # 計算原始 spread 的統計量
        original_stats = df['spread'].describe()
        logger.info("原始 spread 統計量:\n%s", original_stats)
        
        # 方法1：使用 IQR 方法標記異常值
        Q1 = df['spread'].quantile(0.25)
        Q3 = df['spread'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        df_processed['is_spread_outlier_iqr'] = ((df['spread'] < lower_bound) | (df['spread'] > upper_bound)).astype(int)
        
        # 方法2：使用固定閾值標記異常值
        df_processed['is_spread_outlier_threshold'] = (df['spread'] > 10).astype(int)
        
        # 計算兩種方法的異常值比例
        iqr_outlier_ratio = df_processed['is_spread_outlier_iqr'].mean() * 100
        threshold_outlier_ratio = df_processed['is_spread_outlier_threshold'].mean() * 100
        
        logger.info("IQR 方法異常值比例: %.2f%%", iqr_outlier_ratio)
        logger.info("固定閾值方法異常值比例: %.2f%%", threshold_outlier_ratio)
        
        # 可視化處理前後的分布
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
        output_file = os.path.join(plots_dir, 'spread_distribution.png')
        plt.savefig(output_file)
        logger.info("已生成分布圖: %s", output_file)
        
        return df_processed
        
    except Exception as e:
        logger.error("處理 spread 數據時發生錯誤: %s", str(e))
        raise

def process_tick_volume(df, output_dir):
    """
    處理 tick_volume 的異常值：
    1. 進行對數轉換
    2. 標記異常值
    3. 可視化處理前後的分布
    
    Args:
        df (pd.DataFrame): 原始數據框
        output_dir (str): 輸出目錄路徑
    Returns:
        pd.DataFrame: 處理後的數據框
    """
    logger.info("開始處理 tick_volume 數據")
    
    try:
        # 創建 plots 目錄
        plots_dir = os.path.join(output_dir, 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        
        # 創建新的數據框副本
        df_processed = df.copy()
        
        # 計算原始 tick_volume 的統計量
        original_stats = df['tick_volume'].describe()
        logger.info("原始 tick_volume 統計量:\n%s", original_stats)
        
        # 進行對數轉換（添加 1 避免 log(0)）
        df_processed['tick_volume_log'] = np.log1p(df['tick_volume'])
        
        # 計算對數轉換後的統計量
        log_stats = df_processed['tick_volume_log'].describe()
        logger.info("對數轉換後 tick_volume 統計量:\n%s", log_stats)
        
        # 使用 IQR 方法標記異常值
        Q1 = df_processed['tick_volume_log'].quantile(0.25)
        Q3 = df_processed['tick_volume_log'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # 標記異常值
        df_processed['is_tick_volume_outlier'] = ((df_processed['tick_volume_log'] < lower_bound) | (df_processed['tick_volume_log'] > upper_bound)).astype(int)
        
        # 計算異常值比例
        outlier_ratio = df_processed['is_tick_volume_outlier'].mean() * 100
        logger.info("異常值比例: %.2f%%", outlier_ratio)
        
        # 可視化處理前後的分布
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
        output_file = os.path.join(plots_dir, 'tick_volume_distribution.png')
        plt.savefig(output_file)
        logger.info("已生成分布圖: %s", output_file)
        
        return df_processed
        
    except Exception as e:
        logger.error("處理 tick_volume 數據時發生錯誤: %s", str(e))
        raise

def check_data_quality(df):
    """
    檢查數據框中的缺漏值和異常值
    
    Args:
        df (pd.DataFrame): 要檢查的數據框
    """
    logger.info("開始數據質量檢查")
    
    try:
        # 檢查缺漏值
        logger.info("1. 缺漏值檢查:")
        missing_values = df.isnull().sum()
        logger.info("缺漏值統計:\n%s", missing_values)
        
        # 檢查異常值（使用 IQR 方法）
        logger.info("2. 異常值檢查:")
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]
            logger.info("%s 的異常值數量: %d", col, len(outliers))
            if len(outliers) > 0:
                logger.info("異常值範圍: %f 到 %f", outliers.min(), outliers.max())
        
        # 檢查時間序列的連續性
        logger.info("3. 時間序列連續性檢查:")
        # 檢查數據框的索引是否為日期時間類型
        if isinstance(df.index, pd.DatetimeIndex):
            time_diff = df.index.to_series().diff()
            gaps = time_diff[time_diff > pd.Timedelta(minutes=1)]
            if len(gaps) > 0:
                logger.info("發現 %d 個時間間隔", len(gaps))
                logger.info("最大的時間間隔: %s", gaps.max())
            else:
                logger.info("時間序列是連續的")
        else:
            logger.warning("警告：數據框的索引不是日期時間類型")
            logger.warning("請確保數據框的索引是日期時間類型以進行時間序列檢查")
            
    except Exception as e:
        logger.error("數據質量檢查時發生錯誤: %s", str(e))
        raise 