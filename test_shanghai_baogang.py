import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voice_agent'))

print("=" * 80)
print("完整对话场景测试 - 上海宝钢案例")
print("=" * 80)
print()

from voice_agent.services.llm_service import extract_visitor_info
from voice_agent.services.rule_engine import rule_based_extract
from voice_agent.services.storage import init_db, save_visitor

init_db()

print("【模拟对话流程】")
print("-" * 50)

conversation = [
    "你好，我是来送货的",
    "我是去上海宝钢",
    "上海宝钢有限公司，苏A12345",
    "13011111111"
]

state = {
    'history': [],
    'plate_number': '',
    'company': '',
    'phone': '',
    'purpose': '',
    'retry_count': 0,
    'last_question': ''
}

print("AI: 您好！我是园区门卫AI助手，请告诉我您的车牌号、来访单位和事由。")

for i, user_input in enumerate(conversation, 1):
    print(f"\n用户: {user_input}")
    
    state['history'].append({'role': 'user', 'content': user_input})
    
    current_context = {
        'plate_number': state['plate_number'],
        'company': state['company'],
        'phone': state['phone'],
        'purpose': state['purpose']
    }
    
    llm_result = extract_visitor_info(user_input, state['history'], current_context)
    
    llm_plate = llm_result.get('plate_number')
    llm_company = llm_result.get('company')
    llm_phone = llm_result.get('phone')
    llm_purpose = llm_result.get('purpose')
    
    if llm_plate and llm_plate != 'None' and llm_plate != 'none' and not state['plate_number']:
        state['plate_number'] = str(llm_plate).strip()
        print(f"[LLM] 提取车牌: {state['plate_number']}")
    
    if llm_company and llm_company != 'None' and llm_company != 'none' and not state['company']:
        state['company'] = str(llm_company).strip()
        print(f"[LLM] 提取公司: {state['company']}")
    
    if llm_phone and llm_phone != 'None' and llm_phone != 'none' and not state['phone']:
        state['phone'] = ''.join(filter(str.isdigit, str(llm_phone)))
        print(f"[LLM] 提取电话: {state['phone']}")
    
    if llm_purpose and llm_purpose != 'None' and llm_purpose != 'none' and not state['purpose']:
        state['purpose'] = str(llm_purpose).strip()
        print(f"[LLM] 提取事由: {state['purpose']}")
    
    rule_result = rule_based_extract(user_input)
    
    if rule_result['plate_number'] and not state['plate_number']:
        state['plate_number'] = rule_result['plate_number']
        print(f"[RULE] 规则引擎提取车牌: {state['plate_number']}")
    
    if rule_result['company'] and not state['company']:
        state['company'] = rule_result['company']
        print(f"[RULE] 规则引擎提取公司: {state['company']}")
    
    if rule_result['phone'] and not state['phone']:
        state['phone'] = rule_result['phone']
        print(f"[RULE] 规则引擎提取电话: {state['phone']}")
    
    if rule_result['purpose'] and not state['purpose']:
        state['purpose'] = rule_result['purpose']
        print(f"[RULE] 规则引擎提取事由: {state['purpose']}")
    
    has_plate = state['plate_number'] != ''
    has_company = state['company'] != ''
    has_phone = state['phone'] != ''
    has_purpose = state['purpose'] != ''
    
    if llm_result.get('action') == 'submit' or (has_plate and has_company and has_purpose and has_phone):
        visitor_data = {
            'plate_number': state['plate_number'] or '未提供',
            'company': state['company'] or '未提供',
            'phone': state['phone'] or '未提供',
            'purpose': state['purpose'] or '未说明'
        }
        print(f"\n[COMPLETE] 登记完成!")
        print(f"AI: 好的！{visitor_data['plate_number']}，{visitor_data['company']}，{visitor_data['purpose']}，已通知门卫抬杆，请慢走。")
        save_visitor(visitor_data)
        print("[OK] 已保存到数据库")
        break
    
    elif has_plate and has_company and has_purpose and not has_phone:
        question = '收到，手机号方便留一下吗？'
        print(f"AI: {question}")
        state['history'].append({'role': 'assistant', 'content': question})
        continue
    
    question = llm_result.get('question', '')
    llm_failed = not question or question == 'None' or '请再说一遍' in question or '再说一遍' in question
    
    if llm_failed:
        state['retry_count'] += 1
        
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
    print(f"AI: {question}")
    state['history'].append({'role': 'assistant', 'content': question})

print("\n" + "="*80)
print("最终登记信息:")
print(f"  车牌号: {state['plate_number']}")
print(f"  公司: {state['company']}")
print(f"  电话: {state['phone']}")
print(f"  事由: {state['purpose']}")
print("="*80)