import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voice_agent'))

print("=" * 70)
print("智能对话测试 - 不同回答方式")
print("测试数据：浙AMS999 露帕股份有限公司 技术测试 18620250703")
print("=" * 70)
print()

from voice_agent.services.llm_service import extract_visitor_info
from voice_agent.services.storage import init_db, save_visitor
from voice_agent.services.notify import send_notification

init_db()
print("[OK] 数据库初始化完成")
print()

test_cases = [
    {
        "name": "完整信息（正常顺序）",
        "input": "浙AMS999，来露帕股份有限公司技术测试，手机号18620250703",
        "expected": {"action": "submit", "plate": "浙AMS999", "company": "露帕股份有限公司", "purpose": "技术测试", "phone": "18620250703"}
    },
    {
        "name": "完整信息（顺序混乱）",
        "input": "技术测试，露帕股份有限公司，浙AMS999，18620250703",
        "expected": {"action": "submit", "plate": "浙AMS999", "company": "露帕股份有限公司", "purpose": "技术测试", "phone": "18620250703"}
    },
    {
        "name": "只有车牌",
        "input": "浙AMS999",
        "expected": {"action": "continue", "contains": ["公司", "事儿"]}
    },
    {
        "name": "只有公司和事由",
        "input": "来露帕股份有限公司技术测试",
        "expected": {"action": "continue", "contains": ["车牌"]}
    },
    {
        "name": "只有事由",
        "input": "技术测试",
        "expected": {"action": "continue", "contains": ["车牌", "公司"]}
    },
    {
        "name": "车牌+公司（缺事由和手机）",
        "input": "浙AMS999，露帕股份有限公司",
        "expected": {"action": "continue", "contains": ["事儿"]}
    },
    {
        "name": "车牌+公司+事由（缺手机）",
        "input": "浙AMS999，露帕股份有限公司，技术测试",
        "expected": {"action": "continue", "contains": ["手机号"]}
    },
    {
        "name": "车牌+手机（缺公司和事由）",
        "input": "浙AMS999，手机号18620250703",
        "expected": {"action": "continue", "contains": ["公司", "事儿"]}
    },
    {
        "name": "简短表述",
        "input": "浙A MS999 露帕 技术测试",
        "expected": {"action": "continue", "contains": ["手机号"]}
    },
    {
        "name": "口语化表达",
        "input": "我是来技术测试的，车牌浙AMS999，去露帕股份",
        "expected": {"action": "continue", "contains": ["手机号"]}
    }
]

print("测试不同回答方式：")
print()

for i, test in enumerate(test_cases, 1):
    print("[{}] {}".format(i, test["name"]))
    print("-" * 50)
    print("用户输入: {}".format(test["input"]))
    
    result = extract_visitor_info(test["input"])
    print("AI输出: {}".format(result))
    
    if result.get("action") == "submit":
        plate_ok = result.get("plate_number") == test["expected"].get("plate")
        company_ok = test["expected"].get("company") in (result.get("company") or "")
        purpose_ok = test["expected"].get("purpose") in (result.get("purpose") or "")
        phone_ok = test["expected"].get("phone") == result.get("phone")
        
        print("验证结果:")
        print("  车牌识别: {}".format("正确" if plate_ok else "错误"))
        print("  公司识别: {}".format("正确" if company_ok else "错误"))
        print("  事由识别: {}".format("正确" if purpose_ok else "错误"))
        print("  手机识别: {}".format("正确" if phone_ok else "错误"))
        
        if plate_ok and company_ok:
            print("  [OK] 信息提取正确！")
            
            visitor_data = {
                "plate_number": result.get("plate_number"),
                "company": result.get("company"),
                "phone": result.get("phone") or "未提供",
                "purpose": result.get("purpose") or "未说明"
            }
            
            save_visitor(visitor_data)
            print("  [OK] 已保存到数据库")
            
            notify_result = send_notification(visitor_data)
            if notify_result.get("type") == "serverchan" and notify_result["result"]["status"] == "success":
                print("  [OK] 已推送微信通知")
            else:
                print("  [WARN] 微信推送未配置或失败")
        else:
            print("  [ERROR] 信息提取有误")
    
    elif result.get("action") == "continue":
        question = result.get("question", "")
        contains_expected = all(word in question for word in test["expected"].get("contains", []))
        print("追问内容: {}".format(question))
        print("验证结果: {}".format("[OK] 追问合理" if contains_expected else "[ERROR] 追问不正确"))
    
    print()

print("=" * 70)
print("多轮对话流程演示")
print("=" * 70)
print()

print("【场景】用户只回答部分信息")
print("-" * 50)
print("AI: 喂您好，这里是园区门卫，请说一下车牌号和去哪家公司，什么事儿？")
print("用户: 浙AMS999")

result1 = extract_visitor_info("浙AMS999")
print("AI: {}".format(result1.get("question")))

print("用户: 露帕股份有限公司技术测试")
result2 = extract_visitor_info("露帕股份有限公司技术测试")
print("AI: {}".format(result2.get("question")))

print("用户: 18620250703")
result3 = extract_visitor_info("18620250703", conversation_history=[
    {"role": "user", "content": "浙AMS999"},
    {"role": "assistant", "content": result1.get("question")},
    {"role": "user", "content": "露帕股份有限公司技术测试"},
    {"role": "assistant", "content": result2.get("question")}
])

if result3.get("action") == "submit":
    visitor_data = {
        "plate_number": result3.get("plate_number"),
        "company": result3.get("company"),
        "phone": result3.get("phone") or "未提供",
        "purpose": result3.get("purpose") or "未说明"
    }
    
    save_visitor(visitor_data)
    notify_result = send_notification(visitor_data)
    
    print("AI: 好的！{0}，{1}，{2}，已通知门卫抬杆，请慢走。".format(
        visitor_data["plate_number"],
        visitor_data["company"],
        visitor_data["purpose"]
    ))
    print("[OK] 多轮对话完成！")
    print("[OK] 已保存到数据库")
    if notify_result.get("type") == "serverchan" and notify_result["result"]["status"] == "success":
        print("[OK] 已推送微信通知，请查收")
else:
    print("AI: {}".format(result3.get("question")))

print()
print("=" * 70)
print("测试完成！")
print("=" * 70)