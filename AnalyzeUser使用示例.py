#!/usr/bin/env python3
"""
用户购买习惯分析API使用示例
展示如何在前端项目中调用分析功能
"""

from analyze_user_api import (
    analyze_user,           # 完整分析
    get_user_summary,       # 摘要信息
    get_category_spending,  # 类别开销
    get_available_users     # 获取用户列表
)
import json

def example_basic_usage():
    """基础使用示例"""
    print("=== 基础使用示例 ===")
    
    # 1. 获取可用用户列表
    users = get_available_users(10)
    print(f"可用用户: {users}")
    
    if users:
        user_id = users[0]
        
        # 2. 获取用户摘要信息（轻量级）
        summary = get_user_summary(user_id)
        print(f"\n用户 {user_id} 摘要:")
        print(f"  订单数: {summary['total_orders']}")
        print(f"  消费总额: ¥{summary['total_amount']:.2f}")
        print(f"  平均每单: ¥{summary['avg_order_amount']:.2f}")
        print(f"  偏好类别: {summary['top_category']}")

def example_detailed_analysis():
    """详细分析示例"""
    print("\n=== 详细分析示例 ===")
    
    user_id = 25
    
    # 完整分析
    result = analyze_user(user_id)
    
    if not result.get('error'):
        print(f"用户 {user_id} 详细分析:")
        print(f"  分析时段: {result['period']}")
        print(f"  订单总数: {result['total_orders']}")
        print(f"  消费总额: ¥{result['total_amount']:.2f}")
        
        # 频繁购买商品
        if result['frequent_products']:
            print("\n  频繁购买商品:")
            for product in result['frequent_products'][:3]:
                print(f"    - {product['product_name']}: {product['purchase_count']}次")
        
        # 偏好类别
        if result['frequent_categories']:
            print("\n  偏好商品类别:")
            for category in result['frequent_categories'][:3]:
                print(f"    - {category['category']}: {category['purchase_count']}次 ({category['percentage']}%)")

def example_category_spending():
    """类别开销分析示例"""
    print("\n=== 类别开销分析示例 ===")
    
    user_id = 25
    category_spending = get_category_spending(user_id)
    
    if category_spending:
        print(f"用户 {user_id} 各类商品平均开销:")
        for item in category_spending:
            print(f"  {item['category']}: 平均¥{item['avg_spending']:.2f}/次 "
                  f"(总计¥{item['total_spending']:.2f}, {item['purchase_count']}次)")

def example_json_api():
    """JSON API示例（适合Web前端）"""
    print("\n=== JSON API示例 ===")
    
    user_id = 25
    
    # 获取完整分析结果
    result = analyze_user(user_id)
    
    # 转换为JSON格式（适合前端使用）
    json_result = json.dumps(result, ensure_ascii=False, indent=2)
    print("JSON格式结果（前端可直接使用）:")
    print(json_result[:500] + "..." if len(json_result) > 500 else json_result)

def example_error_handling():
    """错误处理示例"""
    print("\n=== 错误处理示例 ===")
    
    # 测试不存在的用户
    result = analyze_user(99999)
    
    if result.get('error'):
        print(f"错误处理: {result['message']}")
    else:
        print("用户分析成功")

def example_custom_date_range():
    """自定义日期范围示例"""
    print("\n=== 自定义日期范围示例 ===")
    
    user_id = 25
    
    # 分析2024年全年数据
    result = analyze_user(user_id, "2024-01-01", "2024-12-31")
    
    if not result.get('error'):
        print(f"用户 {user_id} 全年分析:")
        print(f"  订单总数: {result['total_orders']}")
        print(f"  消费总额: ¥{result['total_amount']:.2f}")

if __name__ == "__main__":
    print("🛍️ 用户购买习惯分析API使用示例")
    print("=" * 50)
    
    example_basic_usage()
    example_detailed_analysis()
    example_category_spending()
    example_json_api()
    example_error_handling()
    example_custom_date_range()
    
    print("\n✅ 所有示例运行完成！")
    print("\n💡 提示: 这些函数可以直接在你的前端项目中导入使用")