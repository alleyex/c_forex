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
from typing import Optional

def setup_logger(
    name: str,
    log_dir: Optional[str] = None,
    log_file: Optional[str] = None,
    level: int = logging.INFO
) -> logging.Logger:
    """
    設置並配置日誌記錄器
    
    這個函數會創建一個新的日誌記錄器，並設置以下配置：
    - 可自定義日誌級別
    - 同時輸出到檔案和控制台
    - 可自定義日誌檔案路徑和名稱
    - 使用 UTF-8 編碼確保中文正確顯示
    
    Args:
        name (str): 日誌記錄器的名稱，通常使用模組名稱
        log_dir (str, optional): 日誌檔案目錄，預設為 'logs'
        log_file (str, optional): 日誌檔案名稱，預設為 'mt5_YYYYMMDD.log'
        level (int, optional): 日誌級別，預設為 logging.INFO
        
    Returns:
        logging.Logger: 配置好的日誌記錄器實例
        
    Example:
        >>> logger = setup_logger('mt5_trading')
        >>> logger = setup_logger('mt5_trading', log_dir='custom_logs', log_file='custom.log')
    """
    # 設置日誌目錄
    if log_dir is None:
        log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    # 設置日誌檔案名稱
    if log_file is None:
        log_file = f'forex_{datetime.now().strftime("%Y%m%d")}.log'
    log_path = os.path.join(log_dir, log_file)
    
    # 創建日誌記錄器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 如果已經有處理器，則不重複添加
    if not logger.handlers:
        # 設置日誌格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 檔案處理器
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # 控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


