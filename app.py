import os
from flask import Flask, request, jsonify
import boto3
import sagemaker
from dotenv import load_dotenv
import json

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# 初始化 AWS 客户端 - 使用默认凭证链
session = boto3.Session(
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)

# 初始化 SageMaker 运行时客户端
sagemaker_runtime = session.client('sagemaker-runtime')
endpoint_name = os.getenv('SAGEMAKER_ENDPOINT_NAME')

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_input = data.get('message', '')
        
        if not user_input:
            return jsonify({'error': 'No message provided'}), 400

        # 调用 SageMaker 端点
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='application/json',
            Body=json.dumps({'inputs': user_input})
        )
        
        # 解析响应
        result = json.loads(response['Body'].read().decode())
        
        return jsonify({
            'response': result,
            'status': 'success'
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)