import requests
import json
import os
import time
from datetime import datetime, timedelta, timezone

DATA_FILE = "data.json"
MAX_HISTORY = 5000  # 修改点：保留最近 5000 个区块（约 35 天数据）

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
    """同时获取交易数据和区块时间"""
    url = f"https://blockchain.info/rawblock/{block_hash}"
    try:
        resp = requests.get(url, timeout=30).json()
        
        # 1. 获取区块时间戳
        block_time = resp.get('time', int(time.time()))
        
        # 2. 获取最大交易
        all_txs = []
        for tx in resp['tx']:
            total_value = sum(out['value'] for out in tx['out']) / 100000000
            all_txs.append({"txid": tx['hash'], "value": total_value})
        all_txs.sort(key=lambda x: x['value'], reverse=True)
        
        return all_txs[:3], block_time
    except Exception as e:
        print(f"解析区块详情失败: {e}")
        return [], int(time.time())

def main():
    now_bj = get_beijing_time()
    today_str = now_bj.strftime("%Y-%m-%d")

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                store = json.load(f)
            except:
                store = {}
    else:
        store = {}

    if "last_height" not in store:
        store["last_height"] = get_latest_height() - 1
    if "history" not in store:
        store["history"] = []
    # 兼容旧数据：如果没有 daily_max 字段，初始化它
    if "daily_max" not in store or store.get("last_date") != today_str:
        store["daily_max"] = {"value": 0, "txid": "N/A", "height": 0}
        store["last_date"] = today_str

    current_height = get_latest_height()
    last_height = store["last_height"]

    if current_height and current_height > last_height:
        print(f"🚀 发现新区块: {last_height + 1} -> {current_height}")
        
        for h in range(last_height + 1, current_height + 1):
            time.sleep(1) 
            try:
                # 获取区块哈希
                block_info = requests.get(f"https://blockchain.info/block-height/{h}?format=json", timeout=20).json()
                block_hash = block_info['blocks'][0]['hash']
                
                # 获取详情（含时间）
                top_3, block_ts = get_block_details(block_hash)
                
                # 更新今日最大
                if top_3 and top_3[0]['value'] > store["daily_max"]["value"]:
                    store["daily_max"] = {
                        "value": top_3[0]['value'],
                        "txid": top_3[0]['txid'],
                        "height": h
                    }

                # 存入历史（新增 time 字段）
                store["history"].append({
                    "height": h, 
                    "time": block_ts, # 新增时间戳
                    "top_txs": top_3
                })
                print(f"区块 {h} 处理完毕")

            except Exception as e:
                print(f"处理区块 {h} 出错: {e}")
                continue
        
        # 修改点：只保留最近 MAX_HISTORY 个
        store["history"] = store["history"][-MAX_HISTORY:]
        store["last_height"] = current_height

        with open(DATA_FILE, "w") as f:
            json.dump(store, f, indent=4)
        print("✅ 数据同步完成")
    else:
        print("😴 暂无新区块")

if __name__ == "__main__":
    main()
