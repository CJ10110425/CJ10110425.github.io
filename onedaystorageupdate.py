import json
import os
from datetime import datetime, timedelta

# 儲水池參數
TANK_LENGTH = 100  # cm
TANK_WIDTH = 200   # cm
TANK_HEIGHT = 100  # cm

def load_rainfall_data():
    file_path = 'rainfall_data.json'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    else:
        data = {"data": []}
    return data

def load_hourly_storage_data():
    file_path = 'hourly_storage.json'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    else:
        data = {"data": []}  # 初始為空列表
    return data

def save_hourly_storage_data(storage_data):
    file_path = 'hourly_storage.json'
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(storage_data, file, indent=4, ensure_ascii=False)

def calculate_water_volume(storage_percentage):
    tank_volume = TANK_LENGTH * TANK_WIDTH * TANK_HEIGHT  # cm³
    water_volume = tank_volume * (storage_percentage / 100)  # cm³
    return water_volume

def calculate_evaporation(temperature, rainfall):
    # 蒸發量公式
    evaporation = 0.0195 * temperature/82 - 0.015 * rainfall
    return max(0, evaporation)  # 確保蒸發量不為負數

def update_hourly_storage_data(storage_data, update_time, new_storage_percentage):
    # 將更新信息加入 `data` 列表
    storage_data["data"].append({
        "update_time": update_time,
        "water_storage": f"{new_storage_percentage} %"
    })

    # 保留 `data` 中最近 24 小時的記錄
    if len(storage_data["data"]) > 24:
        storage_data["data"] = storage_data["data"][-24:]

    return storage_data

def main():
    current_time = datetime.now()
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M")

    # 加載 rainfall_data 和 hourly_storage_data
    local_data = load_rainfall_data()
    hourly_storage_data = load_hourly_storage_data()

    # 讀取上一次的儲水趴數並計算 cm³
    previous_percentage = float(hourly_storage_data["data"][-1]["water_storage"].split(
        "%")[0] if hourly_storage_data["data"] else 10)  # 假設上次的初始儲水百分比為 10%
    current_volume_cm3 = calculate_water_volume(previous_percentage)

    # 從 rainfall_data 中找到最新的一小時數據
    if not local_data["data"]:
        print("沒有降雨資料，無法更新")
        return

    last_record = local_data["data"][-1]
    temperature = last_record["temperature"]
    rainfall = last_record["rainfall"]

    # 計算蒸發量
    evaporation_percentage = calculate_evaporation(temperature, rainfall)

    # 新的儲水百分比
    new_storage_percentage = max(
        0, previous_percentage - evaporation_percentage + rainfall)
    # new_storage_percentage = round(new_storage_percentage, 2)  # 保留小數點後兩位

    print(f"當前時間 ({current_time_str}) 進行每小時儲水更新。")
    print(f"上一次儲水: {previous_percentage}%, 容量: {current_volume_cm3} cm³")
    print(f"溫度: {temperature}°C, 降雨量: {rainfall} mm")
    print(f"蒸發影響: {evaporation_percentage}%")
    print(f"更新後儲水: {new_storage_percentage}%")

    # 更新 hourly_storage.json 資料
    hourly_storage_data = update_hourly_storage_data(
        hourly_storage_data, current_time_str, new_storage_percentage)
    save_hourly_storage_data(hourly_storage_data)

    print(f"儲水資料每小時更新成功，並儲存到 hourly_storage.json。")

if __name__ == "__main__":
    for i in range(72):
        main()
