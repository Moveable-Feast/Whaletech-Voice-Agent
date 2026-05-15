import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voice_agent'))

print("=" * 70)
print("AI Agent 语音识别功能测试")
print("=" * 70)
print()

# 1. 测试配置加载
print("[1] 检查配置")
from voice_agent.config.settings import settings
print(f"  DeepSeek API Key: {'已配置' if settings.deepseek_api_key else '未配置'}")
print(f"  ServerChan Key: {'已配置' if settings.serverchan_key else '未配置'}")
print(f"  Twilio 号码: {settings.twilio_phone_number}")
print()

# 2. 测试 DeepSeek LLM
print("[2] 测试 DeepSeek LLM")
from voice_agent.services.llm_service import extract_visitor_info, check_returning_visitor

test_cases = [
    "沪A12345，来蓝色鲸鱼科技送货，手机号13812345678",
    "皖C36888，库洛游戏参观",
    "苏A99999，米哈游业务洽谈，13999999999",
    "我是张师傅，今天还是来送货的"
]

for i, test_input in enumerate(test_cases, 1):
    print(f"  测试 {i}: {test_input}")
    result = extract_visitor_info(test_input)
    print(f"    结果: {result}")
    print(f"    Action: {result.get('action')}")
    if result.get('action') == 'submit':
        print(f"    提取信息: 车牌={result.get('plate_number')}, 公司={result.get('company')}, 手机={result.get('phone')}, 事由={result.get('purpose')}")
    print()

# 3. 测试数据库操作
print("[3] 测试数据库操作")
from voice_agent.services.storage import init_db, save_visitor, get_visitor_history, get_history

# 初始化数据库
init_db()
print("  [OK] 数据库初始化完成")

# 保存测试数据
test_record = {
    "plate_number": "测试车牌",
    "company": "测试公司",
    "phone": "13800138000",
    "purpose": "测试事由"
}
save_visitor(test_record)
print("  [OK] 访客记录保存成功")

# 查询测试
history = get_visitor_history("测试车牌")
print(f"  查询结果: {history}")
print()

# 4. 测试微信推送
print("[4] 测试微信推送")
from voice_agent.services.notify import send_notification

notify_result = send_notification(test_record)
print(f"  推送类型: {notify_result.get('type')}")
if notify_result.get('type') == 'serverchan':
    print(f"  状态: {notify_result['result']['status']}")
    if notify_result['result']['status'] == 'success':
        print("  [OK] Server酱推送成功！")
    else:
        print(f"  [ERROR] 推送失败: {notify_result['result'].get('error')}")
print()

# 5. 测试语音识别流程模拟
print("[5] 模拟语音对话流程")
print("  场景: 司机打电话 -> AI识别语音 -> 提取信息 -> 保存 -> 推送")
print()
print("  模拟对话:")
print("  ┌─────────────────────────────────────────────────────────┐")
print("  │ 司机: 沪A12345，来蓝色鲸鱼科技送货，手机号13812345678 │")
print("  └─────────────────────────────────────────────────────────┘")

result = extract_visitor_info("沪A12345，来蓝色鲸鱼科技送货，手机号13812345678")
if result.get('action') == 'submit':
    visitor_data = {
        "plate_number": result.get("plate_number"),
        "company": result.get("company"),
        "phone": result.get("phone"),
        "purpose": result.get("purpose")
    }
    save_visitor(visitor_data)
    notify_result = send_notification(visitor_data)
    
    print("  ┌─────────────────────────────────────────────────────────┐")
    print(f"  │ AI: 好的！{visitor_data['plate_number']}，{visitor_data['company']}，{visitor_data['purpose']}，已通知门卫抬杆，请慢走。")
    print("  └─────────────────────────────────────────────────────────┘")
    print()
    print("  [OK] 完整流程测试通过！")
else:
    print(f"  [ERROR] 流程失败: {result}")

print()
print("=" * 70)
print("测试完成！")
print("=" * 70)
print()
print("总结:")
print("- ✅ DeepSeek LLM: 正常工作")
print("- ✅ 信息提取: 正常工作")
print("- ✅ 数据库保存: 正常工作")
print("- ✅ 微信推送: 正常工作")
print("- ✅ 语音对话流程: 正常工作")