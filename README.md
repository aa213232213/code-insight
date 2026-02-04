# Code Insight

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](#)
[![Ollama](https://img.shields.io/badge/Ollama-required-brightgreen)](#)
[![License](https://img.shields.io/badge/License-MIT-black)](#license)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](#)

一个“浏览器扩展 + 本地 Python 服务 + Ollama”的 GitHub 仓库分析工具：  
在 GitHub 仓库页面一键分析代码结构、技术栈与用途，输出中文总结。

---

## 目录

- [1. 功能](#1-功能)
- [2. 环境要求](#2-环境要求)
- [3. 安装](#3-安装)
- [4. 配置（必读）](#4-配置必读)
- [5. 快速开始（Quick Start）](#5-快速开始quick-start)
- [6. 工作流程](#6-工作流程)
- [7. 推荐模型](#7-推荐模型)
- [8. 项目结构](#8-项目结构)
- [9. API](#9-api)
- [10. 开发与调试](#10-开发与调试)
- [11. 常见问题与排查（FAQ / Troubleshooting）](#11-常见问题与排查faq--troubleshooting)
- [12. Security](#14-security)
- [13. License](#15-license)

---

## 1. 功能

- 🔍 一键分析 GitHub 仓库（架构 / 技术栈 / 使用场景）
- 🤖 支持 Ollama 本地模型推理（你本机有什么模型就用什么）
- 📡 自动获取仓库信息（README / 文件列表 / 元信息）
- 🧩 浏览器扩展侧边栏展示结果
- 🌐 可选 Clash 代理（网络受限时启用）
- 🧠 适合快速理解陌生仓库、代码审阅、学习开源项目

---

## 2. 环境要求

- Python 3.9+
- Ollama（本地模型服务）
- Chrome / Edge（用于安装扩展）

---

## 3. 安装

### 3.1 克隆项目

```bash
git clone https://github.com/aa213232213/code-insight.git
cd code-insight
3.2 安装 Python 依赖
pip install -r requirements.txt
3.3 安装并启动 Ollama
启动：

ollama serve
查看本机模型列表（模型名以这里为准）：

ollama list
4. 配置（必读）
4.1 GitHub Token（必选）
本项目通过 GitHub API 获取仓库信息。
未认证请求只有 60 次/小时，容易触发 403 rate limit，因此必须配置 Token。

在项目根目录创建 .env：

GITHUB_TOKEN=ghp_xxx你的tokenxxx
USE_CLASH_PROXY=0
CLASH_PROXY=http://127.0.0.1:7890
字段说明：

GITHUB_TOKEN：必填（建议使用最小权限）

USE_CLASH_PROXY：是否启用代理（0/1）

CLASH_PROXY：Clash HTTP 代理地址（默认 7890）

5. 快速开始（Quick Start）
5.1 启动后端服务
python local_server.py
默认地址：

服务：http://127.0.0.1:5000

健康检查：http://127.0.0.1:5000/health

5.2 安装浏览器扩展
Chrome / Edge：

打开 chrome://extensions/

开启 开发者模式

点击 加载已解压的扩展程序

选择扩展目录（包含 manifest.json 的文件夹）

5.3 开始使用
打开任意 GitHub 仓库页面

点击扩展侧边栏 开始分析

选择模型（必须存在于 ollama list）

等待输出结果

6. 工作流程
扩展从当前 GitHub 页面获取仓库 URL

扩展请求本地服务 POST /analyze

后端通过 GitHub API 拉取仓库信息（需要 Token）

后端整理为 prompt

调用本机 Ollama 模型生成分析

扩展展示分析结果

7. 推荐模型
说明：本项目不会下载模型，只使用你本机已有模型（以 ollama list 为准）。

建议：

快速分析：deepseek-coder:6.7b / qwen2.5:7b

更强结构理解：deepseek-coder:33b（需要更强硬件）

中文表达更稳：qwen / glm 系列

8. 项目结构
code-insight/
├─ README.md
├─ requirements.txt
├─ .env                       # 你自己创建（必选）
│
├─ local_server.py            # Flask 后端：GitHub 拉取 + Ollama 推理
├─ diagnose.py                # 网络/Token/Ollama 诊断脚本
├─ setup_clash.py             # Clash 代理检测/提示脚本
│
├─ background.js              # 扩展后台脚本
├─ content.js                 # 页面注入脚本（如有）
├─ manifest.json              # 扩展清单（如有）
└─ (sidebar / popup / ui)     # 扩展 UI（如有）
9. API
9.1 POST /analyze
请求示例：

{
  "url": "https://github.com/owner/repo",
  "model": "deepseek-coder:6.7b"
}
返回示例：

{
  "success": true,
  "data": {
    "analysis": "...",
    "model_used": "deepseek-coder:6.7b"
  }
}
9.2 GET /health
用于检查：

后端服务是否存活

Token 是否加载

是否启用代理

10. 开发与调试
10.1 后端调试
python local_server.py
10.2 扩展调试
扩展页面打开 F12 查看 Console

chrome://extensions/ 中点击扩展的 “背景页 / Service Worker” 查看日志

11. 常见问题与排查（FAQ / Troubleshooting）
11.1 403 rate limit exceeded
原因：GitHub API 未认证或 token 未生效。

验证：

curl -I https://api.github.com/repos/aa213232213/code-insight
判断：

X-RateLimit-Limit: 60：未认证

X-RateLimit-Limit: 5000：已认证

11.2 RemoteDisconnected / 连接被关闭
优先排查代理：

不需要代理：.env 设 USE_CLASH_PROXY=0

需要代理：确认 Clash 已启动，端口正确（默认 7890）

建议跑诊断：

python diagnose.py
11.3 Ollama 无法连接
检查：

ollama serve 是否启动

访问 http://127.0.0.1:11434/api/tags 是否能返回模型列表

11.4 分析很慢 / 超时
建议：

换更小模型（7B）

仓库很大时减少拉取文件数量（需要在后端做限制）

优先使用更稳定网络或启用代理

12. Security

Token 建议最小权限原则

13. License
MIT
