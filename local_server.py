# -*- coding: utf-8 -*-
import os
import requests
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 强制设置 Clash 代理
clash_proxy = "http://127.0.0.1:7890"
os.environ['HTTP_PROXY'] = clash_proxy
os.environ['HTTPS_PROXY'] = clash_proxy

print(f"🔧 使用 Clash 代理: {clash_proxy}")

app = Flask(__name__)
CORS(app)

# 创建带代理的会话
def create_clash_session():
    session = requests.Session()
    session.proxies = {
        'http': clash_proxy,
        'https': clash_proxy
    }
    return session

# 全局使用这个会话
GITHUB_SESSION = create_clash_session()
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
} if GITHUB_TOKEN else {'Accept': 'application/vnd.github.v3+json'}

print("GitHub Token:", "已设置" if GITHUB_TOKEN else "未设置")

def extract_owner_repo(github_url):
    """
    从 GitHub URL 中提取所有者和仓库名
    """
    clean_url = github_url.replace('https://github.com/', '').replace('.git', '').rstrip('/')
    parts = clean_url.split('/')
    
    if len(parts) >= 2:
        return parts[0], parts[1]
    else:
        raise ValueError(f"无效的 GitHub URL: {github_url}")

def get_repo_data(owner, repo):
    """
    获取仓库的核心数据
    """
    base_url = f"https://api.github.com/repos/{owner}/{repo}"
    
    try:
        # 1. 获取仓库基本信息
        print("📡 正在获取仓库信息...")
        repo_response = GITHUB_SESSION.get(base_url, headers=HEADERS, timeout=10)
        repo_response.raise_for_status()
        repo_info = repo_response.json()
        
        default_branch = repo_info.get('default_branch', 'main')
        repo_name = repo_info.get('name', '')
        description = repo_info.get('description', '')
        
        print(f"✅ 获取到仓库: {repo_name}")
        if description:
            print(f"📝 描述: {description}")
        
        # 2. 获取文件树结构
        print("📁 正在获取文件结构...")
        tree_url = f"{base_url}/git/trees/{default_branch}?recursive=1"
        tree_response = GITHUB_SESSION.get(tree_url, headers=HEADERS, timeout=10)
        tree_response.raise_for_status()
        
        file_list = []
        tree_data = tree_response.json()
        for item in tree_data.get('tree', []):
            if item['type'] == 'blob':  # 只关心文件
                file_list.append(item['path'])
        
        print(f"📊 找到 {len(file_list)} 个文件")
        
        # 3. 获取 README 内容
        print("📖 正在获取 README...")
        readme_url = f"{base_url}/readme"
        readme_response = GITHUB_SESSION.get(readme_url, headers=HEADERS, timeout=10)
        
        readme_content = ""
        if readme_response.status_code == 200:
            readme_data = readme_response.json()
            readme_content = base64.b64decode(readme_data['content']).decode('utf-8')
            print(f"✅ 获取到 README ({len(readme_content)} 字符)")
        else:
            print(f"⚠️ 未找到 README 文件 (HTTP {readme_response.status_code})")
        
        return repo_name, file_list, readme_content
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求错误: {e}")
        return "", [], ""
    except Exception as e:
        print(f"❌ 处理数据时出错: {e}")
        return "", [], []

def filter_code_files(file_list):
    """只保留常见的源代码文件"""
    code_extensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
        '.go', '.rs', '.php', '.rb', '.cs', '.swift', '.kt', '.md', '.json',
        '.yaml', '.yml', '.xml', '.html', '.css', '.scss', '.sql'
    }
    
    code_files = []
    for file_path in file_list:
        if any(file_path.lower().endswith(ext) for ext in code_extensions):
            code_files.append(file_path)
    
    return code_files

def call_ollama_analysis(repo_name, code_files, readme_content, model='deepseek-coder:6.7b'):
    """调用本地 Ollama 进行分析 - 支持完整模型列表"""
    
    # 模型超时配置
    model_timeouts = {
        'deepseek-coder:6.7b': 90,
        'gpt-oss:20b': 120,
        'deepseek-r1:8b': 120,
        'llama3.2:latest': 90,
        'deepseek-v3.1:671b-cloud': 180,
        'qwen3-coder:480b-cloud': 180,
        'gpt-oss:120b-cloud': 180,
        'glm-4.6:cloud': 150,
        'kimi-k2:1t-cloud': 180
    }
    
    timeout = model_timeouts.get(model, 120)
    
    prompt = f"""
请用中文输出，并严格遵循以下结构：

**项目简介：**
用一两句话说明项目是什么，解决什么问题

**技术架构：**
- 实现语言
- 核心模块  
- 部署方式

**主要场景：**
1. 场景1
2. 场景2

请分析以下代码库信息：
仓库名称：{repo_name}
文件数量：{len(code_files)}
主要文件：{', '.join(code_files[:10])}
README：{readme_content[:2000]}
"""
    
    try:
        print(f"🤖 使用模型 {model} 进行分析 (超时: {timeout}秒)...")
        ollama_response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': model,
                'prompt': prompt,
                'stream': False
            },
            timeout=timeout
        )
        
        if ollama_response.status_code == 200:
            result = ollama_response.json().get('response', '分析失败')
            print(f"✅ 分析完成 ({len(result)} 字符)")
            return result
        else:
            error_msg = f"Ollama 服务错误: {ollama_response.status_code}"
            print(f"❌ {error_msg}")
            return error_msg
            
    except requests.exceptions.Timeout:
        error_msg = f"模型 {model} 响应超时 ({timeout}秒)，请尝试更小的模型"
        print(f"⏰ {error_msg}")
        return error_msg
    except requests.exceptions.RequestException as e:
        error_msg = f"无法连接到 Ollama: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@app.route('/analyze', methods=['POST'])
def analyze_repo():
    """分析 GitHub 仓库的主要接口 - 支持模型选择"""
    data = request.json
    github_url = data.get('url')
    model = data.get('model', 'deepseek-coder:6.7b')
    
    if not github_url:
        return jsonify({'success': False, 'error': '未提供 URL'})
    
    try:
        print(f"\n🎯 开始分析: {github_url}")
        print(f"🤖 使用模型: {model}")
        
        owner, repo = extract_owner_repo(github_url)
        repo_name, file_list, readme_content = get_repo_data(owner, repo)
        
        if not repo_name:
            return jsonify({'success': False, 'error': '无法获取仓库信息，请检查URL和网络连接'})
        
        code_files = filter_code_files(file_list)
        print(f"🔍 过滤后代码文件: {len(code_files)} 个")
        
        analysis_result = call_ollama_analysis(repo_name, code_files, readme_content, model)
        
        return jsonify({
            'success': True,
            'data': {
                'repo_name': repo_name,
                'file_count': len(code_files),
                'file_sample': code_files[:10],
                'analysis': analysis_result,
                'model_used': model
            }
        })
        
    except Exception as e:
        error_msg = f"分析过程中出错: {e}"
        print(f"❌ {error_msg}")
        return jsonify({
            'success': False,
            'error': error_msg
        })

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy', 
        'service': 'code-insight',
        'proxy': 'clash:7890',
        'version': '1.0'
    })

@app.route('/')
def home():
    """首页"""
    return '''
    <html>
        <head>
            <title>Code Insight Server</title>
            <style>
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; 
                    margin: 40px; 
                    background: #f6f8fa;
                    color: #000000;
                }
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    padding: 40px;
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                }
                .status { 
                    color: #1a7f37; 
                    font-weight: 700; 
                    font-size: 18px;
                    padding: 12px 20px;
                    background: #f0fff4;
                    border: 2px solid #1a7f37;
                    border-radius: 8px;
                    display: inline-block;
                }
                .endpoints { 
                    margin: 30px 0; 
                }
                .endpoint { 
                    margin: 16px 0; 
                    padding: 20px; 
                    background: #f8f9fa; 
                    border-radius: 8px;
                    border: 2px solid #e1e4e8;
                }
                .endpoint strong {
                    color: #000000;
                    font-size: 16px;
                }
                a {
                    color: #0969da;
                    text-decoration: none;
                    font-weight: 600;
                }
                a:hover {
                    text-decoration: underline;
                }
                h1 {
                    color: #000000;
                    border-bottom: 3px solid #1a7f37;
                    padding-bottom: 12px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>✅ Code Insight 服务器运行正常</h1>
                <div class="status">状态: 运行中</div>
                
                <div class="endpoints">
                    <h3>可用端点:</h3>
                    <div class="endpoint">
                        <strong>GET /health</strong> - 健康检查<br>
                        <a href="/health" target="_blank">http://127.0.0.1:5000/health</a>
                    </div>
                    <div class="endpoint">
                        <strong>POST /analyze</strong> - 分析 GitHub 仓库<br>
                        参数: {"url": "https://github.com/owner/repo", "model": "deepseek-coder:6.7b"}
                    </div>
                </div>
                
                <h3>支持模型:</h3>
                <ul>
                    <li>🚀 DeepSeek Coder 6.7B (本地) - 编程专用</li>
                    <li>🧠 GPT 20B (本地) - 平衡的本地模型</li>
                    <li>💫 DeepSeek R1 8B (本地) - 推理优化</li>
                    <li>🦙 Llama 3.2 (本地) - 稳定通用</li>
                    <li>🔥 DeepSeek V3.1 671B (云) - 最强推理</li>
                    <li>💻 Qwen Coder 480B (云) - 编程专精</li>
                    <li>🧠 GPT OSS 120B (云) - 通用对话</li>
                    <li>🌐 GLM 4.6 (云) - 中文优秀</li>
                    <li>🌟 Kimi K2 (云) - 中文理解</li>
                </ul>
                
                <h3>浏览器扩展使用说明:</h3>
                <p>1. 确保浏览器扩展已安装</p>
                <p>2. 访问任意 GitHub 仓库页面</p>
                <p>3. 点击右下角的 <strong>🔍 Insight</strong> 按钮</p>
                <p>4. 在侧边栏中选择模型并点击"开始分析"</p>
            </div>
        </body>
    </html>
    '''

@app.route('/test', methods=['GET'])
def test_endpoint():
    """测试端点"""
    return jsonify({
        'message': '服务器连接正常',
        'service': 'code-insight',
        'proxy_configured': True,
        'ollama_endpoint': 'http://localhost:11434'
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 启动 Code Insight 服务器")
    print("📡 地址: http://127.0.0.1:5000")
    print("🔧 代理: Clash (127.0.0.1:7890)")
    print("🤖 AI引擎: Ollama (支持9个模型)")
    print("🎨 界面: 完整模型支持版本")
    print("=" * 60)
    
    try:
        app.run(host='127.0.0.1', port=5000, debug=True)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("可能的原因:")
        print("1. 端口5000已被占用")
        print("2. 防火墙阻止")
        print("3. 代理配置错误")
        input("按回车键退出...")