---
name: mcp-minimax
description: Use this skill whenever the user wants to generate image from image description
license: Proprietary. LICENSE.txt has complete terms
---

# image generation Processing Guide

## 使用方法

当用户要求生成图片时按以下步骤操作：

### 步骤1：收集图片描述信息

从用户输入中提取：
   1. 图片描述信息(image_desc),例如： "请帮我生成一张夕阳下的海滩图片" 中的图片描述信息是 "夕阳下的海滩图片"。
   2. 图片风格信息(image_style),例如 图片风格信息是 "卡通风格","写实风格","印象风格","油画风格"。
   3. 图片长宽比例(aspect_ratio),例如 图片大小是 "1:1"，"16:9"
   4. 图片张数(image_num),例如 图片张数是 "1"，"2"，"3"
- 如果用户没有提供足够的信息，可以通过友好地提问来获取更多细节
- 一次只提出一个问题，等待用户回答后再继续提问，不要对已知信息提问或重复提问,直到收集到足够的信息为止。
**当用户提供了足够的信息后**，将收集到的信息展示给用户，提示下一步的操作 需要用户确认是否继续生成图片，例如：
- "你想要生成一张夕阳下的海滩图片，风格     是卡通风格，尺寸是512x512，对吗？如果需要修改，请告诉我你想要的图片是什么样子的？"
- 当用户确认后(yes/是的)，进入下一步操作 否则取消操作，结束流程。

### 步骤2：生成图片

使用 `python_repl` 工具调用 `invoke_text_to_image` 函数进行图片生成：

```python
import base64
import requests
import os
from datetime import datetime
minimax_api_key = os.environ["MINIMAX_API_KEY"]
headers = {"Authorization": f"Bearer {minimax_api_key}"}
import time

# --- Step 1: Create a image generation task ---
# The API supports four modes: text-to-image, 
# Each function below starts an asynchronous task and returns a unique task_id.

def invoke_text_to_image(image_desc:str,image_style:str,image_size:str,image_num:int) -> str:
    """(Mode 1) Create a video generation task from a text description.
    
    return :返回当前已生成图片的访问地址url
    """
    url = "https://api.minimax.io/v1/image_generation"
    payload = {
    "model": "image-01",
    "prompt":image_desc,
    "aspect_ratio": "16:9",
    "response_format": "base64",
    "n":image_num
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    images = response.json()["data"]["image_base64"]
    image_url=None
    for i in range(image_num):
        filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
        file_path=f"./out_put/image/gen_out_put/{filename}"
        # file_path=f"/tmp/nginx/static/image/gen_out_put/{filename}"
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(images[i]))
            #image_url=f"http://localhost:8080/static/image/gen_out_put/{filename}"
            image_url=f"file_path:{file_path}"
    return image_url

    
    # time.sleep(5)  # 模拟图片生成的时间
    # return "http://localhost:8080/static/image/gen_out_put/sample.jpg"

```

## Python Libraries

### pypdf - Basic Operations

