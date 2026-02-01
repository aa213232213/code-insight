import requests
import sys

def diagnose():
    print("🔍 运行系统诊断...")
    
    # 测试代理
    try:
        response = requests.get('https://api.github.com', 
                              proxies={'https': 'http://127.0.0.1:7890'},
                              timeout=10)
        print("✅ Clash 代理: 正常")
    except:
        print("❌ Clash 代理: 失败")
    
    # 测试 Ollama
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        print("✅ Ollama 服务: 正常")
    except:
        print("❌ Ollama 服务: 失败")
    
    # 测试 Flask
    try:
        response = requests.get('http://127.0.0.1:5000/health', timeout=5)
        print("✅ Flask 服务器: 正常")
    except:
        print("❌ Flask 服务器: 失败")

if __name__ == "__main__":
    diagnose()