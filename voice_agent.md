# Take Home Exam — Voice Agent

<aside>
💡

加入我们，让世界听到AI未来的新声音
在这里，你的创想，改变大模型的未来 🎉 🎉

</aside>

🌟 **公司介绍**

上海蓝色鲸鱼科技有限公司🐳是一家2025年5月新成立的人工智能基础大模型公司🤖，专注于基础研究工作，方向是大语言模型（LLM）尤其是新构架（dLLM）的研发，测试，部署。创始人王宏和闻馨从美国回来，原哈佛大学ES26课程（LLM预训练）讲师。公司愿景是研究双向注意力的高效基础大模型构架，铺平通往AGI道路，让人类的工作更有意义。更多介绍请移步[官网](http://whaletech.ai)[www.whaletech.ai](http://www.whaletech.ai) 
更多公司介绍

公司官网 www.whaletech.ai

[Whaletech AI - Building the Future of Artificial Intelligence](http://www.whaletech.ai)

路演汇报视频：https://youtu.be/a_rxCQsoEs0  

[路演报告 蓝色鲸鱼](https://www.youtube.com/watch?v=a_rxCQsoEs0)

### **致候选人的一封信**

你好！首先感谢你对上海蓝色鲸鱼公司的兴趣，也恭喜你成功通过我们的初步简历筛选。
蓝色鲸鱼大模型集结了一批最顶尖的大模型研究和Agent小天才，我们每天都在追逐突破大模型的前沿构架。我们希望你和我们一样由衷的喜欢追逐前沿技术并且积极地推动技术发展
在这里我们有自由的算力，顶尖的B级和GB显卡集群，最强大的国内外AI工具，透明而热烈的技术讨论交流氛围，吃不完的零食冰淇淋和五星级的工作居住环境。加入我们，在广阔的平台上改变世界！

## 一、项目概述

本项目是一个端到端的 Voice Agent 实战评估，模拟真实业务场景：为工业园区设计一套语音AI访客登记系统，替代传统保安人工问询流程。

我们考察的不是"会不会写代码"，而是你的技术筛选能力、方案评估能力和持续迭代能力。AI Coding时代，系统架构的选择远比写代码本身重要——它体现的是你的工程Taste和学习速度。

---

## 二、业务场景

园区每天有大量车辆进出。内部车辆已录入海康威视门禁系统，可自动识别放行。访客车辆则需要保安走到车旁进行人工问询和登记，流程低效。

### 当前流程（人工）

访客车辆到达停车场入口 → 海康门禁识别车牌，提示"未登记" → 保安携带纸质登记表走出保安室 → 口头询问并手工填写信息 → 遥控器手动抬杆放行。

![image.png](attachment:f5b17445-554d-48cd-93e2-bc5edf6061c6:image.png)

![image.png](attachment:66757bac-24d7-420e-8daf-7c8d3bcf8493:bda6b299-99f8-437b-ab1c-40c709a30ef9.png)

### 需采集的信息

| 字段 | 说明 | 示例 |
| --- | --- | --- |
| 车牌号 | 访客车辆牌照 | 沪A12345 |
| 来访单位 | 园区内目标公司名称 | 蓝色鲸鱼科技 |
| 手机号 | 访客联系电话 | 138xxxx1234 |
| 来访事由 | 如送货、拜访、面试等 | 送货 |
| 入场时间 | 系统自动记录 | 2025-04-13 14:30 |

### 目标流程（AI自动化）

停车场入口张贴一个电话号码。未登记车辆的驾驶员拨打该号码，Voice Agent自动接听并在自然对话中采集所有必要信息，随后将结构化的访客信息推送至保安微信，保安确认后远程放行。

---

## 三、交付要求

### 必须交付

1. **全链路跑通：** 用户拨打号码（可用你自己的电话作为Demo）→ Agent接听 → 自然对话采集信息 → 推送完整访客消息至保安微信（个人微信或企业微信均可作为Demo）。
2. **25秒内完成：** 从电话接通（Agent开始说话）到微信消息发出，不含拨号振铃时间。
3. **Human Friendly：** 对话必须像真人门卫一样自然简洁，不能机械式一问一答（那种逻辑代码就能做，不需要LLM）。具体标准见下方「对话体验标准」。
4. **可演示部署：** 至少本地电脑部署可运行。
5. **GitHub仓库：** commit message清晰，README简明扼要（架构图 + 部署步骤 + 环境变量，控制在一页以内）。
6. **实战测试：** 请亲朋好友实际拨打测试，收集反馈并迭代优化。

### 加分项（非必须，但能体现更强的能力）

- **Serverless部署：** 例如 GitHub Actions CI/CD + Cloudflare Workers + OpenRouter AI API + Neon PostgreSQL + Auth。这只是一个示例组合，欢迎你用任何你认为合理的云原生架构。
- **门卫查询Agent：** 保安可以通过自然语言与Agent对话，查询"本周一共多少访问车辆""什么时间段访问最多""张师傅这个月来了几次"等信息。我们致力于创造一个未来不需要人工值守重复劳动的愿景。
- **回访识别：** 系统自动关联历史记录，对回访者直接确认（如"张师傅您好，今天是不是和上周一样来蓝色鲸鱼送货？"），而不是从头采集。
- **多路并发**（多辆车同时拨打）

### 我们的期望

- **技术选型是考察重点。** Backend、Frontend、AI LLM均不限。我们希望看到你的筛选、评估和判断过程，而不是简单搭个脚手架。
- **涉及微信或电话的方案，大胆想象不受局限。** LLM经常会推荐一些过时或不合规的方案，请你独立判断、实际验证。可以了解目前市面上的QClaw、OpenClaw等项目，但只要你能跑通且稳定就行。
- **我们鼓励并期待你充分使用AI辅助编码（Vibe Coding）。** 展现你与Coding Agent高效协作的能力——如何引导AI、如何审查AI生成的代码、如何在AI辅助下做出更好的架构决策。

---

## 四、对话体验标准

"像人一样"不是口号，而是可衡量的标准。以下是正反例对比：

### ✗ 机械式一问一答（不可接受）

`AI：您好，请问您的车牌号是多少？
用户：沪A12345
AI：好的，请问您来访哪家公司？
用户：蓝色鲸鱼
AI：请问您来访的事由是？
用户：送货
AI：请问您的手机号？
用户：138xxxx1234
AI：请问您预计停留多久？
（全程6轮对话，约45秒）`

### ✓ 自然对话（期望效果）

`AI：您好，请问车牌号多少，今天找哪家公司，什么事儿？
用户：沪A12345，来蓝色鲸鱼送货的。
AI：收到，手机号方便留一下吗？
用户：138xxxx1234。
AI：好的！沪A12345，蓝色鲸鱼送货，已通知门卫，请稍等放行。
（全程3轮对话，约15秒）`

### ✓ 回访场景（加分项的理想效果）

`AI：张师傅您好，今天是不是和上周二一样来蓝色鲸鱼送货？
用户：对对对，还是老地方。
AI：好的，已通知门卫，请稍等。
（全程2轮，约8秒）`

---

## 五、提交方式

1. **GitHub仓库链接**（确保我们有访问权限）
2. **一段1-2分钟的演示：** 从拨打电话到保安微信收到消息的完整流程
3. **简要的技术选型说明**（可放在README中）
4. **截止时间：** 收到题目后第7天 23:59

### 技术答辩

提交后我们会安排一次30分钟的技术答辩，你需要能够：

- 讲解架构设计和关键技术决策（为什么选这个方案，不选那个）
- 演示核心功能并回答技术细节问题
- 讨论遇到的困难和解决思路
- 如果使用了AI辅助编码，说明你如何引导和审查AI生成的代码

> 💡 答辩的重点不是"做得多完美"，而是你的思考过程、技术判断力和解决问题的方式。遇到搞不定的部分，记录下你尝试了什么、卡在哪里，这比硬凑一个半成品更有价值。
> 

---

## 六、常见问题

**Q: 电话号码怎么解决？**
A: 这本身就是考察的一部分。Twilio、阿里云语音、SIP Trunk、或其他方案，你说了算。遇到困难请记录下来，答辩时讨论。

**Q: 可以用商业SaaS（如VAPI、Retell）吗？**
A: 可以，但请在选型说明中解释为什么选它而不是自建方案，并说明trade-off。

**Q: 微信推送用什么方案都行吗？**
A: 不限。企业微信Webhook、企业微信API、或其他你能跑通的方案都可以。我们看的是结果和你的判断过程。

**Q: 可以用AI Agent Vibe Coding吗？**
A: 强烈鼓励。但你需要在答辩中能够解释架构决策和关键代码的设计意图。

**Q: 25秒怎么计时？**
A: 从电话接通（Agent开始说话）到微信消息发出，不含拨号振铃时间。

---

## 七、参考资料

以下仅供参考，鼓励你自行调研。选型本身也是考察的一部分。

| 类型 | 链接/说明 |
| --- | --- |
| 语音Agent框架 | LiveKit Agents: github.com/livekit/agents |
| 语音Agent框架 | Pipecat (Daily.co): github.com/pipecat-ai/pipecat |
| 实时语音API | OpenAI Realtime API: platform.openai.com/docs/guides/realtime |
| 微信/电话方案 | QClaw、OpenClaw等开源项目，请自行调研评估 |
| 概念演示视频 | youtube.com/watch?v=XV5bhkDpL7U |

---

祝你享受这个项目，期待看到你的作品！
如有任何疑问，请联系你的对接人或发邮件至 hr[@whaletech.ai](mailto:hr@whaletech.ai)

## 参考链接，千万别局限以下，大胆想象发挥

[Building Voice Agents with Gemini 3](https://www.youtube.com/watch?v=XV5bhkDpL7U)

[Build Hour: Voice Agents](https://www.youtube.com/watch?v=rpj1m0wYs8M)

https://github.com/QwenLM/Qwen3-TTS

[AI Voice Agents | Build & Deploy with Vapi](https://vapi.ai/ai-voice-agents?utm_cid=23463558651&utm_adgroupid=191829270956&utm_adid=797155826344&utm_targetid=kwd-2418395646238&hstk_creative=797155826344&hstk_campaign=23463558651&hstk_network=googleAds&utm_source=gsearch&utm_term=create%20ai%20voice%20agent&utm_medium=ppc&utm_campaign=ai_voice_agents&hsa_acc=4500971697&hsa_cam=23463558651&hsa_grp=191829270956&hsa_ad=797155826344&hsa_src=g&hsa_tgt=kwd-2418395646238&hsa_kw=create%20ai%20voice%20agent&hsa_mt=p&hsa_net=adwords&hsa_ver=3&gad_source=1&gad_campaignid=23463558651&gbraid=0AAAAA-2cnbxg5F3rpLJvVWDHQ3q3mpMQF&gclid=Cj0KCQjwqPLOBhCiARIsAKRMPZo_FpTQ4emKUm4ckdBdyNvNZuxFllqZXxmxrVLeMRhPQl0WV1BRNmQaAgxZEALw_wcB)

## 八、面试预约

<aside>
📌

**预约流程**

1.通过下方链接预约面试时间

[https://whaletech.notion.site/2e35f589aa80800c9af0e5b6d0e753cf?pvs=105](https://www.notion.so/2e35f589aa80800c9af0e5b6d0e753cf?pvs=21)

2.再通过**企业微信**将代码仓库和 Demo 发送给我们

</aside>