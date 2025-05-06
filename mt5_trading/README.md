# MT5 Trading Python 模組

這是一個用於與 MetaTrader 5 (MT5) 交易平台進行交互的 Python 模組。該模組提供了簡化的 API 來執行交易操作、獲取帳戶資訊和歷史數據。

## 功能特點

- 自動化 MT5 連接管理
- 帳戶資訊查詢
- 交易操作（開倉、平倉、修改訂單）
- 歷史數據查詢
- 持倉管理
- 日誌記錄

## 安裝需求

- Python 3.6+
- MetaTrader 5 平台
- 相關 Python 套件（請參考 requirements.txt）

## 使用方法

1. 首先確保 MT5 平台已安裝並運行
2. 在 `credential.json` 中配置您的 MT5 帳戶資訊
3. 導入模組並開始使用：

```python
from mt5_trading import MT5Connection, Account, Positions, History

# 建立連接
mt5 = MT5Connection()
mt5.connect()

# 獲取帳戶資訊
account = Account()
balance = account.get_balance()

# 查詢持倉
positions = Positions()
current_positions = positions.get_all()

# 獲取歷史數據
history = History()
historical_data = history.get_rates("EURUSD", "H1", 100)
```

## 模組結構

- `connection.py`: MT5 連接管理
- `account.py`: 帳戶相關操作
- `positions.py`: 持倉管理
- `history.py`: 歷史數據查詢
- `utils.py`: 工具函數
- `credential.json`: 帳戶憑證配置

## 注意事項

- 使用前請確保 MT5 平台已正確安裝並運行
- 交易操作請謹慎使用，建議先在模擬帳戶測試
- 定期檢查日誌以監控操作狀態

## 歷史數據使用說明

`history.py` 模組提供了獲取歷史數據和即時報價的功能。以下是詳細的使用方法：

### 獲取歷史K線數據

```python
from mt5_trading import MT5Connection, MT5History
from datetime import datetime, timedelta

# 建立連接
connection = MT5Connection()
connection.connect()

# 建立歷史數據管理器
history = MT5History(connection)

# 獲取指定時間範圍的歷史數據
end_time = datetime.now()
start_time = end_time - timedelta(days=1)
df = history.get_historical_data(
    symbol="EURUSD",
    timeframe="H1",  # 支援的時間週期：M1, M5, M15, M30, H1, H4, D1, W1, MN1
    start_time=start_time,
    end_time=end_time
)

# 獲取指定數量的歷史數據
df = history.get_historical_data(
    symbol="EURUSD",
    timeframe="H1",
    count=100  # 獲取最近的 100 根 K 線
)
```

### 獲取即時報價數據

```python
# 獲取指定時間範圍的即時報價
ticks = history.get_ticks(
    symbol="EURUSD",
    start_time=start_time,
    end_time=end_time
)

# 獲取指定數量的即時報價
ticks = history.get_ticks(
    symbol="EURUSD",
    count=10  # 獲取最近的 10 筆報價
)
```

## 憑證配置說明

`credential.json` 是用於存儲 MT5 帳戶登入資訊的配置文件。請按照以下格式創建該文件：

```json
{
    "login_id": "您的 MT5 帳號",
    "password": "您的 MT5 密碼",
    "server": "您的 MT5 伺服器名稱"
}
```

### 注意事項

1. 請確保 `credential.json` 文件位於專案根目錄下
2. 請妥善保管您的帳號密碼，不要將該文件提交到版本控制系統
3. 建議在 `.gitignore` 中添加 `credential.json` 以防止意外提交

