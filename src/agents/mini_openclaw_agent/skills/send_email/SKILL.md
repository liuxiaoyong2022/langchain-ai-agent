---
name: send_email
description: 发送电子邮件的技能
license: Proprietary
---

# send_email

**描述**: 发送电子邮件到指定邮箱

## 使用方法

当用户需要发送邮件时，使用此技能。

### 输入参数
- 收件人邮箱 (to_email)
- 邮件主题 (subject)
- 邮件内容 (body)
- 发件人邮箱 (from_email) - 可选，默认为配置的邮箱
- 发件人密码 (password) - 可选，从环境变量读取

### 步骤
1. 检查必要的配置信息
2. 使用Python的smtplib发送邮件
3. 返回发送结果

### 环境变量配置
需要设置的环境变量：
- SMTP_SERVER: SMTP服务器地址（如：smtp.gmail.com）
- SMTP_PORT: SMTP端口（如：587）
- EMAIL_USER: 发件人邮箱
- EMAIL_PASSWORD: 发件人密码或应用密码

### 安全建议
- 建议使用环境变量存储密码
- 建议使用OAuth2认证
- 不要硬编码密码在代码中
