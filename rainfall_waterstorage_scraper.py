import json
import requests
import os
from datetime import datetime

# API 端點及參數
url = 'https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0002-001'
params = {
    'Authorization': 'CWA-AC09013D-FEAF-4F96-8122-DD18C2A01252',
    'limit': 100,
    'offset': 0,
    'format': 'JSON',
    'StationId': 'C0D660'  # 替換成你要查詢的測站ID
}

def load_local_data():
    file_path = 'rainfall_data.json'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    else:
        data = {"data": []}
    return data

def convert_to_24hr_format(dt):
    return dt.strftime("%Y-%m-%d-%H:%M")

def save_local_data(data):
    file_path = 'rainfall_data.json'
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def fetch_precipitation_data():
    response = requests.get(url, params=params)
    return response.json()

def get_current_temperature(latitude = 24.785361, longitude = 120.997750, api_key = "33b559d192ee1b14e1bfd1a2fef64d01"):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'lat': latitude,
        'lon': longitude,
        'appid': api_key,
        'units': 'metric',  # 使用攝氏溫度
        'lang': 'zh_tw'     # 使用繁體中文
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        current_temp = data['main']['temp']
        return current_temp
    else:
        print(f"無法獲取經緯度 ({latitude}, {longitude}) 的天氣數據。HTTP狀態碼: {response.status_code}, 訊息: {response.json().get('message')}")

# 每小時運行的資料更新
def update_data():
    local_data = load_local_data()
    
    # 獲取實時資料
    current_time = datetime.now()
    precipitation_data = fetch_precipitation_data()
    precipitation_past1hr = precipitation_data['records']['Station'][0]['RainfallElement']['Past1hr']['Precipitation']
    temperature = get_current_temperature()
    
    # 將每小時的數據新增到 data
    local_data["data"].append({
        "update_time": convert_to_24hr_format(current_time),
        "temperature": temperature,
        "rainfall": precipitation_past1hr
    })

    # 儲存資料
    save_local_data(local_data)
    print(f"已更新資料至 {convert_to_24hr_format(current_time)}")

if __name__ == "__main__":
    update_data()
