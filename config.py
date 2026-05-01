"""
config.py — 全局配置
====================
所有可调参数集中在此管理，方便部署时修改。
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ---------- LLM 配置 ----------
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
DEFAULT_TEMPERATURE: float = float(os.getenv("DEFAULT_TEMPERATURE", "0.3"))

# ---------- 是否使用 Demo 模式（无需 API Key） ----------
DEMO_MODE: bool = os.getenv("DEMO_MODE", "false").lower() == "true"

# ---------- 知识库配置 ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_STORE_PATH: str = os.path.join(BASE_DIR, "vector_store")
CHUNK_SIZE: int = 500
CHUNK_OVERLAP: int = 50

# ---------- 分类类别 ----------
QUERY_CATEGORIES: list[str] = [
    "产品咨询",    # product_inquiry
    "订单查询",    # order_tracking
    "售后服务",    # after_sale
    "技术支持",    # technical_support
“投诉建议”, # 投诉
“其他”, # 其他
]
