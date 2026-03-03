---
name: mcp-minimax
description: Use this skill whenever the user wants to generate image from image description
license: Proprietary. LICENSE.txt has complete terms
---

# image generation Processing Guide

## Overview

从用户输入中提取图片描述信息,然后调用文生图方法进行图片生成
可以 通过 python_repl 调用invoke_text_to_image 
## simple image generation by text 


```python
import base64
import requests
import os
from datetime import datetime
minimax_api_key = os.environ["MINIMAX_API_KEY"]
headers = {"Authorization": f"Bearer {minimax_api_key}"}


# --- Step 1: Create a image generation task ---
# The API supports four modes: text-to-image, 
# Each function below starts an asynchronous task and returns a unique task_id.

def invoke_text_to_image(image_desc:str) -> str:
    """(Mode 1) Create a video generation task from a text description.
    
    return :返回当前已生成图片的访问地址url
    """
    url = "https://api.minimax.io/v1/image_generation"
    payload = {
    "model": "image-01",
    "prompt":image_desc,
    "aspect_ratio": "16:9",
    "response_format": "base64",
}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    images = response.json()["data"]["image_base64"]
    image_url=None
    for i in range(len(images)):
        filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
        file_path=f"/tmp/nginx/static/image/gen_out_put/{filename}"
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(images[i]))
        image_url=f"http://localhost:8080/static/image/gen_out_put/{filename}"
    return image_url
```

## Python Libraries

### pypdf - Basic Operations

