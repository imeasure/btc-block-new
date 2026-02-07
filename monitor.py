import requests
import json
import os
import time

DATA_FILE = "data.json"

def get_latest_height():
    """获取当前最新区块高度"""
    try:
        resp = requests.get("https://blockchain.info/latestblock", timeout=10)
        return resp.json()['height']
    except Exception as e:
        print(f"获取最新高度失败: {e}")
        return None

def get_block_top_3(block_hash):
    """获取指定区块内转账金额前三的交易"""
    url = f"https://blockchain.info/rawblock/{block_hash}"
    try:
        resp = requests.get(url, timeout=30).json()
        all_txs = []
        for tx in resp['tx']:
            # 计算该笔交易所有输出金额的总和
            total_value = sum(out['value'] for out in tx['out']) / 100000000
            all_txs.append({"txid": tx['hash'], "value": total_value})
        
        # 按金额降序排序，取前三名
        all_txs.sort(key=lambda x: x['value'], reverse=True)
        return all_txs[:3]
    except Exception as e:
        print(f"解析区块 {block_hash} 失败: {e}")
        return []

def main():
    # 1. 加载本地已存储的数据
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            store = json.load(f)
    else:
        # 如果是第一次运行，默认从当前高度的前 1 个块开始
        init_height = get_latest_height()
        store = {"last_height": init_height - 1, "history": []}

    current_height = get_latest_height()
    last_height = store["last_height"]

    if current_height is None:
        return

    # 2. 检查是否有新区块
    if current_height > last_height:
        print(f"🚀 发现新区块: 从 {last_height + 1} 到 {current_height}")
        
        for h in range(last_height + 1, current_height + 1):
            print(f"正在处理高度: {h}...")
            # 增加 1 秒延迟，防止 API 频率过快被封
            time.sleep(1) 
            
            try:
                # 根据高度获取区块 Hash
                block_info = requests.get(f"https://blockchain.info/block-height/{h}?format=json", timeout=20).json()
                block_hash = block_info['blocks'][0]['hash']
                
                # 获取该块前三名
                top_3 = get_block_top_3(block_hash)
                
                # 存入历史记录
                store["history"].append({
                    "height": h,
                    "top_txs": top_3
                })
            except Exception as e:
                print(f"处理区块 {h} 时出错: {e}")
                continue
        
        # 3. 更新状态并持久化
        # 只保留最近 100 个区块的历史，防止 data.json 过大导致网页加载慢
        store["history"] = store["history"][-100:]
        store["last_height"] = current_height

        with open(DATA_FILE, "w") as f:
            json.dump(store, f, indent=4)
        print("✅ 数据同步完成")
    else:
        print("😴 暂无新区块，等待下次运行")

if __name__ == "__main__":
    main()
