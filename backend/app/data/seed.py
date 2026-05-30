"""知识库种子数据初始化"""

import logging

from app.rag.vector_store import vector_store

logger = logging.getLogger(__name__)

FAQ_DOCUMENTS = [
    # ── 简历相关 ──
    "简历一般控制在1-2页A4纸以内，重点突出与目标岗位相关的经验和技能。使用PDF格式投递可确保排版一致。",
    "简历的STAR原则：Situation（情境）、Task（任务）、Action（行动）、Result（结果）。每段项目经历都应包含这四个要素，特别是量化结果。",
    "简历中常见的空洞动词包括：负责、参与、协助、处理。建议替换为：设计、实现、优化、搭建、主导、推动。",
    "技术简历的技能清单应分为：精通（日常使用）、熟悉（项目用过）、了解（学习过）三个等级，避免所有技能都写「熟练掌握」。",

    # ── 面试相关 ──
    "技术面试一般包括：自我介绍（1-2分钟）、项目深挖（STAR追问）、基础知识（算法/系统设计/语言特性）、场景题（开放性问题）、反问环节。",
    "行为面试常见问题：「请分享一次你解决困难问题的经历」「描述一次团队冲突你如何处理」「你的职业规划是什么」。建议用STAR结构回答。",
    "面试反问环节可以问：团队技术栈和研发流程、这个岗位的核心挑战、团队成员的成长路径、代码评审流程等。避免问薪资和加班时间。",
    "系统设计面试常用框架：需求分析→数据模型→系统架构→核心流程→扩展性考虑。把思考过程说出来比最终答案更重要。",

    # ── 求职策略 ──
    "2026年AI Agent方向热门技能：LangGraph/CrewAI等Agent框架、RAG检索增强生成、Prompt Engineering、Function Calling、向量数据库、SSE流式。",
    "投递策略：海投（每天投20-30家）+ 精准投递（针对心仪公司定制简历）。数据显示定制简历的面试邀请率是海投的3倍。",
    "在校生找实习的最佳时间：大厂通常提前3-6个月开放暑期实习，建议前一年9-10月开始准备，次年1-3月集中投递。",
    "GitHub开源项目是展示技术能力的最佳方式，建议保持活跃提交、写好README、使用GitHub Pages做Demo展示。",

    # ── 职业发展 ──
    "AI Agent工程师的核心能力：LLM API集成与调优、多Agent编排（LangGraph/AutoGPT）、RAG检索增强、Prompt Engineering、Function Calling/Tool Use、评估体系设计。",
    "初级工程师成长建议：前3年深耕一个方向（如Agent开发），建立完整知识体系；多读开源项目代码；定期做技术输出（博客/分享）。",
    "技术面试准备建议提前3-4周开始，每天保持2-3小时练习。推荐资源：LeetCode（算法）、System Design Interview（系统设计）、各公司面经。",
]

INTERVIEW_QUESTIONS = [
    {
        "category": "technical",
        "question": "请解释LangGraph中StateGraph和MessageGraph的区别，以及你在项目中为什么选择StateGraph？",
        "expected_points": ["StateGraph有自定义状态", "MessageGraph简化版", "选型要考虑状态复杂度"],
    },
    {
        "category": "technical",
        "question": "RAG系统中你如何处理检索结果的去重和重排序？",
        "expected_points": ["MMR去重", "Cross-encoder重排序", "上下文窗口管理"],
    },
    {
        "category": "project",
        "question": "在多Agent系统中，如何处理某个Agent调用失败的情况？",
        "expected_points": ["重试机制", "降级策略", "错误传播控制", "用户友好提示"],
    },
    {
        "category": "behavioral",
        "question": "请分享一次你在项目中遇到的技术难点，以及你是如何解决的。",
        "expected_points": ["STAR结构", "具体问题具体方案", "量化结果"],
    },
    {
        "category": "technical",
        "question": "Streaming模式下，如何保证前端能正确解析并展示Agent的思考过程？",
        "expected_points": ["SSE事件格式设计", "事件类型区分", "前端状态管理"],
    },
]


def seed_knowledge_base():
    """初始化知识库向量数据"""
    if vector_store.count() > 0:
        logger.info(f"knowledge base already contains {vector_store.count()} documents")
        return

    # FAQ 文档
    faq_metadatas = [
        {"type": "faq", "topic": "简历", "source": "career-guide"}
        for _ in FAQ_DOCUMENTS
    ]
    vector_store.add_documents(FAQ_DOCUMENTS, faq_metadatas)

    # 面试题
    question_texts = [
        f"面试题（{q['category']}）：{q['question']} | 要点：{'、'.join(q['expected_points'])}"
        for q in INTERVIEW_QUESTIONS
    ]
    question_metadatas = [
        {"type": "interview_question", "category": q["category"], "source": "interview-bank"}
        for q in INTERVIEW_QUESTIONS
    ]
    vector_store.add_documents(question_texts, question_metadatas)

    logger.info(f"seeded {len(FAQ_DOCUMENTS)} FAQ + {len(INTERVIEW_QUESTIONS)} interview questions")
