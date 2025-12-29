#!/usr/bin/env python3
"""
智能商品推荐系统使用示例
"""

from product_recommend_api import recommend_products, ProductRecommendationAPI, get_available_options

def main():
    print("🎁 智能商品推荐系统使用示例")
    print("=" * 50)
    
    # 1. 查看可用选项
    print("\n1️⃣ 查看系统可用选项:")
    options = get_available_options()
    print(f"   送礼对象: {list(options['gift_recipients'].keys())}")
    print(f"   商品类别数量: {len(options['product_categories'])}")
    print(f"   价格范围: ¥{options['price_range']['min']:.2f} - ¥{options['price_range']['max']:.2f}")
    
    # 2. 查看用户购物习惯
    print("\n2️⃣ 查看用户购物习惯:")
    api = ProductRecommendationAPI()
    user_id = 25
    user_summary = api.get_user_summary(user_id)
    
    if 'error' not in user_summary:
        print(f"   用户{user_id}的平均每单消费: ¥{user_summary['avg_order_amount']:.2f}")
    else:
        print(f"   获取用户信息失败: {user_summary['error']}")
    
    # 3. 基本推荐示例
    print("\n3️⃣ 基本推荐示例（无预算限制）:")
    result1 = recommend_products(
        user_id=25,
        requirement="想买一些日常用品"
    )
    
    if result1["success"]:
        print("   ✅ 推荐成功！")
        print(f"   📊 输入信息: {result1['input']}")
        if 'budget_reference' in result1['input'] and result1['input']['budget_reference']:
            print(f"   💰 预算参考: ¥{result1['input']['budget_reference']:.2f}")
    else:
        print(f"   ❌ 推荐失败: {result1.get('error', '未知错误')}")
    
    # 4. 完整参数推荐示例
    print("\n4️⃣ 完整参数推荐示例:")
    result2 = recommend_products(
        user_id=25,
        budget=800.0,
        recipient="朋友",
        recipient_info="28岁男性，程序员，喜欢科技产品",
        requirement="生日礼物，希望实用且有科技感"
    )
    
    if result2["success"]:
        print("   ✅ 推荐成功！")
        print(f"   📊 输入信息:")
        print(f"      - 预算: ¥{result2['input']['budget']:.2f}")
        print(f"      - 送礼对象: {result2['input']['recipient']}")
        print(f"      - 对象信息: {result2['input']['recipient_info']}")
        print(f"      - 需求: {result2['input']['requirement']}")
    else:
        print(f"   ❌ 推荐失败: {result2.get('error', '未知错误')}")
    
    # 5. 送给父母的推荐示例
    print("\n5️⃣ 送给父母的推荐示例:")
    result3 = recommend_products(
        user_id=25,
        recipient="父母",
        recipient_info="60岁左右，注重健康养生",
        requirement="春节礼品，希望对健康有益"
    )
    
    if result3["success"]:
        print("   ✅ 推荐成功！")
        print(f"   📊 会使用用户平均消费作为预算参考")
        if 'budget_reference' in result3['input'] and result3['input']['budget_reference']:
            print(f"   💰 预算参考: ¥{result3['input']['budget_reference']:.2f}")
    else:
        print(f"   ❌ 推荐失败: {result3.get('error', '未知错误')}")
    
    print("\n" + "=" * 50)
    print("💡 使用提示:")
    print("1. 如果不设置预算，系统会自动使用用户的平均消费作为参考")
    print("2. 送礼对象不是'自己'时，需要提供详细的对象信息")
    print("3. 需求描述越详细，推荐结果越精准")
    print("4. 需要设置通义千问API密钥才能获得AI推荐")
    print("\n🔑 API密钥设置方法:")
    print("   方法1: 环境变量 export QWEN_API_KEY='你的密钥'")
    print("   方法2: 函数参数 recommend_products(..., api_key='你的密钥')")

if __name__ == "__main__":
    main()