from services.storage import save_visitor, check_return_visitor
from services.notify import send_wechat_notification
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

visitor_tool_schema = {
    "type": "function",
    "name": "submit_visitor_info",
    "description": "提交访客登记信息，包括车牌号、来访单位、手机号和来访事由",
    "parameters": {
        "type": "object",
        "properties": {
            "plate_number": {
                "type": "string",
                "description": "车牌号，如'沪A12345'"
            },
            "company_name": {
                "type": "string",
                "description": "来访单位名称，如'蓝色鲸鱼科技'"
            },
            "phone_number": {
                "type": "string",
                "description": "手机号码，如'13812345678'"
            },
            "purpose": {
                "type": "string",
                "description": "来访事由，如'送货'、'拜访'、'面试'"
            }
        },
        "required": ["plate_number", "company_name", "phone_number", "purpose"]
    }
}

def submit_visitor_info(arguments: dict) -> str:
    try:
        plate_number = arguments.get("plate_number", "").strip()
        company_name = arguments.get("company_name", "").strip()
        phone_number = arguments.get("phone_number", "").strip()
        purpose = arguments.get("purpose", "").strip()
        
        if not all([plate_number, company_name, phone_number, purpose]):
            return "错误：信息不完整，请提供车牌号、来访单位、手机号和来访事由"
        
        visitor_info = {
            "plate_number": plate_number,
            "company_name": company_name,
            "phone_number": phone_number,
            "purpose": purpose,
            "entry_time": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        save_visitor(visitor_info)
        logger.info(f"Visitor saved: {plate_number}")
        
        send_wechat_notification(visitor_info)
        logger.info(f"WeChat notification sent for: {plate_number}")
        
        return f"访客信息已提交：车牌号{plate_number}，{company_name}，{purpose}，已通知门卫，请稍等放行。"
    
    except Exception as e:
        logger.error(f"Error in submit_visitor_info: {e}")
        return f"提交失败：{str(e)}"

history_tool_schema = {
    "type": "function",
    "name": "check_return_visitor",
    "description": "查询回访访客信息，根据手机号或车牌号查询历史记录",
    "parameters": {
        "type": "object",
        "properties": {
            "phone_number": {
                "type": "string",
                "description": "手机号码"
            },
            "plate_number": {
                "type": "string",
                "description": "车牌号"
            }
        },
        "required": []
    }
}

def check_return_visitor_info(arguments: dict) -> str:
    phone_number = arguments.get("phone_number", "").strip()
    plate_number = arguments.get("plate_number", "").strip()
    
    visitor = check_return_visitor(phone_number, plate_number)
    
    if visitor:
        return f"回访访客识别成功：车牌号{visitor['plate_number']}，{visitor['company_name']}，{visitor['purpose']}，上次来访{visitor['last_visit']}"
    else:
        return "未找到历史访问记录"

tools_map = {
    "submit_visitor_info": submit_visitor_info,
    "check_return_visitor": check_return_visitor_info
}

def get_tools_definition():
    return [visitor_tool_schema, history_tool_schema]