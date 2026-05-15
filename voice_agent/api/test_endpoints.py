from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.storage import save_visitor, get_history, get_visitor_history
from services.notify import send_notification
from services.llm_service import extract_visitor_info
from datetime import datetime
from typing import List, Optional

router = APIRouter(prefix="/api")

class VisitorInput(BaseModel):
    plate_number: str
    company: str
    phone: str = ""
    purpose: str = ""

class ConversationMessage(BaseModel):
    role: str
    content: str

class ConversationTest(BaseModel):
    user_input: str
    history: Optional[List[ConversationMessage]] = []

@router.post("/test/submit")
def test_submit(visitor: VisitorInput):
    record = {
        "plate_number": visitor.plate_number,
        "company": visitor.company,
        "phone": visitor.phone or "未提供",
        "purpose": visitor.purpose or "未说明",
    }

    save_visitor(record)
    notification_result = send_notification(record)

    return {
        "status": "success",
        "record": record,
        "notification_result": notification_result
    }

@router.post("/test/conversation")
def test_conversation(test: ConversationTest):
    history = [{"role": msg.role, "content": msg.content} for msg in test.history]
    result = extract_visitor_info(test.user_input, history)
    return {
        "user_input": test.user_input,
        "result": result,
        "history": history
    }

@router.get("/test/quick/{input_text}")
def quick_test(input_text: str):
    result = extract_visitor_info(input_text)
    return {
        "input": input_text,
        "result": result
    }

@router.get("/visits/{plate_number}")
def get_visit_history(plate_number: str):
    history = get_history(plate_number)
    if history:
        return {
            "plate_number": plate_number,
            "company": history[0],
            "purpose": history[1]
        }
    raise HTTPException(status_code=404, detail="No history found")

@router.get("/visits/{plate_number}/detail")
def get_visit_history_detail(plate_number: str):
    history = get_visitor_history(plate_number)
    if history:
        return {
            "plate_number": plate_number,
            "data": history
        }
    raise HTTPException(status_code=404, detail="No history found")