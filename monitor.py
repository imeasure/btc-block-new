import requests
import json
import os
import time
from datetime import datetime, timedelta, timezone

# --- 配置区 ---
LATEST_FILE = "data.json"
ARCHIVE_DIR = "archive"
KEEP_LATEST_COUNT = 1000
BLOCK_REWARD = 3.125  # 当前比特币区块奖励

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

def get_block_details_and_stats(block_hash):
    """
    获取区块详情，并计算：
    1. Top 3 巨额交易
    2. 区块总手续费 (BTC)
    3. 区块全网转账总额 (BTC)
    """
    url = f"https://blockchain.info/rawblock/{block_hash}"
    try:
        resp = requests.get(url, timeout=30).json()
        block_time = resp.get('time', int(time.time()))
        
        # --- 1. 计算手续费 ---
        # Blockchain.info API 的 fee 是以聪 (Satoshi) 为单位，需要除以 1亿
        # 有些 API 返回里直接有 fee，如果没有，则需要 (输入总和 - 输出总和)
        # 这里为了简化和稳定，我们使用 fee 字段，如果没有则设为 0
        total_fee_sats = resp.get('fee', 0) 
        total_fee_btc = total_fee_sats / 100000000

        # --- 2. 计算全网移动数量 (Total Output Volume) ---
        total_volume_btc = 0
        all_txs = []
        
        for tx in resp['tx']:
            # 计算该笔交易的总输出
            tx_val = sum(out['value'] for out in tx['out']) / 100000000
            total_volume_btc += tx_val
            
            all_txs.append({"txid": tx['hash'], "value": tx_val})
        
        all_txs.sort(key=lambda x: x['value'], reverse=True)
        
        return all_txs[:3], block_time, total_fee_btc, total_volume_btc

    except Exception as e:
        print(f"解析失败: {e}")
        return [], int(time.time()), 0, 0

def save_to_archive(new_blocks):
    """归档逻辑保持不变"""
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
                try: current_archive = json.load(f)
                except: current_archive = []
        
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

    # 读取现有数据
    if os.path.exists(LATEST_FILE):
        with open(LATEST_FILE, "r") as f:
            try: store = json.load(f)
            except: store = {}
    else:
        store = {}

    store.setdefault("last_height", get_latest_height() - 1)
    store.setdefault("history", [])
    store.setdefault("daily_max", {"value": 0, "txid": "N/A", "height": 0})
    # --- 新增：每日统计数据 ---
    store.setdefault("daily_stats", {}) 

    # 跨天处理：重置今日最大
    if store.get("last_date") != today_str:
        store["daily_max"] = {"value": 0, "txid": "N/A", "height": 0}
        store["last_date"] = today_str

    # 确保今天的数据桶存在
    if today_str not in store["daily_stats"]:
        store["daily_stats"][today_str] = {
            "mining_output": 0,    # 挖矿产出 (BTC)
            "on_chain_volume": 0,  # 链上移动量 (BTC)
            "block_count": 0       # 出了多少个块
        }

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
                
                # 获取增强版详情
                top_3, block_ts, fee_btc, vol_btc = get_block_details_and_stats(block_hash)
                
                # 1. 更新今日最大转账
                if top_3 and top_3[0]['value'] > store["daily_max"]["value"]:
                    store["daily_max"] = {
                        "value": top_3[0]['value'],
                        "txid": top_3[0]['txid'],
                        "height": h
                    }

                # 2. 更新每日统计 (关键步骤)
                # 注意：这里要用区块的时间戳来决定加到哪一天，而不是脚本运行的时间
                block_date_str = datetime.fromtimestamp(block_ts, timezone(timedelta(hours=8))).strftime("%Y-%m-%d")
                
                if block_date_str not in store["daily_stats"]:
                     store["daily_stats"][block_date_str] = {"mining_output": 0, "on_chain_volume": 0, "block_count": 0}
                
                # 累加数据
                # 挖矿产出 = 固定奖励 + 手续费
                mining_total = BLOCK_REWARD + fee_btc
                
                store["daily_stats"][block_date_str]["mining_output"] += mining_total
                store["daily_stats"][block_date_str]["on_chain_volume"] += vol_btc
                store["daily_stats"][block_date_str]["block_count"] += 1

                # 3. 存入历史列表
                block_data = {
                    "height": h,
                    "time": block_ts,
                    "top_txs": top_3
                }
                store["history"].append(block_data)
                new_blocks_buffer.append(block_data)
                print(f"处理: {h} | 产出: {mining_total:.2f} | 移动: {vol_btc:.2f}")

            except Exception as e:
                print(f"错误 {h}: {e}")
                continue
        
        # 维护数据大小
        store["history"] = store["history"][-KEEP_LATEST_COUNT:] 
        # 只保留最近 60 天的每日统计，防止 JSON 无限膨胀
        sorted_dates = sorted(store["daily_stats"].keys())
        if len(sorted_dates) > 60:
            new_stats = {}
            for d in sorted_dates[-60:]:
                new_stats[d] = store["daily_stats"][d]
            store["daily_stats"] = new_stats

        store["last_height"] = current_height

        with open(LATEST_FILE, "w") as f:
            json.dump(store, f, indent=4)
        
        if new_blocks_buffer:
            save_to_archive(new_blocks_buffer)
            
        print("✅ 同步完成")
    else:
        print("😴 无新区块")

if __name__ == "__main__":
    main()
