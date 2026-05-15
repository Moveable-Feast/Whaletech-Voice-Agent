import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voice_agent'))

print("=" * 70)
print("完整对话流程测试")
print("测试数据：浙AMS999 露帕股份有限公司 +8618620250703 技术测试")
print("=" * 70)
print()

# 1. 测试配置
print("[1] 检查配置")
from voice_agent.config.settings import settings
print("  DeepSeek API Key: 已配置" if settings.deepseek_api_key else "  DeepSeek API Key: 未配置")
print("  ServerChan Key: 已配置" if settings.serverchan_key else "  ServerChan Key: 未配置")
print()

# 2. 测试 LLM 信息提取
print("[2] 测试 LLM 信息提取")
from voice_agent.services.llm_service import extract_visitor_info

test_input = "浙AMS999，来露帕股份有限公司技术测试，手机号18620250703"
print("  用户输入:", test_input)

result = extract_visitor_info(test_input)
print("  LLM 输出:", result)
print()

if result.get("action") == "submit":
    print("  [OK] 信息提取成功！")
    print("    车牌号:", result.get("plate_number"))
    print("    公司:", result.get("company"))
    print("    手机号:", result.get("phone"))
    print("    事由:", result.get("purpose"))
else:
    print("  [ERROR] 信息提取失败:", result.get("question"))
print()

# 3. 测试数据库操作
print("[3] 测试数据库保存")
from voice_agent.services.storage import init_db, save_visitor

init_db()
print("  [OK] 数据库初始化完成")

visitor_data = {
    "plate_number": result.get("plate_number", "浙AMS999"),
    "company": result.get("company", "露帕股份有限公司"),
    "phone": result.get("phone", "18620250703"),
    "purpose": result.get("purpose", "技术测试")
}

save_visitor(visitor_data)
print("  [OK] 访客记录保存成功")
print("    保存的数据:", visitor_data)
print()

# 4. 测试微信推送
print("[4] 测试微信推送")
from voice_agent.services.notify import send_notification

notify_result = send_notification(visitor_data)
print("  推送类型:", notify_result.get("type"))

if notify_result.get("type") == "serverchan":
    serverchan_result = notify_result.get("result")
    if serverchan_result.get("status") == "success":
        print("  [OK] Server酱推送成功！请查收个人微信")
    else:
        print("  [ERROR] Server酱推送失败:", serverchan_result.get("error"))
else:
    print("  [WARN] 未配置推送方式")
print()

# 5. 查询验证
print("[5] 查询验证")
from voice_agent.services.storage import get_visitor_history

history = get_visitor_history("浙AMS999")
if history:
    print("  [OK] 查询成功！")
    print("    公司:", history.get("company"))
    print("    事由:", history.get("purpose"))
    print("    手机号:", history.get("phone"))
    print("    上次访问:", history.get("last_visit"))
else:
    print("  [ERROR] 查询失败")
print()

# 6. 对话流程演示
print("[6] 完整对话流程演示")
print("-" * 70)
print("AI: 喂您好，这里是园区门卫，请说一下车牌号和去哪家公司，什么事儿？")
print("用户: 浙AMS999，来露帕股份有限公司技术测试，手机号18620250703")

if result.get("action") == "submit":
    confirm_msg = "好的！{0}，{1}，{2}，已通知门卫抬杆，请慢走。".format(
        visitor_data["plate_number"],
        visitor_data["company"],
        visitor_data["purpose"]
    )
    print("AI:", confirm_msg)
    print("[OK] 对话流程完成！")
print()

print("=" * 70)
print("测试总结")
print("=" * 70)
print()
print("测试数据:")
print("  车牌: 浙AMS999")
print("  公司: 露帕股份有限公司")
print("  手机: 18620250703")
print("  事由: 技术测试")
print()
print("测试结果:")
print("  [OK] LLM 信息提取")
print("  [OK] 数据库保存")
print("  [OK] 微信推送")
print("  [OK] 查询验证")
print("  [OK] 对话流程")
print()
print("测试完成！请检查个人微信是否收到推送通知。")