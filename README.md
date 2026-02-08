
# 🟠 Habfut Bitcoin Intel / 比特币情报终端

> **A real-time, serverless Bitcoin blockchain monitor powered by GitHub Actions.**
> **一个基于 GitHub Actions 的实时、无服务器比特币链上情报监控终端。**

![Habfut Intel Screenshot](https://raw.githubusercontent.com/lovexw/btc-block-new/main/screenshot.png)
*(建议上传一张你刚刚截的最终效果图，命名为 screenshot.png 放在仓库根目录)*

## ✨ Features / 核心功能

* **🔍 Real-time Monitoring**: Automatically fetches the latest blocks via GitHub Actions (CRON).
    * **实时监控**：利用 GitHub Actions 定时任务，自动抓取最新区块数据。
* **🐋 Whale Alert**: Tracks the largest transaction in every block and daily top transfers.
    * **巨鲸追踪**：自动锁定每个区块内的最大单笔转账，并统计今日“转账之王”。
* **📊 Visual Trends**: Professional charts for transaction volume, mining rewards, and whale movements.
    * **可视化趋势**：内置专业图表，展示资金流向、每日挖矿产出及全网交易总量。
* **⚡ Zero Cost & Fast**: Hosted on GitHub Pages, accelerated by jsDelivr CDN for global access.
    * **零成本秒开**：完全托管在 GitHub，配合 CDN 加速，国内访问也丝滑流畅。
* **📱 Responsive Design**: Perfectly adapted for both desktop and mobile devices.
    * **全端适配**：完美支持手机端和电脑端，随时随地查看链上情报。
* **🗄️ Auto Archiving**: Automatically archives historical data for long-term analysis.
    * **自动归档**：历史数据自动按月归档，支持查看长周期的历史趋势。

---

## 🚀 Quick Start / 快速部署

### 1. Fork this Repository (Fork 本仓库)
Click the `Fork` button in the top right corner to copy this project to your own GitHub account.
点击右上角的 `Fork` 按钮，将本项目复制到你自己的 GitHub 账号下。

### 2. Enable GitHub Actions (开启自动运行)
1.  Go to the **Actions** tab in your forked repository.
    进入你仓库的 **Actions** 栏目。
2.  Click the green button **"I understand my workflows, go ahead and enable them"**.
    点击绿色按钮开启 Workflow。
3.  (Optional) You can manually trigger the "Update Bitcoin Data" workflow to test it immediately.
    (可选) 你可以手动运行一次 "Update Bitcoin Data" 来测试效果。

### 3. Update Configuration (修改配置)
Edit `index.html` file, find the following lines and change them to your username:
编辑 `index.html` 文件，找到以下几行，修改为你自己的 GitHub 用户名和仓库名：

```javascript
// Change these to your own repo info
const REPO_OWNER = 'your-github-username'; // 你的 GitHub 用户名
const REPO_NAME = 'your-repo-name';        // 你的仓库名 (例如 btc-monitor)

```

### 4. Enable GitHub Pages (开启网页托管)

1. Go to **Settings** -> **Pages**.
进入 **Settings** -> **Pages**。
2. Select **Source** as `Deploy from a branch`.
选择来源为 `Deploy from a branch`。
3. Select **Branch** as `main` and folder `/ (root)`.
选择分支为 `main`，文件夹选 `/ (root)`。
4. Click **Save**. You will get your website URL shortly!
点击保存。稍等片刻，你就能获得你的专属情报站链接了！

---

## 🛠️ How it Works / 工作原理

1. **Backend (Python)**:
* The `monitor.py` script runs every 5-10 minutes (triggered by GitHub Actions).
* It fetches data from `blockchain.info` API.
* It updates `data.json` (hot data) and archives old data into `archive/` folder (cold data).
* It calculates daily stats (mining rewards, total volume).
* Finally, it commits and pushes the changes back to the repo.


2. **Frontend (HTML/JS)**:
* The user visits the GitHub Pages website.
* The browser fetches data from `cdn.jsdelivr.net` (mirrored from your repo) for fast access.
* `Chart.js` renders the beautiful charts based on the data.



---

## 📂 Project Structure / 目录结构

```text
.
├── .github/workflows/
│   └── update.yml      # GitHub Actions configuration (定时任务配置)
├── archive/            # Historical data storage (历史档案存储)
│   └── 2026_02.json
├── monitor.py          # Python script for data fetching (核心抓取脚本)
├── index.html          # Frontend dashboard (前端展示页面)
├── data.json           # Latest data cache (最新热数据)
└── README.md           # Documentation (说明文档)

```

---

## 🤝 Contributing / 贡献

We welcome contributions! If you have ideas for new charts or features, feel free to open an issue or submit a pull request.
欢迎提交代码！如果你有新的图表创意或功能建议，欢迎提交 Issue 或 PR。

## 📄 License

This project is open-sourced under the MIT License.
本项目基于 MIT 协议开源，完全免费。

---

<p align="center">
Made with ❤️ by Habfut
</p>
