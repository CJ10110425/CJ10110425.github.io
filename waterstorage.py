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


def load_storage_data():
    file_path = 'storage.json'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    else:
        data = {"data": []}  # 初始為空列表
    return data


def save_storage_data(storage_data):
    file_path = 'storage.json'
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(storage_data, file, indent=4, ensure_ascii=False)


def calculate_water_volume(storage_percentage):
    tank_volume = TANK_LENGTH * TANK_WIDTH * TANK_HEIGHT  # cm³
    water_volume = tank_volume * (storage_percentage / 100)  # cm³
    return water_volume


def should_update(storage_data, today):
    # 檢查 storage.json 最後一次更新日期是否超過 3 天
    if len(storage_data["data"]) == 0:
        return True
    last_date_str = storage_data["data"][-1]["update_date"]
    last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
    return (today - last_date).days >= 3


def update_storage_data(storage_data, today_str, new_storage_percentage, total_rainfall):
    # 將更新信息加入 `data` 列表
    storage_data["data"].append({
        "update_date": today_str,
        "water_storage": f"{round(new_storage_percentage, 2)} %",
        "rainfall": round(total_rainfall, 2)
    })

    # 保留 `data` 中最近 3 次的更新記錄
    if len(storage_data["data"]) > 3:
        storage_data["data"] = storage_data["data"][-3:]

    return storage_data


def calculate_evaporation(average_temperature, total_rainfall):
    # 蒸發量公式
    evaporation = 0.0195 * average_temperature - 0.015 * total_rainfall
    return max(0, evaporation)  # 確保蒸發量不為負數


def main():
    today = datetime.now()  # 直接使用 datetime.now()
    today_str = today.strftime("%Y-%m-%d")

    # 加載 rainfall_data 和 storage_data
    local_data = load_rainfall_data()
    storage_data = load_storage_data()

    # 判斷是否需要更新
    if should_update(storage_data, today):
        # 讀取上一次的儲水趴數並計算 cm³
        previous_percentage = float(storage_data["data"][-1]["water_storage"].split(
            "%")[0] if storage_data["data"] else 10)  # 假設上次的初始儲水百分比為 10%
        current_volume_cm3 = calculate_water_volume(previous_percentage)

        # 假設平均氣溫和降雨量可以從 rainfall_data 中獲得 (簡單取最近 3 天內的平均)
        sum_temp = 0
        sum_rain = 0
        count = 0
        for record in local_data["data"][-72:]:  # 選擇最近 3 天的 72 小時資料
            sum_temp += record["temperature"]
            sum_rain += record["rainfall"]
            count += 1

        average_temperature = sum_temp / count if count else 0
        total_rainfall = sum_rain

        # 計算蒸發量
        evaporation_percentage = calculate_evaporation(
            average_temperature, total_rainfall)

        # 新的儲水百分比
        new_storage_percentage = max(
            0, previous_percentage - evaporation_percentage)
        new_storage_percentage = round(new_storage_percentage, 2)  # 保留小數點後兩位

        print(f"今天 ({today_str}) 進行儲水更新。")
        print(f"上一次儲水: {previous_percentage}%, 容量: {current_volume_cm3} cm³")
        print(f"蒸發影響: {evaporation_percentage}%")
        print(f"更新後儲水: {new_storage_percentage}%, 總降雨量: {total_rainfall} mm")

        # 更新 storage.json 資料
        storage_data = update_storage_data(
            storage_data, today_str, new_storage_percentage, total_rainfall)
        save_storage_data(storage_data)

        print(f"儲水資料更新成功，並儲存到 storage.json。")
    else:
        print(f"今天 ({today_str}) 無需更新儲水資料。")


if __name__ == "__main__":
    main()
