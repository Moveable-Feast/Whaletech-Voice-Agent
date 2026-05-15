import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voice_agent'))

# 先检查配置
from voice_agent.config.settings import settings

print("=" * 70)
print("Server 酱推送诊断")
print("=" * 70)
print()

# 检查配置
print("[1] 检查配置")
print(f"  SERVERCHAN_KEY 配置: {'已配置' if settings.serverchan_key and settings.serverchan_key != 'your_serverchan_key' else '未配置'}")
print(f"  Key 值: {settings.serverchan_key[:10]}...{settings.serverchan_key[-10:] if settings.serverchan_key else ''}")
print()

# 测试 Server 酱 API
print("[2] 测试 Server 酱 API")
import requests

test_key = settings.serverchan_key
if not test_key or test_key == 'your_serverchan_key':
    print("  [ERROR] ServerChan Key 未配置")
    sys.exit(1)

try:
    # 发送测试消息
    response = requests.post(
        f"https://sctapi.ftqq.com/{test_key}.send",
        data={"title": "测试消息", "desp": "这是一条来自访客登记系统的测试消息"},
        timeout=30
    )
    
    print(f"  HTTP 状态码: {response.status_code}")
    print(f"  响应内容: {response.text}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"  API 返回码: {result.get('code')}")
            print(f"  API 消息: {result.get('message')}")
            
            if result.get("code") == 0:
                print("  [OK] Server 酱推送成功！请查收微信")
            else:
                print("  [ERROR] Server 酱返回错误: ", result.get('message'))
        except:
            print("  [ERROR] 响应不是有效的 JSON")
    else:
        print(f"  [ERROR] HTTP 请求失败: {response.status_code}")
        
except requests.exceptions.RequestException as e:
    print(f"  [ERROR] 请求异常: {str(e)}")

print()
print("=" * 70)
print("诊断完成！")
print("=" * 70)