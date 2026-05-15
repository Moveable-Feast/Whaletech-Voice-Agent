import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voice_agent'))
from voice_agent.services.storage import save_visitor
from voice_agent.services.notify import send_notification

print("=" * 70)
print("添加访客记录")
print("=" * 70)
print()

# 访客数据
visitor_data = {
    "plate_number": "粤ARH123",
    "company": "鹰角网络",
    "phone": "18633550336",
    "purpose": "参观公司"
}

print("访客信息:")
print(f"  车牌: {visitor_data['plate_number']}")
print(f"  公司: {visitor_data['company']}")
print(f"  手机: {visitor_data['phone']}")
print(f"  事由: {visitor_data['purpose']}")
print()

# 保存到数据库
print("[1] 保存到数据库...")
try:
    save_visitor(visitor_data)
    print("    [OK] 数据库保存成功")
except Exception as e:
    print(f"    [ERROR] 保存失败: {e}")

print()

# 推送到微信
print("[2] 推送到微信...")
try:
    result = send_notification(visitor_data)
    notif_type = result.get('type')
    
    if notif_type == "wechat":
        wechat_result = result.get('result')
        print(f"    企业微信推送: {wechat_result.get('status')}")
        if wechat_result.get('status') == 'success':
            print("    [OK] 企业微信推送成功！")
        elif wechat_result.get('status') == 'skipped':
            print(f"    [WARN] 企业微信跳过: {wechat_result.get('reason')}")
    elif notif_type == "serverchan":
        serverchan_result = result.get('result')
        print(f"    Server酱推送: {serverchan_result.get('status')}")
        if serverchan_result.get('status') == 'success':
            print("    [OK] Server酱推送成功！请查收个人微信")
        elif serverchan_result.get('status') == 'skipped':
            print(f"    [WARN] Server酱跳过: {serverchan_result.get('reason')}")
    else:
        wechat_result = result.get('wechat_result')
        serverchan_result = result.get('serverchan_result')
        print(f"    企业微信: {wechat_result.get('status')}")
        print(f"    Server酱: {serverchan_result.get('status')}")
        print("    [WARN] 请配置企业微信或Server酱")
        print("    配置方法: 编辑 voice_agent/.env 文件")
    
except Exception as e:
    print(f"    [ERROR] 推送异常: {e}")

print()
print("=" * 70)
print("完成！")
print("=" * 70)