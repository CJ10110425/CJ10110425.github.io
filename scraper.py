import json
import requests
import os
from bs4 import BeautifulSoup

# API 端點及參數
url = 'https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0002-001'
params = {
    'Authorization': 'CWA-F6DA1B3E-FAEB-4876-8674-6F8B5F2F23A1',
    'limit': 100,
    'offset': 0,
    'format': 'JSON',
    'StationId': 'C0D660'  # 替換成你要查詢的測站ID
}

# 儲水效率和蒸發係數
STORAGE_EFFICIENCY = 0.95
EVAPORATION_RATE = 0.95

# 儲水池最大容量（毫米）
MAX_CAPACITY = 100.0

# 發送 API 請求
response = requests.get(url, params=params)
data = response.json()

# 取得 Past1hr 的降雨量
precipitation_past1hr = data['records']['Station'][0]['RainfallElement']['Past1hr']['Precipitation']

# 檢查是否已經有 precipitation_data.json 文件，沒有就創建
file_path = 'precipitation_data.json'
if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        precipitation_data = json.load(file)
else:
    precipitation_data = {
        "total_precipitation": 10.0,  # 初始化水庫儲水量（毫米）
        "data": []  # 用來存儲每次的降雨量數據
    }

# 獲取前一天的儲水量
previous_storage = precipitation_data["total_precipitation"]

# 計算新儲水量
if precipitation_past1hr == 0.0:
    # 如果沒有降雨，考慮蒸發效應
    new_storage = previous_storage * EVAPORATION_RATE
else:
    # 如果有降雨，考慮儲水效率和蒸發效應
    new_storage = previous_storage * EVAPORATION_RATE + precipitation_past1hr * STORAGE_EFFICIENCY

# 確保儲水量不超過水庫最大容量
new_storage = min(new_storage, MAX_CAPACITY)

# 更新 precipitation_data 的儲水量和每次的降雨記錄
precipitation_data["total_precipitation"] = new_storage
precipitation_data["data"].append({
    'date': data['records']['Station'][0]['ObsTime']['DateTime'],
    'precipitation_past1hr': precipitation_past1hr,
    'storage': new_storage
})

# 將數據寫回 JSON 文件
with open(file_path, 'w', encoding='utf-8') as file:
    json.dump(precipitation_data, file, indent=4, ensure_ascii=False)

print(f"已更新 Past1hr 降雨量：{precipitation_past1hr} 毫米")
print(f"目前水庫儲水量：{new_storage} 毫米")

# 計算儲水百分比
water_percentage = (new_storage / MAX_CAPACITY) * 100
water_percentage = min(water_percentage, 100.0)  # 確保百分比不超過 100%

print(f"目前儲水趴數：{water_percentage}%")

# 根據儲水百分比計算藍色格子數量
total_blocks = 10  # 格子總數
blue_blocks = int(water_percentage / 10)  # 每10%顯示一個藍色格子
white_blocks = total_blocks - blue_blocks  # 剩下的格子為白色

# 組合藍色和白色格子的字符串
block_display = '🟦 ' * blue_blocks + '⬜️ ' * white_blocks

# 將儲水趴數顯示為百分比
block_display_with_percentage = f"{block_display} {water_percentage}%"

# 讀取 HTML 文件
html_file_path = 'index.html'
with open(html_file_path, 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

# 找到「格子顯示」部分並更新
card_announcement = soup.find('div', class_='announcement_content')
if card_announcement:
    card_announcement.string = block_display_with_percentage

# 找到「目前存水量」並更新
subtitle = soup.find('span', id='subtitle')
if subtitle:
    subtitle.string = f"目前存水量：{water_percentage}%"

# 找到 JavaScript 中的 typedJSFn.init 並更新
script_tag = soup.find('script', text=lambda t: 'typedJSFn.init' in t if t else False)
if script_tag:
    # 使用正則表達式來更新 "目前存水量" 的百分比顯示
    updated_script = script_tag.string.replace(
        '"目前存水量：50%"', 
        f'"目前存水量：{water_percentage}%"'
    )
    script_tag.string = updated_script

# 將更新後的 HTML 寫回文件
with open(html_file_path, 'w', encoding='utf-8') as file:
    file.write(str(soup))

print(f"已將最新的格子顯示 {block_display_with_percentage} 和目前存水量寫入 {html_file_path}")
