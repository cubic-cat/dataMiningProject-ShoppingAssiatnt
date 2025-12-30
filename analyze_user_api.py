#!/usr/bin/env python3
"""
用户购买习惯分析工具 - API版本
提供简洁的函数接口，便于前端调用
"""

import csv
from datetime import datetime
from collections import Counter, defaultdict

class UserPurchaseAnalyzer:
    def __init__(self, purchase_data_path="data/user_purchase_data.csv", product_data_path="data/product_data.csv"):
        self.purchase_data_path = purchase_data_path
        self.product_data_path = product_data_path
        self.purchase_data = []
        self.product_map = {}
        self.product_prices = {}  
        self.load_data()
    
    def load_data(self):
        """加载数据文件"""
        try:
            # 加载商品数据
            with open(self.product_data_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    product_id = int(row['商品ID'])
                    self.product_map[product_id] = row['商品种类']
                    self.product_prices[product_id] = float(row['单价(元)'])
            
            # 加载购买数据
            with open(self.purchase_data_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row['用户ID'] = int(row['用户ID'])
                    row['购买商品数量'] = int(row['购买商品数量'])
                    row['购买总金额(元)'] = float(row['购买总金额(元)'])
                    row['购买时间'] = datetime.strptime(row['购买时间'], '%Y-%m-%d %H:%M:%S')
                    self.purchase_data.append(row)
            
        except FileNotFoundError as e:
            print(f"❌ 文件未找到: {e}")
        except Exception as e:
            print(f"❌ 数据加载失败: {e}")
    
    def analyze_user_habits(self, user_id, start_date="2025-11-01", end_date="2026-1-31"):
        """
        分析指定用户的购买习惯
        
        Returns:
            dict: 完整的分析结果，包含所有统计信息
        """
        if not self.purchase_data:
            return None
        
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        # 筛选数据
        user_data = []
        for record in self.purchase_data:
            if (record['用户ID'] == user_id and 
                start_date <= record['购买时间'] <= end_date and
                record['是否退款'] == '否'):
                user_data.append(record)
        
        if len(user_data) == 0:
            return {
                'user_id': user_id,
                'period': f"{start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}",
                'total_orders': 0,
                'total_amount': 0,
                'avg_order_amount': 0,
                'frequent_products': [],
                'frequent_categories': [],
                'category_avg_spending': [],
                'purchase_timeline': [],
                'message': '该用户在指定时间段内没有有效购买记录'
            }
        
        # 计算基本统计
        total_amount = sum(record['购买总金额(元)'] for record in user_data)
        avg_order_amount = total_amount / len(user_data)
        
        # 分析商品购买频次
        all_products = []
        for record in user_data:
            products_str = record['商品ID'].strip('"')
            product_ids = [int(pid.strip()) for pid in products_str.split(',')]
            all_products.extend(product_ids)
        
        # 频繁购买商品统计
        product_counter = Counter(all_products)
        frequent_products = []
        for product_id, count in product_counter.most_common():
            if count >= 3:  # 购买次数≥3才算频繁
                product_name = self.product_map.get(product_id, f"未知商品({product_id})")
                frequent_products.append({
                    'product_id': product_id,
                    'product_name': product_name,
                    'purchase_count': count
                })
        
        # 分析商品类别和每类商品平均开销
        all_categories = []
        category_amounts = defaultdict(list)  # 存储每个类别的消费金额
        
        for product_id in all_products:
            category = self.product_map.get(product_id)
            if category:
                all_categories.append(category)
                # 获取该商品的单价
                product_price = self.product_prices.get(product_id, 0)
                category_amounts[category].append(product_price)
        
        category_counter = Counter(all_categories)
        frequent_categories = []
        category_avg_spending = []
        
        for category, count in category_counter.most_common(5):  # 取前5个最频繁的类别
            percentage = round(count / len(all_categories) * 100, 1) if all_categories else 0
            frequent_categories.append({
                'category': category,
                'purchase_count': count,
                'percentage': percentage
            })
            
            # 计算该类别的平均开销
            if category in category_amounts:
                avg_spending = sum(category_amounts[category]) / len(category_amounts[category])
                total_spending = sum(category_amounts[category])
                category_avg_spending.append({
                    'category': category,
                    'avg_spending': round(avg_spending, 2),
                    'total_spending': round(total_spending, 2),
                    'purchase_count': count
                })
        
        # 购买时间线
        purchase_timeline = []
        for record in user_data:
            purchase_timeline.append({
                'date': record['购买时间'].strftime('%Y-%m-%d'),
                'amount': record['购买总金额(元)'],
                'product_count': record['购买商品数量']
            })
        
        purchase_timeline.sort(key=lambda x: x['date'])
        
        return {
            'user_id': user_id,
            'period': f"{start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}",
            'total_orders': len(user_data),
            'total_amount': round(total_amount, 2),
            'avg_order_amount': round(avg_order_amount, 2),
            'frequent_products': frequent_products,
            'frequent_categories': frequent_categories,
            'category_avg_spending': category_avg_spending,
            'purchase_timeline': purchase_timeline
        }
    
    def get_user_list(self, limit=10):
        """获取用户列表"""
        user_ids = set()
        for record in self.purchase_data:
            user_ids.add(record['用户ID'])
            if len(user_ids) >= limit:
                break
        return sorted(list(user_ids))

# ============== 前端调用API函数 ==============

# 全局分析器实例（避免重复加载数据）
_analyzer = None

def get_analyzer():
    """获取分析器实例（单例模式）"""
    global _analyzer
    if _analyzer is None:
        _analyzer = UserPurchaseAnalyzer()
    return _analyzer

def analyze_user(user_id, start_date="2025-11-01", end_date="2026-01-31"):
    """
    分析用户购买习惯 - 前端调用接口
    
    Args:
        user_id (int): 用户ID
        start_date (str): 开始日期，格式 YYYY-MM-DD
        end_date (str): 结束日期，格式 YYYY-MM-DD
    
    Returns:
        dict: 分析结果，包含以下字段：
            - user_id: 用户ID
            - period: 分析时间段
            - total_orders: 订单总数
            - total_amount: 消费总额
            - avg_order_amount: 平均每单金额
            - frequent_products: 频繁购买商品列表
            - frequent_categories: 偏好商品类别列表
            - category_avg_spending: 各类商品平均开销列表
            - purchase_timeline: 购买时间线
            - message: 错误信息（如果有）
    """
    analyzer = get_analyzer()
    if not analyzer.purchase_data:
        return {
            'error': True,
            'message': '数据加载失败'
        }
    
    try:
        result = analyzer.analyze_user_habits(user_id, start_date, end_date)
        if result:
            result['error'] = False
        return result
    except Exception as e:
        return {
            'error': True,
            'message': f'分析过程中出现错误: {str(e)}'
        }

def get_user_summary(user_id, start_date="2025-11-01", end_date="2026-01-31"):
    """
    获取用户购买摘要信息 - 简化版接口
    
    Returns:
        dict: 分析结果，包含以下字段：
            - avg_order_amount: 平均每单金额
            - frequent_products: 频繁购买商品列表
            - frequent_categories: 偏好商品类别列表
    """
    result = analyze_user(user_id, start_date, end_date)
    if result.get('error'):
        return result
    
    return {
        'error': False,
        'avg_order_amount': result['avg_order_amount'],
        'frequent_products': result['frequent_products'][0]['product_name'] if result['frequent_products'] else '无',
        'frequent_categories': result['frequent_categories'][0]['category'] if result['frequent_categories'] else '无',
    }

def get_category_spending(user_id, start_date="2025-11-01", end_date="2026-01-31"):
    """
    获取用户各类商品平均开销 - 专门接口
    
    Returns:
        list: 各类商品平均开销列表
    """
    result = analyze_user(user_id, start_date, end_date)
    if result.get('error'):
        return []
    
    return result.get('category_avg_spending', [])

def get_available_users(limit=20):
    """
    获取可用的用户ID列表
    
    Returns:
        list: 用户ID列表
    """
    analyzer = get_analyzer()
    if not analyzer.purchase_data:
        return []
    
    return analyzer.get_user_list(limit)

# ============== 命令行接口（测试用） ==============

def print_analysis_report(analysis_result):
    """打印分析报告（用于命令行调用）"""
    if not analysis_result or analysis_result.get('error'):
        print("❌ 无分析结果可显示")
        if analysis_result:
            print(f"错误信息: {analysis_result.get('message', '未知错误')}")
        return
    
    print("\n" + "="*60)
    print(f"用户购买习惯分析报告")
    print("="*60)
    
    print(f"👤 用户ID: {analysis_result['user_id']}")
    print(f"📅 分析时段: {analysis_result['period']}")
    
    if analysis_result['total_orders'] == 0:
        print(f"📝 {analysis_result.get('message', '无购买记录')}")
        return
    
    print(f"📊 订单总数: {analysis_result['total_orders']} 单")
    print(f"💰 消费总额: ¥{analysis_result['total_amount']:.2f}")
    print(f"📈 平均每单金额: ¥{analysis_result['avg_order_amount']:.2f}")
    
    print(f"\n🔥 频繁购买商品 (购买次数≥3):")
    if analysis_result['frequent_products']:
        for i, product in enumerate(analysis_result['frequent_products'], 1):
            print(f"   {i}. {product['product_name']} (ID: {product['product_id']}) - 购买 {product['purchase_count']} 次")
    else:
        print("   暂无频繁购买的商品")
    
    print(f"\n📦 偏好商品类别:")
    if analysis_result['frequent_categories']:
        for i, category in enumerate(analysis_result['frequent_categories'], 1):
            print(f"   {i}. {category['category']} - {category['purchase_count']} 次 ({category['percentage']}%)")
    else:
        print("   暂无数据")
    
    print(f"\n💳 各类商品平均开销:")
    if analysis_result.get('category_avg_spending'):
        for i, category_spending in enumerate(analysis_result['category_avg_spending'], 1):
            print(f"   {i}. {category_spending['category']} - 平均¥{category_spending['avg_spending']:.2f}/次 "
                  f"(总计¥{category_spending['total_spending']:.2f}, {category_spending['purchase_count']}次)")
    else:
        print("   暂无数据")
    
    print("="*60)

def main():
    """命令行主函数"""
    import sys
    
    if len(sys.argv) != 2:
        print("🛍️ 用户购买习惯分析工具")
        print("使用方法: python3 analyze_user_api.py <用户ID>")
        print("示例: python3 analyze_user_api.py 25")
        
        # 显示示例用户ID
        sample_users = get_available_users(10)
        if sample_users:
            print(f"📋 可用的示例用户ID: {sample_users}")
        return
    
    try:
        user_id = int(sys.argv[1])
        result = analyze_user(user_id)
        print_analysis_report(result)
    except ValueError:
        print("❌ 用户ID必须是数字")
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")

if __name__ == "__main__":
    main()