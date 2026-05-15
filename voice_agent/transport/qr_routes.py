"""
二维码相关路由
生成访客登记二维码
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, StreamingResponse
import qrcode
import io
import os

router = APIRouter(prefix="/api/qr", tags=["qr_code"])

def generate_qr_code(url: str) -> bytes:
    """生成二维码图片"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    return buf.getvalue()

@router.get("/generate")
async def get_qr_code(request: Request):
    """
    生成访客登记二维码
    扫码后直接进入登记页面
    """
    scheme = request.url.scheme
    host = request.url.hostname
    
    register_url = f"{scheme}://{host}"
    
    qr_bytes = generate_qr_code(register_url)
    
    return StreamingResponse(
        io.BytesIO(qr_bytes),
        media_type="image/png"
    )

@router.get("/display", response_class=HTMLResponse)
async def display_qr_page():
    """显示二维码展示页面"""
    html_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'qr_display.html')
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return "<h1>页面未找到</h1>"