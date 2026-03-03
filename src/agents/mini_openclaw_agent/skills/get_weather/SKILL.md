---
name: get_weather
description: 当用户要求对指定城市或地区进行天气查询或要获取某个城市的天气信息时, 那么就可以使用访技能.
license: Proprietary. LICENSE.txt has complete terms
---

# get_weather

**描述**: 获取指定城市的实时天气信息

## 使用方法

当用户询问天气时，按以下步骤操作：

### 步骤1：确定城市

从用户输入中提取城市名称（中文或英文）

### 步骤2：调用天气API

使用 `fetch_url` 工具访问天气服务：

fetch_url("https://wttr.in/{城市名}?format=j1&lang=zh")


示例：
fetch_url("https://wttr.in/北京?format=j1&lang=zh")


### 步骤3：解析结果

API 返回 JSON 格式数据，包含：
- `current_condition`: 当前天气
- `weather`: 未来几天预报

使用 `python_repl` 提取关键信息：

```python
import json

# 假设 weather_data 是 fetch_url 返回的内容
data = json.loads(weather_data)

current = data['current_condition'][0]
temp = current['temp_C']
desc = current['weatherDesc'][0]['value']
humidity = current['humidity']

print(f"当前温度: {temp}°C")
print(f"天气状况: {desc}")
print(f"湿度: {humidity}%")
步骤4：友好呈现
用自然语言告诉用户结果，例如： "北京现在的天气是晴天，气温25°C，湿度60%。"

示例对话
用户: 上海今天天气怎么样？

你的行动:

read_file("src/agents/mini_openclaw_agent/skills/get_weather/SKILL.md") ← 你正在做这一步
fetch_url("https://wttr.in/上海?format=j1&lang=zh")
使用 python_repl 解析数据
告诉用户结果
备用方案
如果 wttr.in 不可用，可以尝试：

OpenWeatherMap API
高德天气 API
或者告诉用户服务暂时不可用
