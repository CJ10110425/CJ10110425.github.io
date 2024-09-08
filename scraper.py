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
        "total_precipitation": 4.25,  # 初始化累加的降雨量
        "data": []  # 用來存儲每次的降雨量數據
    }

# 累加之前的降雨量
previous_total = precipitation_data["total_precipitation"]
new_total = previous_total + precipitation_past1hr

# 更新 precipitation_data 的總降雨量和每次的降雨記錄
precipitation_data["total_precipitation"] = new_total
precipitation_data["data"].append({
    'date': data['records']['Station'][0]['ObsTime']['DateTime'],
    'precipitation_past1hr': precipitation_past1hr
})

# 將數據寫回 JSON 文件
with open(file_path, 'w', encoding='utf-8') as file:
    json.dump(precipitation_data, file, indent=4, ensure_ascii=False)

print(f"已更新 Past1hr 降雨量：{precipitation_past1hr} 毫米")
print(f"累計降雨量：{new_total} 毫米")

# 儲水池最大容量：100毫米
max_capacity = 100.0

# 計算儲水百分比
water_percentage = (new_total / max_capacity) * 100
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

# 將更新後的 HTML 寫回文件
with open(html_file_path, 'w', encoding='utf-8') as file:
    file.write(str(soup))

print(f"已將最新的格子顯示 {block_display_with_percentage} 和目前存水量寫入 {html_file_path}")
