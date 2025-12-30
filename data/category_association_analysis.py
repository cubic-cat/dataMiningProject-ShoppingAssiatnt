#!/usr/bin/env python3
"""
商品种类关联分析
基于商品种类（分析用户购买记录中经常一起购买的商品类别对
"""

import pandas as pd
import numpy as np
from itertools import combinations
from collections import defaultdict, Counter
import csv
import os
from typing import Dict, List, Tuple, Set


class CategoryAssociationAnalyzer:
    """商品种类关联分析器"""
    
    def __init__(self, purchase_data_path: str, product_data_path: str):
        """
        初始化种类关联分析器
        
        Args:
            purchase_data_path: 用户购买数据文件路径
            product_data_path: 商品数据文件路径
        """
        self.purchase_data_path = purchase_data_path
        self.product_data_path = product_data_path
        self.purchase_data = []
        self.product_category_map = {}  # 商品ID -> 商品种类
        self.category_transactions = defaultdict(set)  # 商品种类 -> 包含该种类的交易ID集合
        self.transaction_categories = defaultdict(set)  # 交易ID -> 商品种类集合
        self.total_transactions = 0
        
        self._load_product_data()
        self._load_purchase_data()
        self._process_transactions()
    
    def _load_product_data(self):
        """加载商品数据，建立商品ID到种类的映射"""
        try:
            df = pd.read_csv(self.product_data_path, encoding='utf-8')
            self.product_category_map = dict(zip(df['商品ID'], df['商品种类']))
            print(f"成功加载 {len(self.product_category_map)} 个商品的种类信息")
            
            # 统计商品种类
            categories = set(self.product_category_map.values())
            print(f"📊 共有 {len(categories)} 种商品类别")
            
        except Exception as e:
            print(f"❌ 加载商品数据失败: {e}")
            raise
    
    def _load_purchase_data(self):
        """加载购买数据"""
        try:
            df = pd.read_csv(self.purchase_data_path, encoding='utf-8')
            self.purchase_data = df.to_dict('records')
            print(f"成功加载 {len(self.purchase_data)} 条购买记录")
        except Exception as e:
            print(f"❌ 加载购买数据失败: {e}")
            raise
    
    def _process_transactions(self):
        """处理交易数据，构建商品种类-交易映射"""
        print("📊 处理交易数据，转换为商品种类...")
        
        for record in self.purchase_data:
            transaction_id = record['记录ID']
            product_ids_str = str(record['商品ID'])
            
            # 解析商品ID（可能是单个ID或逗号分隔的多个ID）
            if ',' in product_ids_str:
                product_ids = [int(pid.strip()) for pid in product_ids_str.split(',')]
            else:
                product_ids = [int(product_ids_str)]
            
            # 转换为商品种类
            categories_in_transaction = set()
            for product_id in product_ids:
                if product_id in self.product_category_map:
                    category = self.product_category_map[product_id]
                    categories_in_transaction.add(category)
                else:
                    print(f"⚠️ 警告: 商品ID {product_id} 在商品数据中未找到")
            
            # 建立映射关系
            if categories_in_transaction:  # 只处理有有效种类的交易
                self.transaction_categories[transaction_id] = categories_in_transaction
                for category in categories_in_transaction:
                    self.category_transactions[category].add(transaction_id)
        
        self.total_transactions = len(self.transaction_categories)
        print(f"✅ 处理完成: {self.total_transactions} 个有效交易, {len(self.category_transactions)} 种商品类别")
    
    def calculate_support(self, category_set: Set[str]) -> float:
        """
        计算商品种类集合的支持度
        
        Args:
            category_set: 商品种类集合
            
        Returns:
            支持度 (0-1之间)
        """
        if not category_set:
            return 0.0
        
        # 找到包含所有种类的交易
        transactions_with_all = None
        for category in category_set:
            category_transactions = self.category_transactions[category]
            if transactions_with_all is None:
                transactions_with_all = category_transactions.copy()
            else:
                transactions_with_all &= category_transactions
        
        return len(transactions_with_all) / self.total_transactions if transactions_with_all else 0.0
    
    def calculate_confidence(self, antecedent: Set[str], consequent: Set[str]) -> float:
        """
        计算置信度: P(consequent|antecedent)
        
        Args:
            antecedent: 前件商品种类集合
            consequent: 后件商品种类集合
            
        Returns:
            置信度 (0-1之间)
        """
        antecedent_support = self.calculate_support(antecedent)
        if antecedent_support == 0:
            return 0.0
        
        combined_support = self.calculate_support(antecedent | consequent)
        return combined_support / antecedent_support
    
    def calculate_lift(self, category_a: Set[str], category_b: Set[str]) -> float:
        """
        计算提升度: P(A,B) / (P(A) * P(B))
        
        Args:
            category_a: 商品种类集合A
            category_b: 商品种类集合B
            
        Returns:
            提升度
        """
        support_a = self.calculate_support(category_a)
        support_b = self.calculate_support(category_b)
        support_ab = self.calculate_support(category_a | category_b)
        
        if support_a == 0 or support_b == 0:
            return 0.0
        
        return support_ab / (support_a * support_b)
    
    def find_frequent_category_pairs(self, min_support: float = 0.001, min_confidence: float = 0.03) -> List[Dict]:
        """
        找出频繁商品种类对
        
        Args:
            min_support: 最小支持度阈值
            min_confidence: 最小置信度阈值
            
        Returns:
            频繁商品种类对列表
        """
        print(f"🔍 分析商品种类关联 (最小支持度: {min_support}, 最小置信度: {min_confidence})...")
        
        frequent_pairs = []
        all_pairs_info = []  # 存储所有商品对的信息用于调试
        categories = list(self.category_transactions.keys())
        
        # 生成所有商品种类对组合
        total_pairs = len(list(combinations(categories, 2)))
        print(f"📈 需要分析 {total_pairs} 个商品种类对...")
        
        processed = 0
        support_count = 0  # 满足支持度的计数
        confidence_count = 0  # 满足置信度的计数
        
        for category_a, category_b in combinations(categories, 2):
            processed += 1
            if processed % 1000 == 0:
                print(f"  进度: {processed}/{total_pairs} ({processed/total_pairs*100:.1f}%)")
            
            set_a = {category_a}
            set_b = {category_b}
            set_ab = {category_a, category_b}
            
            # 计算各种指标
            support_ab = self.calculate_support(set_ab)
            confidence_a_to_b = self.calculate_confidence(set_a, set_b)
            confidence_b_to_a = self.calculate_confidence(set_b, set_a)
            lift = self.calculate_lift(set_a, set_b)
            
            # 记录所有商品对信息（前100个用于调试）
            if len(all_pairs_info) < 100:
                all_pairs_info.append({
                    'category_a': category_a,
                    'category_b': category_b,
                    'support': support_ab,
                    'confidence_a_to_b': confidence_a_to_b,
                    'confidence_b_to_a': confidence_b_to_a,
                    'lift': lift,
                    'transactions_count': int(support_ab * self.total_transactions)
                })
            
            # 检查支持度
            if support_ab >= min_support:
                support_count += 1
                
                # 检查置信度
                if confidence_a_to_b >= min_confidence or confidence_b_to_a >= min_confidence:
                    confidence_count += 1
                    frequent_pairs.append({
                        'category_a': category_a,
                        'category_b': category_b,
                        'support': support_ab,
                        'confidence_a_to_b': confidence_a_to_b,
                        'confidence_b_to_a': confidence_b_to_a,
                        'lift': lift,
                        'transactions_count': int(support_ab * self.total_transactions)
                    })
        
        # 按支持度排序
        frequent_pairs.sort(key=lambda x: x['support'], reverse=True)
        all_pairs_info.sort(key=lambda x: x['support'], reverse=True)
        
        # 输出调试信息
        print(f"\n📊 调试信息:")
        print(f"  总商品种类对数: {total_pairs}")
        print(f"  满足支持度阈值({min_support})的对数: {support_count}")
        print(f"  满足置信度阈值({min_confidence})的对数: {confidence_count}")
        print(f"  最终找到的关联对数: {len(frequent_pairs)}")
        
        print(f"\n🔝 支持度最高的前10个商品种类对:")
        for i, pair in enumerate(all_pairs_info[:10], 1):
            max_conf = max(pair['confidence_a_to_b'], pair['confidence_b_to_a'])
            print(f"{i:2d}. {pair['category_a']} ↔ {pair['category_b']}")
            print(f"    支持度: {pair['support']:.4f} | 最大置信度: {max_conf:.4f} | 提升度: {pair['lift']:.2f} | 共现次数: {pair['transactions_count']}")
        
        # 如果没有找到满足条件的对，输出更多统计信息
        if len(frequent_pairs) == 0:
            print(f"\n⚠️ 未找到满足条件的商品种类对，建议:")
            print(f"  1. 降低支持度阈值 (当前: {min_support})")
            print(f"  2. 降低置信度阈值 (当前: {min_confidence})")
            
            # 统计支持度分布
            support_values = [pair['support'] for pair in all_pairs_info]
            if support_values:
                print(f"\n📈 支持度统计:")
                print(f"  最大支持度: {max(support_values):.4f}")
                print(f"  平均支持度: {np.mean(support_values):.4f}")
                print(f"  中位数支持度: {np.median(support_values):.4f}")
                print(f"  支持度 > 0.001 的对数: {sum(1 for s in support_values if s > 0.001)}")
                print(f"  支持度 > 0.005 的对数: {sum(1 for s in support_values if s > 0.005)}")
        
        print(f"✅ 找到 {len(frequent_pairs)} 个满足条件的商品种类对")
        return frequent_pairs
    
    def save_associations_to_csv(self, associations: List[Dict], output_path: str):
        """
        将关联结果保存为CSV文件
        
        Args:
            associations: 关联分析结果
            output_path: 输出文件路径
        """
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    '商品种类A', '商品种类B', '支持度', 'A→B置信度', 'B→A置信度', '提升度'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for assoc in associations:
                    writer.writerow({
                        '商品种类A': assoc['category_a'],
                        '商品种类B': assoc['category_b'],
                        '支持度': f"{assoc['support']:.4f}",
                        'A→B置信度': f"{assoc['confidence_a_to_b']:.4f}",
                        'B→A置信度': f"{assoc['confidence_b_to_a']:.4f}",
                        '提升度': f"{assoc['lift']:.4f}"
                    })
            
            print(f"✅ 关联分析结果已保存到: {output_path}")
            
        except Exception as e:
            print(f"❌ 保存文件失败: {e}")
    
    def get_category_statistics(self) -> Dict:
        """获取商品种类统计信息"""
        category_counts = {}
        for category, transactions in self.category_transactions.items():
            category_counts[category] = len(transactions)
        
        return {
            'total_categories': len(self.category_transactions),
            'total_transactions': self.total_transactions,
            'avg_categories_per_transaction': np.mean([len(categories) for categories in self.transaction_categories.values()]),
            'most_frequent_categories': sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        }
    
    def print_analysis_summary(self, associations: List[Dict]):
        """打印分析摘要"""
        if not associations:
            print("📊 分析摘要: 未找到满足条件的商品种类关联")
            return
        
        print("\n📊 商品种类关联分析摘要")
        print("=" * 50)
        
        stats = self.get_category_statistics()
        print(f"总商品种类数: {stats['total_categories']}")
        print(f"总交易数: {stats['total_transactions']}")
        print(f"平均每笔交易商品种类数: {stats['avg_categories_per_transaction']:.2f}")
        
        print(f"\n🔝 最常购买的商品种类 Top 10:")
        for i, (category, count) in enumerate(stats['most_frequent_categories'][:10], 1):
            print(f"{i:2d}. {category}: {count} 次交易 ({count/stats['total_transactions']*100:.1f}%)")
        
        print(f"\n找到 {len(associations)} 个商品种类关联对:")
        
        # 显示前10个最强关联
        print("\n🔝 Top 10 最强关联商品种类对:")
        for i, assoc in enumerate(associations[:10], 1):
            max_conf = max(assoc['confidence_a_to_b'], assoc['confidence_b_to_a'])
            print(f"{i:2d}. {assoc['category_a']} ↔ {assoc['category_b']} "
                  f"(置信度: {max_conf:.3f}, 支持度: {assoc['support']:.3f}, "
                  f"提升度: {assoc['lift']:.2f})")


def analyze_category_associations(purchase_data_path: str, 
                                product_data_path: str,
                                output_path: str = None,
                                min_support: float = 0.001,
                                min_confidence: float = 0.03) -> List[Dict]:
    """
    分析商品种类关联的便捷函数
    
    Args:
        purchase_data_path: 购买数据文件路径
        product_data_path: 商品数据文件路径
        output_path: 输出CSV文件路径（可选）
        min_support: 最小支持度
        min_confidence: 最小置信度
        
    Returns:
        关联分析结果列表
    """
    # 创建分析器
    analyzer = CategoryAssociationAnalyzer(purchase_data_path, product_data_path)
    
    # 执行关联分析
    associations = analyzer.find_frequent_category_pairs(min_support, min_confidence)
    
    # 打印摘要
    analyzer.print_analysis_summary(associations)
    
    # 保存结果
    if output_path:
        analyzer.save_associations_to_csv(associations, output_path)
    else:
        # 默认保存路径
        base_dir = os.path.dirname(purchase_data_path)
        default_output = os.path.join(base_dir, "category_associations.csv")
        analyzer.save_associations_to_csv(associations, default_output)
    
    return associations


if __name__ == "__main__":
    # 测试代码
    print("🛒 商品种类关联分析工具")
    print("=" * 50)
    
    # 数据文件路径
    purchase_data_path = "/Users/afonsoyi/CodeBuddy/Shopping Assistant/data/user_purchase_data.csv"
    product_data_path = "/Users/afonsoyi/CodeBuddy/Shopping Assistant/data/product_data.csv"
    output_path = "/Users/afonsoyi/CodeBuddy/Shopping Assistant/data/category_associations.csv"
    
    # 检查数据文件是否存在
    if not os.path.exists(purchase_data_path):
        print(f"❌ 购买数据文件不存在: {purchase_data_path}")
        exit(1)
    
    if not os.path.exists(product_data_path):
        print(f"❌ 商品数据文件不存在: {product_data_path}")
        exit(1)
    
    try:
        # 执行关联分析
        associations = analyze_category_associations(
            purchase_data_path=purchase_data_path,
            product_data_path=product_data_path,
            output_path=output_path,
            min_support=0.001,     
            min_confidence=0.03    
        )
        
        print(f"\n🎉 分析完成! 结果已保存到: {output_path}")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()