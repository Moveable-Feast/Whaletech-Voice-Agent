import sys
import os

# 修复编码问题
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voice_agent'))

print("=" * 70)
print("网页端语音访客登记系统 - 功能测试")
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

print("【测试场景】模拟网页端多轮对话")
print("-" * 50)

conversation = MockConversationState()

print("AI: 喂您好，这里是园区门卫，请说一下车牌号和去哪家公司，什么事儿？")

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
print("服务访问地址:")
print(f"  本地: http://localhost:8000")
print("=" * 70)
print("\n使用说明:")
print("  1. 确保服务已启动 (python voice_agent/app.py --port 8000)")
print("  2. 在手机上使用 Chrome 浏览器访问 http://localhost:8000")
print("  3. 点击「开始语音登记」按钮")
print("  4. 授权麦克风权限后开始对话")
print("  5. 测试完成后检查微信是否收到通知")