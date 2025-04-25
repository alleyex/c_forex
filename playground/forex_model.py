import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
from process_data import process_forex_data

def train_forex_model(X_train, y_train, X_test, y_test):
    """
    訓練外匯預測模型
    
    參數:
        X_train: 訓練數據特徵
        y_train: 訓練數據標籤
        X_test: 測試數據特徵
        y_test: 測試數據標籤
        
    返回:
        model: 訓練好的模型
    """
    # 初始化模型
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    
    # 訓練模型
    print("訓練模型...")
    model.fit(X_train.reshape(X_train.shape[0], -1), y_train.ravel())
    
    # 預測
    print("進行預測...")
    y_pred = model.predict(X_test.reshape(X_test.shape[0], -1))
    
    # 評估模型
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"均方誤差 (MSE): {mse:.4f}")
    print(f"R² 分數: {r2:.4f}")
    
    # 繪製預測結果
    plt.figure(figsize=(12, 6))
    plt.plot(y_test, label='實際值', color='blue')
    plt.plot(y_pred, label='預測值', color='red')
    plt.title('外匯價格預測結果')
    plt.xlabel('時間')
    plt.ylabel('價格')
    plt.legend()
    plt.savefig('forex_prediction.png')
    plt.close()
    
    return model

def main():
    # 處理數據
    X_train, y_train, X_test, y_test = process_forex_data()
    
    # 訓練模型
    model = train_forex_model(X_train, y_train, X_test, y_test)
    
    # 保存模型
    import joblib
    joblib.dump(model, 'forex_model.joblib')
    print("模型已保存為 'forex_model.joblib'")

if __name__ == "__main__":
    main() 