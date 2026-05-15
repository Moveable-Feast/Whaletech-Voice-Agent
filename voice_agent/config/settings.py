import os

class Settings:
    def __init__(self):
        self.load_from_env()
    
    def load_from_env(self):
        # 获取 voice_agent 目录路径（配置文件在 voice_agent/.env）
        voice_agent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env_path = os.path.join(voice_agent_dir, ".env")
        
        print(f"[DEBUG] Looking for .env at: {env_path}")
        print(f"[DEBUG] File exists: {os.path.exists(env_path)}")
        
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        setattr(self, key.lower(), value.strip())
        
        # 设置默认值
        if not hasattr(self, 'deepseek_api_key'):
            self.deepseek_api_key = ""
        if not hasattr(self, 'deepseek_base_url'):
            self.deepseek_base_url = "https://api.deepseek.com"
        if not hasattr(self, 'wechat_webhook_url'):
            self.wechat_webhook_url = ""
        if not hasattr(self, 'serverchan_key'):
            self.serverchan_key = ""
        if not hasattr(self, 'twilio_phone_number'):
            self.twilio_phone_number = ""
        if not hasattr(self, 'database_path'):
            self.database_path = ""
        
        # 设置数据库路径
        if not self.database_path:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.database_path = os.path.join(project_root, "visitors.db")

settings = Settings()