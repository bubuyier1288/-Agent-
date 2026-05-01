"""
agents/reply_agent.py — 代理3：自动生成回复
==============================================
根据分类信息 + 检索到的知识 + 用户原文，生成最终回复。
"""

from __future__ import annotations

import re

from config import (
演示模式,
默认模型,
默认温度,
OpenAI API密钥,
)
从知识库导入文档、知识库
从提示词导入回复器系统提示词、回复器用户提示词


类ReplyAgent：
    """
    回复 Agent
    =========
    职责：综合所有上下文信息，生成友好、准确的客服回复。
    """

名称 =“回复Agent（回复代理）”

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
        user_input: str,
类别: 字符串,
摘要: 字符串,
        retrieved_docs: list[Document],
    )-> 字符串：
        """生成回复。"""
        knowledge_context = KnowledgeBase.format_docs(retrieved_docs)

        if DEMO_MODE:
            return self._demo_reply(user_input, category, summary, retrieved_docs)

system_prompt = REPLIER_SYSTEM_PROMPT。format(
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
.*?\n", “”, text, flags=re.DOTALL)
text = re.sub(r"\n```$", “”, text)
return text.strip()

# ==================== 演示模式 ====================
def _demo_reply(
    self,
用户输入: 字符串,
类别: 字符串,
摘要: 字符串,
    retrieved_docs: list[Document],
)-> 字符串：
    “在Demo模式下基于模板生成回复。”
    # 根据类别选择回复模板
    templates = {
        "产品咨询": (
“您好！感谢您对我们产品的关注。”
根据您的咨询「{summary}」，我为您找到了以下相关信息：
            "{info}\n\n"
            "如果您需要了解更多详情，或有其他疑问，欢迎随时咨询！😊"
        ),
        "订单查询": (
“您好！关于您的订单问题：  ”
“根据您的查询「{summary}」，以下是相关信息：  ”
            "{info}\n\n"
            "如需进一步帮助，请提供订单号，我将为您详细查询。还有其他问题吗？"
        ),
        "售后服务": (
            "您好！关于您的售后问题，我非常理解您的感受。\n\n"
“针对「{summary}」，这里为您提供以下解决方案：  ”
            "{info}\n\n"
            "如果以上信息未能完全解决您的问题，建议拨打售后热线 400-888-9999，"
            "我们的专员会为您提供一对一服务。祝您生活愉快！"
        ),
        "技术支持": (
            "您好！关于您遇到的技术问题：\n\n"
            "「{summary}」— 以下是一些常见的解决方案：\n\n"
            "{info}\n\n"
            "如果问题仍然存在，请联系技术支持邮箱 tech@example.com，"
            "我们会尽快协助您解决。还有其他问题吗？"
        ),
        "投诉建议": (
“您好！非常感谢您的宝贵反馈。  ”
“关于「{summary}」，我们深表歉意/感谢。  ”
            "{info}\n\n"
            "您的反馈已记录，我们会在3个工作日内跟进处理。"
            "如需紧急处理，请致电 400-888-9999 转 9。谢谢！"
        ),
        "其他": (
“您好！感谢您的咨询。  ”
“关于「{summary}」，以下是我能为您提供的信息：  ”
            "{info}\n\n"
            "如需更专业的解答，我将为您转接人工客服。还有其他问题吗？"
        ),
    }

template = templates.get(category, templates[“其他”])

    # 从检索结果中提取关键信息
    info_parts = []
    for doc in retrieved_docs[:2]:
        source = doc.metadata.get("source", "未知")
        info_parts.append(f"【{source}】{doc.page_content[:150]}{'...' if len(doc.page_content) > 150 else ''}\n\n")
    info_text = "\n".join(info_parts) if info_parts else "暂无匹配的知识条目，正在为您转接人工客服..."

    reply = template.format(summary=summary, info=info_text)
    return reply
