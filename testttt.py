from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import json
import time

app = Flask(__name__)
CORS(app)  # 允许跨域请求

def task_distribution(text: str) -> dict:
    """
    任务分发器 - 根据文本内容判断任务类型
    """
    # 模拟分析过程
    time.sleep(0.5)  # 模拟分析时间
    
    # 定义关键词
    market_keywords = ["产品", "市场", "竞争", "销售", "价格", "保费", "保险产品", "市场份额", "竞争对手", "比较", "排名"]
    macro_keywords = ["宏观", "经济", "政策", "趋势", "发展", "环境", "法规", "监管", "行业", "未来", "预测", "展望"]
    
    # 统计关键词出现次数
    market_count = sum(1 for keyword in market_keywords if keyword in text)
    macro_count = sum(1 for keyword in macro_keywords if keyword in text)
    
    # 根据关键词数量决定任务类型
    if market_count > macro_count:
        return {"task_type": "产品市场概览"}
    elif macro_count > market_count:
        return {"task_type": "宏观保险分析"}
    else:
        # 如果关键词数量相等，根据特定关键词决定
        if any(keyword in text for keyword in ["产品", "市场", "竞争"]):
            return {"task_type": "产品市场概览"}
        else:
            return {"task_type": "宏观保险分析"}

def generate_market_dataframe() -> dict:
    """
    生成产品市场概览的DataFrame数据
    """
    # 模拟数据处理时间
    time.sleep(1)
    
    data = {
        "保险产品": ["健康险", "人寿险", "车险", "财产险", "意外险"],
        "市场份额(%)": [25.3, 18.7, 32.1, 15.4, 8.5],
        "年增长率(%)": [12.5, 8.3, 5.7, 9.2, 15.8],
        "平均保费(元)": [3200, 4500, 2800, 1800, 850],
        "主要竞争者": ["平安、国寿、太保", "平安、太平、新华", "人保、平安、太保", "太保、大地、阳光", "众安、泰康、平安"]
    }
    
    df = pd.DataFrame(data)
    print(df)
    print({
        "columns": df.columns.tolist(),
        "data": df.values.tolist()
    })
    
    # 将DataFrame转换为可序列化的字典格式
    return {
        "columns": df.columns.tolist(),
        "data": df.values.tolist()
    }

def generate_macro_analysis_response(text: str) -> str:
    """
    生成宏观保险分析的详细回复
    """
    # 模拟数据处理时间
    time.sleep(1)
    
    detailed_responses = [
        "从宏观角度看，保险行业正面临低利率环境、监管变化和科技创新的三重挑战。数字化转型成为行业共识，人工智能和大数据分析正在重塑保险价值链。2023年，全球保险科技投资达到创纪录的158亿美元，同比增长22%。主要投资领域包括数据分析(35%)、物联网应用(28%)和区块链技术(18%)。",
        
        "宏观经济波动对保险业产生显著影响。在经济下行周期，保障型产品需求相对稳定，而投资型产品销售可能受到冲击。人口老龄化是长期驱动因素，预计到2035年，中国60岁以上人口占比将超过30%，这将显著增加养老和健康保险需求。同时，中产阶级扩张和收入增长为保险渗透率提升提供了坚实基础。",
        
        "监管环境日趋严格，数据隐私和消费者保护成为关注焦点。2023年新出台的《保险科技监管指引》强调风险管控和消费者权益保护。同时，监管沙盒等创新机制为保险科技公司提供了试验空间，已有47家机构参与试点，推动了保险产品和服务创新。",
        
        "保险行业数字化转型加速，线上渠道保费占比从2020年的15%提升至2023年的28%。人工智能在核保、理赔和客服环节的应用显著提升了效率，平均处理时间缩短40%。区块链技术在再保险和防欺诈领域的应用也取得突破性进展。"
    ]
    
    # 简单逻辑：根据文本长度选择回复
    return detailed_responses[len(text) % len(detailed_responses)]

def text_process(text: str, task_type: str) -> dict:
    """
    根据任务类型处理文本并返回相应格式的响应
    """
    if task_type == "产品市场概览":
        dataframe_data = generate_market_dataframe()
        return {
            "response": "以下是当前保险产品市场概览数据：",
            "response_type": "dataframe",
            "dataframe": dataframe_data
        }
    elif task_type == "宏观保险分析":
        detailed_response = generate_macro_analysis_response(text)
        return {
            "response": "宏观保险分析已完成",
            "response_type": "text", 
            "detailed_response": detailed_response
        }
    else:
        return {
            "response": "感谢您的咨询。请提供更多关于您感兴趣的保险类型的信息。",
            "response_type": "text",
            "detailed_response": "未能识别具体的任务类型，请尝试使用更明确的关键词，如'市场情况'、'产品比较'、'行业趋势'或'政策分析'等。"
        }

@app.route('/process', methods=['POST'])
def process_text():
    """
    处理前端发送的文本
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': '没有收到文本'}), 400
        
        # 调用任务分发器
        task_result = task_distribution(text)
        task_type = task_result.get('task_type', '未知任务')
        
        # 根据任务类型处理文本
        response_data = text_process(text, task_type)
        response_data['task_type'] = task_type
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)