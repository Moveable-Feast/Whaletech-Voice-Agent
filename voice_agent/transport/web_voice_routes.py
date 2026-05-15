"""
网页端语音交互路由
使用浏览器Web Speech API，无需电话号码
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse
from services.llm_service import extract_visitor_info
from services.rule_engine import rule_based_extract, validate_plate, validate_phone
from services.storage import save_visitor, init_db
from services.notify import send_notification
import os

router = APIRouter(prefix="", tags=["web_voice"])

# 对话状态存储（使用客户端IP作为会话标识）
conversation_states = {}

@router.get("/", response_class=HTMLResponse)
async def get_voice_page():
    """返回语音登记页面"""
    html_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'index.html')
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return "<h1>页面未找到</h1>"

@router.get("/test_speech", response_class=HTMLResponse)
async def get_test_speech_page():
    """返回语音识别测试页面"""
    html_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'test_speech.html')
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return "<h1>测试页面未找到</h1>"

@router.post("/api/voice/chat")
async def handle_voice_chat(request: Request):
    """
    处理网页端语音对话
    """
    try:
        data = await request.json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return {
                'success': True,
                'response': '抱歉，我没有听清，请再说一遍好吗？',
                'complete': False
            }
        
        client_host = request.client.host if request.client else 'unknown'
        session_id = client_host
        
        if session_id not in conversation_states:
            conversation_states[session_id] = {
                'history': [],
                'plate_number': '',
                'company': '',
                'phone': '',
                'purpose': '',
                'retry_count': 0,
                'last_question': ''
            }
        
        state = conversation_states[session_id]
        
        state['history'].append({'role': 'user', 'content': user_message})
        
        current_context = {
            'plate_number': state['plate_number'],
            'company': state['company'],
            'phone': state['phone'],
            'purpose': state['purpose']
        }
        
        result = extract_visitor_info(user_message, state['history'], current_context)
        
        result_plate = result.get('plate_number')
        result_company = result.get('company')
        result_phone = result.get('phone')
        result_purpose = result.get('purpose')
        
        if result_plate and result_plate != 'None' and result_plate != 'none' and not state['plate_number']:
            plate_str = str(result_plate).strip()
            if validate_plate(plate_str) or len(plate_str) >= 7:
                state['plate_number'] = plate_str
        
        if result_company and result_company != 'None' and result_company != 'none' and not state['company']:
            company_str = str(result_company).strip()
            if len(company_str) >= 2:
                state['company'] = company_str
        
        if result_phone and result_phone != 'None' and result_phone != 'none' and not state['phone']:
            phone_str = str(result_phone).strip()
            phone_str = ''.join(filter(str.isdigit, phone_str))
            if validate_phone(phone_str) or len(phone_str) == 11:
                state['phone'] = phone_str
        
        if result_purpose and result_purpose != 'None' and result_purpose != 'none' and not state['purpose']:
            purpose_str = str(result_purpose).strip()
            if len(purpose_str) >= 1:
                state['purpose'] = purpose_str
        
        rule_result = rule_based_extract(user_message)
        
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
        
        if result.get('action') == 'submit' or (has_plate and has_company and has_purpose and has_phone):
            visitor_data = {
                'plate_number': state['plate_number'] or '未提供',
                'company': state['company'] or '未提供',
                'phone': state['phone'] or '未提供',
                'purpose': state['purpose'] or '未说明'
            }
            
            init_db()
            save_visitor(visitor_data)
            
            notify_result = send_notification(visitor_data)
            print(f"通知结果: {notify_result}")
            
            del conversation_states[session_id]
            
            response_text = f"好的！{visitor_data['plate_number']}，{visitor_data['company']}，{visitor_data['purpose']}，已通知门卫抬杆，请慢走。"
            
            return {
                'success': True,
                'response': response_text,
                'complete': True,
                'data': visitor_data
            }
        elif has_plate and has_company and has_purpose and not has_phone:
            question = '收到，手机号方便留一下吗？'
            state['last_question'] = question
            state['history'].append({'role': 'assistant', 'content': question})
            
            return {
                'success': True,
                'response': question,
                'complete': False
            }
        else:
            question = result.get('question', '')
            
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
                    elif not has_purpose:
                        question = '请问有什么事吗？'
                    elif not has_phone:
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
                        elif not has_purpose:
                            question = '请问有什么事吗？'
                        elif not has_phone:
                            question = '方便留个手机号吗？'
            
            state['last_question'] = question
            state['history'].append({'role': 'assistant', 'content': question})
            
            return {
                'success': True,
                'response': question,
                'complete': False,
                'data': {
                    'plate_number': state['plate_number'],
                    'company': state['company'],
                    'phone': state['phone'],
                    'purpose': state['purpose']
                }
            }
    
    except Exception as e:
        print(f"对话处理错误: {str(e)}")
        return {
            'success': False,
            'response': f'抱歉，处理出错了: {str(e)}',
            'complete': False
        }

@router.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "service": "voice-gate-registration"}