# 🎁 智能购物助手 (Shopping Assistant)

基于通义千问大模型和Dify，提供智能导购、售后客服和商品比价等一站式购物服务。

## ✨ 功能特性

### 核心功能
- 📊 **用户画像分析**: 基于用户历史购买数据，深度分析用户购买偏好、消费习惯和类别偏好
- 🤖 **AI智能分析**: 使用通义千问大模型进行智能推荐和需求分析
- 🎯 **商品关联性分析**: 基于购买数据分析商品关联，并根据用户购买记录，推送高关联性商品
- 🎁 **智能售后**: 基于用户购买记录和自定义售后规范，为用户提供智能售后服务
- 💰 **商品比价**: 输入商品名称，自动对比多平台商品价格


## 📁 项目结构

```
datamining_project/
├── analyze_user_api.py              # 用户购买习惯分析API
├── product_recommend_api.py         # 商品推荐API（核心模块）
├── web_demo.py                      # Web演示界面（Flask应用）
├── AnalyzeUser使用示例.py          # 用户分析使用示例
├── ProductRecomd使用示例.py        # 推荐系统使用示例
├── requirements.txt                 # Python依赖包列表
├── README.md                        # 项目说明文档
├── static/                          # 静态资源目录
│   └── avatar.png                   # 用户头像图片
└── data/                            # 数据目录
    ├── user_purchase_data.csv       # 用户购买数据
    ├── product_data.csv             # 商品数据
    ├── category_associations.csv    # 商品类别关联数据
    ├── user_purchase_data_generator.py    # 购买数据生成器
    ├── product_data_generator.py          # 商品数据生成器
    └── category_association_analysis.py   # 类别关联分析脚本
```

## 🚀 快速开始

### 环境要求

- Python 3.7+
- 通义千问API密钥（可在[阿里云DashScope](https://dashscope.console.aliyun.com/)获取）

### 1. 安装依赖

```bash
# 使用 pip 安装
pip install -r requirements.txt

# 或手动安装
pip install flask>=2.0.0 requests>=2.25.0
```

### 2. 配置API密钥

在 `product_recommend_api.py` 中配置通义千问API密钥：

```python
# 第26行，修改为你的API密钥
self.api_key = "your_qwen_api_key_here"
```

或者在使用时传入：

```python
api = ProductRecommendationAPI(api_key="your_qwen_api_key_here")
```

### 3. 启动Web界面

```bash
python web_demo.py
# 或
python3 web_demo.py
```

启动成功后，访问 `http://localhost:5000` 使用Web界面。

### 4. 使用示例

#### Web界面使用

1. 在左侧输入或选择用户ID
2. 设置预算（可选）
3. 选择送礼对象
4. 填写对象详细画像（可选）
5. 在输入框输入需求，如"想要一个新年礼物"
6. 点击发送或按Enter键获取推荐

#### Python API使用

```python
from product_recommend_api import ProductRecommendationAPI

# 创建API实例
api = ProductRecommendationAPI()

# 获取商品推荐
result = api.get_product_recommendations(
    user_id=25,
    budget=500.0,
    recipient="朋友",
    recipient_info="25岁，喜欢科技产品",
    requirement="生日礼物推荐"
)

if result["success"]:
    print("推荐结果:", result["recommendations"])
    print("购买建议:", result["buying_tips"])
else:
    print("推荐失败:", result["error"])
```

## 🔌 API接口文档

### ProductRecommendationAPI 类

#### `get_product_recommendations()`

获取商品推荐结果。

**参数：**
- `user_id` (int): 用户ID，必填
- `budget` (float, optional): 预算金额，可选
- `recipient` (str): 送礼对象，可选值：`"自己"`, `"朋友"`, `"对象"`, `"父母"`
- `recipient_info` (str, optional): 对象详细画像，如年龄、爱好等
- `requirement` (str): 具体需求描述，必填

**返回：**
```python
{
    "success": True,
    "analysis": "需求分析文本",
    "recommendations": [
        {
            "category": "商品类别",
            "products": ["商品1", "商品2"],
            "price_range": "价格范围",
            "reason": "推荐理由"
        }
    ],
    "buying_tips": ["建议1", "建议2"],
    "input": {...}  # 输入参数信息
}
```

#### `get_user_summary()`

获取用户购物习惯摘要。

**参数：**
- `user_id` (int): 用户ID

**返回：**
```python
{
    "avg_order_amount": 299.50,  # 平均每单消费
    "total_orders": 10,           # 总订单数
    "top_category": "电子产品"    # 最常购买类别
}
```

#### `get_smart_suggestions()`

获取基于用户购买记录的智能建议（用于Web界面左侧提示）。

**参数：**
- `user_id` (int): 用户ID

**返回：**
```python
{
    "success": True,
    "suggestions": [
        {
            "title": "建议标题",
            "message": "建议内容"
        }
    ]
}
```

### UserPurchaseAnalyzer 类

#### `analyze_user_habits()`

分析用户购买习惯。

**参数：**
- `user_id` (int): 用户ID

**返回：** 包含用户购物习惯的字典

## 📊 数据格式

### 用户购买数据格式 (user_purchase_data.csv)

```csv
用户ID,商品ID,购买数量,购买总金额(元),购买日期
1,101,2,299.98,2023-01-15
1,205,1,599.00,2023-02-20
```

### 商品数据格式 (product_data.csv)

```csv
商品ID,商品名称,商品类别,价格(元)
101,iPhone 14,电子产品,5999.00
205,运动鞋,服装鞋帽,599.00
```

### 商品类别关联数据格式 (category_associations.csv)

```csv
类别A,类别B,关联度
电子产品,数码配件,0.85
服装鞋帽,箱包皮具,0.72
```

## 🛠️ 技术栈

- **后端框架**: Flask 2.0+
- **AI模型**: 通义千问 (Qwen) - 阿里云DashScope
- **HTTP请求**: Requests
- **前端技术**: HTML5, CSS3, JavaScript (原生)
- **数据格式**: CSV, JSON
- **API设计**: RESTful API

## 📝 使用示例

### 示例1: 基本推荐

```python
from product_recommend_api import recommend_products

result = recommend_products(
    user_id=25,
    requirement="想买一些日常用品"
)
```

### 示例2: 完整参数推荐

```python
result = recommend_products(
    user_id=25,
    budget=800.0,
    recipient="朋友",
    recipient_info="25岁，喜欢摄影和户外运动",
    requirement="生日礼物推荐"
)
```

### 示例3: 查看可用选项

```python
from product_recommend_api import get_available_options

options = get_available_options()
print("送礼对象:", list(options['gift_recipients'].keys()))
print("商品类别:", options['product_categories'])
print("价格范围:", options['price_range'])
```

更多示例请参考：
- `AnalyzeUser使用示例.py` - 用户分析示例
- `ProductRecomd使用示例.py` - 推荐系统示例

## ❓ 常见问题

### Q: 如何获取通义千问API密钥？

A: 访问[阿里云DashScope控制台](https://dashscope.console.aliyun.com/)，注册账号后创建API密钥。

### Q: 端口5000被占用怎么办？

A: 修改 `web_demo.py` 第936行，将 `port=5000` 改为其他端口，如 `port=5001`。

### Q: 如何添加自己的商品数据？

A: 按照数据格式要求，编辑 `data/product_data.csv` 文件，添加商品信息。

### Q: 推荐结果不准确怎么办？

A: 
- 确保用户购买数据足够丰富
- 提供更详细的需求描述
- 填写对象详细画像信息
- 检查API密钥是否有效

### Q: 如何自定义Web界面样式？

A: 编辑 `web_demo.py` 中的 `HTML_TEMPLATE` 变量，修改CSS样式。

## 🔧 开发说明

### 运行测试

```bash
# 运行用户分析示例
python AnalyzeUser使用示例.py

# 运行推荐系统示例
python ProductRecomd使用示例.py
```

### 生成测试数据

```bash
# 生成用户购买数据
python data/user_purchase_data_generator.py

# 生成商品数据
python data/product_data_generator.py
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📮 联系方式

如有问题或建议，请通过GitHub Issues反馈。

---

**注意**: 使用本系统需要有效的通义千问API密钥。请确保API密钥的安全性，不要将其提交到公开代码仓库。
