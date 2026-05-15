import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voice_agent'))

from voice_agent.services.llm_service import extract_visitor_info
from voice_agent.services.storage import save_visitor
from voice_agent.config.settings import settings

print("=" * 70)
print("自然对话效果测试 - 新访客场景")
print("=" * 70)
print()

print("【场景一】用户提供完整信息")
print("-" * 70)
test_input = "沪A12345，来蓝色鲸鱼科技送货，手机号13812345678"
print(f"用户说：{test_input}")

result = extract_visitor_info(test_input)
print(f"AI返回：{result}")
print()

if result.get("action") == "submit":
    print("✅ 成功：AI直接提交了信息，没有机械追问！")
    print(f"  - 车牌：{result.get('plate_number')}")
    print(f"  - 公司：{result.get('company')}")
    print(f"  - 手机：{result.get('phone')}")
    print(f"  - 事由：{result.get('purpose')}")
else:
    print(f"⚠️  AI返回了追问：{result.get('question')}")

print()
print("=" * 70)
print("【场景二】用户只提供部分信息（缺手机号）")
print("-" * 70)
test_input = "沪A12345，来蓝色鲸鱼科技送货"
print(f"用户说：{test_input}")

result = extract_visitor_info(test_input)
print(f"AI返回：{result}")
print()

if result.get("action") == "continue" and "手机" in result.get("question", ""):
    print("✅ 成功：AI只追问缺失的手机号，没有重复确认已有的信息！")
    print(f"  - 追问：{result.get('question')}")
elif result.get("action") == "submit":
    print("⚠️  AI直接提交了（如果不需要手机号也是可以的）")
else:
    print(f"⚠️  结果不符合预期")

print()
print("=" * 70)
print("【场景三】用户说得很简洁")
print("-" * 70)
test_input = "沪A12345 蓝色鲸鱼 13812345678"
print(f"用户说：{test_input}")

result = extract_visitor_info(test_input)
print(f"AI返回：{result}")
print()

if result.get("action") == "submit":
    print("✅ 成功：AI能识别简洁表述！")
else:
    print(f"⚠️  结果：{result}")

print()
print("=" * 70)
print("测试完成！")
print("=" * 70)