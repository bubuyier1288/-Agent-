"""
agents/retriever_agent.py — Agent 2: 知识库检索
================================================
根据分类结果和用户消息，从知识库中检索相关文档片段。
"""

from __future__ import annotations

from knowledge_base import Document, KnowledgeBase


class RetrieverAgent:
    """
    检索 Agent
    =========
    职责：理解用户意图 + 分类信息，构建检索查询，返回相关知识。
    """

名称 ="检索 Agent"

    def __init__(self, knowledge_base: KnowledgeBase | None = None) -> None:
        self.kb = knowledge_base or KnowledgeBase()

    def 检索(
        self,
用户输入: 字符串,
类别: 字符串,
摘要: 字符串,
        top_k: int = 3,
    )-> 列表[文档]:
        """
        执行检索。

        参数:
            user_input : 用户原始消息
            category   : 分类 Agent 输出的类别
            summary    : 分类 Agent 输出的摘要
            top_k      : 返回文档数量

        返回:
            最相关的 Document 列表
        """
        # 构建检索 query：融合用户原文 + 类别信息
        query = f"{user_input} {category} {summary}"
        docs = self.kb.retrieve(query, top_k=top_k)
        返回文档
