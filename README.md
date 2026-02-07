# ₿ Habfut BTC Professional Intelligence 终端

> **一款基于 GitHub Actions + Cloudflare Pages 的轻量级、自动化比特币大额交易监控系统。**

---

## 📖 项目简介

本项目旨在为用户提供一个无需维护服务器、零成本运行的比特币区块情报站。通过自动化脚本每 30 分钟抓取最新区块数据，分析并提取每个区块中金额最高的 **前三笔转账**，并以专业金融终端的风格进行展示。

### ✨ 核心特性

* **零成本运行**：利用 GitHub Actions 进行数据处理，Cloudflare Pages 托管前端。
* **断点续传**：智能识别 `data.json` 中的最后记录高度，确保数据连续不遗漏。
* **双屏响应式设计**：桌面端采用专业双栏布局，移动端完美适配单屏滑动。
* **安全访问**：集成前端口令校验系统（默认口令：`habfut.com`）。
* **专业视觉**：采用金融级浅色调 UI，支持实时搜索与分页浏览。

---

## 🛠️ 技术架构

1. **数据层 (`monitor.py`)**: Python 脚本通过 Blockchain.info API 获取区块数据。
2. **工作流 (`.github/workflows/monitor.yml`)**: 每 30 分钟触发一次，更新 `data.json` 并推回仓库。
3. **展示层 (`index.html`)**: 基于 Tailwind CSS 驱动的高级前端页面。
4. **部署层**: Cloudflare Pages 实时同步仓库代码并分发全球。

---

## 🚀 快速部署指南

### 1. 仓库准备

* 在 GitHub 上创建一个新仓库（建议公开）。
* 上传 `monitor.py`、`index.html` 以及这个 `README.md`。

### 2. 配置权限 (关键)

为了让 GitHub Actions 能够更新数据，请务必开启写入权限：

1. 进入仓库的 **Settings** -> **Actions** -> **General**。
2. 滚动到 **Workflow permissions**。
3. 勾选 **Read and write permissions** 并点击 **Save**。

### 3. 连接 Cloudflare Pages

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)。
2. 选择 **Workers & Pages** -> **Create application** -> **Pages** -> **Connect to Git**。
3. 选择你的 GitHub 仓库。
4. **Build settings** 均保持默认（因为是纯静态页面），点击 **Save and Deploy**。

---

## 📂 文件说明

| 文件名 | 描述 |
| --- | --- |
| `monitor.py` | 核心抓取脚本，负责 API 调用、数据过滤与断点逻辑。 |
| `index.html` | 前端展示页面，包含口令校验、搜索、分页及响应式布局。 |
| `data.json` | 自动生成的数据文件，存储最近 100 个区块的情报。 |
| `.github/workflows/monitor.yml` | 自动化定时任务配置文件。 |

---

## 🔒 安全说明

* **访问口令**：默认访问码为 `habfut.com`。如需修改，请编辑 `index.html` 中 `verify()` 函数内的逻辑。
* **私密性**：如果您希望数据完全私有，可将仓库设为 **Private**。Cloudflare Pages 依然可以读取私有仓库进行部署。

---

## ⚖️ 免责声明

本工具仅用于区块链技术研究与数据分析展示，所提供的数据均来自公共 API。请勿用于任何非法用途，作者不对因使用本工具造成的任何直接或间接损失负责。

---

> **Habfut** —— 让比特币数据触手可及。
