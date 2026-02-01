@echo off
chcp 65001
title Code Insight with Clash Proxy

echo 设置代理环境...
set HTTP_PROXY=http://127.0.0.1:7890
set HTTPS_PROXY=http://127.0.0.1:7890

echo 激活虚拟环境...
call venv\Scripts\activate

echo 启动 Code Insight 服务器...
python local_server.py

pause