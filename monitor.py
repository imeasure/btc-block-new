import requests
import json
import os
import time
from datetime import datetime, timedelta, timezone

# --- 配置区 ---
LATEST_FILE = "data.json"       # 热数据：给首页看
ARCHIVE_DIR = "archive"         # 冷数据：仓库目录
KEEP_LATEST_COUNT = 1000        # 首页保留最近多少个块

def get_beijing_time():
    tz_bj = timezone(timedelta(hours=8))
    return datetime.now(tz_bj)

def get_latest_height():
    try:
        resp = requests.get("https://blockchain.info/latestblock", timeout=10)
        return resp.json()['height']
    except Exception as e:
        print(f"获取最新高度失败: {e}")
        return None

def get_block_details(block_hash):
    """获取区块详情，包含时间戳和交易"""
    url = f"https://blockchain.info/rawblock/{block_hash}"
    try:
        resp = requests.get(url, timeout=30).json()
        block_time = resp.get('time', int(time.time()))
        
        all_txs = []
        for tx in resp['tx']:
            total_value = sum(out['value'] for out in tx['out']) / 100000000
            all_txs.append({"txid": tx['hash'], "value": total_value})
        all_txs.sort(key=lambda x: x['value'], reverse=True)
        
        return all_txs[:3], block_time
    except Exception as e:
        print(f"解析失败: {e}")
        return [], int(time.time())

def save_to_archive(new_blocks):
    """核心功能：将新区块按月份归档到 archive 文件夹"""
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)

    # 按月份分组数据
    grouped_data = {}
    for block in new_blocks:
        # 将时间戳转换为 YYYY_MM 格式 (例如 2026_02)
        dt = datetime.fromtimestamp(block['time'], timezone(timedelta(hours=8)))
        month_key = dt.strftime("%Y_%m")
        
        if month_key not in grouped_data:
            grouped_data[month_key] = []
        grouped_data[month_key].append(block)

    # 分别写入对应的月份文件
    for month_key, blocks in grouped_data.items():
        file_path = os.path.join(ARCHIVE_DIR, f"{month_key}.json")
        
        # 1. 读取旧档案
        current_archive = []
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try:
                    current_archive = json.load(f)
                except:
                    current_archive = []
        
        # 2. 合并并去重 (通过高度判断)
        existing_heights = {b['height'] for b in current_archive}
        for b in blocks:
            if b['height'] not in existing_heights:
                current_archive.append(b)
        
        # 3. 排序并保存
        current_archive.sort(key=lambda x: x['height']) # 按高度升序
        
        with open(file_path, "w") as f:
            json.dump(current_archive, f, indent=None, separators=(',', ':')) # 压缩格式保存
        print(f"📦 已归档 {len(blocks)} 个区块到 {file_path}")

def main():
    now_bj = get_beijing_time()
    today_str = now_bj.strftime("%Y-%m-%d")

    # --- 1. 读取热数据 (data.json) ---
    if os.path.exists(LATEST_FILE):
        with open(LATEST_FILE, "r") as f:
            try:
                store = json.load(f)
            except:
                store = {}
    else:
        store = {}

    # 初始化字段
    store.setdefault("last_height", get_latest_height() - 1)
    store.setdefault("history", [])
    store.setdefault("daily_max", {"value": 0, "txid": "N/A", "height": 0})
    if store.get("last_date") != today_str:
        store["daily_max"] = {"value": 0, "txid": "N/A", "height": 0}
        store["last_date"] = today_str

    current_height = get_latest_height()
    last_height = store["last_height"]

    if current_height and current_height > last_height:
        print(f"🚀 新区块: {last_height + 1} -> {current_height}")
        
        new_blocks_buffer = []

        for h in range(last_height + 1, current_height + 1):
            time.sleep(1)
            try:
                info_url = f"https://blockchain.info/block-height/{h}?format=json"
                block_info = requests.get(info_url, timeout=20).json()
                block_hash = block_info['blocks'][0]['hash']
                
                top_3, block_ts = get_block_details(block_hash)
                
                # 更新今日最大
                if top_3 and top_3[0]['value'] > store["daily_max"]["value"]:
                    store["daily_max"] = {
                        "value": top_3[0]['value'],
                        "txid": top_3[0]['txid'],
                        "height": h
                    }

                block_data = {
                    "height": h,
                    "time": block_ts,
                    "top_txs": top_3
                }
                
                store["history"].append(block_data)
                new_blocks_buffer.append(block_data) # 加入归档缓冲区
                print(f"处理: {h}")

            except Exception as e:
                print(f"错误 {h}: {e}")
                continue
        
        # --- 2. 存入热数据 (只留最近1000个) ---
        store["history"] = store["history"][-KEEP_LATEST_COUNT:] 
        store["last_height"] = current_height

        with open(LATEST_FILE, "w") as f:
            json.dump(store, f, indent=4)
        
        # --- 3. 存入冷档案 (永久保存) ---
        if new_blocks_buffer:
            save_to_archive(new_blocks_buffer)
            
        print("✅ 同步完成：热数据已更新，冷档案已归档")
    else:
        print("😴 无新区块")

if __name__ == "__main__":
    main()
