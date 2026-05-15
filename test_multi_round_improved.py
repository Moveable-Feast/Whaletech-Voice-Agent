import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voice_agent'))

print("=" * 70)
print("智能多轮对话测试")
print("测试数据：浙AMS999 露帕股份有限公司 技术测试 18620250703")
print("=" * 70)
print()

from voice_agent.services.llm_service import extract_visitor_info
from voice_agent.services.storage import init_db, save_visitor
from voice_agent.services.notify import send_notification

init_db()
print("[OK] 数据库初始化完成")
print()

class MockConversationState:
    def __init__(self):
        self.state = {
            "plate_number": "",
            "company": "",
            "phone": "",
            "purpose": "",
            "history": [],
            "is_returning": False,
            "returning_context": None,
            "question_count": 0
        }
    
    def update_from_result(self, result):
        extracted_plate = result.get("plate_number", "")
        extracted_company = result.get("company", "")
        extracted_phone = result.get("phone", "")
        extracted_purpose = result.get("purpose", "")
        
        if extracted_plate:
            self.state["plate_number"] = extracted_plate
        if extracted_company:
            self.state["company"] = extracted_company
        if extracted_phone:
            self.state["phone"] = extracted_phone
        if extracted_purpose:
            self.state["purpose"] = extracted_purpose
        
        return self.state

print("【测试场景】多轮对话 - 用户分步回答")
print("-" * 50)

conversation = MockConversationState()

print("AI: 喂您好，这里是园区门卫，请说一下车牌号和去哪家公司，什么事儿？")
user_input = "浙AMS999"
print("用户:", user_input)

conversation.state["history"].append({"role": "user", "content": user_input})
result = extract_visitor_info(user_input, conversation.state["history"])
conversation.update_from_result(result)

print("AI:", result.get("question"))
print()

print("用户: 露帕股份有限公司技术测试")
conversation.state["history"].append({"role": "user", "content": "露帕股份有限公司技术测试"})
result = extract_visitor_info("露帕股份有限公司技术测试", conversation.state["history"])
conversation.update_from_result(result)

print("AI:", result.get("question"))
print()

print("用户: 18620250703")
conversation.state["history"].append({"role": "user", "content": "18620250703"})
result = extract_visitor_info("18620250703", conversation.state["history"])
conversation.update_from_result(result)

if result.get("action") == "submit":
    visitor_data = {
        "plate_number": result.get("plate_number", conversation.state["plate_number"]) or conversation.state["plate_number"],
        "company": result.get("company", conversation.state["company"]) or conversation.state["company"],
        "phone": result.get("phone", conversation.state["phone"]) or conversation.state["phone"] or "未提供",
        "purpose": result.get("purpose", conversation.state["purpose"]) or conversation.state["purpose"] or "未说明"
    }
    
    save_visitor(visitor_data)
    print("[OK] 已保存到数据库")
    
    notify_result = send_notification(visitor_data)
    
    print("AI: 好的！{0}，{1}，{2}，已通知门卫抬杆，请慢走。".format(
        visitor_data["plate_number"],
        visitor_data["company"],
        visitor_data["purpose"]
    ))
    print("[OK] 多轮对话完成！")
    print("最终数据:", visitor_data)
    
    if notify_result.get("type") == "serverchan" and notify_result["result"]["status"] == "success":
        print("[OK] 已推送微信通知，请查收个人微信")
    else:
        print("[WARN] 微信推送未配置或失败")
else:
    print("AI:", result.get("question"))
    print("[ERROR] 对话未完成")

print()
print("=" * 70)
print("测试完成！")
print("=" * 70)