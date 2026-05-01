"""
orchestrator.py — 多 Agent 编排器
=================================
协调三个 Agent 的调用顺序和数据流转。

处理流水线:
  用户输入 → ClassifierAgent → RetrieverAgent → ReplyAgent → 最终回复
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from agents import ClassifierAgent, ReplyAgent, RetrieverAgent
from agents.classifier_agent import ClassificationResult
from knowledge_base import Document, KnowledgeBase


@dataclass
class PipelineResult:
    """编排器的完整处理结果。"""
    user_input: str
    classification: ClassificationResult | None = None
    retrieved_docs: list[Document] = field(default_factory=list)
    reply: str = ""
    elapsed_time: float = 0.0
    error: str | None = None


class MultiAgentOrchestrator:
    """
    多 Agent 编排器
    ==============
    串联三个 Agent，形成完整的客服自动处理流水线。
    """

    def __init__(self, knowledge_base: KnowledgeBase | None = None) -> None:
        self.classifier = ClassifierAgent()
        self.kb = knowledge_base or KnowledgeBase()
        self.retriever = RetrieverAgent(knowledge_base=self.kb)
        self.replier = ReplyAgent()

    def process(self, user_input: str) -> PipelineResult:
        """
        完整处理一条用户消息。

        流程:
        ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
        │  Classifier  │ ──▶ │  Retriever   │ ──▶ │   Replier   │
        │  Agent       │     │  Agent       │     │   Agent     │
        └─────────────┘     └──────────────┘     └─────────────┘
              ↑                                         │
           用户输入                                  最终回复

        参数:
            user_input: 用户原始消息

        返回:
            PipelineResult 包含所有中间结果和最终回复
        """
        start_time = time.time()
        result = PipelineResult(user_input=user_input)

        try:
            # ---- 第一步：分类 ----
            result.分类= self.分类器.分类(用户输入)

            # ---- 第二步：检索 ----
            result.retrieved_docs = self.retriever.retrieve(
用户输入=用户输入,
类别=结果。分类.类别,
摘要=结果。分类.摘要,
                top_k=3,
            )

            # ---- 第三步：生成回复 ----
结果。回复= self。回复器。回复(
用户输入=用户输入,
类别=结果。分类.类别,
摘要=结果。分类.摘要,
                retrieved_docs=result.retrieved_docs,
            )

        except Exception as e:
            result.error = str(e)
结果。回复 = (
                抱歉，处理您的请求时出现了问题：{e} "
                "已为您转接人工客服，请稍候..."
            )

结果。运行时间= 时间。时间()- 开始时间
        返回结果
