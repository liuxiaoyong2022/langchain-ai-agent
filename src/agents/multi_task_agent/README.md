# 多任务协作智能体 (Multi-Task Agent)

基于 LangGraph 1.x 构建的多智能体协作系统，支持多种任务的处理和协作。

## 架构设计

### 智能体层次结构

```
┌─────────────────────────────────────────────────────┐
│           Orchestrator Agent (主控智能体)              │
│  - 意图识别                                           │
│  - 任务分发                                           │
│  - 结果汇总                                           │
└─────────────────────────────────────────────────────┘
                          │
                          ├──────────────────┬──────────────────┬──────────────────┬──────────────────┬──────────────────┐
                          │                  │                  │                  │                  │                  │
                          ▼                  ▼                  ▼                  ▼                  ▼                  ▼
              ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
              │  Mail Agent  │  │ Image Agent  │  │  TTS Agent   │  │Weather Agent │  │ DigitalHuman │  │  Other Tasks │
              │   邮件子智能体  │  │ 图片生成子智能体│  │  TTS子智能体  │  │ 天气查询子智能体│  │   Agent      │  │  (待扩展)     │
              └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

### 核心组件

1. **主控智能体 (Orchestrator Agent)**
   - 负责理解用户意图
   - 将任务路由到对应的子智能体
   - 汇总子智能体的执行结果

2. **功能子智能体**
   - **邮件子智能体** (Mail Agent): 处理邮件发送任务
   - **图片生成子智能体** (Image Agent): 处理图片生成任务
   - **TTS子智能体** (TTS Agent): 处理文本转语音任务
   - **天气查询子智能体** (Weather Agent): 处理天气查询任务
   - **数字人子智能体** (DigitalHuman Agent): 处理数字人视频制作任务

3. **工具层 (Tools)**
   - 提供各个子智能体所需的具体工具
   - 包括参数校验工具和任务执行工具

## 工作流程

### 1. 邮件任务流程

```
用户输入 → 主控智能体识别意图 → 邮件子智能体
                                    ↓
                            多轮对话收集信息
                            - 收件人邮箱
                            - 邮件主题
                            - 邮件内容
                                    ↓
                            参数校验
                                    ↓
                            展示信息并请求确认
                                    ↓
                            用户确认 (yes/no)
                                    ↓
                            发送邮件或取消
```

### 2. 图片生成任务流程

```
用户输入 → 主控智能体识别意图 → 图片生成子智能体
                                    ↓
                            多轮对话收集信息
                            - 图片描述
                            - 图片风格
                            - 图片尺寸 (宽*高)
                            - 图片数量
                                    ↓
                            参数校验
                                    ↓
                            展示信息并请求确认
                                    ↓
                            用户确认 (yes/no)
                                    ↓
                            生成图片或取消
```

### 3. TTS任务流程

```
用户输入 → 主控智能体识别意图 → TTS子智能体
                                    ↓
                            多轮对话收集信息
                            - 语音文案
                            - 语音样本 (可选)
                                    ↓
                            参数校验
                                    ↓
                            展示信息并请求确认
                                    ↓
                            用户确认 (yes/no)
                                    ↓
                            生成TTS或取消
```

### 4. 天气查询任务流程

```
用户输入 → 主控智能体识别意图 → 天气查询子智能体
                                    ↓
                            多轮对话收集信息
                            - 城市名
                                    ↓
                            查询天气
                                    ↓
                            返回天气信息
```

### 5. 数字人任务流程

```
用户输入 → 主控智能体识别意图 → 数字人子智能体
                                    ↓
                            多轮对话收集信息
                            - 数字人图片
                            - 口播文稿
                            - 声音样本 (可选)
                                    ↓
                            参数校验
                                    ↓
                            展示信息并请求确认
                                    ↓
                            用户确认 (yes/no)
                                    ↓
                            制作数字人视频或取消
```

## 文件结构

```
src/agents/multi_task_agent/
├── __init__.py              # 模块初始化
├── context.py               # 上下文配置
├── state.py                 # 状态定义
├── tools.py                 # 工具定义
├── graph.py                 # 主图构建
├── metadata.toml            # 元数据配置
├── README.md                # 说明文档
└── agents/                  # 子智能体实现
    ├── __init__.py
    ├── mail_agent.py        # 邮件子智能体
    ├── image_agent.py       # 图片生成子智能体
    ├── tts_agent.py         # TTS子智能体
    ├── weather_agent.py     # 天气查询子智能体
    └── digital_human_agent.py # 数字人子智能体
```

## 核心特性

### 1. 多轮对话信息收集

每个子智能体都支持多轮对话来收集必要的信息，确保信息的完整性和准确性。

### 2. 参数校验机制

在执行任务前，会对所有参数进行校验，确保参数的合法性和完整性。

### 3. 用户确认机制

对于实质性操作（如发送邮件、生成图片等），在执行前会向用户展示关键信息并请求确认，确保操作的安全性。

### 4. 友好的交互体验

保持对话的自然和友好，提供清晰的操作指引和反馈。

### 5. 可扩展性

基于 LangGraph 的模块化设计，可以轻松添加新的子智能体和功能。

## 使用示例

### 发送邮件

```python
from langchain_core.messages import HumanMessage
from src.agents.multi_task_agent import MultiTaskAgent

agent = MultiTaskAgent()

async for message, metadata in agent.stream_messages(
    messages=[HumanMessage(content="帮我发个邮件")],
    input_context={
        "thread_id": "your_thread_id",
        "user_id": "your_user_id",
    },
):
    print(message.content)
```

对话流程：
1. 用户：帮我发个邮件
2. 智能体：好的，我可以帮您发送邮件。请告诉我收件人邮箱地址是什么？
3. 用户：test@example.com
4. 智能体：邮件主题是什么？
5. 用户：项目进展
6. 智能体：邮件内容是什么？
7. 用户：项目进展顺利
8. 智能体：准备发送邮件：[展示信息] 请确认是否发送（回复 yes 或 no）：
9. 用户：yes
10. 智能体：[执行发送] 邮件已成功发送！

### 生成图片

```python
from langchain_core.messages import HumanMessage
from src.agents.multi_task_agent import MultiTaskAgent

agent = MultiTaskAgent()

async for message, metadata in agent.stream_messages(
    messages=[HumanMessage(content="帮我生成一张猫的图片")],
    input_context={
        "thread_id": "your_thread_id",
        "user_id": "your_user_id",
    },
):
    print(message.content)
```

### 查询天气

```python
from langchain_core.messages import HumanMessage
from src.agents.multi_task_agent import MultiTaskAgent

agent = MultiTaskAgent()

async for message, metadata in agent.stream_messages(
    messages=[HumanMessage(content="今天北京的天气怎么样")],
    input_context={
        "thread_id": "your_thread_id",
        "user_id": "your_user_id",
    },
):
    print(message.content)
```

## 技术栈

- **LangChain 1.x**: LLM 应用框架
- **LangGraph 1.x**: 多智能体编排框架
- **Python 3.12+**: 编程语言

## 扩展指南

### 添加新的子智能体

1. 在 `agents/` 目录下创建新的子智能体文件
2. 实现子智能体节点函数
3. 在 `agents/__init__.py` 中导出
4. 在 `graph.py` 中注册节点和路由逻辑
5. 在 `tools.py` 中添加必要的工具

### 自定义工具

所有工具都在 `tools.py` 中定义，每个工具包含：
- 参数校验工具（validate_*）
- 任务执行工具（execute_*）

可以根据实际需求修改或添加新的工具。

## 注意事项

1. **模型选择**: 建议使用能力较强的模型（如 DeepSeek-V3）以获得更好的意图识别和对话效果
2. **API配置**: 需要配置相应的 API Key（如邮件服务、图片生成服务等）
3. **错误处理**: 当前实现为模拟工具，实际使用时需要接入真实的服务接口
4. **性能优化**: 可以通过调整模型的 temperature、max_tokens 等参数来优化性能

## 测试

运行测试脚本：

```bash
docker compose exec api uv run python test_multi_task_agent.py
```

或在容器中：

```bash
cd /app
uv run python test_multi_task_agent.py
```
