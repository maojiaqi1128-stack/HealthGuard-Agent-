"""
HealthGuard-Agent - 病历分析脚本
用法: python analyze.py
输入病历文本 -> 输出结构化分析 + 相关指南建议
"""
import os
import sys
import json
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


async def analyze(note: str):
    from langchain_openai import ChatOpenAI
    from healthguard.config import get_settings
    from healthguard.rag.vectorstore import VectorStoreManager
    from healthguard.agents.cleaner import DataCleanerAgent
    from healthguard.agents.coder import ICD10CoderAgent

    settings = get_settings()

    # 初始化 LLM（DeepSeek）
    llm = ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_api_base,
        temperature=0.1,
    )

    print("\n" + "=" * 60)
    print("  HealthGuard-Agent 病历分析")
    print("=" * 60)
    print(f"\n病历内容：\n{note}\n")
    print("-" * 60)

    # ─── Step 1: 数据清洗 ───────────────────────────────────────
    print("\n[1/4] 数据清洗中...")
    cleaner = DataCleanerAgent(llm)
    state = {"raw_clinical_note": note, "processing_time": {}, "metadata": {}}
    cleaned = await cleaner.run(state)
    state.update(cleaned)
    sd = state.get("structured_data", {})

    print("  完成！提取到的关键信息：")
    demo = sd.get("demographics", {})
    if demo:
        print(f"  · 年龄/性别: {demo.get('age', '未知')}岁 / {demo.get('gender', '未知')}")
    pi = sd.get("present_illness", "")
    if pi:
        print(f"  · 现病史: {pi[:100]}...")
    meds = sd.get("medications", [])
    if meds:
        print(f"  · 用药: {', '.join(meds[:3])}")

    # ─── Step 2: ICD 编码 ──────────────────────────────────────
    print("\n[2/4] ICD-10 编码中...")
    coder = ICD10CoderAgent(llm)
    coded = await coder.run(state)
    state.update(coded)
    icd_codes = state.get("icd_codes", [])

    if icd_codes:
        print(f"  完成！共 {len(icd_codes)} 个编码：")
        for c in icd_codes:
            print(f"  · {c.get('code')} - {c.get('description')} (置信度 {c.get('confidence', 0):.0%})")
    else:
        print("  未生成 ICD 编码")

    # ─── Step 3: 构建查询词 ────────────────────────────────────
    print("\n[3/4] 检索相关指南...")
    query_parts = []
    if pi:
        query_parts.append(pi[:200])
    if sd.get("chief_complaint"):
        query_parts.append(sd["chief_complaint"])
    mh = sd.get("medical_history") or sd.get("past_medical_history", [])
    if mh:
        query_parts.extend(mh[:3])
    for c in icd_codes[:3]:
        if c.get("description"):
            query_parts.append(c["description"])
    # 兜底：直接用原始病历
    if not query_parts:
        query_parts.append(note[:400])

    query = " ".join(query_parts)[:500]
    print(f"  查询词: {query[:80]}...")

    vs = VectorStoreManager()
    results = vs.search(query=query, collection_name="clinical_guidelines", n_results=5)
    print(f"  找到 {len(results)} 条相关指南")

    # ─── Step 4: LLM 生成指南建议 ────────────────────────────
    print("\n[4/4] 生成临床指南建议...")

    from langchain_core.messages import SystemMessage, HumanMessage

    guideline_summaries = []
    for doc in results[:3]:
        title = doc.get("metadata", {}).get("title", "未知指南")
        content = doc.get("content", "")[:1000]
        score = doc.get("score", 0)

        prompt = f"""你是一个临床指南分析助手。
根据以下病历和指南内容，提取与该患者直接相关的建议。

病历摘要：{note[:300]}

指南内容：
标题：{title}
内容：{content}

请返回 JSON：
{{"summary": "2-3句关键摘要", "recommendations": ["建议1", "建议2", "建议3"]}}

只返回 JSON，不要解释。"""

        try:
            resp = await llm.ainvoke([
                SystemMessage(content="你是临床指南分析专家，只输出 JSON。"),
                HumanMessage(content=prompt),
            ])
            txt = resp.content.strip()
            if txt.startswith("```"):
                txt = txt.split("\n", 1)[1] if "\n" in txt else txt[3:]
                txt = txt.rsplit("```", 1)[0]
            parsed = json.loads(txt)
            guideline_summaries.append({
                "title": title,
                "score": score,
                "summary": parsed.get("summary", ""),
                "recommendations": parsed.get("recommendations", []),
            })
        except Exception as e:
            guideline_summaries.append({
                "title": title,
                "score": score,
                "summary": content[:200],
                "recommendations": [],
            })

    # ─── 输出报告 ──────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  分析报告")
    print("=" * 60)

    print("\n【患者基本信息】")
    demo = sd.get("demographics", {})
    print(f"  年龄: {demo.get('age', '未知')}岁")
    print(f"  性别: {demo.get('gender', '未知')}")
    vitals = sd.get("vitals", {})
    if vitals:
        print(f"  生命体征: {vitals}")

    print("\n【现病史】")
    print(f"  {sd.get('present_illness', note[:200])}")

    if sd.get("past_medical_history") or sd.get("medical_history"):
        mh = sd.get("past_medical_history") or sd.get("medical_history", [])
        print("\n【既往史】")
        for item in mh:
            print(f"  · {item}")

    if meds:
        print("\n【当前用药】")
        for m in meds:
            print(f"  · {m}")

    print("\n【ICD-10 编码】")
    if icd_codes:
        for c in icd_codes:
            print(f"  · {c.get('code')} - {c.get('description')}")
    else:
        print("  未生成编码")

    print("\n" + "=" * 60)
    print("  相关临床指南建议")
    print("=" * 60)

    if guideline_summaries:
        for i, g in enumerate(guideline_summaries, 1):
            score_pct = int(g["score"] * 100)
            print(f"\n{i}. 《{g['title']}》 （相关度 {score_pct}%）")
            if g["summary"]:
                print(f"   摘要：{g['summary']}")
            if g["recommendations"]:
                print("   关键建议：")
                for r in g["recommendations"]:
                    print(f"   ✓ {r}")
    else:
        print("  未找到相关指南，请检查知识库是否已导入数据。")

    print("\n" + "=" * 60)
    print("  分析完成")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    # 可直接修改这里的病历内容
    CLINICAL_NOTE = """
患者男性，65岁，主诉胸闷气短3天。
既往高血压10年，糖尿病5年。
体格检查：BP 150/95 mmHg，心率82次/分，节律整齐。
心电图示ST段压低0.5mm。
既往用药：二甲双胍 500mg bid，氨氯地平 5mg qd。
空腹血糖 8.2 mmol/L，HbA1c 7.8%。
""".strip()

    asyncio.run(analyze(CLINICAL_NOTE))
