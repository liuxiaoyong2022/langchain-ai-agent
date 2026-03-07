# 主控+子智能体系统 (Master-Sub Agent)

基于 `deep_agent` 架构，使用 `SubAgentMiddleware` 实现主控智能体和多个子智能体协作。

## 架构设计

```
┌─────────────────────────────────────────────────────┐
│         Master Agent (主控智能体)                     │
│  - 理解用户意图                                       │
│  - 调度子智能体                                       │
│  - 汇总结果                                           │
└─────────────────────────────────────────────────────┘
                          │
                          ├──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
                          │              │              │              │              │              │
                          ▼              ▼              ▼              ▼              ▼              ▼
              ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
              │  mail-agent  │  │ image-agent  │  │  tts-agent   │  │weather-agent │  │digital-human │
              │  邮件子智能体  │  │ 图片生成子智能体│  │  TTS子智能体  │  │ 天气查询子智能体│  │    -agent     │
              └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

## 核心特性

### 1. 主控智能体
- 理解用户意图
- 调度子智能体处理任务
- 汇总子智能体的执行结果

### 2. 子智能体
- **mail-agent**: 处理邮件发送任务
- **image-agent**: 处理图片生成任务
- **tts-agent**: 处理文本转语音任务
- **weather-agent**: 处理天气查询任务
- **digital-human-agent**: 处理数字人视频制作任务

### 3. SubAgentMiddleware
- 管理所有子智能体
- 自动将任务路由到对应的子智能体
- 处理子智能体的调用和结果汇总

## 工作流程

### 标准任务流程

```
用户输入
    ↓
主控智能体理解意图
    ↓
SubAgentMiddleware 路由到对应的子智能体
    ↓
子智能体处理任务
    ↓
子智能体返回结果
    ↓
主控智能体汇总结果
    ↓
返回给用户
```

## 子智能体详解

### 1. mail-agent（邮件子智能体）
**功能**：发送邮件
**工具**：
- `validate_email_address`: 验证邮箱格式
- `send_email`: 发送邮件

**工作流程**：
1. 多轮对话收集：收件人邮箱、主题、内容
2. 使用 `validate_email_address` 验证邮箱格式
3. 展示信息并请求用户确认（yes/no）
4. 用户确认后调用 `send_email` 发送邮件

### 2. image-agent（图片生成子智能体）
**功能**：生成图片
**工具**：
- `validate_image_params`: 验证图片参数
- `generate_image`: 生成图片

**工作流程**：
1. 多轮对话收集：图片描述、风格、尺寸、数量
2. 使用 `validate_image_params` 验证参数
3. 展示信息并请求用户确认（yes/no）
4. 用户确认后调用 `generate_image` 生成图片

### 3. tts-agent（TTS子智能体）
**功能**：生成语音
**工具**：
- `validate_tts_params`: 验证TTS参数
- `generate_tts`: 生成语音

**工作流程**：
1. 多轮对话收集：语音文案、声音样本（可选）
2. 使用 `validate_tts_params` 验证参数
3. 展示信息并请求用户确认（yes/no）
4. 用户确认后调用 `generate_tts` 生成语音

### 4. weather-agent（天气查询子智能体）
**功能**：查询天气
**工具**：
- `query_weather`: 查询天气

**工作流程**：
1. 多轮对话收集：城市名
2. 直接调用 `query_weather` 查询天气（无需确认）

### 5. digital-human-agent（数字人子智能体）
**功能**：制作数字人视频
**工具**：
- `validate_digital_human_params`: 验证数字人参数
- `create_digital_human`: 创建数字人视频

**工作流程**：
1. 多轮对话收集：数字人图片、口播文稿、声音样本（可选）
2. 使用 `validate_digital_human_params` 验证参数
3. 展示信息并请求用户确认（yes/no）
4. 用户确认后调用 `create_digital_human` 制作视频

## 文件结构

```
src/agents/master_sub_agent/
├── __init__.py              # 模块初始化
├── context.py               # 上下文配置
├── tools.py                 # 工具定义
├── graph.py                 # 主图构建
└── metadata.toml            # 元数据配置
```

## 与 multi_task_agent 的对比

### multi_task_agent
- 所有逻辑在一个智能体中
- LLM 直接调用工具
- 简单但不够模块化

### master_sub_agent（当前实现）
- 主控智能体 + 多个子智能体
- SubAgentMiddleware 自动路由
- 更模块化，更易维护
- 子智能体独立配置和优化

## 使用示例

### 发送邮件

```python
from langchain_core.messages import HumanMessage
from src.agents.master_sub_agent import MasterSubAgent

agent = MasterSubAgent()

async for message, metadata in agent.stream_messages(
    messages=[HumanMessage(content="帮我发个邮件")],
    input_context={
        "thread_id": "your_thread_id",
        "user_id": "your_user_id",
    },
):
    print(message.content)
```

**对话流程**：
1. 用户：帮我发个邮件
2. 主控智能体：识别意图，调用 mail-agent
3. mail-agent：好的，我可以帮您发送邮件。请问收件人的邮箱地址是什么？
4. 用户：test@example.com
5. mail-agent：[调用 validate_email_address] 邮箱主题是什么？
6. ...（后续对话由 mail-agent 处理）

### 生成图片

```python
async for message, metadata in agent.stream_messages(
    messages=[HumanMessage(content="帮我生成一张猫的图片")],
    input_context={...},
):
    print(message.content)
```

## 技术栈

- **LangChain 1.x**: LLM 应用框架
- **LangGraph 1.x**: 图构建框架
- **SubAgentMiddleware**: 子智能体管理（来自 deepagents）
- **Python 3.12+**: 编程语言

## 扩展指南

### 添加新的子智能体

1. 在 `graph.py` 中定义新的子智能体函数
2. 实现子智能体的 `system_prompt`
3. 指定子智能体需要的工具
4. 将子智能体添加到 `subagents` 列表

### 自定义工具

所有工具都在 `tools.py` 中定义，可以根据实际需求修改或添加新工具。

## 注意事项

1. **模型选择**：建议使用能力较强的模型（如 DeepSeek-V3）
2. **API配置**：实际使用时需要配置相应的 API Key
3. **错误处理**：当前实现为模拟工具，需接入真实服务接口
4. **子智能体配置**：每个子智能体可以独立配置模型和工具

## 测试

运行测试脚本：

```bash
docker compose exec api uv run python test_master_sub_agent.py
```

或在容器中：

```bash
cd /app
uv run python test_master_sub_agent.py
```

## 版本历史

- **v1.0**: 初始版本，基于 deep_agent 架构实现主控+子智能体系统
