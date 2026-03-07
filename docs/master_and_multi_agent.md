我有一个场景 需要有 
## 1.邮件子智能体 
- 邮件信息收集,必要时多输对话收集(
         1. 收件人邮箱{mail_address}
         2. 邮件主题{mail_topic}
         3. 邮件内容{mail_content})
- 邮件地址检查，邮箱地址合法性检查
- 邮件起草 根据收集到的信息起草邮件内容
- 邮件发送，发送前需要展示邮件内容，并提示是否以前邮件信息进行发送 当用户同明确同意（yes/no）确认后才执行发送任务 （实际执行模拟发送即可）
## 2. 图片生成子智能体
- 必要时多输对话收集（1. {description}:图片描述, 
                 2. {style}: 图片风格(比如 "写实"，"印象"）, 
                 3.{width*height}:图片大小(宽*高 象素单位 比如 1024*768), 
                 4. {count} 图片张数 
                 ）
- 展示图片生成的关键信息 并提示是否以前图片信息进行生成 当用户同明确同意（yes/no）后才执行生成任务
- 信息完整后才能调用适当的工具进行图片生成
## 3. TTS 子智能体 
- 在进行tts生成前,从用户的输入中提取以下信息2个必要信息
                1. tts语音文案{tts_content}
                2. 语音样本文件{voice_sample_url}(可能没有 用默认语音样本)
            如果没有 就多输对话收集
- 展示tts生成的关键信息 并当用户同明确同意（yes/no）后才执行tts生成任务
- 信息完整后才能调用适当的工具进行tts 生成
## 4. 天气子智能体 根据城市名进行天气查询的能力
## 5. 数字人子智能体 数字人制作能力
- 必要时多输对话收集（1. {digital_image}:数字人图片, 
                 2. {digital_conent}: 数字人口播文稿( 后继可以用tts 生成语音文件), 
                 3.{digital_sample}:数字人口播声音样本, 
                 

需要的智能体可能有
- Orchestrator Agent（主控智能体 langGraph 1.x 实现）：对话入口、意图识别、任务分发、结果汇总、与用户交互
- Task Planner Agent（任务规划智能体）：把用户需求拆成具体任务步骤
- Validation Agent（校验智能体）：邮箱、参数格式、必填项完整性检查
- Mail Agent（邮件子智能体）
- Image Agent（图片生成子智能体）
- TTS Agent（TTS 子智能体）
- Weather Agent（天气子智能体）
- DigitalHuman Agent（数字人子智能体）
按以上要求进行设计


**特别注意：** 可参考 src.agents.deep_agent 用langchain 1.x + langGraph 1.x 实现以上需求 生成的代码存放在src.agents.multi_task_agent中

现在 multi_task_agent 邮件，图片制作，tts生成 天气查询 数字人制作逻逻辑都是对的，不过不应该把所有方法都放在一个agent上 应该用 主控智能体+多个子智能体的结构来构建所以 以src/agents/deep_agent 重构 multi_task_agent 生成的代码放入src/agents/master_sub_agent中 不要动multi_task_agent目录下的文件