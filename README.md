# Voice Gate - 园区访客语音登记系统

一个智能的园区访客登记系统，支持语音和文字两种交互方式，自动识别车牌、公司、手机号和来访事由，并将数据推送到微信。

## 📋 目录

- [项目概述](#项目概述)
- [技术选型](#技术选型)
- [项目架构](#项目架构)
- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [部署指南](#部署指南)
- [使用说明](#使用说明)

---

## 项目概述

Voice Gate 是一个基于 AI 的智能园区访客登记系统，采用自然对话的方式收集访客信息，支持语音和文字两种交互模式，适用于企业园区、写字楼等场所的访客管理。

### 核心能力

- 🎤 **语音对话**：支持浏览器 Web Speech API 语音识别
- 💬 **文字对话**：提供文字输入模式，适应不同场景
- 🤖 **智能理解**：使用 DeepSeek LLM 理解自然语言
- 📋 **信息收集**：自动提取车牌号、公司、手机号、事由
- 📱 **微信推送**：自动推送访客信息到保安微信
- 📱 **二维码访问**：支持手机扫码登记
- 📊 **数据存储**：SQLite 数据库持久化存储

---

## 技术选型

### 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **FastAPI** | 最新 | Web 框架，提供高性能 API 服务 |
| **Python** | 3.8+ | 主要开发语言 |
| **DeepSeek API** | - | 大语言模型，处理自然语言理解 |
| **SQLite** | - | 轻量级数据库，存储访客记录 |
| **Uvicorn** | - | ASGI 服务器，运行 FastAPI 应用 |
| **qrcode** | - | 生成访客登记二维码 |
| **requests** | - | HTTP 请求库，调用外部 API |

### 前端技术栈

| 技术 | 用途 |
|------|------|
| **HTML5** | 页面结构 |
| **CSS3** | 样式设计 |
| **JavaScript** | 交互逻辑 |
| **Web Speech API** | 浏览器端语音识别和合成 |

### 第三方服务

| 服务 | 用途 |
|------|------|
| **DeepSeek** | 大语言模型 API |
| **Server酱** | 微信消息推送 |
| **Twilio** (可选) | 电话语音交互 |
| **ngrok** (可选) | 内网穿透，临时公网访问 |
| **Cloudflare Tunnel** (可选) | 免费稳定的公网访问方案 |

---

## 项目架构

### 目录结构

```
bluewhale2605/
├── voice_agent/                 # 主项目目录
│   ├── app.py                  # 应用入口
│   ├── config/                 # 配置模块
│   │   └── settings.py        # 配置管理
│   ├── services/              # 业务服务层
│   │   ├── llm_service.py     # LLM 服务 (DeepSeek)
│   │   ├── rule_engine.py     # 规则引擎 (备用方案)
│   │   ├── storage.py         # 数据库存储服务
│   │   └── notify.py          # 消息通知服务
│   ├── transport/             # 传输层
│   │   ├── web_voice_routes.py # 网页语音交互路由
│   │   ├── twilio_transport.py # Twilio 电话路由 (可选)
│   │   └── qr_routes.py        # 二维码路由
│   ├── api/                   # API 接口
│   │   └── test_endpoints.py  # 测试端点
│   ├── agents/                # AI Agent 模块
│   │   └── gate_agent.py      # 门卫 Agent
│   ├── tools/                 # 工具模块
│   │   └── visitor_tools.py   # 访客工具
│   └── static/                # 静态文件
│       ├── index.html         # 主页面
│       └── test_speech.html   # 语音识别测试页面
├── test_*.py                  # 测试脚本
└── README.md                  # 项目文档
```

### 系统架构图

```
┌─────────────────┐    ┌─────────────────┐
│  浏览器/Web App  │    │  手机/移动设备   │
│ (语音/文字输入)  │    │  (扫码访问)      │
└────────┬────────┘    └────────┬────────┘
         │                      │
         └──────────┬───────────┘
                    │
         ┌──────────▼───────────┐
         │    FastAPI 服务      │
         │  (app.py + 路由)     │
         └──────────┬───────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
┌───▼───┐      ┌───▼───┐     ┌───▼───┐
│ LLM   │      │ 规则   │     │存储   │
│服务   │      │ 引擎   │     │服务   │
└───┬───┘      └───┬───┘     └───────┘
    │              │
    └──────┬───────┘
           │
    ┌──────▼───────┐
    │  通知服务    │
    │ (微信推送)   │
    └─────────────┘
```

---

## 功能特性

### 核心功能

1. **多模式交互**
   - 🎤 语音模式：使用浏览器 Web Speech API
   - 💬 文字模式：键盘输入，兼容所有设备

2. **智能信息提取**
   - 🚗 车牌号识别（支持规则和 LLM 两种方式）
   - 🏢 公司名称识别（常见公司库 + 自然语言理解）
   - 📱 手机号识别
   - 📝 来访事由识别

3. **自然对话体验**
   - 合并问题提问，避免机械式一问一答
   - 支持信息顺序混乱的回答
   - 智能追问缺失信息
   - 双引擎机制：LLM 优先，规则引擎兜底

4. **数据管理**
   - SQLite 轻量级数据库
   - 访客记录持久化
   - 支持历史查询

5. **通知推送**
   - Server酱微信消息推送
   - 结构化信息展示

### 扩展功能

1. **二维码访问**
   - 自动生成访客登记二维码
   - 手机扫码快速访问

2. **测试页面**
   - 语音识别独立测试
   - 完整流程端到端测试

---

## 快速开始

### 环境要求

- Python 3.8 或更高版本
- Chrome 浏览器（推荐，最佳语音识别体验）
- DeepSeek API Key

### 安装步骤

1. **克隆项目**
   ```bash
   cd bluewhale2605
   ```

2. **安装依赖**
   ```bash
   pip install fastapi uvicorn pydantic python-dotenv requests qrcode
   ```

3. **配置环境变量**
   ```bash
   # 复制并编辑 .env 文件
   cd voice_agent
   # 创建 .env 文件，填入配置
   ```

4. **启动服务**
   ```bash
   python voice_agent/app.py --port 8080
   ```

5. **访问应用**
   - 主页：`http://localhost:8080`
   - 二维码：`http://localhost:8080/qr`
   - 语音测试：`http://localhost:8080/test_speech`

---

## 配置说明

### 环境变量配置

在 `voice_agent/.env` 文件中配置：

```env
# DeepSeek API 配置
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 微信推送配置 (Server酱)
SERVERCHAN_KEY=your_serverchan_send_key

# 数据库配置 (可选)
DATABASE_PATH=visitors.db

# Twilio 配置 (可选)
TWILIO_PHONE_NUMBER=+1234567890
```

### 获取 API Key

1. **DeepSeek API Key**
   - 访问 [https://platform.deepseek.com/](https://platform.deepseek.com/)
   - 注册账号并创建 API Key

2. **Server酱 Key**
   - 访问 [https://sct.ftqq.com/](https://sct.ftqq.com/)
   - 微信扫码登录获取 SendKey

---

## 部署指南

### 本地开发

```bash
# 启动服务
python voice_agent/app.py --port 8080

# 访问
# 浏览器打开 http://localhost:8080
```

### 临时公网访问（ngrok）

```bash
# 安装 ngrok
# 访问 https://ngrok.com/download

# 启动隧道
ngrok http 8080

# 访问显示的 Forwarding 地址
```

### 云服务器部署（推荐）

1. **选择云服务商**
   - 阿里云 ECS
   - 腾讯云 CVM
   - 华为云 ECS

2. **部署步骤**
   ```bash
   # 1. 登录服务器
   ssh root@your-server-ip

   # 2. 安装环境
   sudo apt update
   sudo apt install -y python3 python3-pip nginx

   # 3. 上传项目并安装依赖
   pip3 install fastapi uvicorn pydantic python-dotenv requests qrcode

   # 4. 启动服务
   nohup python3 voice_agent/app.py --port 8080 &

   # 5. 配置 Nginx 反向代理（可选）
   ```

### 域名配置（可选）

配置 Nginx 反向代理，绑定域名：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/project/voice_agent/static/;
    }
}
```

---

## 使用说明

### 语音模式

1. 访问主页，选择"语音对话"
2. 点击"开始语音登记"
3. 允许浏览器麦克风权限
4. 按照提示自然对话
5. 完成登记后，信息会自动保存并推送

### 文字模式

1. 访问主页，选择"文字输入"
2. 在输入框中输入内容
3. 点击"发送"或按 Enter 键
4. 完成信息收集

### 测试页面

访问 `http://localhost:8080/test_speech` 测试浏览器语音识别功能。

---

## 技术亮点

### 1. 双引擎信息提取机制

- **LLM 优先**：使用 DeepSeek LLM 进行自然语言理解
- **规则兜底**：内置规则引擎，当 LLM 失败时自动切换
- **常见公司库**：预配置 300+ 常见公司名称，提升识别准确率

### 2. 自然对话设计

- 合并问题提问，减少交互次数
- 支持信息顺序混乱的回答
- 智能判断信息完整性，仅追问缺失内容

### 3. 多模式支持

- 语音模式：利用 Web Speech API
- 文字模式：兼容所有浏览器和设备
- 二维码：手机快速访问

### 4. 模块化架构

- 清晰的分层架构（配置 → 服务 → 路由 → API）
- 易于扩展和维护
- 支持多种传输层（Web、电话等）

---

## 测试

项目包含完整的测试脚本：

```bash
# 端到端测试
python test_e2e.py

# 规则引擎测试
python test_rule_engine.py

# 对话流程测试
python test_conversation_flow.py

# 上海宝钢场景测试
python test_shanghai_baogang.py
```

---

## 常见问题

### Q: 语音识别没有反应？

A: 请检查：
1. 使用 Chrome 浏览器
2. 允许浏览器麦克风权限
3. 系统麦克风设备正常工作
4. 访问 `http://localhost:8080/test_speech` 测试

### Q: 微信收不到推送？

A: 请检查：
1. Server酱 Key 是否正确配置
2. 微信是否关注了 Server酱 公众号
3. 查看测试脚本输出

### Q: 如何让手机访问？

A: 方案：
1. 临时测试：使用 ngrok
2. 长期使用：部署到云服务器

---

## 许可证

本项目仅供学习和研究使用。

---

## 贡献

欢迎提交 Issue 和 Pull Request！

---

## 联系方式

如有问题，请提交 Issue。

---

**Enjoy Voice Gate! 🚗**