# SMTP 邮件发送

Python 使用内置 `smtplib` 和 `email` 模块发送邮件。

## 基础邮件发送

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

msg = MIMEMultipart()
msg['From'] = 'sender@example.com'
msg['To'] = 'receiver@example.com'
msg['Subject'] = '测试邮件'

body = "这是一封测试邮件"
msg.attach(MIMEText(body, 'plain'))

server = smtplib.SMTP('smtp.example.com', 587)
server.starttls()
server.login('sender@example.com', 'password')
server.send_message(msg)
server.quit()
```

## 科研实战场景

### 1. 实验完成通知

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

class ExperimentNotifier:
    def __init__(self, smtp_server: str, email: str, password: str):
        self.smtp_server = smtp_server
        self.email = email
        self.password = password

    def send_experiment_complete(
        self, to_email: str, experiment_name: str, metrics: dict
    ):
        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = to_email
        msg['Subject'] = f"[实验完成] {experiment_name}"

        body = f'''
实验名称：{experiment_name}
状态：完成
Loss: {metrics.get('loss')}
Accuracy: {metrics.get('accuracy')}
        '''
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(self.smtp_server, 587) as server:
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)
```

### 2. 异常告警

```python
import traceback

def send_alert_on_failure(experiment_name: str, error: Exception, alert_email: str):
    msg = MIMEMultipart()
    msg['Subject'] = f"[告警] 实验失败：{experiment_name}"
    body = f"错误：{str(error)}\n\n{traceback.format_exc()}"
    msg.attach(MIMEText(body, 'plain'))
    # 发送...
```

## 易错点

### 1. Gmail 需要应用专用密码
Gmail 不再支持直接使用账户密码，需要启用 2FA 并生成应用专用密码。

### 2. 端口和加密
- SMTP (无加密) - 端口 25
- SMTP + STARTTLS - 端口 587 (推荐)
- SMTPS (SSL/TLS) - 端口 465

## 性能提示

邮件发送是 IO 密集型操作，建议使用异步或后台任务。
