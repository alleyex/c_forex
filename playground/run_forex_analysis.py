#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
外匯分析流程
這個腳本用於運行整個外匯分析流程，包括數據下載、特徵工程、模型訓練和預測。
"""

import os
import sys
from download_utils import download_forex_data
from process_data import process_forex_data
from forex_model import train_forex_model

def main():
    """
    運行整個外匯分析流程
    """
    print("=" * 50)
    print("開始外匯分析流程")
    print("=" * 50)
    
    # 下載數據
    print("\n1. 下載數據")
    print("-" * 30)
    download_forex_data()
    
    # 處理數據
    print("\n2. 處理數據")
    print("-" * 30)
    X_train, y_train, X_test, y_test = process_forex_data()
    
    # 訓練模型
    print("\n3. 訓練模型")
    print("-" * 30)
    model = train_forex_model(X_train, y_train, X_test, y_test)
    
    print("\n分析完成！")
    print("=" * 50)
    print("結果已保存為 'forex_prediction.png'")
    print("模型已保存為 'forex_model.joblib'")

if __name__ == "__main__":
    main() 