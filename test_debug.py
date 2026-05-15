import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voice_agent'))

print("=" * 80)
print("访客登记系统 - 详细调试")
print("=" * 80)
print()

from voice_agent.services.llm_service import extract_visitor_info, chat_with_deepseek
from voice_agent.services.storage import init_db, save_visitor
import json

init_db()
print("[DEBUG] 数据库初始化完成")
print()

def debug_conversation():
    state = {
        'history': [],
        'plate_number': '',
        'company': '',
        'phone': '',
        'purpose': ''
    }
    
    test_cases = [
        {"input": "浙AMS999", "expected_plate": "浙AMS999"},
        {"input": "露帕股份有限公司", "expected_company": "露帕股份有限公司"},
        {"input": "技术测试", "expected_purpose": "技术测试"},
        {"input": "18620250703", "expected_phone": "18620250703"}
    ]
    
    for i, test in enumerate(test_cases, 1):
        user_input = test["input"]
        print(f"\n{'='*60}")
        print(f"第 {i} 轮对话")
        print(f"{'='*60}")
        print(f"用户输入: {user_input}")
        print(f"当前状态: {state}")
        
        state['history'].append({'role': 'user', 'content': user_input})
        
        current_context = {
            'plate_number': state['plate_number'],
            'company': state['company'],
            'phone': state['phone'],
            'purpose': state['purpose']
        }
        
        print(f"发送给LLM的上下文: {current_context}")
        print(f"对话历史长度: {len(state['history'])}")
        
        try:
            result = extract_visitor_info(user_input, state['history'], current_context)
            
            print(f"LLM原始响应类型: {type(result)}")
            print(f"LLM响应内容: {result}")
            
            if isinstance(result, dict):
                print(f"action字段: {result.get('action')}")
                print(f"question字段: {result.get('question')}")
                print(f"plate_number字段: {result.get('plate_number')}")
                print(f"company字段: {result.get('company')}")
                print(f"phone字段: {result.get('phone')}")
                print(f"purpose字段: {result.get('purpose')}")
                
                if result.get('plate_number') and not state['plate_number']:
                    state['plate_number'] = result['plate_number']
                    print(f"[UPDATE] 车牌号更新为: {state['plate_number']}")
                if result.get('company') and not state['company']:
                    state['company'] = result['company']
                    print(f"[UPDATE] 公司更新为: {state['company']}")
                if result.get('phone') and not state['phone']:
                    state['phone'] = result['phone']
                    print(f"[UPDATE] 电话更新为: {state['phone']}")
                if result.get('purpose') and not state['purpose']:
                    state['purpose'] = result['purpose']
                    print(f"[UPDATE] 事由更新为: {state['purpose']}")
                
                print(f"更新后的状态: {state}")
                
                if result.get('action') == 'submit':
                    print("[COMPLETE] 登记完成！")
                    return True
                else:
                    question = result.get('question', '请继续说')
                    print(f"AI回复: {question}")
                    state['history'].append({'role': 'assistant', 'content': question})
            else:
                print(f"[ERROR] LLM返回不是字典: {result}")
                print("[FALLBACK] 使用默认回复")
                
        except Exception as e:
            print(f"[EXCEPTION] 处理失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    return False

print("【测试1】正常多轮对话")
success = debug_conversation()

print("\n" + "="*80)
if success:
    print("测试通过！")
else:
    print("测试失败 - 需要进一步排查")
print("="*80)