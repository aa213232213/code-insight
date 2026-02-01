import requests
import json
import time

def test_complete_workflow():
    print("🚀 最终完整工作流测试")
    print("=" * 50)
    
    # 测试仓库列表
    test_repos = [
        "https://github.com/torvalds/linux",
        "https://github.com/microsoft/vscode", 
        "https://github.com/facebook/react"
    ]
    
    for i, repo_url in enumerate(test_repos[:1], 1):
        print(f"\n📦 测试 {i}/1: {repo_url}")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                'http://127.0.0.1:5000/analyze',
                json={'url': repo_url},
                timeout=120  # 2分钟超时
            )
            
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                if result['success']:
                    print(f"✅ 分析成功! (耗时: {elapsed_time:.1f}秒)")
                    print(f"   仓库: {result['data']['repo_name']}")
                    print(f"   代码文件: {result['data']['file_count']} 个")
                    
                    # 显示分析结果
                    analysis = result['data']['analysis']
                    print(f"   分析结果: {len(analysis)} 字符")
                    print("\n" + "="*30 + " 分析内容 " + "="*30)
                    print(analysis)
                    print("="*70)
                    
                else:
                    print(f"❌ 分析失败: {result['error']}")
                    
            else:
                print(f"❌ HTTP 错误: {response.status_code}")
                print(f"   响应: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ 请求超时 (超过 120 秒)")
        except Exception as e:
            print(f"💥 意外错误: {e}")

if __name__ == "__main__":
    test_complete_workflow()
    print("\n🎯 测试完成!")
    input("按回车键退出...")