import requests
import json
import os
import time
from datetime import datetime, timedelta, timezone

DATA_FILE = "data.json"

def get_beijing_time():
    """获取当前的北京时间 (UTC+8)"""
    tz_bj = timezone(timedelta(hours=8))
    return datetime.now(tz_bj)

def get_latest_height():
    try:
        resp = requests.get("https://blockchain.info/latestblock", timeout=10)
        return resp.json()['height']
    except Exception as e:
        print(f"获取最新高度失败: {e}")
        return None

def get_block_top_3(block_hash):
    url = f"https://blockchain.info/rawblock/{block_hash}"
    try:
        resp = requests.get(url, timeout=30).json()
        all_txs = []
        for tx in resp['tx']:
            total_value = sum(out['value'] for out in tx['out']) / 100000000
            all_txs.append({"txid": tx['hash'], "value": total_value})
        all_txs.sort(key=lambda x: x['value'], reverse=True)
        return all_txs[:3]
    except Exception as e:
        print(f"解析区块 {block_hash} 失败: {e}")
        return []

def main():
    now_bj = get_beijing_time()
    today_str = now_bj.strftime("%Y-%m-%d")

    # 1. 加载或初始化数据
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                store = json.load(f)
            except:
                store = {}
    else:
        store = {}

    # 初始化必要字段
    if "last_height" not in store:
        store["last_height"] = get_latest_height() - 1
    if "history" not in store:
        store["history"] = []
    if "daily_max" not in store or store.get("last_date") != today_str:
        print(f"📅 开启新的一天统计: {today_str}")
        store["daily_max"] = {"value": 0, "txid": "N/A", "height": 0}
        store["last_date"] = today_str

    current_height = get_latest_height()
    last_height = store["last_height"]

    if current_height and current_height > last_height:
        print(f"🚀 发现新区块: {last_height + 1} -> {current_height}")
        
        for h in range(last_height + 1, current_height + 1):
            time.sleep(1) 
            try:
                block_info = requests.get(f"https://blockchain.info/block-height/{h}?format=json", timeout=20).json()
                block_hash = block_info['blocks'][0]['hash']
                top_3 = get_block_top_3(block_hash)
                
                # 实时对比并替换今日最大转账
                if top_3 and top_3[0]['value'] > store["daily_max"]["value"]:
                    store["daily_max"] = {
                        "value": top_3[0]['value'],
                        "txid": top_3[0]['txid'],
                        "height": h
                    }
                    print(f"🔥 捕获到今日新高: {top_3[0]['value']} BTC")

                store["history"].append({"height": h, "top_txs": top_3})
            except Exception as e:
                print(f"处理区块 {h} 出错: {e}")
                continue
        
        store["history"] = store["history"][-100:]
        store["last_height"] = current_height

        with open(DATA_FILE, "w") as f:
            json.dump(store, f, indent=4)
        print("✅ 数据写入完成")
    else:
        print("😴 暂无新区块")

if __name__ == "__main__":
    main()
