# 长期记忆

## 2026-02-06
- 系统初始化完成
- 核心工具已配置：terminal, python_repl, fetch_url, read_file, search_knowledge_base

## 2025-02-13
### 系统技能总结

#### 核心工具（内置能力）：
1. **终端命令执行** (safter_terminal) - 在沙箱环境中执行shell命令
2. **Python代码执行** (python_repl) - 在隔离的REPL环境中运行Python代码
3. **网页内容获取** (fetch_url) - 从URL获取内容并转换为Markdown格式
4. **文件读取** (read_file) - 读取本地文件系统上的文件内容
5. **知识库搜索** (search_knowledge_base) - 搜索知识库中的相关信息

#### 已配置的技能（通过SKILL.md学习）：
1. **天气查询技能** (get_weather)
   - 功能：获取指定城市的实时天气信息
   - 使用方法：从用户输入提取城市名，调用天气API，解析并返回结果
   - 示例：fetch_url("https://wttr.in/北京?format=j1&lang=zh")

2. **图片生成技能** (mcp-minimax)
   - 功能：根据文字描述生成图片
   - 使用方法：调用Minimax API进行文生图
   - 需要环境变量：MINIMAX_API_KEY

3. **PDF处理技能** (pdf)
   - 功能：处理PDF文件的全面能力
   - 包括：读取/提取文本和表格、合并/拆分PDF、旋转页面、添加水印、创建新PDF、填充表单、加密/解密、提取图像、OCR扫描PDF等
   - 使用Python库：pypdf、pdfplumber、reportlab等

#### 智能体特性：
- **透明可控**：所有操作对用户可见，拒绝黑盒
- **文件即记忆**：记忆以Markdown/JSON文件形式存储
- **技能即插件**：通过阅读SKILL.md文件学习新能力
- **本地优先**：数据存储在用户本地，属于用户所有

#### 工作流程：
1. 理解用户需求
2. 检查是否有匹配的技能
3. 阅读技能文档（如果需要）
4. 调用基础工具执行任务
5. 将重要信息写入记忆

#### 行为准则：
- **透明化**：始终告诉用户正在调用哪个工具、执行什么操作
- **诚实性**：失败时如实报告错误
- **主动学习**：遇到新技能时立即read_file学习用法
- **安全意识**：执行危险操作前需二次确认

## 2025-02-13 图片生成记录
- 成功使用mcp-minimax技能生成图片
- 图片描述："一只可爱的熊猫在竹林里吃竹子，阳光透过竹叶洒下斑驳的光影，画面温馨自然"
- 生成时间：07:26:13
- 文件保存位置：/tmp/nginx/static/image/gen_out_put/20260213_072613_0.jpg
- 文件大小：283.9 KB
- 分辨率：1280×720 像素
- 格式：JPEG
- 使用API：Minimax Image Generation API (model: image-01)
- 展示页面：/tmp/generated_panda_image.html
## 2026-02-13 图片生成技能路径记录
- 图片生成技能(mcp-minimax)的正确路径是: ./src/agents/mini_openclaw_agent/skills/mcp-minimax/SKILL.md
- 注意：available_skills列表中的location路径'./skills/mcp-minimax/SKILL.md'是错误的，应该使用'./src/agents/mini_openclaw_agent/skills/mcp-minimax/SKILL.md'
- 其他技能的正确路径格式：./src/agents/mini_openclaw_agent/skills/{技能名}/SKILL.md

