
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from datetime import datetime
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 从环境变量获取DeepSeek API密钥，如果没有则使用默认值
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'sk-a283b025a918497fb0945aca55908ff1')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"  # 请根据实际API端点调整

@app.route('/process_speech', methods=['POST'])
def process_speech():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': '没有接收到文本'}), 400
        
        print(f"接收到语音文本: {text}")
        
        # 调用DeepSeek API
        deepseek_response = call_deepseek_api(text)
        
        # 返回响应
        return jsonify({
            'response': deepseek_response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"处理请求时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

def call_deepseek_api(text):
    """
    调用DeepSeek API并返回响应
    """
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}'
        }
        
        payload = {
            'model': 'deepseek-chat',  # 根据实际情况调整模型名称
            'messages': [
                {'role': 'user', 'content': text}
            ],
            'max_tokens': 500,
            'temperature': 0.7
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # 提取AI回复内容
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        else:
            return "抱歉，我没有理解您的问题。"
            
    except requests.exceptions.RequestException as e:
        print(f"调用DeepSeek API时出错: {str(e)}")
        return f"API调用错误: {str(e)}"
    except Exception as e:
        print(f"处理DeepSeek响应时出错: {str(e)}")
        return f"处理响应时出错: {str(e)}"







if __name__ == '__main__':
    # 启动服务器
    app.run(host='0.0.0.0', port=5000, debug=True)