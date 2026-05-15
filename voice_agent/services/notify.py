import requests
import logging
from datetime import datetime
from config.settings import settings

logger = logging.getLogger(__name__)

def send_to_wechat(record):
    """发送消息到企业微信群机器人"""
    webhook_url = settings.wechat_webhook_url
    
    if not webhook_url or webhook_url == "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_webhook_key":
        logger.warning("WECHAT_WEBHOOK_URL not configured, skipping WeChat notification")
        return {"status": "skipped", "reason": "webhook not configured"}
    
    content = f"""【访客通知】
车牌：{record.get("plate_number", "未提供")}
拜访单位：{record.get("company", "未提供")}
手机号：{record.get("phone", "未提供")}
事由：{record.get("purpose", "未说明")}
时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
请确认后放行。"""

    try:
        response = requests.post(
            webhook_url,
            json={"msgtype": "text", "text": {"content": content}},
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        if result.get("errcode") == 0:
            logger.info(f"WeChat message sent successfully for {record.get('plate_number')}")
            return {"status": "success", "data": result}
        else:
            logger.error(f"WeChat API error: {result.get('errmsg')}")
            return {"status": "failed", "error": result.get('errmsg')}
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send WeChat message: {str(e)}")
        return {"status": "failed", "error": str(e)}

def send_to_serverchan(record):
    """发送消息到个人微信（Server酱）"""
    serverchan_key = settings.serverchan_key
    
    if not serverchan_key or serverchan_key == "your_serverchan_key":
        logger.warning("SERVERCHAN_KEY not configured, skipping ServerChan notification")
        return {"status": "skipped", "reason": "serverchan key not configured"}
    
    title = f"访客通知 - {record.get('plate_number', '未提供')}"
    content = f"""车牌：{record.get("plate_number", "未提供")}
拜访单位：{record.get("company", "未提供")}
手机号：{record.get("phone", "未提供")}
事由：{record.get("purpose", "未说明")}
时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
请确认后放行。"""
    
    try:
        response = requests.post(
            f"https://sctapi.ftqq.com/{serverchan_key}.send",
            data={"title": title, "desp": content},
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        if result.get("code") == 0:
            logger.info(f"ServerChan message sent successfully for {record.get('plate_number')}")
            return {"status": "success", "data": result}
        else:
            logger.error(f"ServerChan API error: {result.get('message')}")
            return {"status": "failed", "error": result.get('message')}
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send ServerChan message: {str(e)}")
        return {"status": "failed", "error": str(e)}

def send_notification(record):
    """发送通知（自动选择可用的方式）"""
    # 优先尝试企业微信
    wechat_result = send_to_wechat(record)
    if wechat_result.get("status") == "success":
        return {"type": "wechat", "result": wechat_result}
    
    # 尝试 Server酱
    serverchan_result = send_to_serverchan(record)
    if serverchan_result.get("status") == "success":
        return {"type": "serverchan", "result": serverchan_result}
    
    # 如果都失败，返回状态
    return {"type": "none", "wechat_result": wechat_result, "serverchan_result": serverchan_result}