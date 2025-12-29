#!/usr/bin/env python3
"""
智能商品推荐系统 - Web演示界面
使用Flask创建简单的Web界面
"""

try:
    from flask import Flask, render_template_string, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from product_recommend_api import ProductRecommendationAPI, get_available_options
import json

# HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎁 智能商品推荐系统</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #555;
        }
        input, select, textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
            box-sizing: border-box;
        }
        textarea {
            height: 80px;
            resize: vertical;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
        }
        button:hover {
            background-color: #0056b3;
        }
        .result {
            margin-top: 30px;
            padding: 20px;
            border-radius: 5px;
        }
        .success {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        .error {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        .recommendation-card {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        .recommendation-header {
            font-weight: bold;
            color: #495057;
            margin-bottom: 10px;
            font-size: 16px;
        }
        .product-list {
            margin: 8px 0;
        }
        .product-item {
            background: #e9ecef;
            padding: 5px 10px;
            margin: 3px 0;
            border-radius: 4px;
            display: inline-block;
            margin-right: 8px;
        }
        .price-range {
            color: #28a745;
            font-weight: bold;
        }
        .reason {
            color: #6c757d;
            font-style: italic;
            margin-top: 8px;
        }
        .analysis-section {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            margin: 15px 0;
        }
        .tips-section {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 15px 0;
        }
        .budget-section {
            background: #d1ecf1;
            border-left: 4px solid #17a2b8;
            padding: 15px;
            margin: 15px 0;
        }
        .summary-section {
            background: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 15px 0;
        }
        .section-title {
            font-weight: bold;
            margin-bottom: 10px;
            color: #495057;
        }
        .tip-item {
            margin: 5px 0;
            padding-left: 20px;
            position: relative;
        }
        .tip-item:before {
            content: "💡";
            position: absolute;
            left: 0;
        }
        .info {
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
            margin-bottom: 20px;
        }
        .loading {
            display: none;
            text-align: center;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎁 智能商品推荐系统</h1>
        


        <form id="recommendForm">
            <div class="form-group">
                <label for="user_id">用户ID:</label>
                <input type="number" id="user_id" name="user_id" value="25" required>
            </div>

            <div class="form-group">
                <label for="budget">预算 (可选):</label>
                <input type="number" id="budget" name="budget" step="0.01" placeholder="不填写将使用用户平均消费作为参考">
            </div>

            <div class="form-group">
                <label for="recipient">送礼对象:</label>
                <select id="recipient" name="recipient" required>
                    {% for key, value in gift_recipients_dict.items() %}
                    <option value="{{ key }}">{{ key }} ({{ value }})</option>
                    {% endfor %}
                </select>
            </div>

            <div class="form-group">
                <label for="recipient_info">对象补充信息:</label>
                <input type="text" id="recipient_info" name="recipient_info" placeholder="年龄、爱好、职业等（送给自己可不填）">
            </div>

            <div class="form-group">
                <label for="requirement">具体需求:</label>
                <textarea id="requirement" name="requirement" placeholder="请描述您的具体需求，如：生日礼物、日常用品、科技产品等" required></textarea>
            </div>

            <button type="submit">🔍 获取推荐</button>
        </form>

        <div class="loading" id="loading">
            ⏳ 正在分析用户习惯并生成推荐...
        </div>

        <div id="result"></div>
    </div>

    <script>
        document.getElementById('recommendForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            // 显示加载状态
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').innerHTML = '';
            
            try {
                const response = await fetch('/recommend', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                // 隐藏加载状态
                document.getElementById('loading').style.display = 'none';
                
                // 显示结果
                const resultDiv = document.getElementById('result');
                if (result.success) {
                    resultDiv.className = 'result success';
                    resultDiv.innerHTML = formatRecommendationResult(result);
                } else {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `<strong>❌ 推荐失败</strong><br><br>${result.error || result.errors?.join('<br>') || '未知错误'}`;
                }
            } catch (error) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('result').className = 'result error';
                document.getElementById('result').innerHTML = `<strong>❌ 请求失败</strong>\\n\\n${error.message}`;
            }
        });

        // 格式化推荐结果显示
        function formatRecommendationResult(result) {
            let html = '<div class="recommendation-result">';
            
            // 标题
            html += '<h3>🎁 智能推荐结果</h3>';
            
            // 分析部分
            if (result.analysis) {
                html += `<div class="analysis-section">
                    <div class="section-title">📊 需求分析</div>
                    <div>${result.analysis}</div>
                </div>`;
            }
            
            // 推荐商品
            if (result.recommendations && result.recommendations.length > 0) {
                html += '<div class="section-title">🛍️ 推荐商品</div>';
                result.recommendations.forEach((rec, index) => {
                    html += `<div class="recommendation-card">
                        <div class="recommendation-header">${index + 1}. ${rec.category}</div>
                        <div class="price-range">💰 ${rec.price_range}</div>
                        <div class="product-list">
                            ${rec.products.map(product => `<span class="product-item">${product}</span>`).join('')}
                        </div>
                        <div class="reason">${rec.reason}</div>
                    </div>`;
                });
            }
            
            // 购买建议
            if (result.buying_tips && result.buying_tips.length > 0) {
                html += `<div class="tips-section">
                    <div class="section-title">💡 购买建议</div>
                    ${result.buying_tips.map(tip => `<div class="tip-item">${tip}</div>`).join('')}
                </div>`;
            }
            
            // 预算建议
            if (result.budget_advice) {
                html += `<div class="budget-section">
                    <div class="section-title">💳 预算建议</div>
                    <div>${result.budget_advice}</div>
                </div>`;
            }
            
            // 总结
            if (result.summary) {
                html += `<div class="summary-section">
                    <div class="section-title">📝 总结</div>
                    <div>${result.summary}</div>
                </div>`;
            }
            
            // 输入信息回显
            html += `<div style="margin-top: 20px; padding: 10px; background: #f8f9fa; border-radius: 5px; font-size: 12px; color: #6c757d;">
                <strong>输入信息：</strong>
                预算: ${result.input.budget ? '¥' + result.input.budget : '无限制'}
                ${result.input.budget_reference ? ' (参考: ¥' + result.input.budget_reference.toFixed(2) + ')' : ''} | 
                对象: ${result.input.recipient} | 
                需求: ${result.input.requirement}
            </div>`;
            
            html += '</div>';
            return html;
        }

        // 根据送礼对象显示/隐藏补充信息
        document.getElementById('recipient').addEventListener('change', function() {
            const recipientInfo = document.getElementById('recipient_info');
            if (this.value === '自己') {
                recipientInfo.placeholder = '送给自己可不填写';
                recipientInfo.required = false;
            } else {
                recipientInfo.placeholder = '请提供详细信息（年龄、爱好、职业等）';
                recipientInfo.required = true;
            }
        });
    </script>
</body>
</html>
"""

def create_app():
    """创建Flask应用"""
    if not FLASK_AVAILABLE:
        print("❌ Flask未安装，无法启动Web界面")
        print("安装方法: pip3 install flask")
        return None
    
    app = Flask(__name__)
    api = ProductRecommendationAPI()
    
    @app.route('/')
    def index():
        """主页"""
        options = get_available_options()
        user_summary = api.get_user_summary(25)
        
        return render_template_string(HTML_TEMPLATE,
            gift_recipients=list(options['gift_recipients'].keys()),
            gift_recipients_dict=options['gift_recipients'],
            category_count=len(options['product_categories']),
            price_min=f"{options['price_range']['min']:.2f}",
            price_max=f"{options['price_range']['max']:.2f}",
            avg_spending=f"{user_summary.get('avg_order_amount', 0):.2f}"
        )
    
    @app.route('/recommend', methods=['POST'])
    def recommend():
        """处理推荐请求"""
        try:
            data = request.json
            
            # 转换数据类型
            user_id = int(data['user_id'])
            budget = float(data['budget']) if data.get('budget') else None
            recipient = data['recipient']
            recipient_info = data.get('recipient_info', '')
            requirement = data['requirement']
            
            # 使用默认API实例（已包含API密钥）
            result = api.get_product_recommendations(
                user_id=user_id,
                budget=budget,
                recipient=recipient,
                recipient_info=recipient_info,
                requirement=requirement
            )
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"处理请求时出错: {str(e)}"
            })
    
    return app

def main():
    """主函数"""
    print("🎁 智能商品推荐系统")
    print("=" * 50)
    
    if not FLASK_AVAILABLE:
        print("❌ Flask未安装，无法启动Web界面")
        print("安装方法: pip3 install flask")
        print("\n📝 你可以直接使用Python代码调用:")
        print("from product_recommend_api import recommend_products")
        print("result = recommend_products(user_id=25, requirement='圣诞礼物')")
        return
    
    app = create_app()
    if app:
        print("🌐 启动Web界面...")
        print("📱 访问地址: http://localhost:5000")
        print("✅ API密钥已配置，可以直接获得完整推荐")
        print("⏹️  按 Ctrl+C 停止服务")
        
        try:
            app.run(debug=True, host='0.0.0.0', port=5000)
        except KeyboardInterrupt:
            print("\n👋 服务已停止")

if __name__ == "__main__":
    main()