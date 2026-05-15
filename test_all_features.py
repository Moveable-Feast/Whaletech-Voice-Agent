import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voice_agent'))

print("=" * 70)
print("访客登记系统 - 功能验证")
print("=" * 70)
print()

from voice_agent.services.llm_service import extract_visitor_info
from voice_agent.services.storage import init_db, save_visitor
from voice_agent.services.notify import send_notification
import qrcode
import io

init_db()
print("[OK] 数据库初始化完成")
print()

print("【功能1】二维码生成测试")
print("-" * 50)
try:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data("http://localhost:8080")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    print("[OK] 二维码生成成功")
except Exception as e:
    print(f"[ERROR] 二维码生成失败: {e}")
print()

print("【功能2】信息提取测试")
print("-" * 50)

test_cases = [
    {"input": "浙AMS999", "expected": {"plate_number": "浙AMS999"}},
    {"input": "露帕股份有限公司技术测试", "expected": {"company": "露帕股份有限公司", "purpose": "技术测试"}},
    {"input": "18620250703", "expected": {"phone": "18620250703"}}
]

for test in test_cases:
    result = extract_visitor_info(test["input"])
    success = True
    for key, expected in test["expected"].items():
        if result.get(key) != expected:
            success = False
            break
    status = "✓" if success else "✗"
    print(f"{status} {test['input']}")

print()
print("【功能3】多轮对话测试")
print("-" * 50)

conversation_history = []
inputs = ["浙AMS999", "露帕股份有限公司技术测试", "18620250703"]

for user_input in inputs:
    conversation_history.append({"role": "user", "content": user_input})
    result = extract_visitor_info(user_input, conversation_history)
    
    print(f"用户: {user_input}")
    print(f"AI: {result.get('question', result.get('action'))}")
    
    if result.get("action") == "submit":
        visitor_data = {
            "plate_number": result.get("plate_number"),
            "company": result.get("company"),
            "phone": result.get("phone"),
            "purpose": result.get("purpose")
        }
        save_visitor(visitor_data)
        print("[OK] 登记完成，已保存")
        break
    conversation_history.append({"role": "assistant", "content": result.get("question")})
    print()

print()
print("=" * 70)
print("服务访问地址:")
print(f"  访客登记页面: http://localhost:8080")
print(f"  二维码展示页面: http://localhost:8080/api/qr/display")
print(f"  健康检查: http://localhost:8080/health")
print("=" * 70)
print()
print("💡 使用说明:")
print("  1. 在门卫处打开二维码页面打印或显示")
print("  2. 司机扫描二维码进入登记页面")
print("  3. 选择语音或文字模式进行登记")
print("  4. 完成后系统自动通知门卫")