# C Forex Trading System

這是一個用於外匯交易的系統，使用 Python 和 MetaTrader 5 進行開發。

## 專案結構

```
c_forex/
├── src/                 # 核心功能
│   └── feature_engineering.py  # 特徵工程相關功能
├── feature_engineering/ # 特徵工程相關資料
├── mt5_trading/        # MT5交易相關功能
├── experiments/        # 實驗性程式碼
├── tests/             # 測試程式碼
├── docs/              # 文件
├── config/            # 設定檔
├── logs/              # 日誌
└── requirements.txt   # 依賴套件
```

## 功能說明

- `src/`: 包含核心功能模組
- `feature_engineering/`: 特徵工程相關的資料和處理
- `mt5_trading/`: MetaTrader 5 交易相關功能
- `experiments/`: 實驗性程式碼和測試
- `tests/`: 單元測試和功能測試
- `docs/`: 專案文件
- `config/`: 設定檔
- `logs/`: 系統日誌

## 安裝說明

1. 安裝依賴套件：
```bash
pip install -r requirements.txt
```

2. 設定 MetaTrader 5 帳號資訊（在 config/ 目錄下）

3. 執行測試：
```bash
python -m pytest tests/
```

## 使用說明

詳細的使用說明請參考 `docs/` 目錄下的文件。 