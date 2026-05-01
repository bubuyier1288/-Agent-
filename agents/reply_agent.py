"""
agents/reply_agent.py — Agent 3: 自动回复生成
==============================================
根据分类信息 + 检索到的知识 + 用户原文，生成最终回复。
"""

from __future__ import annotations

import re

from config import (
    DEMO_MODE,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    OPENAI_API_KEY,
)
from knowledge_base import Document, KnowledgeBase
from prompts import REPLIER_SYSTEM_PROMPT, REPLIER_USER_PROMPT


class ReplyAgent:
    """
    回复 Agent
    =========
    职责：综合所有上下文信息，生成友好、准确的客服回复。
    """

    name = "ReplyAgent（回复 Agent）"

    def __init__(self) -> None:
        if not DEMO_MODE:
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(
                model=DEFAULT_MODEL,
                temperature=DEFAULT_TEMPERATURE,
                openai_api_key=OPENAI_API_KEY,
            )

    def reply(
        self,
用户输入: 字符串,
类别: 字符串,
摘要: 字符串,
        retrieved_docs: list[文档],
    ) -> str:
        """生成回复。"""
        knowledge_context = KnowledgeBase.format_docs(retrieved_docs)

        如果DEMO_MODE:
            返回self._demo_reply(用户输入, 类别, 摘要, 检索到的文档)

系统提示 = 回复器系统提示.格式化(
类别=类别,
摘要=摘要,
用户输入=用户输入,
知识上下文=知识上下文,
        )

响应 = self.llm.调用(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": REPLIER_USER_PROMPT},
            ]
        )
        返回self._clean_reply(response.content)

    def _clean_reply(self, text: str) -> str:
        “””清理LLM输出（去除可能的markdown引用等）。””
        text = re.sub(r"^
