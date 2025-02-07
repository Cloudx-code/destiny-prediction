from flask import Flask, render_template, request, jsonify
from datetime import datetime
import os
from dotenv import load_dotenv
import json
import requests

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

def generate_ai_prediction(user_data):
    """使用智谱AI生成预测"""
    try:
        print("开始生成AI预测...")
        print(f"用户数据: {json.dumps(user_data, ensure_ascii=False)}")
        
        birth_date = datetime.strptime(user_data['birthDate'], '%Y-%m-%dT%H:%M')
        
        # 构建请求数据
        request_data = {
            "model": "glm-4-flash",
            "messages": [
                {
                    "role": "user",
                    "content": f"""你是一位德高望重的命理大师，精通中国传统命理学、八字、五行、风水等领域，并且能够用现代人易于理解的方式来解读命理。请根据用户提供的信息，结合传统智慧和现代分析方法，为用户提供未来运势预测。预测需要积极向上、实用可行、有理有据。

请为以下用户提供2024年和2025年的运势预测：

用户基本信息：
姓名：{user_data['name']}
出生时间：{user_data['birthDate']}
出生地：{user_data['birthPlace']}

请按照以下格式提供预测：

一、2024年运势
1. 重大事件预测：
   - 事业发展
   - 财运变化
   - 感情状况
   - 健康情况
2. 需要特别注意的事项：
   - 重点时间段
   - 具体注意事项

二、2025年运势
1. 重大事件预测：
   - 事业发展
   - 财运变化
   - 感情状况
   - 健康情况
2. 需要特别注意的事项：
   - 重点时间段
   - 具体注意事项

三、文化解读
1. 命理分析依据
2. 五行特点分析
3. 吉凶方位建议
4. 开运建议"""
                }
            ]
        }

        print("正在调用智谱AI API...")
        print(f"使用的API密钥前8位: {api_key[:8]}...")

        try:
            # 发送HTTP请求
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                headers=headers,
                json=request_data
            )
            
            response_json = response.json()
            print(f"智谱AI原始响应: {json.dumps(response_json, ensure_ascii=False)}")
            
            if response.status_code == 200:
                prediction_text = response_json['choices'][0]['message']['content']
                print(f"成功获取预测文本: {prediction_text[:100]}...")
                
                # 分割预测内容
                sections = prediction_text.split('\n\n')
                prediction_2024 = {'events': '', 'attention': ''}
                prediction_2025 = {'events': '', 'attention': ''}
                cultural_interpretation = ''
                
                current_section = None
                for section in sections:
                    if '2024年运势' in section:
                        current_section = '2024'
                        prediction_2024['events'] = section
                    elif '2025年运势' in section:
                        current_section = '2025'
                        prediction_2025['events'] = section
                    elif '文化解读' in section:
                        cultural_interpretation = section
                    elif current_section == '2024' and '注意' in section:
                        prediction_2024['attention'] = section
                    elif current_section == '2025' and '注意' in section:
                        prediction_2025['attention'] = section
                
                return {
                    'prediction2024': prediction_2024,
                    'prediction2025': prediction_2025,
                    'culturalInterpretation': cultural_interpretation
                }
            else:
                print(f"智谱AI返回错误状态码: {response.status_code}")
                print(f"错误信息: {response_json.get('error', {}).get('message', 'Unknown error')}")
                
        except Exception as api_error:
            print(f"调用智谱AI API时发生错误: {str(api_error)}")
            import traceback
            print(f"API调用错误详情:\n{traceback.format_exc()}")
        
        return generate_fallback_prediction(user_data)
            
    except Exception as e:
        import traceback
        print(f"生成预测时发生错误: {str(e)}")
        print(f"错误详情:\n{traceback.format_exc()}")
        return generate_fallback_prediction(user_data)

def generate_fallback_prediction(user_data):
    """生成备用预测（当AI服务不可用时）"""
    birth_date = datetime.strptime(user_data['birthDate'], '%Y-%m-%dT%H:%M')
    zodiac = get_chinese_zodiac(birth_date.year)
    star_sign = get_zodiac_sign(birth_date.month, birth_date.day)
    
    return {
        'prediction2024': {
            'events': f'根据您的生肖{zodiac}和星座{star_sign}分析，2024年将是充满机遇的一年。建议保持积极乐观的心态，把握机会。',
            'attention': '在重要决策时多听取他人建议，注意劳逸结合。'
        },
        'prediction2025': {
            'events': f'2025年运势平稳向上，适合尝试新的领域和挑战。您的{star_sign}特质将帮助您克服困难。',
            'attention': '注意保持良好的作息规律，适当运动健身。'
        },
        'culturalInterpretation': f'从传统命理学角度来看，您的生肖{zodiac}与星座{star_sign}的组合显示出独特的个性特征。建议在行动时充分发挥自身优势，规避潜在风险。'
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        user_data = request.json
        prediction_result = generate_ai_prediction(user_data)
        return jsonify(prediction_result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
