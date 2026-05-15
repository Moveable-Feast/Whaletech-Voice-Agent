import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voice_agent'))
from voice_agent.services.storage import save_visitor, get_visitor_history
from voice_agent.services.notify import send_notification

print("=" * 70)
print("完整流程测试")
print("=" * 70)
print()

# 测试数据
test_visitors = [
    {
        "plate_number": "皖C36888",
        "company": "库洛游戏",
        "phone": "13001140514",
        "purpose": "参观"
    },
    {
        "plate_number": "苏A99999",
        "company": "米哈游",
        "phone": "13999999999",
        "purpose": "业务洽谈"
    }
]

for i, visitor in enumerate(test_visitors, 1):
    print(f"--- 测试 {i}/{len(test_visitors)} ---")
    print()
    
    print("访客信息:")
    print(f"  车牌: {visitor['plate_number']}")
    print(f"  公司: {visitor['company']}")
    print(f"  手机: {visitor['phone']}")
    print(f"  事由: {visitor['purpose']}")
    print()

    # 保存到数据库
    print("[1] 保存到数据库...")
    try:
        save_visitor(visitor)
        print("    [OK] 数据库保存成功")
    except Exception as e:
        print(f"    [ERROR] 保存失败: {e}")
        print()
        continue

    print()

    # 推送到微信
    print("[2] 推送到微信...")
    try:
        result = send_notification(visitor)
        notif_type = result.get('type')
        
        if notif_type == "wechat":
            wechat_result = result.get('result')
            print(f"    企业微信推送: {wechat_result.get('status')}")
            if wechat_result.get('status') == 'success':
                print("    [OK] 企业微信推送成功！")
        elif notif_type == "serverchan":
            serverchan_result = result.get('result')
            print(f"    Server酱推送: {serverchan_result.get('status')}")
            if serverchan_result.get('status') == 'success':
                print("    [OK] Server酱推送成功！请查收个人微信")
        else:
            wechat_result = result.get('wechat_result')
            serverchan_result = result.get('serverchan_result')
            print(f"    企业微信: {wechat_result.get('status')}")
            print(f"    Server酱: {serverchan_result.get('status')}")
            print("    [WARN] 请配置企业微信或Server酱")
        
    except Exception as e:
        print(f"    [ERROR] 推送异常: {e}")
    
    print()
    
    # 查询验证
    print("[3] 验证数据库记录...")
    try:
        history = get_visitor_history(visitor['plate_number'])
        if history:
            print("    [OK] 查询成功:")
            print(f"      公司: {history['company']}")
            print(f"      事由: {history['purpose']}")
            print(f"      手机: {history['phone']}")
            print(f"      上次访问: {history['days_since']}天前")
        else:
            print("    [ERROR] 未找到记录")
    except Exception as e:
        print(f"    [ERROR] 查询失败: {e}")
    
    print()
    print()

print("=" * 70)
print("测试完成！")
print("=" * 70)
print()
print("请运行 'python select_visitors.py' 查看所有记录")