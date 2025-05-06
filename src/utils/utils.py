"""
MT5 交易平台的通用工具函數

這個模組提供了 MT5 交易平台所需的通用工具函數，包括日誌設置、錯誤處理等功能。
目前主要包含日誌配置相關的功能，未來可能會擴展更多實用工具。

模組依賴:
    - logging: Python 標準日誌模組
    - os: 作業系統相關功能
    - datetime: 日期時間處理
"""

import logging
import os
from datetime import datetime

def setup_logger(name: str) -> logging.Logger:
    """
    設置並配置日誌記錄器
    
    這個函數會創建一個新的日誌記錄器，並設置以下配置：
    - 日誌級別為 INFO
    - 同時輸出到檔案和控制台
    - 日誌檔案按日期命名，存放在 logs 目錄下
    - 使用 UTF-8 編碼確保中文正確顯示
    
    Args:
        name (str): 日誌記錄器的名稱，通常使用模組名稱
        
    Returns:
        logging.Logger: 配置好的日誌記錄器實例
        
    Example:
        >>> logger = setup_logger('mt5_trading')
        >>> logger.info('這是一條日誌訊息')
    """
    # 創建 logs 目錄（如果不存在）
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # 設置日誌檔案名稱（使用當前日期）
    log_file = f'logs/mt5_{datetime.now().strftime("%Y%m%d")}.log'
    
    # 配置日誌
    logging.basicConfig(
        level=logging.INFO,  # 設置日誌級別為 INFO
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 日誌格式
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),  # 檔案輸出
            logging.StreamHandler()  # 控制台輸出
        ]
    )
    
    return logging.getLogger(name) 


