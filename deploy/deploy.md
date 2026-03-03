# 1. 系统部署



## 1.1 python环境准备(conda 为例)

```bash
conda create -n langchain-agent python=3.12.4 -y
conda activate langchain-agent
##  暂时不需要
#conda install -c conda-forge ffmpeg -y
#pip install -e .
```
## 1.2 依赖包安装

```bash
# 检查pip 是不就继，如果不存在就执行相应安装
pip --version (以下是相应pip版本信息)
pip 25.3 from /opt/miniconda3/envs/langchain-dev/lib/python3.12/site-packages/pip (python 3.12)
#在部署路径下获取工程
git clone http://8.137.51.150:9527/gitlab-instance-1463bf5d/Carbot-AI.git
cd Carbot-AI/deploy
#进行工程运行所需依赖安装
pip install -r requirements.txt
#或者 (生产环境)
proxychains4 pip install -r requirements.txt     
# 另外生产环境 用户是user 需要对它赋权  (sudo passworld:Password@021)
sudo chown -R user:user /export/deploy/python


```

## 1.3 docker 环境安装

```bash

#在当前工程根目录(Carbot-AI)下执行docker-complse 命令

#通过docker-compose 启动相服务,
docker-compose -f docker-compose.yml up     --->前台运行模式
docker-compose -f docker-compose.yml up -d  --->后台运行模式

conda activate langchain-agent

# mysql 单独运行(运行mysql docker 容器是为了验证客服agent访问本地数据库，如果不要客服agent mysql docker 就不用装) 
docker run --name mysql-container \
-e MYSQL_ROOT_PASSWORD=123456 \
-e MYSQL_DATABASE=mydb \
-e MYSQL_USER=myuser \
-e MYSQL_PASSWORD=123456 \
-p 3306:3306 \
-v mysql_data:/var/lib/mysql \
-d  mysql:latest

#注意docker-compose.yml在工程根目录下，其中只开放了必要的服务,如果要运行全部服务，就完全放开所有注释

```


## 1.4 启动服务

```bash

#在当前工程根目录(root)下执行
uvicorn server.main:app --host="0.0.0.0" --port=5050 --workers=1
#生产启动

nohup uvicorn server.main:app --host="0.0.0.0" --port=5050 --workers=1 > ../uvicorn.log 2>&1 &

```
## 1.5 运行一个mcp样例服务(确保一个独立的服务已运行，这里以weather_server为例)

```bash

#在当前工程根目录(root)下执行
python server/third-mcp-service/weather_server.py


```

## 1.6 服务就续验证(postman为例)

```bash

#在当前工程根目录(root)下执行
post 请求  http://0.0.0.0:5050/api/chat/agent/WeatherAgent

请求body传json格式数据:
{
    "query": "get current weather in tokyo",
    "config": {"thread_id": "",
                 "model":"local-ollama/cnshenyang/qwen3-nothink:14b"},
    "meta": {
            "query": "",
            "agent_id": "WeatherAgent",
            "server_model_name": "",
            "thread_id": "thread_test",
            "has_image": false
        }
    
}

# 返回的信息流中应该包含以下信息（从weather-server返回）

...
"request_id": "2dc14602-e454-4b41-a505-b0848671921e",
    "response": null,
    "msg": {
        "content": "Current Weather for Tokyo:\n🌡️  Temperature: 28°C\n☁️  Condition: Sunny\n💧 Humidity: 55%\n💨 Wind Speed: 8 km/h\n📝 Description: Clear skies and warm temperature",
        "additional_kwargs": {},
        "response_metadata": {},
        "type": "tool",
        "name": "get_weather",
        "id": "ee7b4ce3-911e-43ce-9fc6-a43f0f23d5a1",
        "tool_call_id": "call_egzlzag7",
        "artifact": null,
        "status": "success"
    },
....


```
## 1.7 启动前端web服务

```bash

#进行web目录 执行
nvm use 22
pnpm run dev
或者
pnpm run server
```

## 1.8 deepagent升级

从 0.3 升级到0.4.4 解决 无法从 chatbot 加载智能体: No module named 'deepagents.middleware.skills' 问题
```bash

pip install --upgrade deepagents==0.4.4   
```


