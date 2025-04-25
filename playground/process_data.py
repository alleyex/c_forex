# 導入必要的庫
from FeatureEngineering import FeatureEngineering
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

def process_forex_data(csv_file='usdjpy-m1.csv', window_size=8, test_size=100):
    """
    處理外匯數據
    
    參數:
        csv_file (str): CSV 文件路徑
        window_size (int): 時間窗口大小
        test_size (int): 測試數據大小
        
    返回:
        tuple: (X_train, y_train, X_test, y_test)
    """
    # 讀取數據
    raw_data = pd.read_csv(csv_file)
    raw_data['time'] = pd.to_datetime(raw_data['time'])
    raw_data.set_index('time', inplace=True)
    
    # 初始化特徵工程工具
    tool = FeatureEngineering()
    
    # 創建特徵
    print("創建技術指標...")
    indi_df = tool.create_indicators(raw_data)
    
    print("特徵縮放...")
    scal_df = tool.feature_scaling(indi_df)
    
    print("創建特徵...")
    feat_df, feature_size = tool.create_features(scal_df)
    
    print("創建時間窗口...")
    wind_df = tool.windowed(feat_df, window_size)
    
    # 分割測試數據和訓練數據
    print("分割數據...")
    test_data = wind_df.tail(test_size)
    train_data = wind_df.head(-test_size)
    
    X_test = test_data.iloc[:, :window_size].tail(test_size)
    y_test = test_data.y.tail(test_size).to_numpy()
    
    # 打亂訓練數據
    print("打亂訓練數據...")
    train_data = train_data.sample(frac=1).reset_index(drop=True)
    
    # 提取訓練數據的特徵和標籤
    X_train = train_data.iloc[:, :window_size]
    y_train = train_data.iloc[:, -1:].to_numpy()
    
    # 處理數據為模型輸入格式
    print("處理數據...")
    X_train = tool.process_data(X_train, window_size, feature_size)
    X_test = tool.process_data(X_test, window_size, feature_size)
    
    print(f"訓練數據形狀: {X_train.shape}")
    print(f"測試數據形狀: {X_test.shape}")
    
    return X_train, y_train, X_test, y_test

if __name__ == "__main__":
    # 處理數據
    X_train, y_train, X_test, y_test = process_forex_data() 