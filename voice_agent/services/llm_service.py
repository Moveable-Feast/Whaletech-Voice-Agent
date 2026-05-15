from openai import OpenAI
from config.settings import settings
import json
import logging

logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=settings.deepseek_api_key,
    base_url=settings.deepseek_base_url
)

GATE_AGENT_INSTRUCTIONS = """
【最重要的规则】只输出JSON！只输出JSON！只输出JSON！不要任何其他文字！

你是一名园区门卫老张，经验丰富，说话亲切自然，像是在跟熟人聊天一样接待访客。

=== 核心人设 ===
- 姓名：老张
- 性格：热情、干练、话不多但很亲切
- 说话风格：像小区门口的门卫大叔一样，自然不生硬
- 语气：口语化、接地气、带点人情味

=== 对话原则 ===
1. 自然流畅，像真人聊天一样，绝对不能像机器人！
2. 快速收集信息，但要有温度，不能太机械
3. 一句话合并多个问题，不要分开追问
4. 灵活应对各种回答方式，不要死板

=== 信息收集顺序 ===
第一步：收集车牌号、目标公司、拜访事由（这三个先收集）
第二步：收集手机号（前三个收集完后再问）

=== 对话风格要求 ===
1. 开场要热情自然，一句话问完所有需要的信息
2. 看到用户提供的信息，要及时回应确认，让用户感觉被听见
3. 追问时要有礼貌，不要重复问已有的信息
4. 说话要简短，但要有温度
5. 不管用户回答顺序如何，都能正确识别并归类

=== 当前已收集的信息 ===
CURRENT_CONTEXT_PLACEHOLDER

=== 对话示例与对应的JSON输出 ===

【用户提供所有信息】
用户：送货的，沪A12345，去蓝色鲸鱼，13812345678
输出JSON：{"action": "submit", "plate_number": "沪A12345", "company": "蓝色鲸鱼", "phone": "13812345678", "purpose": "送货"}

【用户提供部分信息（车牌+公司+事由）】
用户：沪A12345，去蓝色鲸鱼送货
输出JSON：{"action": "continue", "question": "好的，收到！手机号方便留一下吗？", "plate_number": "沪A12345", "company": "蓝色鲸鱼", "phone": "", "purpose": "送货"}

【用户只说事由】
用户：我来送货的
输出JSON：{"action": "continue", "question": "好的，请问车牌号多少，去哪家公司？", "plate_number": "", "company": "", "phone": "", "purpose": "送货"}

【用户只说公司】
用户：去蓝色鲸鱼
输出JSON：{"action": "continue", "question": "好的，请问车牌号多少，什么事儿？", "plate_number": "", "company": "蓝色鲸鱼", "phone": "", "purpose": ""}

【用户只说车牌】
用户：沪A12345
输出JSON：{"action": "continue", "question": "好的，请问去哪家公司，什么事儿？", "plate_number": "沪A12345", "company": "", "phone": "", "purpose": ""}

【用户信息顺序混乱】
用户：送货的，蓝色鲸鱼，沪A12345
输出JSON：{"action": "continue", "question": "好的，明白了！手机号方便留一下吗？", "plate_number": "沪A12345", "company": "蓝色鲸鱼", "phone": "", "purpose": "送货"}

【用户提供手机号】
用户：13812345678
输出JSON：{"action": "submit", "plate_number": "沪A12345", "company": "蓝色鲸鱼", "phone": "13812345678", "purpose": "送货"}

=== 信息收集规则 ===
- 车牌号、公司名称是必填项
- 事由尽量收集，如果用户没说，可以默认"未说明"
- 手机号在车牌、公司、事由收集完后再问
- 如果用户主动提供手机号，可以提前收集
- 如果用户拒绝提供手机号，可以用"未提供"
- 如果用户说"不知道"、"忘了"、"没有"，对应字段可以留空或填"未提供"

=== 自然表达库（question字段可用这些表达让对话更自然）===
确认信息："好的"、"收到"、"明白了"、"好嘞"、"没问题"
追问信息："请问"、"麻烦说一下"、"方便说一下吗"
结束登记："好的！这就给您通知门卫"、"收到，已登记完成"

=== 输出格式（最后再强调一遍：只输出JSON！）===

当信息收集完整（有车牌号、公司、事由、手机号），输出：
{"action": "submit", "plate_number": "车牌号", "company": "公司名", "phone": "手机号", "purpose": "事由"}

如果还需要继续询问，输出：
{"action": "continue", "question": "追问内容", "plate_number": "已识别的车牌", "company": "已识别的公司", "phone": "已识别的手机号", "purpose": "已识别的事由"}

【再次强调】只输出JSON对象，不要任何其他文字、说明、前缀、后缀！
"""

QUERY_AGENT_INSTRUCTIONS = """
你是访客记录管理员，可以回答有关来访车辆的任何统计查询。

你可以根据数据库中的记录回答以下问题：
- 本周一共多少访问车辆
- 什么时间段访问最多
- 某车牌号的来访记录
- 某公司的来访记录

使用 query_visitor_history 工具查询详细记录。
"""

def chat_with_deepseek(messages: list, tools: list = None) -> str:
    try:
        params = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.1,
        }
        if tools:
            params["tools"] = tools

        response = client.chat.completions.create(**params)
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"DeepSeek API error: {e}")
        return ""

def extract_visitor_info(transcript: str, conversation_history: list = None, context: dict = None) -> dict:
    if conversation_history is None:
        conversation_history = []

    system_prompt = GATE_AGENT_INSTRUCTIONS

    if context:
        context_info = "\n".join([
            f"- 车牌号: {context.get('plate_number') or '未收集'}",
            f"- 公司名称: {context.get('company') or '未收集'}",
            f"- 联系电话: {context.get('phone') or '未收集'}",
            f"- 来访事由: {context.get('purpose') or '未收集'}"
        ])
        system_prompt = system_prompt.replace("CURRENT_CONTEXT_PLACEHOLDER", context_info)
        
        if context.get("is_returning"):
            system_prompt = system_prompt + f"\n\n【回访上下文】这位访客上次是{context.get('last_visit_days', '几天')}前来过，{context.get('last_purpose', '送货')}。"
    else:
        system_prompt = system_prompt.replace("CURRENT_CONTEXT_PLACEHOLDER", "- 车牌号: 未收集\n- 公司名称: 未收集\n- 联系电话: 未收集\n- 来访事由: 未收集")

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": transcript})

    response = chat_with_deepseek(messages)
    logger.info(f"DeepSeek response: {response}")

    try:
        response = response.strip()
        # 移除可能的 Markdown 代码块标记
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        if response.lower().startswith("json"):
            response = response[4:].strip()
        
        # 尝试找到 JSON 对象的起始和结束位置
        start_idx = response.find("{")
        end_idx = response.rfind("}")
        if start_idx != -1 and end_idx != -1:
            response = response[start_idx:end_idx+1]
        
        result = json.loads(response)
        return result
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        logger.error(f"Raw response: {response}")
        return {"action": "continue", "question": "不好意思，请再说一遍？"}

def check_returning_visitor(transcript: str, plate_number: str = None) -> dict:
    if not plate_number:
        return {"is_returning": False}

    from services.storage import get_visitor_history
    history = get_visitor_history(plate_number)

    if not history:
        return {"is_returning": False}

    messages = [
        {"role": "system", "content": """你是一个信息匹配助手。判断用户的回答是否与历史记录匹配。

历史记录包含：上次来访的公司、来访事由、间隔天数
用户可能使用简称、简称或者直接说"对"、"是的"来确认

输出格式：
{"matched": true/false, "name": "称呼如张师傅", "summary": "上次情况的简要描述"}
"""},
        {"role": "user", "content": f"历史记录：{history}\n用户回答：{transcript}"}
    ]

    response = chat_with_deepseek(messages)

    try:
        result = json.loads(response)
        if result.get("matched"):
            return {
                "is_returning": True,
                "name": result.get("name", ""),
                "summary": result.get("summary", ""),
                "history": history
            }
    except:
        pass

    return {"is_returning": False}

def query_with_deepseek(question: str, context: str = "") -> str:
    messages = [
        {"role": "system", "content": QUERY_AGENT_INSTRUCTIONS},
        {"role": "user", "content": f"上下文：{context}\n\n问题：{question}"}
    ]

    response = chat_with_deepseek(messages)
    return response