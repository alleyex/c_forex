def download_file(filename, url):
    """
    通用文件下載函數
    
    參數:
        filename (str): 要保存的文件名
        url (str): 文件的 URL
        
    返回:
        bool: 下載是否成功
    """
    import requests
    import os
    
    # 檢查文件是否已存在
    if os.path.exists(filename):
        print(f"文件 '{filename}' 已存在，跳過下載。")
        return True
    
    try:
        # 發送 GET 請求獲取文件內容
        response = requests.get(url)
        response.raise_for_status()  # 檢查請求是否成功
        
        # 將文件內容寫入本地文件
        with open(filename, "wb") as f:
            f.write(response.content)
        
        print(f"文件 '{filename}' 已成功下載到當前目錄。")
        return True
    except Exception as e:
        print(f"下載文件時發生錯誤：{str(e)}")
        return False

def _download_forex_data():
    """
    下載外匯數據文件（私有函數）
    """
    # 下載 USD/JPY 數據文件
    usdjpy_filename = "usdjpy-m1.csv"
    usdjpy_url = "https://raw.githubusercontent.com/alleyex/c_forex/refs/heads/main/playground/usdjpy-m1.csv"
    download_file(usdjpy_filename, usdjpy_url)
    
    # 下載 forex_utils.py 文件
    forex_utils_filename = "forex_utils.py"
    forex_utils_url = "https://raw.githubusercontent.com/alleyex/c_forex/refs/heads/main/forex_utils.py"
    download_file(forex_utils_filename, forex_utils_url)

# 公共接口函數
def download_forex_data():
    """
    公共接口函數，用於下載外匯數據
    """
    return _download_forex_data()

if __name__ == "__main__":
    download_forex_data() 