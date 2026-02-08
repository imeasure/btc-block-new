import requests
import json
import os
import time
from datetime import datetime, timedelta, timezone

LATEST_FILE = "data.json"
ARCHIVE_DIR = "archive"
KEEP_LATEST_COUNT = 1000

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
    """获取区块详情，并提取【区块奖励】和【总交易量】"""
    url = f"https://blockchain.info/rawblock/{block_hash}"
    try:
        resp = requests.get(url, timeout=30).json()
        block_time = resp.get('time', int(time.time()))
        
        all_txs = []
        block_reward = 0
        total_volume = 0
        
        for i, tx in enumerate(resp['tx']):
            # 计算单笔交易的总输出
            tx_value = sum(out.get('value', 0) for out in tx.get('out', [])) / 100000000
            
            # 第0笔交易永远是矿工的 Coinbase 交易 (区块奖励 + 手续费)
            if i == 0:
                block_reward = tx_value
            
            total_volume += tx_value
            all_txs.append({"txid": tx.get('hash', ''), "value": tx_value})
            
        all_txs.sort(key=lambda x: x['value'], reverse=True)
        
        return all_txs[:3], block_time, block_reward, total_volume
    except Exception as e:
        print(f"解析失败: {e}")
        return [], int(time.time()), 0, 0

def save_to_archive(new_blocks):
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)
    grouped_data = {}
    for block in new_blocks:
        dt = datetime.fromtimestamp(block['time'], timezone(timedelta(hours=8)))
        month_key = dt.strftime("%Y_%m")
        if month_key not in grouped_data:
            grouped_data[month_key] = []
        grouped_data[month_key].append(block)

    for month_key, blocks in grouped_data.items():
        file_path = os.path.join(ARCHIVE_DIR, f"{month_key}.json")
        current_archive = []
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try:
                    current_archive = json.load(f)
                except: pass
        
        existing_heights = {b['height'] for b in current_archive}
        for b in blocks:
            if b['height'] not in existing_heights:
                current_archive.append(b)
        
        current_archive.sort(key=lambda x: x['height'])
        with open(file_path, "w") as f:
            json.dump(current_archive, f, indent=None, separators=(',', ':'))

def main():
    now_bj = get_beijing_time()
    today_str = now_bj.strftime("%Y-%m-%d")

    if os.path.exists(LATEST_FILE):
        with open(LATEST_FILE, "r") as f:
            try: store = json.load(f)
            except: store = {}
    else:
        store = {}

    store.setdefault("last_height", get_latest_height() - 1)
    store.setdefault("history", [])
    store.setdefault("daily_max", {"value": 0, "txid": "N/A", "height": 0})
    
    # 核心新增：初始化每日统计数据面板
    store.setdefault("daily_stats", {}) 

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
                
                # 接收新增的奖励和交易量数据
                top_3, block_ts, reward, volume = get_block_details(block_hash)
                
                # 将时间戳转换为北京时间的日期，用于按日统计
                block_date = datetime.fromtimestamp(block_ts, timezone(timedelta(hours=8))).strftime("%Y-%m-%d")
                
                # 累加每日数据
                if block_date not in store["daily_stats"]:
                    store["daily_stats"][block_date] = {"reward": 0, "volume": 0}
                store["daily_stats"][block_date]["reward"] += reward
                store["daily_stats"][block_date]["volume"] += volume

                if top_3 and top_3[0]['value'] > store["daily_max"]["value"]:
                    store["daily_max"] = {
                        "value": top_3[0]['value'],
                        "txid": top_3[0]['txid'],
                        "height": h
                    }

                block_data = {"height": h, "time": block_ts, "top_txs": top_3}
                store["history"].append(block_data)
                new_blocks_buffer.append(block_data)
                print(f"✅ 处理区块 {h} | 奖励: {reward:.2f} | 交易量: {volume:.2f}")

            except Exception as e:
                print(f"错误 {h}: {e}")
                continue
        
        store["history"] = store["history"][-KEEP_LATEST_COUNT:] 
        store["last_height"] = current_height

        with open(LATEST_FILE, "w") as f:
            json.dump(store, f, indent=4)
        
        if new_blocks_buffer:
            save_to_archive(new_blocks_buffer)
            
        print("✅ 同步完成：热数据、冷档案、每日统计均已更新")
    else:
        print("😴 无新区块")

if __name__ == "__main__":
    main()
