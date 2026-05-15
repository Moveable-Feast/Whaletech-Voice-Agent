import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voice_agent'))

print("=" * 70)
print("网页端访客登记系统 - 文字模式测试")
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
            "history": []
        }
    
    def update_from_result(self, result):
        if result.get("plate_number"):
            self.state["plate_number"] = result["plate_number"]
        if result.get("company"):
            self.state["company"] = result["company"]
        if result.get("phone"):
            self.state["phone"] = result["phone"]
        if result.get("purpose"):
            self.state["purpose"] = result["purpose"]
        return self.state

print("【测试场景】文字输入模式 - 多轮对话")
print("-" * 50)

conversation = MockConversationState()

print("AI: 您好！我是园区门卫AI助手，请告诉我您的车牌号、来访单位和事由。")

user_inputs = [
    "浙AMS999",
    "露帕股份有限公司技术测试",
    "18620250703"
]

for user_input in user_inputs:
    print(f"\n用户: {user_input}")
    conversation.state["history"].append({"role": "user", "content": user_input})
    
    result = extract_visitor_info(user_input, conversation.state["history"])
    conversation.update_from_result(result)
    
    if result.get("action") == "submit":
        visitor_data = {
            "plate_number": result.get("plate_number", conversation.state["plate_number"]),
            "company": result.get("company", conversation.state["company"]),
            "phone": result.get("phone", conversation.state["phone"]),
            "purpose": result.get("purpose", conversation.state["purpose"])
        }
        
        save_visitor(visitor_data)
        print("[OK] 已保存到数据库")
        
        notify_result = send_notification(visitor_data)
        
        response_text = f"好的！{visitor_data['plate_number']}，{visitor_data['company']}，{visitor_data['purpose']}，已通知门卫抬杆，请慢走。"
        print(f"AI: {response_text}")
        print("[OK] 对话完成！")
        
        if notify_result.get("type") == "serverchan" and notify_result["result"]["status"] == "success":
            print("[OK] 微信通知已发送")
        else:
            print("[INFO] 微信通知状态:", notify_result)
        
        print("\n最终登记信息:")
        print(f"  车牌号: {visitor_data['plate_number']}")
        print(f"  来访单位: {visitor_data['company']}")
        print(f"  联系电话: {visitor_data['phone']}")
        print(f"  来访事由: {visitor_data['purpose']}")
        break
    else:
        print(f"AI: {result.get('question')}")
        conversation.state["history"].append({"role": "assistant", "content": result.get("question")})

print()
print("=" * 70)
print("功能说明:")
print("-" * 50)
print("1. 语音对话模式: 通过麦克风与AI语音对话")
print("2. 文字输入模式: 通过键盘输入文字与AI对话")
print("3. 两种模式共用同一套AI逻辑，支持多轮对话")
print("4. 自动提取车牌号、公司、事由、手机号")
print("5. 智能追问缺失信息")
print("6. 完成后自动保存并推送微信通知")
print("=" * 70)
print()
print("服务访问地址: http://localhost:8000")