# TensorFlow 線性回歸演示

這是一個簡單的 TensorFlow 演示，展示如何使用 TensorFlow 創建和訓練一個簡單的線性回歸模型。

## 功能

- 生成帶有噪聲的線性數據 (y = 2x + 1 + 噪聲)
- 使用 TensorFlow 創建一個簡單的線性回歸模型
- 訓練模型並進行預測
- 繪製實際數據和預測結果
- 比較學習到的參數與實際參數

## 安裝依賴

```bash
pip install -r requirements.txt
```

## 運行演示

```bash
python tensorflow_demo.py
```

## 輸出

運行後，程序將：
1. 在控制台輸出學習到的模型參數
2. 生成一個名為 `tensorflow_demo_result.png` 的圖像文件，顯示實際數據點和預測線

## 預期結果

模型應該學習到接近 y = 2x + 1 的關係，考慮到添加的噪聲，學習到的參數可能略有不同。 
