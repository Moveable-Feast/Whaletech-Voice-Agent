from pyngrok import ngrok

# 启动 ngrok 隧道
public_url = ngrok.connect(8000)

print("=" * 70)
print("🌐 网页端语音访客登记系统已启动")
print("=" * 70)
print(f"本地地址: http://localhost:8000")
print(f"公网地址: {public_url}")
print("=" * 70)
print("")
print("📱 使用方式：")
print("  1. 在手机上打开浏览器访问公网地址")
print("  2. 点击「开始语音登记」按钮")
print("  3. 授权麦克风权限")
print("  4. 与AI门卫对话完成登记")
print("")
print("💡 提示：请使用 Chrome 浏览器以获得最佳体验")
print("=" * 70)

# 保持运行
import time
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    ngrok.disconnect(public_url)
    print("隧道已关闭")