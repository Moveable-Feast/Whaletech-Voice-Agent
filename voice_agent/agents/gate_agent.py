from services.storage import save_visitor, get_history
from services.notify import send_to_wechat
import sqlite3
from datetime import datetime

SUBMIT_TOOL_SCHEMA = {
    "type": "function",
    "name": "submit_visitor_info",
    "description": "提交访客登记信息，触发通知门卫",
    "parameters": {
        "type": "object",
        "properties": {
            "plate_number": {"type": "string", "description": "车牌号，如'沪A12345'"},
            "company": {"type": "string", "description": "来访单位名称，如'蓝色鲸鱼科技'"},
            "phone": {"type": "string", "description": "手机号码，如'13812345678'"},
            "purpose": {"type": "string", "description": "来访事由，如'送货'、'拜访'"},
        },
        "required": ["plate_number", "company"]
    }
}

QUERY_HISTORY_TOOL_SCHEMA = {
    "type": "function",
    "name": "query_visitor_history",
    "description": "查询访客历史记录",
    "parameters": {
        "type": "object",
        "properties": {
            "plate_number": {"type": "string", "description": "车牌号"},
            "phone": {"type": "string", "description": "手机号"},
            "company": {"type": "string", "description": "公司名称"}
        },
        "required": []
    }
}

def execute_submit_visitor_info(arguments):
    record = {
        "plate_number": arguments.get("plate_number", ""),
        "company": arguments.get("company", ""),
        "phone": arguments.get("phone") or "未提供",
        "purpose": arguments.get("purpose") or "未说明",
    }
    save_visitor(record)
    send_to_wechat(record)
    return f"访客 {record['plate_number']} 已登记，已通知门卫"

def execute_query_visitor_history(arguments):
    plate_number = arguments.get("plate_number")
    phone = arguments.get("phone")
    company = arguments.get("company")
    
    from config.settings import settings
    
    conn = sqlite3.connect(settings.database_path)
    cursor = conn.cursor()
    
    query = "SELECT plate_number, company, phone, purpose, entry_time FROM visits WHERE 1=1"
    params = []
    
    if plate_number:
        query += " AND plate_number = ?"
        params.append(plate_number)
    if phone:
        query += " AND phone = ?"
        params.append(phone)
    if company:
        query += " AND company LIKE ?"
        params.append(f"%{company}%")
    
    query += " ORDER BY entry_time DESC"
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        return "未找到匹配的访问记录"
    
    result_str = f"共找到 {len(results)} 条记录：\n"
    for i, row in enumerate(results[:10], 1):
        plate, comp, ph, purp, time = row
        result_str += f"{i}. {plate} | {comp} | {purp} | {time[:16]}\n"
    
    return result_str

class GateAgent:
    def __init__(self):
        self.name = "Gate Greeter"
        self.instructions = """
你是一名园区门卫老张，正在通过电话接待访客车辆。电话时间宝贵，必须快速完成登记。
约束：
- 每一轮对话最多问 1 个问题，尽量在一句话里合并多个问题
- 不允许逐项机械式提问
- 信息收集完整后，返回JSON格式的完整信息
"""
        self.tools = [SUBMIT_TOOL_SCHEMA]
    
    def execute_tool(self, tool_name, arguments):
        if tool_name == "submit_visitor_info":
            return execute_submit_visitor_info(arguments)
        return f"未知工具：{tool_name}"

class QueryAgent:
    def __init__(self):
        self.name = "Query Agent"
        self.handoff_description = "查询历史记录的专家"
        self.instructions = """
你是访客记录管理员，可以回答有关来访车辆的任何统计查询。
"""
        self.tools = [QUERY_HISTORY_TOOL_SCHEMA]
    
    def execute_tool(self, tool_name, arguments):
        if tool_name == "query_visitor_history":
            return execute_query_visitor_history(arguments)
        return f"未知工具：{tool_name}"