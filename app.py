import os
from flask import Flask, request, jsonify, render_template
import boto3
import sagemaker
from dotenv import load_dotenv
import json
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 初始化 AWS 客户端 - 使用默认凭证链
session = boto3.Session(
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)

# 初始化 SageMaker 运行时客户端
sagemaker_runtime = session.client('sagemaker-runtime')
endpoint_name = os.getenv('SAGEMAKER_ENDPOINT_NAME')

# 初始化 S3 客户端
s3 = boto3.client('s3')

# 存储上传的文件信息
uploaded_files = {}

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'files' not in request.files:
            return jsonify({'status': 'error', 'error': 'No file part'})

        files = request.files.getlist('files')
        uploaded = []

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_id = str(uuid.uuid4())
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_id)
                file.save(file_path)
                
                # 存储文件信息
                uploaded_files[file_id] = {
                    'name': filename,
                    'path': file_path,
                    'upload_time': datetime.now().isoformat(),
                    'processed': False
                }
                
                # 处理文档（可以在这里添加文档处理逻辑）
                process_document(file_id)
                
                uploaded.append({
                    'id': file_id,
                    'name': filename
                })

        return jsonify({
            'status': 'success',
            'files': uploaded
        })

    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

@app.route('/remove-file/<file_id>', methods=['DELETE'])
def remove_file(file_id):
    try:
        if file_id in uploaded_files:
            file_path = uploaded_files[file_id]['path']
            if os.path.exists(file_path):
                os.remove(file_path)
            del uploaded_files[file_id]
            return jsonify({'status': 'success'})
        return jsonify({'status': 'error', 'error': 'File not found'})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

def process_document(file_id):
    """处理上传的文档，例如提取文本、创建嵌入等"""
    try:
        file_info = uploaded_files[file_id]
        file_path = file_info['path']
        
        # 这里添加文档处理逻辑
        # 例如：提取文本、创建嵌入、存储到向量数据库等
        
        file_info['processed'] = True
        
    except Exception as e:
        print(f"处理文档时出错: {str(e)}")

@app.route('/chat', methods=['POST'])
def chat():
    """处理一般问答"""
    try:
        user_message = request.json.get('message')
        
        # 调用 SageMaker 端点进行一般问答
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='application/json',
            Body=json.dumps({
                'inputs': user_message,
                'parameters': {
                    'max_new_tokens': 500,
                    'temperature': 0.7
                }
            })
        )
        
        response_body = json.loads(response['Body'].read().decode())
        
        return jsonify({
            'status': 'success',
            'response': response_body
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

@app.route('/doc-chat', methods=['POST'])
def doc_chat():
    """处理基于文档的问答"""
    try:
        user_message = request.json.get('message')
        document_ids = request.json.get('documents', [])
        
        # 获取相关文档的内容
        documents_content = []
        for doc_id in document_ids:
            if doc_id in uploaded_files and uploaded_files[doc_id]['processed']:
                with open(uploaded_files[doc_id]['path'], 'r') as f:
                    documents_content.append(f.read())
        
        # 调用 SageMaker 端点进行文档问答
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='application/json',
            Body=json.dumps({
                'inputs': user_message,
                'documents': documents_content,
                'parameters': {
                    'max_new_tokens': 500,
                    'temperature': 0.7
                }
            })
        )
        
        response_body = json.loads(response['Body'].read().decode())
        
        return jsonify({
            'status': 'success',
            'response': response_body
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)