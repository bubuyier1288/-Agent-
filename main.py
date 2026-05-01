"""
main.py — 入口 & 交互式 CLI
============================
支持两种运行方式：
  1. 单次问答模式：python main.py --query "你们的产品怎么收费？"
  2. 交互式对话模式：python main.py （默认）
"""

from __future__ import annotations

import argparse
import sys

from config import DEMO_MODE
from knowledge_base import KnowledgeBase
from orchestrator import MultiAgentOrchestrator

# 尝试使用 rich 进行美观输出，降级为普通 print
try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.text import Text

    console = Console()
    USE_RICH = True
except ImportError:
    USE_RICH = False


def print_banner() -> None:
    """打印欢迎横幅。"""
    banner = """
    ╔══════════════════════════════════════════════════════╗
    ║     🤖 多 Agent 协同客服自动化系统                    ║
    ║     Multi-Agent Customer Service System               ║
    ║                                                       ║
    ║     📂 Agents:                                        ║
    ║        1️⃣  ClassifierAgent  — 用户咨询分类           ║
    ║        2️⃣  RetrieverAgent   — 知识库检索             ║
    ║        3️⃣  ReplyAgent       — 自动回复生成           ║
    ║                                                       ║
    ║     输入 'quit' 或 'exit' 退出                         ║
    ║     输入 'help' 查看使用说明                           ║
    ╚══════════════════════════════════════════════════════╝
    """
    mode_label = "🟢 DEMO 模式" if DEMO_MODE else "🔵 OpenAI API 模式"
    if USE_RICH:
        console.print(Panel(banner, title="🚀 系统启动", border_style="bright_blue"))
        console.print(f"  当前运行模式：[bold]{mode_label}[/bold]\n")
    else:
        print(banner)
        print(f"  当前运行模式：{mode_label}\n")


def print_step(step: int, agent_name: str, content: str) -> None:
    """格式化打印每个 Agent 的处理结果。"""
    if USE_RICH:
        console.print(
            Panel(
                Markdown(content),
                title=f"Step {step}: {agent_name}",
                border_style="cyan",
            )
        )
    else:
        divider = "=" * 60
        print(f"\n{divider}")
        print(f"  Step {step}: {agent_name}")
        print(divider)
        print(content)
        print(divider + "\n")


def print_result(result) -> None:
    """打印完整处理结果。"""
    # Step 1: 分类结果
    c = result.classification
    if c:
        classification_text = (
            f"**类别**: {c.category}\n\n"
            f"**子类别**: {c.subcategory}\n\n"
            f"**置信度**: {c.confidence:.0%}\n\n"
            f"**摘要**: {c.summary}"
        )
        print_step(1, "分类 Agent (Classifier)", classification_text)

    # Step 2: 检索结果
    if result.retrieved_docs:
        retrieval_text = f"共检索到 **{len(result.retrieved_docs)}** 条相关知识：\n\n"
        for i, doc in enumerate(result.retrieved_docs, 1):
            retrieval_text += (
                f"**[{i}]** 来源：{doc.metadata.get('source', '未知')} "
                f"（类别：{doc.metadata.get('category', '未知')}）\n"
                f"> {doc.page_content[:200]}{'...' if len(doc.page_content) > 200 else ''}\n\n"
            )
    else:
        retrieval_text = "未检索到相关知识。"
    print_step(2, "检索 Agent (Retriever)", retrieval_text)

    # Step 3: 回复
    print_step(3, "回复 Agent (Replier)", result.reply)

    # 耗时
    if USE_RICH:
        console.print(
            f"  ⏱️  处理耗时：[bold green]{result.elapsed_time:.2f}s[/bold green]\n"
        )
    else:
        print(f"\n  ⏱️  处理耗时：{result.elapsed_time:.2f}s\n")


def print_help() -> None:
    help_text = """
    📖 使用说明
    ===========
    • 直接输入您的问题，系统会自动分类、检索知识库并生成回复
    • 输入 'quit' 或 'exit' 退出系统
    • 输入 'help' 查看本帮助信息
    • 输入 'kb' 查看知识库概览

    💡 示例问题：
    • 你们的产品怎么收费的？
    • 我的订单怎么还没发货？
    • 我想退货，怎么操作？
    • 登录时总是报错怎么办？
    • 我要投诉你们的服务！
    """
    if USE_RICH:
        console.print(Panel(Markdown(help_text), title="📖 使用说明", border_style="yellow"))
    else:
        print(help_text)


def print_kb_overview(kb: KnowledgeBase) -> None:
    """打印知识库概览。"""
    categories = {}
    for doc in kb.raw_docs:
        cat = doc.get("category", "其他")
        categories[cat] = categories.get(cat, 0) + 1

    text = f"📚 知识库概览\n\n共 **{len(kb.raw_docs)}** 篇文档，**{len(kb.chunks)}** 个文本块。\n\n"
    for cat, count in categories.items():
        text += f"- {cat}: {count} 篇\n"
    print_step("📊", "知识库概览", text)


def run_single(query: str) -> None:
    """单次问答模式。"""
    print_banner()
    if USE_RICH:
        console.print(f"  👤 用户问题：[bold]{query}[/bold]\n")
    else:
        print(f"  👤 用户问题：{query}\n")

    kb = KnowledgeBase()
    orchestrator = MultiAgentOrchestrator(knowledge_base=kb)
    result = orchestrator.process(query)
    print_result(result)


def run_interactive() -> None:
    """交互式对话模式。"""
    print_banner()
    print_help()

    kb = KnowledgeBase()
    orchestrator = MultiAgentOrchestrator(knowledge_base=kb)

    while True:
        try:
            if USE_RICH:
                user_input = console.input("\n[bold cyan]👤 您> [/bold cyan]")
            else:
                user_input = input("\n👤 您> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 再见！")
            break

        if not user_input:
            continue

        cmd = user_input.lower()
        if cmd in ("quit", "exit", "q"):
            print("\n👋 再见！")
            break
        elif cmd == "help":
            print_help()
            continue
        elif cmd == "kb":
            print_kb_overview(kb)
            continue

        result = orchestrator.process(user_input)
        print_result(result)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="🤖 多 Agent 协同客服自动化系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py                           # 交互式对话模式
  python main.py --query "产品怎么收费"      # 单次问答模式
  python main.py --demo                    # 强制 Demo 模式
        """,
    )
    parser.add_argument(
        "--query", "-q",
        type=str,
        default=None,
        help="单次问答模式，直接传入问题",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        default=False,
help=强制使用演示模式（无需 API 密钥）,
    )

    args = parser.parse_args()

    # 如果命令行传入 --demo，覆盖配置
    if args.demo:
        import config
配置。DEMO_MODE = True

    if args.查询:
        运行单个(参数。查询)
否则:
        run_interactive()


如果 __name__ == "__main__":
    主()
