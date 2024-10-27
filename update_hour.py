import json
import os
from bs4 import BeautifulSoup
import re

# 儲水池最大容量（毫米）
MAX_CAPACITY = 100.0

# 加載最新的儲水數據
def load_latest_water_storage():
    file_path = 'hourly_storage.json'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if data["data"]:
                # 返回最新的 water_storage
                num = float(data["data"][-1]["water_storage"].split("%")[0])
                return round(num,2)
    return 0.0

# 計算儲水百分比
def calculate_block_display(water_percentage):
    # 根據儲水百分比計算藍色格子數量
    total_blocks = 10  # 格子總數
    blue_blocks = int(water_percentage / 10)  # 每10%顯示一個藍色格子
    white_blocks = total_blocks - blue_blocks  # 剩下的格子為白色

    # 組合藍色和白色格子的字符串
    block_display = '🟦 ' * blue_blocks + '⬜️ ' * white_blocks

    # 將儲水趴數顯示為百分比
    return f"{block_display} {water_percentage}%"

def update_html(water_percentage):
    # 讀取 HTML 文件
    html_file_path = 'index.html'
    with open(html_file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # 找到「格子顯示」部分並更新
    card_announcement = soup.find('div', class_='announcement_content')
    if card_announcement:
        card_announcement.string = calculate_block_display(water_percentage)

    # 找到「目前存水量」並更新
    subtitle = soup.find('span', id='subtitle')
    if subtitle:
        subtitle.string = f"目前存水量：{water_percentage}%"

    # 找到 JavaScript 中的 typedJSFn.init 並更新
    script_tag = soup.find('script', string=lambda s: 'typedJSFn.init' in s if s else False)
    if script_tag:
        # 使用正則表達式來更新 "目前存水量" 的百分比顯示
        updated_script = re.sub(
            r'"目前存水量：\d+(\.\d+)?%"',
            f'"目前存水量：{water_percentage}%"',
            script_tag.string
        )
        script_tag.string = updated_script

    # 將更新後的 HTML 寫回文件
    with open(html_file_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))

    print(f"已將最新的格子顯示和目前存水量更新為 {water_percentage}% 並寫入 {html_file_path}")

def main():
    # 加載最新的 water_storage 百分比
    latest_water_percentage = load_latest_water_storage()

    # 確保儲水趴數不超過 100%
    latest_water_percentage = min(latest_water_percentage, 100.0)
    latest_water_percentage = round(latest_water_percentage, 2)  # 保留小數點後兩位

    print(f"目前儲水趴數：{latest_water_percentage}%")

    # 更新網頁內容
    update_html(latest_water_percentage)

if __name__ == "__main__":
    main()
