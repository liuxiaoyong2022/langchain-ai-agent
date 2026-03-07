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

## 代码优化记录

### 1. 各子智能体工具集拆分
- all_tools 拆分为各子智能体工具集 比如: mail_agent_tools  image_agent_tools,tts_agent_tools 等，
   具体每个子智能体的工具参考 src/agents/master_sub_agent/README.md中的子智能体说明
- 将对应的子智能体工具集 在子智能体初始化时赋值给对应的子智能体
- 代码修改仅限于 src/agents/master_sub_agent目录下，不要修改其它文件

### 2. 主智能体
- 优化主智能体的返回，让它如实返回子智能体的结果，不让它对智能体的结果进行二次加工
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

