import requests
from bs4 import BeautifulSoup
import json
import datetime
import re

# API 端點及參數
RAIN_DATA_URL = 'https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0002-001'
params = {
    'Authorization': 'CWA-F6DA1B3E-FAEB-4876-8674-6F8B5F2F23A1',
    'limit': 100,
    'offset': 0,
    'format': 'JSON',
    'StationId': 'C0D660'
}

# HTML 檔案位置
HTML_FILE_PATH = 'index.html'

# 儲水效率
STORAGE_EFFICIENCY = 0.95
# 蒸發係數
EVAPORATION_RATE = 0.95
# 水庫總容量（公斤）
TOTAL_CAPACITY = 100

# 從網路上抓取資料
def fetch_data():
    response = requests.get(RAIN_DATA_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return float(data['records']['Station'][0]['RainfallElement']['Past3days']['Precipitation'])
    else:
        print(f"Failed to fetch data from {RAIN_DATA_URL}")
        return None

# 從 HTML 中提取之前的降雨和水庫數據
def extract_previous_data(html_path):
    with open(html_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
    
    script_tag = soup.find('script', string=lambda x: x and 'const data =' in x)
    if script_tag:
        # 使用正則表達式從腳本中提取降雨和水庫數據
        rainfall_match = re.search(r'"Rainfall \(mm\)",\s*"data":\s*\[(.*?)\]', script_tag.string)
        reservoir_match = re.search(r'"Reservoir Water Level \(%\)",\s*"data":\s*\[(.*?)\]', script_tag.string)
        
        if rainfall_match and reservoir_match:
            # 將提取的數據轉換為列表
            rainfall_data = [float(x) for x in rainfall_match.group(1).split(',')]
            reservoir_data = [float(x) for x in reservoir_match.group(1).split(',')]
            return rainfall_data, reservoir_data
    return None, None

# 計算新的水庫存水量百分比
def calculate_reservoir_levels(latest_rainfall, previous_levels):
    # 昨天的儲水量百分比
    previous_level_kg = (previous_levels[-1] / 100) * TOTAL_CAPACITY

    if latest_rainfall == 0.0:
        # 無降雨時，直接考慮蒸發
        new_level = previous_level_kg * EVAPORATION_RATE
    else:
        # 有降雨時，考慮蒸發和儲水效率
        new_level = previous_level_kg * EVAPORATION_RATE + latest_rainfall * STORAGE_EFFICIENCY

    # 計算新儲水量的百分比
    new_level_percentage = (new_level / TOTAL_CAPACITY) * 100
    # 返回新的儲水量列表
    return previous_levels[1:] + [new_level_percentage]  # 移除最舊的一天，加上新的一天

# 更新 HTML 中的折線圖資料
def update_html(html_path, new_rainfall_data, previous_reservoir_data):
    with open(html_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # 找到腳本標籤，並更新其中的數據
    script_tag = soup.find('script', string=lambda x: x and 'const data =' in x)
    if script_tag:
        # 更新日期和資料
        today = datetime.datetime.now()
        new_labels = [
            (today - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(5)
        ][::-1]

        # 計算新的水庫存水量百分比
        new_reservoir_data = calculate_reservoir_levels(new_rainfall_data[4], previous_reservoir_data)

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
        script_tag.string = script_content.replace(
            script_content.split('const data =')[1].split(';')[0], 
            f" {json.dumps(new_data)}"
        )

    # 將更新後的 HTML 寫回文件
    with open(html_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))

# 主程式
def main():
    # 判斷今天是否是更新日（每三天更新一次）
    today = datetime.date.today()
    days_difference = (today - BASE_DATE).days
    if days_difference % 3 != 0:
        print("今天不是更新日，跳過更新。")
        return

    # 從網頁抓取資料
    new_rainfall_data = [fetch_data() for _ in range(5)]  # 假設連續5天的資料
    if all(data is not None for data in new_rainfall_data):
        previous_rainfall_data, previous_reservoir_data = extract_previous_data(HTML_FILE_PATH)
        if previous_rainfall_data and previous_reservoir_data:
            previous_rainfall_data.pop(0)
            previous_rainfall_data.append(new_rainfall_data[-1])
            update_html(HTML_FILE_PATH, previous_rainfall_data, previous_reservoir_data)
            print("HTML file updated successfully!")
        else:
            print("Failed to extract previous data from HTML.")
    else:
        print("Failed to update HTML file due to missing rainfall data.")

if __name__ == "__main__":
    main()