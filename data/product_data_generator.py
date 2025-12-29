import csv
import random

# 配置参数
START_PRODUCT_ID = 1001  # 起始商品ID
END_PRODUCT_ID = 2000    # 结束商品ID (1000个商品)
PRICE_RANGE = (1, 5000)  # 总体单价范围（元）

# 十大类下的商品种类及其价格范围
PRODUCT_CATEGORIES = {
    "服装": {
        "items": ["T恤", "牛仔裤", "卫衣", "羽绒服", "衬衫", "连衣裙", "短裤", "长裤", "外套", "毛衣",
                 "西装", "裙子", "背心", "夹克", "风衣", "棉服", "马甲", "睡衣", "内衣", "袜子"],
        "price_range": (80, 3000)  # 服装价格范围
    },
    "电器": {
        "items": ["蓝牙耳机", "充电宝", "台灯", "吹风机", "加湿器", "电水壶", "电动牙刷", "手机", "平板电脑", "笔记本电脑",
                 "智能手表", "音响", "电视", "空调", "冰箱", "洗衣机", "微波炉", "电饭煲", "榨汁机", "咖啡机"],
        "price_range": (500, 5000)  # 电器价格范围
    },
    "食品": {
        "items": ["牛奶", "面包", "啤酒", "薯片", "方便面", "巧克力", "饼干", "糖果", "果汁", "茶叶",
                 "咖啡", "坚果", "水果", "蔬菜", "肉类", "海鲜", "调料", "零食", "酸奶", "蛋糕"],
        "price_range": (5, 200)  # 食品价格范围
    },
    "美妆": {
        "items": ["口红", "粉底液", "眼影", "睫毛膏", "面膜", "洗面奶", "爽肤水", "乳液", "精华", "防晒霜",
                 "香水", "指甲油", "腮红", "眉笔", "卸妆水", "护手霜", "身体乳", "洗发水", "护发素", "沐浴露"],
        "price_range": (15, 1000)  # 美妆价格范围
    },
    "运动": {
        "items": ["跑鞋", "篮球", "足球", "网球拍", "羽毛球拍", "瑜伽垫", "哑铃", "跳绳", "运动服", "运动裤",
                 "游泳镜", "健身器材", "登山包", "帐篷", "睡袋", "户外鞋", "运动手表", "护膝", "头盔", "滑板"],
        "price_range": (30, 1200)  # 运动用品价格范围
    },
    "家居": {
        "items": ["沙发", "床", "衣柜", "书桌", "椅子", "茶几", "餐桌", "床垫", "枕头", "被子",
                 "窗帘", "地毯", "花瓶", "相框", "台钟", "装饰画", "储物盒", "衣架", "垃圾桶", "拖鞋"],
        "price_range": (10, 2000)  # 家居用品价格范围
    },
    "文具": {
        "items": ["笔记本", "钢笔", "铅笔", "橡皮", "尺子", "计算器", "订书机", "胶水", "剪刀", "文件夹",
                 "便利贴", "标签纸", "打印纸", "墨水", "修正液", "圆规", "三角板", "书包", "笔袋", "白板"],
        "price_range": (2, 300)  # 文具价格范围
    },
    "数码": {
        "items": ["鼠标", "键盘", "显示器", "摄像头", "麦克风", "路由器", "硬盘", "内存卡", "数据线", "充电器",
                 "耳机", "音箱", "投影仪", "打印机", "扫描仪", "电子书", "游戏机", "VR眼镜", "无人机", "智能家居"],
        "price_range": (200, 5000)  # 数码产品价格范围
    },
    "汽车": {
        "items": ["轮胎", "机油", "刹车片", "雨刷", "车载充电器", "行车记录仪", "导航仪", "座椅套", "脚垫", "香水",
                 "洗车用品", "打蜡用品", "防冻液", "玻璃水", "车灯", "后视镜", "方向盘套", "遮阳挡", "车载冰箱", "应急包"],
        "price_range": (10, 2000)  # 汽车用品价格范围
    }
}
# 扁平化所有具体品类（便于随机选取）
ALL_SPECIFIC_CATEGORIES = []
CATEGORY_TO_PRICE_RANGE = {}  # 商品种类到价格范围的映射

for main_cat, cat_data in PRODUCT_CATEGORIES.items():
    items = cat_data["items"]
    price_range = cat_data["price_range"]
    
    ALL_SPECIFIC_CATEGORIES.extend(items)
    # 为每个商品种类记录其价格范围
    for item in items:
        CATEGORY_TO_PRICE_RANGE[item] = price_range

# 生成CSV文件
with open("product_data.csv", "w", newline="", encoding="utf-8") as f:
    # 定义表头
    fieldnames = ["商品ID", "商品种类", "单价(元)"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    
    # 为每个商品ID生成数据
    for product_id in range(START_PRODUCT_ID, END_PRODUCT_ID + 1):
        # 随机选取商品种类
        product_category = random.choice(ALL_SPECIFIC_CATEGORIES)
        
        # 根据商品种类获取对应的价格范围
        price_range = CATEGORY_TO_PRICE_RANGE[product_category]
        
        # 在该品类的价格范围内生成随机单价（保留2位小数）
        price = round(random.uniform(*price_range), 2)
        
        # 确保价格在总体范围内
        price = max(PRICE_RANGE[0], min(price, PRICE_RANGE[1]))
        
        # 写入行数据
        writer.writerow({
            "商品ID": product_id,
            "商品种类": product_category,
            "单价(元)": price
        })

print("商品数据CSV生成完成！文件名为：product_data.csv")