import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voice_agent'))

print("=" * 70)
print("访客登记系统 - 多轮对话测试（修复死循环）")
print("=" * 70)
print()

from voice_agent.services.llm_service import extract_visitor_info
from voice_agent.services.storage import init_db, save_visitor

init_db()
print("[OK] 数据库初始化完成")
print()

print("【测试场景】多轮对话 - 分步回答")
print("-" * 50)

state = {
    'history': [],
    'plate_number': '',
    'company': '',
    'phone': '',
    'purpose': ''
}

test_inputs = [
    "浙AMS999",
    "露帕股份有限公司技术测试",
    "18620250703"
]

for i, user_input in enumerate(test_inputs, 1):
    print(f"\n--- 第 {i} 轮 ---")
    print(f"用户: {user_input}")
    
    state['history'].append({'role': 'user', 'content': user_input})
    
    current_context = {
        'plate_number': state['plate_number'],
        'company': state['company'],
        'phone': state['phone'],
        'purpose': state['purpose']
    }
    
    result = extract_visitor_info(user_input, state['history'], current_context)
    
    print(f"LLM结果: {result}")
    
    if result.get('plate_number') and not state['plate_number']:
        state['plate_number'] = result['plate_number']
    if result.get('company') and not state['company']:
        state['company'] = result['company']
    if result.get('phone') and not state['phone']:
        state['phone'] = result['phone']
    if result.get('purpose') and not state['purpose']:
        state['purpose'] = result['purpose']
    
    if result.get('action') == 'submit':
        print(f"AI: 好的！{state['plate_number']}，{state['company']}，{state['purpose']}，已通知门卫抬杆，请慢走。")
        print("[OK] 登记完成！")
        
        visitor_data = {
            'plate_number': state['plate_number'],
            'company': state['company'],
            'phone': state['phone'],
            'purpose': state['purpose']
        }
        save_visitor(visitor_data)
        print("[OK] 已保存到数据库")
        break
    
    question = result.get('question', '请继续说')
    print(f"AI: {question}")
    state['history'].append({'role': 'assistant', 'content': question})
    
    print(f"当前状态: 车牌={state['plate_number']}, 公司={state['company']}, 电话={state['phone']}, 事由={state['purpose']}")

print()
print("=" * 70)
print("测试完成！")
print("=" * 70)