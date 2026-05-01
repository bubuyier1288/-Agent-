🤖 多 Agent 协同客服自动化系统
基于 LangChain 框架构建的多 Agent 协同客服系统，包含用户咨询分类、知识库检索、自动回复三大 Agent。

📐 系统架构
      ┌──────────────────────────────────────────────────┐
│ 多智能体编排器 │
│ （编排器 - orchestrator.py） │
└──────┬───────────────┬───────────────┬──────────┘
│ │ │
┌──────▼──────┐ ┌─────▼──────┐ ┌────▼───────┐
│ 第一步 │ │ 第二步 │ │ 第三步 │
│ 分类智能体 │ │ 检索智能体│ │ 回复智能体│
│ │ │ │ │ │
│ 分析用户 │ │ 从知识库 │ │ 综合上下文 │
│ 意图并分类 │─▶│ 检索相关 │─▶│ 生成专业 │
│ │ │ 文档片段 │ │ 客服回复 │
└────────────┘ └───────────┘ └────────────┘  复制  
### 三个 Agent 职责说明

|代理|文件|输入|输出|说明|
|-------|------|------|------|------|
| **ClassifierAgent** | `agents/classifier_agent.py` | 用户原始消息 | `{类别, 子类别, 置信度, 摘要}` | 判断用户咨询属于哪个类别 |
| **检索器代理** | `agents/retriever_agent.py` |用户消息 + 分类结果| `Document[]`列表|从知识库中检索最相关的文档片段|
| **ReplyAgent** | `agents/reply_agent.py` | 用户消息 + 分类 + 检索结果 | 最终回复文本 | 综合所有信息，生成友好准确的回复 |

---

## 🚀 快速开始

### 1. 环境准备

   bash Python 3.10+ python --version 创建虚拟环境 python -m venv venv
source venv/bin/activate # Linux/Mac 或 venv\Scripts\activate # Windows 复制
### 2. 安装依赖

   bash
pip install -r requirements.txt 复制
### 3. 配置

复制并编辑环境变量文件：

   bash
cp .env.example .env  复制  
编辑 `.env`：

   env 方式一：使用 OpenAI API（需要有效 API Key） OPENAI_API_KEY=sk-your-key-here
DEFAULT_MODEL=gpt-4o-mini
DEFAULT_TEMPERATURE=0.3
DEMO_MODE=false 方式二：Demo 模式（无需 API Key，使用内置规则引擎） DEMO_MODE=true  复制  
### 4. 运行

#### 🖥️ 交互式对话模式（推荐）

   bash
python main.py  复制  
输出示例：

   ╔══════════════════════════════════════════════════════╗
║ 🤖 多 Agent 协同客服自动化系统 ║
║ ║
║ 输入 ‘quit’ 或 ‘exit’ 退出 ║
║ 输入 ‘help’ 查看使用说明 ║
╚══════════════════════════════════════════════════════╝ 👤 您> 你们的产品怎么收费的？ Step 1: 分类 Agent (Classifier)
─────────────────────────────────────────────────────
类别: 产品咨询
置信度: 80%
摘要: 你们的产品怎么收费的
───────────────────────────────────────────────────── Step 2: 检索 Agent (Retriever)
─────────────────────────────────────────────────────
共检索到 3 条相关知识： [1] 来源：产品A - 云存储服务 我们的云存储服务提供100GB免费空间…
─────────────────────────────────────────────────────  Step 3: 回复 Agent (Replier)
─────────────────────────────────────────────────────
您好！感谢您对我们产品的关注。 根据您的咨询「你们的产品怎么收费的」，我为您找到了以下相关信息： 【产品A - 云存储服务】我们的云存储服务提供100GB免费空间…
【会员体系说明】会员等级分为普通会员、银卡会员… 如果您需要了解更多详情，或有其他疑问，欢迎随时咨询！😊
───────────────────────────────────────────────────── ⏱️ 处理耗时：0.03秒 复制
#### ⚡ 单次问答模式

   bash
python main.py --query “我的订单怎么还没发货？”
python main.py -q “登录时总是报错怎么办？”  复制  
#### 🧪 Demo 模式（无需 API Key）

   bash 方式一：通过 .env 配置 DEMO_MODE=true 方式二：命令行参数 python main.py --demo
python main.py --demo -q “我要退货”  复制  
---

## 📂 项目结构详解

   multi_agent_customer_service/
├── .env # 🔑 环境变量（API Key 等）
├── requirements.txt # 📦 Python 依赖
├── README.md # 📖 本文档
│
├── config.py # ⚙️ 全局配置（模型、路径、类别等）
├── knowledge_base.py # 📚 知识库管理（文档加载、分块、检索）
├── prompts.py # 💬 Prompt 模板集中管理
├── orchestrator.py # 🎯 多 Agent 编排器（核心流水线）
├── main.py # 🚀 入口文件 & CLI 交互界面
│
└── agents/ # 🤖 三个 Agent 实现
├── init.py # Agent 包导出
├── classifier_agent.py # Agent 1: 用户咨询分类
├── retriever_agent.py # Agent 2: 知识库检索
└── reply_agent.py # Agent 3: 自动回复生成 复制
---

## 🧠 核心设计思想

### 1. Agent 职责单一 & 松耦合

每个 Agent 只负责一个明确的任务，通过 **结构化数据**（非自然语言）传递中间结果：

   用户消息
│
▼
分类器代理 ──→ 分类结果（类别、子类别、置信度、摘要）
│
▼
RetrieverAgent ──→ 列表[文档](页面内容，元数据)
│
▼
ReplyAgent ──→ 字符串（最终回复文本） 复制
### 2. Prompt 集中管理

所有 Prompt 模板在 `prompts.py` 中统一定义和维护，方便：
- A/B 测试不同 Prompt
- 非研发人员调整话术
- 版本管理和回溯

### 3. 双模式运行

| 模式 | 适用场景 | LLM | 检索方式 |
|------|---------|-----|---------|
| **API模式** |生产环境|GPT-4o-mini|FAISS向量检索|
| **演示模式** |开发调试 / 演示|规则引擎|关键词匹配|

### 4. 知识库设计

- 内置 8 篇示例文档，覆盖产品、订单、售后、技术、投诉等场景
- 支持自定义文档分块（chunk_size / chunk_overlap）
- 生产环境可替换为 FAISS 持久化向量库

---

## 🔧 自定义扩展

### 添加新的知识文档

编辑 `knowledge_base.py` 中的 `SAMPLE_KNOWLEDGE` 列表：

   python
SAMPLE_KNOWLEDGE.append({
“title”: “新功能说明”,
“content”: “这里写知识内容…”,
“category”: “产品咨询”,
})  复制  
### 添加新的分类类别

1. 在 `config.py` 的 `查询类别` 中添加类别名称
2. 在 `agents/classifier_agent.py` 的 `_demo_classify` 中添加关键词规则
3.提示会自动更新（从`QUERY_CATEGORIES`动态生成）

### 接入真实向量数据库

修改 `knowledge_base.py` 的 `retrieve` 方法，将 `self.kb` 替换为持久化的 FAISS 索引：

   python 首次构建向量库 from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings embeddings = OpenAIEmbeddings(openai_api_key=“your-key”)
db = FAISS.from_documents(chunks, embeddings)

###切换LLM模型

在 `.env` 中修改：

   环境
DEFAULT_MODEL=gpt-4o # 更强大的模型
DEFAULT_MODEL=gpt-3.5-turbo # 更经济的选择 复制
---

## 🧪 测试用例

   产品咨询 bash 产品咨询 python main.py -q “你们的云存储服务怎么收费的？” 订单查询 python main.py -q “我的订单号 2024010001 怎么还没发货？” 售后服务 python main.py -q “我买的的东西想退货，怎么操作？” 技术支持 python main.py -q “登录的时候页面一直转圈圈打不开” 投诉建议 python main.py -q “你们客服态度太差了我要投诉！” 边界测试 python main.py -q “今天天气怎么样？” # 分类为"其他"
python main.py -q “” # 空输入  复制  
---

## 📊 示例对话流程

    您：你们的云存储服务怎么收费的？ 第一步[分类 Agent]：
✅ 类别: 产品咨询 | 置信度: 80% 第二步[检索 Agent]:
📄 检索到 3 条相关知识
├─ [1] 产品A - 云存储服务
├─ [2] 会员体系说明
└─ [3]产品B - 在线办公套件 第3步[回复 代理]:
💬 您好！感谢您对我们产品的关注。
我们的云存储服务提供100GB免费空间，支持多种格式上传。
付费版提供1TB空间，月费仅需29元，还支持文件版本回溯…
⏱️ 耗时: 0.83s  复制  
---

## ⚠️ 注意事项

1. **API 费用**：使用 OpenAI API 模式会产生费用，建议开发时使用 Demo 模式
2. **知识库规模**: 当前为示例知识库，生产环境需要导入真实业务知识文档
3. **并发处理**: 当前为同步处理，高并发场景需引入消息队列和异步框架
4. **安全**: 实际部署时建议加入用户输入过滤、敏感词检测等安全机制

---

## 许可证

MIT 许可证 - 可自由使用、修改和分发。
