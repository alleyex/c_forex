"""
通用工具函數模組

此模組提供了專案中常用的工具函數，包括：
- 專案路徑管理
- 日誌設置
- 其他通用功能
"""

import logging
import os
from datetime import datetime
from typing import Optional

def get_project_root() -> str:
    """
    獲取專案根目錄的絕對路徑
    
    Returns:
        str: 專案根目錄的絕對路徑
    """
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
        log_dir (str, optional): 日誌檔案目錄，預設為專案根目錄下的 'logs'
        log_file (str, optional): 日誌檔案名稱，預設為 'forex_YYYYMMDD.log'
        level (int, optional): 日誌級別，預設為 logging.INFO
        
    Returns:
        logging.Logger: 配置好的日誌記錄器實例
        
    Example:
        >>> logger = setup_logger('mt5_trading')
        >>> logger = setup_logger('mt5_trading', log_dir='custom_logs', log_file='custom.log')
    """
    # 設置日誌目錄
    if log_dir is None:
        log_dir = os.path.join(get_project_root(), 'logs')
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


