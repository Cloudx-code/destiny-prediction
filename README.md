# 智能命运预测系统

这是一个基于AI技术和中国传统命理学的智能命运预测系统，专注于为用户提供2024-2025年的个性化预测分析。

## 项目架构

### 前端部分
- `index.html`: 主页面，包含用户信息输入表单和预测结果展示区域
- `static/css/style.css`: 页面样式文件
- `static/js/main.js`: 主要的JavaScript逻辑文件
- `static/js/prediction.js`: 命运预测相关的JavaScript逻辑

### 后端部分
- `app.py`: Flask应用主文件
- `models/`: 数据模型目录
  - `destiny_model.py`: 命理预测核心模型
  - `user_model.py`: 用户信息模型
- `utils/`: 工具函数目录
  - `date_utils.py`: 日期处理工具
  - `prediction_utils.py`: 预测相关工具函数

## 功能说明

### 1. 用户信息输入
- 姓名（中文/英文）
- 出生日期（年月日时）
- 性别
- 出生地

### 2. 预测结果展示
- 2024年大事件预测
- 2025年大事件预测
- 重点关注事项
- 文化解读说明

## 技术栈
- 前端：HTML5, CSS3, JavaScript
- 后端：Python (Flask)
- 算法：基于传统命理学的AI预测模型

## 开发规范
1. 代码注释必须清晰完整
2. 遵循Python PEP8编码规范
3. JavaScript使用ES6+标准
4. CSS采用BEM命名规范

## 部署说明
1. 安装依赖：`pip install -r requirements.txt`
2. 运行应用：`python app.py`
3. 访问地址：`http://localhost:5000`

## 注意事项
- 所有预测结果仅供参考
- 用户信息严格保密
- 建议使用最新版本的Chrome或Firefox浏览器访问
