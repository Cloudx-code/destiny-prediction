from flask import Flask, render_template, request, jsonify
from datetime import datetime
import os
from dotenv import load_dotenv
import json
import requests
import threading
from queue import Queue

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# 配置智谱AI
api_key = os.getenv('ZHIPUAI_API_KEY')
if not api_key:
    raise ValueError("未找到智谱AI API密钥！请确保.env文件中包含ZHIPUAI_API_KEY")

def get_chinese_zodiac(year):
    """获取生肖"""
    zodiac_animals = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
    return zodiac_animals[(year - 4) % 12]

def get_zodiac_sign(month, day):
    """获取星座"""
    zodiac_dates = [
        (1, 20, '摩羯座'), (2, 19, '水瓶座'), (3, 20, '双鱼座'),
        (4, 20, '白羊座'), (5, 21, '金牛座'), (6, 21, '双子座'),
        (7, 23, '巨蟹座'), (8, 23, '狮子座'), (9, 23, '处女座'),
        (10, 23, '天秤座'), (11, 22, '天蝎座'), (12, 22, '射手座')
    ]
    
    if day < zodiac_dates[month-1][1]:
        return zodiac_dates[month-1][2] if month == 1 else zodiac_dates[month-2][2]
    return zodiac_dates[month-1][2]

def generate_initial_response(user_data):
    """生成初始响应"""
    birth_date = datetime.strptime(user_data['birthDate'], '%Y-%m-%dT%H:%M')
    zodiac = get_chinese_zodiac(birth_date.year)
    star_sign = get_zodiac_sign(birth_date.month, birth_date.day)
    
    return {
        'success': True,
        'status': 'processing',
        'initial_message': f"""尊敬的{user_data['name']}您好！

我正在为您生成详细的运势预测，这可能需要一点时间。

您的基本信息：
- 生肖：{zodiac}
- 星座：{star_sign}

请稍候，完整预测很快就来..."""
    }

def call_zhipu_api(user_data, result_queue):
    """在后台调用智谱AI API"""
    try:
        birth_date = datetime.strptime(user_data['birthDate'], '%Y-%m-%dT%H:%M')
        
        request_data = {
            "model": "glm-4-flash",
            "messages": [
                {
                    "role": "user",
                    "content": f"""您是一位德高望重的命理大师，请为以下用户提供运势预测：

用户信息：
姓名：{user_data['name']}
出生时间：{birth_date.strftime('%Y年%m月%d日 %H时%M分')}
出生地：{user_data['birthPlace']}

请提供简明扼要的预测：

一、2024年运势要点
二、2025年运势要点
三、开运建议"""
                }
            ]
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            headers=headers,
            json=request_data,
            timeout=240  # 设置为4分钟，留出一些缓冲时间
        )
        
        if response.status_code == 200:
            result = response.json()
            prediction = result['choices'][0]['message']['content']
            result_queue.put(('success', prediction))
        else:
            result_queue.put(('error', f"API请求失败: {response.text}"))
            
    except Exception as e:
        result_queue.put(('error', str(e)))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        if not data or not all(key in data for key in ['name', 'birthDate', 'birthPlace']):
            return jsonify({
                'error': '请提供完整的信息：姓名、出生时间和出生地点'
            }), 400

        # 立即返回初始响应
        initial_response = generate_initial_response(data)
        
        # 启动后台线程处理API请求
        result_queue = Queue()
        api_thread = threading.Thread(target=call_zhipu_api, args=(data, result_queue))
        api_thread.start()
        
        # 等待最多8秒获取结果
        api_thread.join(timeout=8)
        
        if not result_queue.empty():
            status, result = result_queue.get()
            if status == 'success':
                return jsonify({
                    'success': True,
                    'status': 'completed',
                    'prediction': result
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result
                }), 500
        else:
            # 如果超时，返回处理中的消息
            return jsonify(initial_response)
            
    except Exception as e:
        print(f"处理请求时发生错误: {str(e)}")
        return jsonify({
            'error': '抱歉，服务器暂时无法处理您的请求，请稍后再试'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
