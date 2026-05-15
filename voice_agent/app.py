from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from transport.twilio_transport import router as twilio_router
from transport.web_voice_routes import router as web_voice_router
from transport.qr_routes import router as qr_router
from api.test_endpoints import router as api_router
from services.storage import init_db
from config.settings import settings
import sys

init_db()

app = FastAPI(title="Voice Gate Registration System")

# 挂载静态文件服务
app.mount("/static", StaticFiles(directory="voice_agent/static"), name="static")

# 添加路由
app.include_router(twilio_router)
app.include_router(web_voice_router)
app.include_router(qr_router)
app.include_router(api_router)

# 根路由由 web_voice_routes 处理，返回语音登记页面

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn

    # 检查是否有 --port 参数
    port = 5050
    if '--port' in sys.argv:
        port_idx = sys.argv.index('--port')
        if port_idx + 1 < len(sys.argv):
            port = int(sys.argv[port_idx + 1])

    # 也可以使用 -p 参数
    elif '-p' in sys.argv:
        port_idx = sys.argv.index('-p')
        if port_idx + 1 < len(sys.argv):
            port = int(sys.argv[port_idx + 1])

    try:
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        print(f"端口 {port} 被占用，尝试使用端口 8000...")
        try:
            uvicorn.run(app, host="0.0.0.0", port=8000)
        except Exception as e2:
            print(f"端口 8000 也被占用，请手动指定其他端口")
            print(f"使用方法: python app.py --port 8080")