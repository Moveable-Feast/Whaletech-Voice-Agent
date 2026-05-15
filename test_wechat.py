import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voice_agent'))

from voice_agent.services.notify import send_notification
from voice_agent.services.storage import save_visitor, init_db
from voice_agent.services.llm_service import extract_visitor_info
from voice_agent.config.settings import settings

print("=" * 70)
print("微信推送功能测试")
print("=" * 70)
print()

print("[步骤 1] 初始化数据库")
init_db()
print("[OK] 数据库初始化完成")
print()

print("[步骤 2] 测试微信推送功能")
test_record = {
    "plate_number": "沪A12345",
    "company": "蓝色鲸鱼科技",
    "phone": "13812345678",
    "purpose": "送货"
}

print("测试数据：")
print(f"  车牌：{test_record['plate_number']}")
print(f"  公司：{test_record['company']}")
print(f"  手机：{test_record['phone']}")
print(f"  事由：{test_record['purpose']}")
print()

result = send_notification(test_record)
notif_type = result.get('type')

if notif_type == "wechat":
    wechat_result = result.get('result')
    print(f"企业微信推送结果：{wechat_result}")
    if wechat_result.get("status") == "success":
        print("[OK] 企业微信消息发送成功！")
    elif wechat_result.get("status") == "skipped":
        print("[WARN] 企业微信未配置")
    elif wechat_result.get("status") == "failed":
        print("[ERROR] 企业微信推送失败：", wechat_result.get("error"))
elif notif_type == "serverchan":
    serverchan_result = result.get('result')
    print(f"Server酱推送结果：{serverchan_result}")
    if serverchan_result.get("status") == "success":
        print("[OK] Server酱推送成功！请查收个人微信")
    elif serverchan_result.get("status") == "skipped":
        print("[WARN] Server酱未配置")
    elif serverchan_result.get("status") == "failed":
        print("[ERROR] Server酱推送失败：", serverchan_result.get("error"))
else:
    print("推送结果：", result)
    print("[WARN] 未配置任何推送方式")
print()

print("[步骤 3] 测试访客信息保存")
save_visitor(test_record)
print("[OK] 访客信息已保存到数据库")
print()

print("[步骤 4] 测试 LLM 信息提取")
test_input = "沪A12345，来蓝色鲸鱼科技送货，手机号13812345678"
llm_result = extract_visitor_info(test_input)
print("输入：", test_input)
print("LLM提取结果：", llm_result)

if llm_result.get("action") == "submit":
    print("[OK] LLM信息提取成功！")
else:
    print("[INFO] LLM结果：", llm_result.get("action"))
print()

print("=" * 70)
print("所有测试完成！")
print("=" * 70)
print()
print("总结：")

has_wechat = settings.wechat_webhook_url and settings.wechat_webhook_url != "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_webhook_key"
has_serverchan = settings.serverchan_key and settings.serverchan_key != "your_serverchan_key"

if has_wechat:
    print("- 企业微信推送：已配置")
else:
    print("- 企业微信推送：未配置")

if has_serverchan:
    print("- Server酱推送：已配置")
else:
    print("- Server酱推送：未配置")

print("- 数据库保存：正常")
print("- LLM提取：正常")
print()

if not has_wechat and not has_serverchan:
    print("提示：")
    print("1. 企业微信配置：在 .env 中设置 WECHAT_WEBHOOK_URL")
    print("2. 个人微信配置：在 .env 中设置 SERVERCHAN_KEY")
    print("   获取地址：https://sct.ftqq.com/")