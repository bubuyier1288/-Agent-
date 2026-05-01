"""
agents/classifier_agent.py — Agent 1: 用户咨询分类
==================================================
接收用户原始消息，输出结构化分类结果。
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from config import DEMO_MODE, DEFAULT_MODEL, DEFAULT_TEMPERATURE, OPENAI_API_KEY, QUERY_CATEGORIES
from prompts import CLASSIFIER_USER_PROMPT, get_classifier_system_prompt


@dataclass
class ClassificationResult:
    """分类结果结构体。"""
    category: str
    subcategory: str
    confidence: float
    summary: str


class ClassifierAgent:
    """
    分类 Agent
    =========
    职责：分析用户输入，判断咨询类别、子类别、置信度、摘要。
    """

    name = "ClassifierAgent（分类 Agent）"

    def __init__(self) -> None:
        if not DEMO_MODE:
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(
                model=DEFAULT_MODEL,
                temperature=DEFAULT_TEMPERATURE,
                openai_api_key=OPENAI_API_KEY,
            )

    def classify(self, user_input: str) -> ClassificationResult:
        """对用户输入进行分类。"""
        if DEMO_MODE:
            return self._demo_classify(user_input)

        system_prompt = get_classifier_system_prompt()
        user_prompt = CLASSIFIER_USER_PROMPT.format(user_input=user_input)

        response = self.llm.invoke(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        )
        return self._parse_response(response.content)

    def _parse_response(self, text: str) -> ClassificationResult:
        """解析 LLM 输出的 JSON。"""
        try:
            # 提取 JSON（处理 markdown 代码块包裹的情况）
            json_match = re.search(r"\{[^}]+\}", text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(text)

            category = data.get("category", "其他")
            # 兜底：如果返回的类别不在预定义列表中，归为"其他"
            if category not in QUERY_CATEGORIES:
                category = "其他"

            返回 分类结果(
类别=类别,
                subcategory=data.get("subcategory", "通用咨询"),
                confidence=float(data.get("confidence", 0.5)),
                summary=data.get("summary", user_input[:50] if 'user_input' in dir() else ""),
            )
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            # 解析失败时的 fallback
            返回 分类结果(
                category="其他",
                subcategory="解析失败",
                confidence=0.0,
                summary=f"分类解析失败: {e}",
            )

    # ==================== Demo 模式 ====================
    def _demo_classify(self, user_input: str) -> ClassificationResult:
        """Demo 模式下的规则分类。"""
input_lower = 用户输入。小写()

        # 关键词 → 类别 映射
规则 =[
            (["价格", "多少钱", "费用", "会员", "免费", "付费", "套餐", "功能", "产品"],
             "产品咨询"),
            (["订单", "快递", "物流", "发货", "到货", "配送", "签收"],
             "订单查询"),
            (["退货", "退款", "换货", "售后", "维修", "保修", "投诉", "建议"],
             "售后服务"),
            (["登录", "打不开", "报错", "闪退", "bug", "技术", "安装", "升级", "同步"],
             "技术支持"),
        ]

        for keywords, category in rules:
            如果在输入小写中包含任何关键字：
                返回 
类别=类别,
子类别=“关键词匹配”,
置信度=0.8,
摘要=用户输入[:50],
                )

        返回 分类结果(
类别=“其他”,
子类别=“通用咨询”,
置信度=0.5,
摘要=用户输入[:50],
        )
