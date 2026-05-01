"""
knowledge_base.py — 知识库构建与向量检索
========================================
提供示例知识数据、文档分块、FAISS 向量库创建和相似度检索。
Demo 模式下使用简单的关键词匹配代替向量检索。
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field

from config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DEFAULT_MODEL,
    DEMO_MODE,
    OPENAI_API_KEY,
    VECTOR_STORE_PATH,
)

# ==================== 内置示例知识文档 ====================
SAMPLE_KNOWLEDGE: list[dict[str, str]] = [
    {
        "title": "产品A - 云存储服务",
        "content": (
            "我们的云存储服务提供100GB免费空间，支持图片、文档、视频等多种格式上传。"
            "付费版提供1TB空间，月费29元。支持文件版本回溯，最多保留30天历史版本。"
            "支持多端同步，包括Windows、Mac、iOS和Android客户端。"
            "上传单文件大小限制：免费用户200MB，付费用户5GB。"
            "共享链接可设置密码保护和有效期，最长可设365天。"
        ),
        "category": "产品咨询",
    },
    {
        "title": "产品B - 在线办公套件",
        "content": (
            "在线办公套件包含文档编辑、表格处理、演示文稿三大模块。"
            "支持多人实时协作编辑，单文档最多支持100人同时在线。"
            "提供丰富的模板库，涵盖报告、方案、合同、简历等场景。"
            "付费版支持导出为PDF、Word、Excel格式，免费版仅支持在线查看。"
            "企业版还提供权限管理、审批流程、水印等高级功能。"
        ),
        "category": "产品咨询",
    },
    {
        "title": "订单状态查询",
        "content": (
            "您可以通过以下方式查询订单状态：\n"
            "1. 登录官网，进入「我的订单」页面查看实时状态；\n"
            "2. 使用订单号在搜索框直接查询；\n"
            "3. 拨打客服热线400-888-9999，提供订单号由客服查询。\n"
            "订单状态说明：\n"
            "- 待支付：订单已创建，等待完成付款；\n"
            "- 处理中：订单已支付，系统正在处理；\n"
            "- 已发货：商品已发出，可查看物流信息；\n"
            "- 已完成：订单已确认收货；\n"
            "- 已取消：订单已被取消。"
        ),
        "category": "订单查询",
    },
    {
        "title": "退换货政策",
        "content": (
            "自签收之日起7天内可申请无理由退换货。退换货条件：\n"
            "1. 商品完好、包装齐全、配件未拆封使用；\n"
            "2. 赠品和发票一并退回；\n"
            "3. 数字产品和定制商品不支持无理由退换。\n"
            "退货流程：在「我的订单」中提交退换申请 → 审核通过后寄回 → 验收后3-5个工作日退款。"
            "退款将原路返回至您的支付账户。"
        ),
        "category": "售后服务",
    },
    {
        "title": "售后服务联系方式",
        "content": (
            "售后服务热线：400-888-9999（工作日 9:00-18:00）\n"
            "在线客服：官网右下角「在线咨询」按钮，7×24小时在线。\n"
            "邮箱：service@example.com，我们会在24小时内回复。\n"
            "微信公众号：搜索「ExampleService」关注后可在线咨询。"
        ),
        "category": "售后服务",
    },
    {
        "title": "技术支持 - 常见问题",
        "content": (
            "常见技术问题及解决方案：\n"
            "1. 无法登录：请检查账号密码是否正确，尝试重置密码；\n"
            "2. 页面加载缓慢：请清除浏览器缓存，或尝试更换浏览器（推荐Chrome最新版）；\n"
            "3. 文件上传失败：请检查文件大小是否超过限制，网络是否稳定；\n"
            "4. 协作编辑冲突：建议同一文档同时编辑人数不超过50人；\n"
            "5. 移动端闪退：请更新App至最新版本，或重新安装。\n"
            "如以上方案无法解决，请联系技术支持邮箱：tech@example.com"
        ),
        "category": "技术支持",
    },
    {
        "title": "投诉与建议渠道",
        "content": (
            "我们非常重视用户的每一条反馈。\n"
            "投诉渠道：\n"
            "- 客服热线：400-888-9999 转 9\n"
            "- 邮箱：feedback@example.com\n"
            "- 官网：进入「帮助中心」→「投诉建议」填写表单\n"
            "处理时效：一般投诉3个工作日内回复，复杂问题5个工作日内回复。\n"
            "建议渠道同上，优秀建议采纳后将获得积分奖励。"
        ),
        "category": "投诉建议",
    },
    {
        "title": "会员体系说明",
        "content": (
            "会员等级分为普通会员、银卡会员、金卡会员、钻石会员四个等级。\n"
            "升级规则：\n"
            "- 消费满500元升级银卡，享受9.5折优惠；\n"
            "- 消费满2000元升级金卡，享受9折优惠+专属客服；\n"
            "- 消费满10000元升级钻石会员，享受8.5折优惠+专属客服+优先发货。\n"
            "会员积分规则：每消费1元获得1积分，积分可在商城兑换礼品或抵扣订单。"
        ),
        "category": "产品咨询",
    },
]


# ==================== 简单文档分割器 ====================
def split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """按句子边界分块，返回文本块列表。"""
    sentences = re.split(r"(?<=[。！？\n])", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    chunks: list[str] = []
    current_chunk = ""
    for sent in sentences:
        if len(current_chunk) + len(sent) <= chunk_size:
            current_chunk += sent
        else:
            if current_chunk:
                chunks.append(current_chunk)
            # 加入 overlap：从上一个 chunk 尾部截取部分句子
            if overlap > 0 and chunks:
                overlap_text = chunks[-1][-overlap:]
                current_chunk = overlap_text + sent
            else:
                current_chunk = sent
    if current_chunk:
        chunks.append(current_chunk)
    return chunks


# ==================== 文档对象 ====================
@dataclass
class Document:
    page_content: str
    metadata: dict = field(default_factory=dict)


# ==================== 知识库管理器 ====================
class KnowledgeBase:
    """管理知识文档的加载、分块、检索。"""

    def __init__(self, documents: list[dict[str, str]] | None = None):
        self.raw_docs = documents or SAMPLE_KNOWLEDGE
        self.chunks: list[Document] = []
        self._build_chunks()

    def _build_chunks(self) -> None:
        """将原始文档切分为小块。"""
        self.chunks = []
        for doc in self.raw_docs:
            chunks = split_text(doc["content"])
            for i, chunk_text in enumerate(chunks):
                self.chunks.append(
                    Document(
                        page_content=chunk_text,
                        metadata={
                            "source": doc["title"],
                            "category": doc.get("category", "其他"),
                            "chunk_index": i,
                        },
                    )
                )

    def retrieve(self, query: str, top_k: int = 3) -> list[Document]:
        """
        检索与 query 最相关的文档块。
        Demo 模式：简单关键词匹配。
        真实模式：调用 LangChain FAISS 向量检索。
        """
        if DEMO_MODE:
            返回self._keyword_retrieve(query, top_k)

        # ---- LangChain FAISS 检索 ----
        try:
            from langchain_community.vectorstores import FAISS
            from langchain_openai import OpenAIEmbeddings

            embeddings = OpenAIEmbeddings(
                openai_api_key=OPENAI_API_KEY,
                model="text-embedding-3-small",
            )
            # 每次检索时构建临时向量库（生产环境应持久化）
            faiss_db = FAISS.from_documents(self.chunks, embeddings)
            results = faiss_db.similarity_search(query, k=top_k)
            返回结果# type: ignore[return-value]
除异常外：
            print(f"[知识库] FAISS 检索失败，降级为关键词匹配: {e}")
            返回self._keyword_retrieve(query, top_k)

     _keyword_retrieve(self, query: str, top_k: int = 3) -> list[Document]:
        “基于关键词频率的简单检索（Demo 用）”
        query_words = set(query)
得分：列表元组[float, 文档]] = []
        对于doc在self.分块:
分数 =(1 对于w在查询词如果w在文档.页面内容)
            如果分数 >
得分.追加((分数, 文档))
得分。排序key=lambdax: x[0], reverse=True)
        返回 [文档for_, 文档in得分[:前k个]]

    def format_docs(self, docs: list[Document]) -> str:
        """将检索到的文档格式化为可读文本。"""
        parts = []
        for i, doc in enumerate(docs, 1):
部分。追加(f"[{i}]来源：doc.metadata.get'source','未知')页面内容"
        返回 "  ---  ".join(parts)
