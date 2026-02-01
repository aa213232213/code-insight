import os
import requests
from dotenv import load_dotenv

load_dotenv()

def setup_clash_proxy():
    """配置 Clash 代理设置"""
    
    clash_proxy = "http://127.0.0.1:7890"
    
    # 设置环境变量
    os.environ['HTTP_PROXY'] = clash_proxy
    os.environ['HTTPS_PROXY'] = clash_proxy
    
    print(f"🎯 已设置 Clash 代理: {clash_proxy}")
    
    # 测试 GitHub 连接
    test_github_connection()

def test_github_connection():
    """测试 GitHub API 连接"""
    
    test_urls = [
        "https://api.github.com/repos/torvalds/linux",
        "https://api.github.com/repos/microsoft/vscode"
    ]
    
    headers = {'Accept': 'application/vnd.github.v3+json'}
    
    for url in test_urls:
        try:
            print(f"测试 {url}...")
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功连接 GitHub!")
                print(f"   仓库: {data.get('name')}")
                print(f"   星标: {data.get('stargazers_count')}")
                return True
            else:
                print(f"❌ HTTP 错误: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 连接失败: {e}")
            return False

if __name__ == "__main__":
    setup_clash_proxy()