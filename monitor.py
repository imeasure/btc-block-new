import requests
import json
import os

DATA_FILE = "data.json"

def get_latest_height():
    return requests.get("https://blockchain.info/latestblock").json()['height']

def get_block_top_3(block_hash):
    resp = requests.get(f"https://blockchain.info/rawblock/{block_hash}").json()
    all_txs = []
    for tx in resp['tx']:
        total_value = sum(out['value'] for out in tx['out']) / 100000000
        all_txs.append({"txid": tx['hash'], "value": total_value})
    # 按金额降序排，取前三
    all_txs.sort(key=lambda x: x['value'], reverse=True)
    return all_txs[:3]

# 读取旧数据
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        store = json.load(f)
else:
    store = {"last_height": get_latest_height() - 1, "history": []}

current_height = get_latest_height()
last_height = store["last_height"]

if current_height > last_height:
    print(f"检测到新区块: 从 {last_height + 1} 到 {current_height}")
    # 依次获取中间所有块的 hash
    for h in range(last_height + 1, current_height + 1):
        block_hash = requests.get(f"https://blockchain.info/block-height/{h}?format=json").json()['blocks'][0]['hash']
        top_3 = get_block_top_3(block_hash)
        store["history"].append({"height": h, "top_txs": top_3})
    
    # 只保留最近 50 个区块的历史，防止文件过大
    store["history"] = store["history"][-50:]
    store["last_height"] = current_height

    with open(DATA_FILE, "w") as f:
        json.dump(store, f, indent=4)
