# SageMaker Chatbot

这是一个基于Amazon SageMaker的聊天机器人应用，使用Flask作为后端框架。

## 项目设置

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 配置环境变量
- 复制 `.env.example` 文件并重命名为 `.env`
- 填入你的AWS凭证和SageMaker端点信息：
  - AWS_ACCESS_KEY_ID
  - AWS_SECRET_ACCESS_KEY
  - AWS_REGION
  - SAGEMAKER_ENDPOINT_NAME

3. 运行应用
```bash
python app.py
```

应用将在 http://localhost:5000 启动

## 项目结构

- `app.py`: Flask应用主文件
- `static/index.html`: 前端界面
- `requirements.txt`: 项目依赖
- `.env`: 环境变量配置（需要自行创建）

## 使用说明

1. 访问 http://localhost:5000
2. 在输入框中输入消息
3. 点击发送按钮或按Enter键发送消息
4. 等待AI响应

## 注意事项

- 确保你有有效的AWS凭证
- 确保指定的SageMaker端点已经部署并且正在运行
- 确保端点接受JSON格式的输入，并返回文本响应