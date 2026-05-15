import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voice_agent'))

from voice_agent.services.llm_service import extract_visitor_info
from voice_agent.services.storage import save_visitor, get_visitor_history
from voice_agent.config.settings import settings
from voice_agent.services.notify import send_notification

print("=" * 70)
print("回访场景测试")
print("=" * 70)
print()

print("【步骤 1】先保存一条历史记录")
print("-" * 70)
record = {
    "plate_number": "京B88888",
    "company": "阿里巴巴",
    "phone": "13988888888",
    "purpose": "拜访",
    "visitor_name": "李师傅"
}
save_visitor(record)
print(f"✅ 已保存：{record['plate_number']} - {record['company']} - {record['purpose']}")
print()

print("【步骤 2】查询历史记录")
print("-" * 70)
history = get_visitor_history("京B88888")
print(f"历史记录：{history}")
print()

print("【步骤 3】模拟回访用户输入")
print("-" * 70)
test_input = "京B88888，还是去阿里巴巴"
print(f"用户说：{test_input}")

context = {
    "is_returning": True,
    "last_visit_days": f"{history.get('days_since')}天前",
    "last_purpose": history.get("purpose")
} if history else None

result = extract_visitor_info(test_input, context=context)
print(f"AI返回：{result}")
print()

print("=" * 70)
print("回访测试完成！")
print("=" * 70)
print()
print("提示：在实际电话场景中，系统会在检测到车牌后查询历史，")
print("      如果检测到是回访，会使用个性化的问候语。")