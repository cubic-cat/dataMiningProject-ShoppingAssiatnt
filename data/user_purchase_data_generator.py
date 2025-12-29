import csv
import random
from datetime import datetime, timedelta

# 配置参数
RECORD_COUNT = 50000  # 生成的记录数
USER_ID_RANGE = (1, 100)  # 用户ID范围
PRODUCT_ID_RANGE = (1001, 2000)  # 商品ID范围 (对应1000个商品)
START_DATE = datetime(2024, 1, 1)  # 购买时间起始
END_DATE = datetime(2024, 12, 31)  # 购买时间结束
# 订单商品数量及对应权重
PRODUCT_COUNT_OPTIONS = [1, 2, 3, 4, 5]
PRODUCT_COUNT_WEIGHTS = [0.3, 0.25, 0.25, 0.15, 0.05]
REFUND_RATE = 0.05  # 退款率5%

# 加载商品价格数据
def load_product_prices():
    """从商品数据文件中加载商品价格信息"""
    product_prices = {}
    try:
        with open("product_data.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                product_id = int(row['商品ID'])
                price = float(row['单价(元)'])
                product_prices[product_id] = price
        print(f"✅ 成功加载 {len(product_prices)} 个商品的价格信息")
    except FileNotFoundError:
        print("❌ 商品数据文件 product_data.csv 未找到！")
        return None
    except Exception as e:
        print(f"❌ 加载商品价格数据失败: {e}")
        return None
    return product_prices

# 生成随机时间
def random_date(start, end):
    delta = end - start
    random_days = random.randint(0, delta.days)
    random_hours = random.randint(0, 23)
    random_minutes = random.randint(0, 59)
    return start + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)

# 生成单个订单的商品列表和总金额
def generate_order_product_info(product_prices):
    """
    生成订单商品信息，从商品表格中获取真实价格
    
    Args:
        product_prices: 商品ID到价格的映射字典
    
    Returns:
        tuple: (商品ID字符串, 总金额, 商品数量)
    """
    # 随机确定订单商品数量（按权重）
    product_count = random.choices(PRODUCT_COUNT_OPTIONS, weights=PRODUCT_COUNT_WEIGHTS)[0]
    
    # 生成对应数量的商品ID（可重复，模拟购买多件同款）
    product_ids = [random.randint(*PRODUCT_ID_RANGE) for _ in range(product_count)]
    
    # 从商品表格中获取每个商品的真实价格，计算总金额
    total_amount = 0
    valid_product_ids = []
    
    for product_id in product_ids:
        if product_id in product_prices:
            valid_product_ids.append(product_id)
            total_amount += product_prices[product_id]
        else:
            # 如果商品ID不存在，重新随机选择一个
            fallback_id = random.choice(list(product_prices.keys()))
            valid_product_ids.append(fallback_id)
            total_amount += product_prices[fallback_id]
    
    # 拼接商品ID（用逗号分隔）
    product_id_str = ",".join(map(str, valid_product_ids))
    total_amount = round(total_amount, 2)
    
    return product_id_str, total_amount, product_count

# 主程序
def main():
    print("🛍️ 开始生成用户购买数据...")
    
    # 加载商品价格数据
    product_prices = load_product_prices()
    if product_prices is None:
        print("❌ 无法加载商品价格数据，程序退出")
        return
    
    # 生成CSV文件
    with open("user_purchase_data.csv", "w", newline="", encoding="utf-8") as f:
        # 定义表头
        fieldnames = [
            "记录ID", "用户ID", "购买商品数量", "商品ID", 
            "购买总金额(元)", "购买时间", "是否退款"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # 生成每条订单记录
        for record_id in range(1, RECORD_COUNT + 1):
            user_id = random.randint(*USER_ID_RANGE)
            
            # 生成订单商品信息（从商品表格获取真实价格）
            product_id_str, total_amount, product_count = generate_order_product_info(product_prices)
            
            purchase_time = random_date(START_DATE, END_DATE).strftime("%Y-%m-%d %H:%M:%S")
            is_refund = random.choices(["是", "否"], weights=[REFUND_RATE, 1-REFUND_RATE])[0]
            
            # 写入行数据
            writer.writerow({
                "记录ID": record_id,
                "用户ID": user_id,
                "购买商品数量": product_count,
                "商品ID": product_id_str,
                "购买总金额(元)": total_amount,
                "购买时间": purchase_time,
                "是否退款": is_refund
            })
            
            # 显示进度
            if record_id % 10000 == 0:
                print(f"📊 已生成 {record_id}/{RECORD_COUNT} 条记录...")
    
    print(f"✅ CSV文件生成完成！文件名为：user_purchase_data.csv")
    print(f"📈 总共生成 {RECORD_COUNT} 条购买记录")

if __name__ == "__main__":
    main()