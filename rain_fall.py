import requests
from bs4 import BeautifulSoup
import json
import datetime
import re
import os
# HTML 檔案位置
HTML_FILE_PATH = 'index.html'

# 儲水池總容量（公斤）
TOTAL_CAPACITY = 100

# 從 `storage.json` 中讀取最新三個更新記錄


def load_latest_storage_data():
    file_path = 'storage.json'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # 取得最近三次更新的記錄
            return data["data"][-3:]
    return []

# 更新 HTML 中的折線圖資料


def update_html(html_path, storage_data):
    with open(html_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # 找到腳本標籤，並更新其中的數據
    script_tag = soup.find(
        'script', string=lambda x: x and 'const data =' in x)
    if script_tag:
        # 取得 storage_data 中的日期、降雨量與儲水量
        new_labels = [record["update_date"] for record in storage_data]
        new_rainfall_data = [record["rainfall"] for record in storage_data]
        new_reservoir_data = [
            float(record["water_storage"].strip('%')) for record in storage_data]

        # 更新數據
        new_data = {
            'labels': new_labels,
            'datasets': [
                {
                    'label': 'Rainfall (mm)',
                    'data': new_rainfall_data,
                    'borderColor': '#004aad',
                    'backgroundColor': '#004aad',
                    'pointBackgroundColor': '#004aad',
                    'pointBorderColor': '#004aad',
                    'fill': False,
                    'tension': 0.2,
                    'yAxisID': 'y'
                },
                {
                    'label': 'Reservoir Water Level (%)',
                    'data': new_reservoir_data,
                    'borderColor': '#FFD700',
                    'backgroundColor': '#FFD700',
                    'pointBackgroundColor': '#FFD700',
                    'pointBorderColor': '#FFD700',
                    'fill': False,
                    'tension': 0.2,
                    'yAxisID': 'y1'
                }
            ]
        }

        # 更新腳本內容
        script_content = script_tag.string
        new_script_content = f"const data = {json.dumps(new_data)};"
        script_tag.string = re.sub(
            r"const data =\s*{.*};",
            new_script_content,
            script_content,
            flags=re.DOTALL
        )

    # 將更新後的 HTML 寫回文件
    with open(html_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))

    print(f"HTML file updated successfully!")

# 主程式


def main():
    # 從 `storage.json` 中讀取最新三次儲水資料
    storage_data = load_latest_storage_data()
    if len(storage_data) == 3:
        # 更新 HTML 文件
        update_html(HTML_FILE_PATH, storage_data)
    else:
        print("Insufficient data in storage.json. Need at least 3 records.")


if __name__ == "__main__":
    main()
