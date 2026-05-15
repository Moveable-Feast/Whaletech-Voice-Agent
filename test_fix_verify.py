import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voice_agent'))

print("=" * 80)
print("访客登记系统 - 修复后测试")
print("=" * 80)
print()

from voice_agent.services.llm_service import extract_visitor_info
from voice_agent.services.storage import init_db, save_visitor
import json

init_db()
print("[DEBUG] 数据库初始化完成")
print()

def simulate_conversation():
    state = {
        'history': [],
        'plate_number': '',
        'company': '',
        'phone': '',
        'purpose': '',
        'retry_count': 0,
        'last_question': ''
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
        print(f"当前状态: plate={state['plate_number']}, company={state['company']}, phone={state['phone']}, purpose={state['purpose']}")
        print(f"重试次数: {state['retry_count']}")
        
        state['history'].append({'role': 'user', 'content': user_input})
        
        current_context = {
            'plate_number': state['plate_number'],
            'company': state['company'],
            'phone': state['phone'],
            'purpose': state['purpose']
        }
        
        try:
            result = extract_visitor_info(user_input, state['history'], current_context)
            
            print(f"LLM响应: {result}")
            
            result_plate = result.get('plate_number')
            result_company = result.get('company')
            result_phone = result.get('phone')
            result_purpose = result.get('purpose')
            
            if result_plate and result_plate != 'None' and result_plate != 'none' and not state['plate_number']:
                state['plate_number'] = str(result_plate)
                print(f"[UPDATE] 车牌号: {state['plate_number']}")
            if result_company and result_company != 'None' and result_company != 'none' and not state['company']:
                state['company'] = str(result_company)
                print(f"[UPDATE] 公司: {state['company']}")
            if result_phone and result_phone != 'None' and result_phone != 'none' and not state['phone']:
                state['phone'] = str(result_phone)
                print(f"[UPDATE] 电话: {state['phone']}")
            if result_purpose and result_purpose != 'None' and result_purpose != 'none' and not state['purpose']:
                state['purpose'] = str(result_purpose)
                print(f"[UPDATE] 事由: {state['purpose']}")
            
            has_plate = state['plate_number'] != ''
            has_company = state['company'] != ''
            
            if result.get('action') == 'submit' or (has_plate and has_company):
                visitor_data = {
                    'plate_number': state['plate_number'] or '未提供',
                    'company': state['company'] or '未提供',
                    'phone': state['phone'] or '未提供',
                    'purpose': state['purpose'] or '未说明'
                }
                print(f"[COMPLETE] 登记完成! {visitor_data}")
                save_visitor(visitor_data)
                print("[OK] 已保存到数据库")
                return True
            else:
                question = result.get('question', '')
                
                if not question or question == 'None' or '请再说一遍' in question or '再说一遍' in question:
                    state['retry_count'] += 1
                    print(f"[RETRY] LLM返回无效回复，重试次数: {state['retry_count']}")
                    
                    if state['retry_count'] >= 2:
                        if not has_plate and not has_company:
                            question = '请问您的车牌号和要去的公司是？'
                        elif not has_plate:
                            question = '麻烦说一下车牌号好吗？'
                        elif not has_company:
                            question = '请问去哪家公司？'
                        elif not state['purpose']:
                            question = '请问有什么事吗？'
                        elif not state['phone']:
                            question = '方便留个手机号吗？'
                        else:
                            question = '好的，已登记完成'
                    else:
                        if state['last_question']:
                            question = state['last_question']
                        else:
                            if not has_plate and not has_company:
                                question = '喂您好，这里是园区门卫，请说一下车牌号和去哪家公司？'
                            elif not has_plate:
                                question = '请问车牌号是多少？'
                            elif not has_company:
                                question = '请问去哪家公司？'
                            elif not state['purpose']:
                                question = '请问有什么事吗？'
                            elif not state['phone']:
                                question = '方便留个手机号吗？'
                
                state['last_question'] = question
                print(f"AI回复: {question}")
                state['history'].append({'role': 'assistant', 'content': question})
                
        except Exception as e:
            print(f"[EXCEPTION] 处理失败: {str(e)}")
    
    return False

print("【测试1】多轮对话测试")
success = simulate_conversation()

print("\n" + "="*80)
if success:
    print("测试通过！")
else:
    print("测试失败")
print("="*80)