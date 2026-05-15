import os
import sys

# 直接测试 Server 酱 API
serverchan_key = "SCT349574TOAVbUH9CwsKjE2yP3Ns13TMM"

print("=" * 70)
print("Server 酱直接测试")
print("=" * 70)
print()

print(f"使用的 Key: {serverchan_key}")
print()

import requests

try:
    print("发送测试消息...")
    response = requests.post(
        f"https://sctapi.ftqq.com/{serverchan_key}.send",
        data={"title": "测试消息", "desp": "这是一条来自访客登记系统的测试消息"},
        timeout=30
    )
    
    print(f"HTTP 状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"API 返回码: {result.get('code')}")
            print(f"API 消息: {result.get('message')}")
            
            if result.get("code") == 0:
                print("")
                print("[OK] Server 酱推送成功！请查收微信")
            else:
                print(f"[ERROR] Server 酱返回错误: {result.get('message')}")
        except Exception as e:
            print(f"[ERROR] 解析JSON失败: {e}")
            print(f"响应内容: {response.text}")
    else:
        print(f"[ERROR] HTTP 请求失败: {response.status_code}")
        
except requests.exceptions.RequestException as e:
    print(f"[ERROR] 请求异常: {str(e)}")

print()
print("=" * 70)