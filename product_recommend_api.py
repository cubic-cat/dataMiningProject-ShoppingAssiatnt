#!/usr/bin/env python3
"""
智能商品推荐API
基于用户购物习惯、需求、预算、送礼对象等信息，使用通义千问大模型推荐合适的商品
"""

import json
import csv
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests
from analyze_user_api import UserPurchaseAnalyzer


class ProductRecommendationAPI:
    """基于用户购物习惯的商品推荐API类"""
    
    def __init__(self, api_key: str = None):
        """
        初始化推荐API
        
        Args:
            api_key: 通义千问API密钥
        """
        self.api_key = api_key or 'sk-d5dc87f4360f4134ac60bb65de4d46a2'
        self.api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
        # 初始化用户购买习惯分析器
        self.user_analyzer = UserPurchaseAnalyzer(
            purchase_data_path="/Users/afonsoyi/CodeBuddy/Shopping Assistant/data/user_purchase_data.csv",
            product_data_path="/Users/afonsoyi/CodeBuddy/Shopping Assistant/data/product_data.csv"
        )
        
        # 送礼对象选项
        self.gift_recipients = {
            "自己": "为自己购买",
            "朋友": "送给朋友",
            "对象": "送给恋人/伴侣",
            "父母": "送给父母"
        }
    
    def _get_budget_reference(self, user_id: int) -> Optional[float]:
        """
        获取用户购物习惯（仅获取平均每单消费金额）
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户购物习惯分析结果（仅包含平均每单消费）
        """
        try:
            # 使用现有的分析API获取用户习惯
            habits = self.user_analyzer.analyze_user_habits(user_id)
            if habits and 'avg_order_amount' in habits:
                return float(habits['avg_order_amount'])
            return None
        except Exception as e:
            print(f"获取用户购物习惯失败: {e}")
            return None
    
    def validate_input(self, user_id: int, budget: Optional[float], recipient: str, 
                      recipient_info: str, requirement: str) -> Dict[str, Any]:
        """
        验证用户输入
        
        Args:
            user_id: 用户ID
            budget: 预算金额
            recipient: 送礼对象
            recipient_info: 送礼对象补充信息
            requirement: 用户需求描述
            
        Returns:
            验证结果字典
        """
        errors = []
        
        # 验证用户ID
        if not isinstance(user_id, int) or user_id <= 0:
            errors.append("用户ID必须是正整数")
        
        # 验证预算
        if budget is not None and budget <= 0:
            errors.append("预算必须大于0")
        
        # 验证送礼对象
        if recipient not in self.gift_recipients:
            errors.append(f"送礼对象必须是: {', '.join(self.gift_recipients.keys())}")
        
        # 验证需求描述
        if not requirement or len(requirement.strip()) < 3:
            errors.append("需求描述至少需要3个字符")
        
        # 如果选择非自己，需要补充信息
        if recipient != "自己" and (not recipient_info or len(recipient_info.strip()) < 2):
            errors.append(f"选择送给{recipient}时，请提供更详细的补充信息（年龄、爱好等）")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _build_recommendation_prompt(self, user_id: int, budget: Optional[float], 
                                   recipient: str, recipient_info: str, requirement: str) -> str:
        """
        构建基于用户购物习惯的推荐提示词
        
        Args:
            user_id: 用户ID
            budget: 预算金额
            recipient: 送礼对象
            recipient_info: 送礼对象补充信息
            requirement: 用户需求描述
            
        Returns:
            完整的提示词
        """
        
        # 如果没有预算，使用用户平均消费作为参考
        budget_info = ""
        if budget is not None:
            budget_info = f"¥{budget:.2f}"
        else:
            avg_budget = self._get_budget_reference(user_id)
            if avg_budget:
                budget_info = f"无特定限制（用户平均每单消费：¥{avg_budget:.2f}，可作为参考）"
            else:
                budget_info = "无特定预算限制"
        
        prompt = f"""你是一个专业的购物顾问，请根据以下信息为用户推荐合适的商品：

用户信息：
- 预算：{budget_info}
- 送礼对象：{self.gift_recipients[recipient]}
- 对象补充信息：{recipient_info if recipient != '自己' else '无'}
- 具体需求：{requirement}

请你：
1. 分析用户的需求和送礼场景
2. 结合用户的消费水平（如有数据）
3. 推荐3-5个最合适的商品类别
4. 每个类别推荐1-2个具体商品建议
5. 说明推荐理由
6. 给出购买建议和注意事项

请严格按照以下JSON格式返回，不要添加任何其他文字：
{{
    "analysis": "基于用户需求和消费习惯的分析",
    "recommendations": [
        {{
            "category": "商品类别",
            "products": ["商品1", "商品2"],
            "price_range": "建议价格范围",
            "reason": "推荐理由"
        }}
    ],
    "buying_tips": ["购买建议1", "购买建议2"],
    "budget_advice": "预算建议（基于用户消费习惯）",
    "summary": "总结建议"
}}

注意：
1. 推荐要符合用户的消费水平和预算范围
2. 结合送礼对象的特点
3. 只返回JSON，不要有其他格式的文字"""

        return prompt
    
    def _call_qwen_api(self, prompt: str) -> Dict[str, Any]:
        """
        调用通义千问API
        
        Args:
            prompt: 提示词
            
        Returns:
            API响应结果
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "未设置通义千问API密钥，请设置环境变量QWEN_API_KEY或在初始化时传入api_key参数"
            }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "qwen-turbo",
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 2000,
                "top_p": 0.8
            }
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # 处理通义千问API的返回格式
            if result.get("output"):
                # 新版API格式：使用 text 字段
                if result["output"].get("text"):
                    content = result["output"]["text"]
                # 旧版API格式：使用 choices 字段
                elif result["output"].get("choices"):
                    content = result["output"]["choices"][0]["message"]["content"]
                else:
                    return {
                        "success": False,
                        "error": f"API返回格式异常: {result}"
                    }
                
                return {
                    "success": True,
                    "content": content,
                    "usage": result.get("usage", {})
                }
            else:
                return {
                    "success": False,
                    "error": f"API返回格式异常: {result}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"API请求失败: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"处理API响应时出错: {str(e)}"
            }
    
    def _parse_ai_response(self, ai_content: str) -> Dict[str, Any]:
        """
        解析AI返回的内容
        
        Args:
            ai_content: AI返回的文本内容
            
        Returns:
            解析后的结构化数据
        """
        try:
            # 尝试直接解析JSON
            if ai_content.strip().startswith('{'):
                return json.loads(ai_content)
            
            # 如果不是纯JSON，尝试提取JSON部分
            import re
            json_match = re.search(r'\{.*\}', ai_content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # 如果无法解析JSON，返回原始文本
            return {
                "analysis": "AI推荐分析",
                "recommendations": [],
                "buying_tips": [],
                "budget_advice": "请参考历史消费习惯",
                "summary": ai_content,
                "raw_response": ai_content
            }
            
        except json.JSONDecodeError:
            # JSON解析失败，返回结构化的错误信息
            return {
                "analysis": "推荐分析",
                "recommendations": [],
                "buying_tips": ["请参考AI的详细建议"],
                "budget_advice": "建议参考历史消费习惯",
                "summary": ai_content,
                "raw_response": ai_content,
                "parse_error": True
            }
    
    def get_product_recommendations(self, user_id: int, budget: Optional[float] = None, 
                                 recipient: str = "自己", 
                                 recipient_info: str = "", 
                                 requirement: str = "") -> Dict[str, Any]:
        """
        获取基于用户购物习惯的商品推荐
        
        Args:
            user_id: 用户ID
            budget: 预算金额（可选，如果不提供则使用用户平均消费作为参考）
            recipient: 送礼对象（自己、朋友、对象、父母）
            recipient_info: 送礼对象补充信息
            requirement: 用户需求描述
            
        Returns:
            推荐结果字典
        """
        # 输入验证
        validation = self.validate_input(user_id, budget, recipient, recipient_info, requirement)
        if not validation["valid"]:
            return {
                "success": False,
                "errors": validation["errors"],
                "timestamp": datetime.now().isoformat()
            }
        
       
        # 如果没有预算，获取用户平均消费作为参考
        budget_reference = None
        if budget is None:
            budget_reference = self._get_budget_reference(user_id)
        
        # 构建提示词
        prompt = self._build_recommendation_prompt(user_id, budget, recipient, recipient_info, requirement)
        
        # 调用AI API
        ai_result = self._call_qwen_api(prompt)
        
        if not ai_result["success"]:
            return {
                "success": False,
                "error": ai_result["error"],
                "timestamp": datetime.now().isoformat()
            }
        
        # 解析AI响应
        recommendations = self._parse_ai_response(ai_result["content"])
        
        return {
            "success": True,
            "input": {             
                "budget": budget,
                "budget_reference": budget_reference,
                "recipient": recipient,
                "recipient_info": recipient_info,
                "requirement": requirement
            },
            "analysis": recommendations.get("analysis", ""),
            "recommendations": recommendations.get("recommendations", []),
            "buying_tips": recommendations.get("buying_tips", []),
            "budget_advice": recommendations.get("budget_advice", ""),
            "summary": recommendations.get("summary", ""),
            "ai_usage": ai_result.get("usage", {}),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_user_summary(self, user_id: int) -> Dict[str, Any]:
        """获取用户购物习惯摘要"""
        try:
            avg_amount = self._get_budget_reference(user_id)
            if avg_amount:
                return {
                    "user_id": user_id,
                    "avg_order_amount": avg_amount
                }
            return {"user_id": user_id, "error": "无购买数据"}
        except Exception as e:
            return {"user_id": user_id, "error": str(e)}
    
    def get_gift_recipients(self) -> Dict[str, str]:
        """获取送礼对象选项"""
        return self.gift_recipients.copy()
    
    def get_product_categories(self) -> List[str]:
        """获取用户常购商品类别"""
        try:
            categories = set()
            if hasattr(self.user_analyzer, 'product_map') and self.user_analyzer.product_map:
                categories.update(self.user_analyzer.product_map.values())
            return list(categories)
        except Exception as e:
            print(f"获取商品类别失败: {e}")
            return []
    
    def get_price_range(self) -> Dict[str, float]:
        """获取用户历史消费价格范围"""
        try:
            if hasattr(self.user_analyzer, 'purchase_data') and self.user_analyzer.purchase_data:
                amounts = [record['购买总金额(元)'] for record in self.user_analyzer.purchase_data]
                return {
                    "min": min(amounts),
                    "max": max(amounts),
                    "avg": sum(amounts) / len(amounts)
                }
            return {"min": 0, "max": 0, "avg": 0}
        except Exception as e:
            print(f"获取价格范围失败: {e}")
            return {"min": 0, "max": 0, "avg": 0}


# 便捷函数接口
def recommend_products(user_id: int, budget: Optional[float] = None, 
                      recipient: str = "自己", 
                      recipient_info: str = "", 
                      requirement: str = "") -> Dict[str, Any]:
    """
    便捷的商品推荐函数
    
    Args:
        user_id: 用户ID
        budget: 预算金额（可选，如果不提供则使用用户平均消费作为参考）
        recipient: 送礼对象
        recipient_info: 送礼对象补充信息
        requirement: 需求描述
        
    Returns:
        推荐结果
    """
    api = ProductRecommendationAPI()  # 使用默认API密钥
    return api.get_product_recommendations(user_id, budget, recipient, recipient_info, requirement)

def get_available_options() -> Dict[str, Any]:
    """
    获取可用选项（用于前端下拉框等）
    
    Returns:
        包含所有可用选项的字典
    """
    api = ProductRecommendationAPI()
    return {
        "gift_recipients": api.get_gift_recipients(),
        "product_categories": api.get_product_categories(),
        "price_range": api.get_price_range()
    }


if __name__ == "__main__":
    # 测试代码
    print("🎁 基于用户购物习惯的智能商品推荐API测试")
    print("=" * 60)
    
    # 获取可用选项
    options = get_available_options()
    print("可用选项:")
    print(f"  送礼对象: {list(options['gift_recipients'].keys())}")
    print(f"  商品类别: {options['product_categories'][:5]}... (共{len(options['product_categories'])}个)")
    print(f"  价格范围: ¥{options['price_range']['min']:.2f} - ¥{options['price_range']['max']:.2f} (平均: ¥{options['price_range']['avg']:.2f})")
    
    # 测试用户推荐 - 使用固定用户ID进行测试
    test_user_id = 25  # 使用一个测试用户ID
    print(f"\n测试用户 {test_user_id} 的购物习惯:")
    
    api = ProductRecommendationAPI()
    user_summary = api.get_user_summary(test_user_id)
    if 'error' not in user_summary:
        print(f"  平均每单消费: ¥{user_summary['avg_order_amount']:.2f}")
    else:
        print(f"  {user_summary['error']}")
    
    print("\n注意: API密钥已配置，可以直接使用AI推荐功能")
    print("示例调用: recommend_products(user_id=25, requirement='圣诞礼物推荐')")