import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

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
    # 創建新的數據框副本
    df_processed = df.copy()
    
    # 計算原始 spread 的統計量
    original_stats = df['spread'].describe()
    print("\n原始 spread 統計量:")
    print(original_stats)
    
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
    
    print(f"\nIQR 方法異常值比例: {iqr_outlier_ratio:.2f}%")
    print(f"固定閾值方法異常值比例: {threshold_outlier_ratio:.2f}%")
    
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
    output_file = os.path.join(output_dir, 'spread_distribution.png')
    plt.savefig(output_file)
    print(f"\n已生成分布圖: {output_file}")
    
    return df_processed

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
    # 創建新的數據框副本
    df_processed = df.copy()
    
    # 計算原始 tick_volume 的統計量
    original_stats = df['tick_volume'].describe()
    print("\n原始 tick_volume 統計量:")
    print(original_stats)
    
    # 進行對數轉換（添加 1 避免 log(0)）
    df_processed['tick_volume_log'] = np.log1p(df['tick_volume'])
    
    # 計算對數轉換後的統計量
    log_stats = df_processed['tick_volume_log'].describe()
    print("\n對數轉換後 tick_volume 統計量:")
    print(log_stats)
    
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
    print(f"\n異常值比例: {outlier_ratio:.2f}%")
    
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
    output_file = os.path.join(output_dir, 'tick_volume_distribution.png')
    plt.savefig(output_file)
    print(f"\n已生成分布圖: {output_file}")
    
    return df_processed

def check_data_quality(df):
    """
    檢查數據框中的缺漏值和異常值
    
    Args:
        df (pd.DataFrame): 要檢查的數據框
    """
    print("\n=== 數據質量檢查 ===")
    
    # 檢查缺漏值
    print("\n1. 缺漏值檢查:")
    missing_values = df.isnull().sum()
    print(missing_values)
    
    # 檢查異常值（使用 IQR 方法）
    print("\n2. 異常值檢查:")
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    for col in numeric_columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]
        print(f"\n{col} 的異常值數量: {len(outliers)}")
        if len(outliers) > 0:
            print(f"異常值範圍: {outliers.min()} 到 {outliers.max()}")
    
    # 檢查時間序列的連續性
    print("\n3. 時間序列連續性檢查:")
    # 檢查數據框的索引是否為日期時間類型
    if isinstance(df.index, pd.DatetimeIndex):
        time_diff = df.index.to_series().diff()
        gaps = time_diff[time_diff > pd.Timedelta(minutes=1)]
        if len(gaps) > 0:
            print(f"發現 {len(gaps)} 個時間間隔")
            print("最大的時間間隔:", gaps.max())
        else:
            print("時間序列是連續的")
    else:
        print("警告：數據框的索引不是日期時間類型")
        print("請確保數據框的索引是日期時間類型以進行時間序列檢查") 