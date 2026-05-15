from fastapi import APIRouter, Request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from services.llm_service import extract_visitor_info, check_returning_visitor, query_with_deepseek
from services.storage import save_visitor, get_visitor_history, get_history
from services.notify import send_notification
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

conversation_state = {}

@router.post("/voice")
async def handle_incoming_call(request: Request):
    response = VoiceResponse()
    gather = Gather(
        input="speech",
        action="/voice/collect",
        method="POST",
        speechTimeout="auto",
        timeout=5,
        language="zh-CN"
    )
    gather.say("喂您好，这里是园区门卫，请说一下车牌号和去哪家公司，什么事儿？", language="zh-CN")
    response.append(gather)
    return Response(content=str(response), media_type="application/xml")

@router.post("/voice/collect")
async def collect_visitor_info(request: Request):
    form_data = await request.form()
    speech_result = form_data.get("SpeechResult", "")
    call_sid = form_data.get("CallSid", "unknown")

    logger.info(f"Call {call_sid} - Received: {speech_result}")

    if not speech_result:
        response = VoiceResponse()
        response.say("不好意思没听清楚，请再说一遍。", language="zh-CN")
        gather = Gather(
            input="speech",
            action="/voice/collect",
            method="POST",
            speechTimeout="auto",
            timeout=5,
            language="zh-CN"
        )
        response.append(gather)
        return Response(content=str(response), media_type="application/xml")

    if call_sid not in conversation_state:
        conversation_state[call_sid] = {
            "plate_number": "",
            "company": "",
            "phone": "",
            "purpose": "",
            "history": [],
            "is_returning": False,
            "returning_context": None,
            "question_count": 0
        }

    state = conversation_state[call_sid]
    state["history"].append({"role": "user", "content": speech_result})
    state["question_count"] += 1

    context = None
    if state["is_returning"] and state["returning_context"]:
        context = state["returning_context"]

    result = extract_visitor_info(speech_result, state["history"], context)

    response = VoiceResponse()

    if result.get("action") == "submit":
        visitor_data = {
            "plate_number": result.get("plate_number", state["plate_number"]) or state["plate_number"],
            "company": result.get("company", state["company"]) or state["company"],
            "phone": result.get("phone", state["phone"]) or state["phone"] or "未提供",
            "purpose": result.get("purpose", state["purpose"]) or state["purpose"] or "未说明",
            "visitor_name": state.get("returning_context", {}).get("name", "")
        }

        save_visitor(visitor_data)
        send_notification(visitor_data)

        confirm_msg = "好的！{0}，{1}，{2}，已通知门卫抬杆，请慢走。".format(
            visitor_data["plate_number"],
            visitor_data["company"],
            visitor_data["purpose"]
        )
        response.say(confirm_msg, language="zh-CN")

        del conversation_state[call_sid]
        logger.info(f"Visitor registered: {visitor_data}")

    elif result.get("action") == "greet_returning":
        returning_info = result
        state["plate_number"] = returning_info.get("plate_number", "") or state["plate_number"]
        state["company"] = returning_info.get("company", "") or state["company"]
        state["purpose"] = returning_info.get("purpose", "") or state["purpose"]
        state["is_returning"] = True
        state["returning_context"] = {
            "name": returning_info.get("name", ""),
            "summary": returning_info.get("history_summary", ""),
            "is_returning": True
        }

        greeting_msg = "{0}，{1}，确认一下可以吗？".format(
            returning_info.get("name", "您好"),
            returning_info.get("history_summary", "欢迎再次光临")
        )
        response.say(greeting_msg, language="zh-CN")

        gather = Gather(
            input="speech",
            action="/voice/collect",
            method="POST",
            speechTimeout="auto",
            timeout=5,
            language="zh-CN"
        )
        response.append(gather)

    elif result.get("action") == "continue":
        question = result.get("question", "请继续说")

        extracted_plate = result.get("plate_number", "")
        extracted_company = result.get("company", "")
        extracted_phone = result.get("phone", "")
        extracted_purpose = result.get("purpose", "")

        if extracted_plate:
            state["plate_number"] = extracted_plate
        if extracted_company:
            state["company"] = extracted_company
        if extracted_phone:
            state["phone"] = extracted_phone
        if extracted_purpose:
            state["purpose"] = extracted_purpose

        if not state["is_returning"] and state["plate_number"]:
            history = get_visitor_history(state["plate_number"])
            if history:
                check_result = check_returning_visitor(speech_result, state["plate_number"])
                if check_result.get("is_returning"):
                    state["is_returning"] = True
                    state["returning_context"] = check_result

        response.say(question, language="zh-CN")
        gather = Gather(
            input="speech",
            action="/voice/collect",
            method="POST",
            speechTimeout="auto",
            timeout=5,
            language="zh-CN"
        )
        response.append(gather)

    else:
        response.say("不好意思，请再说一遍您的信息。", language="zh-CN")
        gather = Gather(
            input="speech",
            action="/voice/collect",
            method="POST",
            speechTimeout="auto",
            timeout=5,
            language="zh-CN"
        )
        response.append(gather)

    return Response(content=str(response), media_type="application/xml")

@router.post("/voice/hangup")
async def handle_hangup(request: Request):
    return Response(content="", status_code=200)