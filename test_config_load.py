import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voice_agent'))

# 直接检查配置类
from voice_agent.config.settings import settings

print("=" * 70)
print("配置加载测试")
print("=" * 70)
print()

print("settings 对象的所有属性:")
print(dir(settings))
print()

print("serverchan_key 属性值:")
print(repr(getattr(settings, 'serverchan_key', 'NOT FOUND')))
print()

print("SERVERCHAN_KEY 属性值:")
print(repr(getattr(settings, 'SERVERCHAN_KEY', 'NOT FOUND')))
print()

print("检查是否为空:")
print(f"serverchan_key is None: {getattr(settings, 'serverchan_key', None) is None}")
print(f"serverchan_key == '': {getattr(settings, 'serverchan_key', '') == ''}")
print()

# 检查 .env 文件路径
config_dir = os.path.dirname(os.path.abspath('voice_agent/config/settings.py'))
env_path = os.path.join(config_dir, ".env")
print(f".env 文件路径: {env_path}")
print(f".env 文件存在: {os.path.exists(env_path)}")

if os.path.exists(env_path):
    print()
    print(".env 文件内容:")
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            print(f"  {line.strip()}")

print()
print("=" * 70)