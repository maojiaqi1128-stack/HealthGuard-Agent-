"""
HealthGuard-Agent 知识库导入脚本
将 knowledge_base/ 目录下的临床指南文本文件向量化存入 ChromaDB
"""

import os
import sys
import hashlib
import time

# 确保 src 在 path 中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
os.environ["PYTHONPATH"] = os.path.join(os.path.dirname(__file__), "src")

from healthguard.config import get_settings
from healthguard.rag.vectorstore import VectorStoreManager
from healthguard.rag.indexer import chunk_text


def main():
    settings = get_settings()
    kb_dir = os.path.join(os.path.dirname(__file__), "knowledge_base")

    print("=" * 50)
    print("HealthGuard-Agent 知识库导入")
    print("=" * 50)
    print(f"指南目录: {kb_dir}")
    print(f"ChromaDB: {settings.chroma_persist_dir}")
    print()

    # 扫描文件
    files = []
    for f in sorted(os.listdir(kb_dir)):
        if f.endswith((".md", ".txt")):
            files.append(os.path.join(kb_dir, f))

    if not files:
        print("[ERROR] 未找到任何指南文件")
        return

    print(f"找到 {len(files)} 个指南文件:")
    for f in files:
        name = os.path.basename(f)
        size = os.path.getsize(f)
        print(f"  - {name} ({size:,} bytes)")
    print()

    # 向量化存储
    vectorstore = VectorStoreManager()
    all_docs = []
    all_metas = []
    all_ids = []

    for fpath in files:
        fname = os.path.basename(fpath)
        print(f"[处理] {fname}...")

        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if not content:
            print(f"  跳过（空文件）")
            continue

        # 提取标题（第一行 # 开头）
        title = fname.replace(".md", "").replace(".txt", "")
        first_line = content.split("\n")[0]
        if first_line.startswith("#"):
            title = first_line.lstrip("# ").strip()

        # 分块
        chunks = chunk_text(content, chunk_size=512, chunk_overlap=64)
        print(f"  分块: {len(chunks)} 段")

        for i, chunk in enumerate(chunks):
            doc_id = hashlib.md5(f"{fname}:{i}".encode()).hexdigest()[:16]
            all_docs.append(chunk)
            all_metas.append({
                "source": "HealthGuard 内建知识库",
                "title": title,
                "source_file": fname,
                "chunk_index": i,
                "total_chunks": len(chunks),
            })
            all_ids.append(doc_id)

    if not all_docs:
        print("[ERROR] 没有可导入的内容")
        return

    print(f"\n总计: {len(all_docs)} 个文本块")
    print("[导入] 正在生成向量嵌入并写入 ChromaDB...")
    start = time.time()

    try:
        vectorstore.add_documents(
            documents=all_docs,
            metadatas=all_metas,
            ids=all_ids,
            collection_name="clinical_guidelines",
        )
        elapsed = time.time() - start
        print(f"[完成] 导入耗时 {elapsed:.1f}s")
        print(f"[完成] 已导入 {len(all_docs)} 个文本块到 ChromaDB")
    except Exception as e:
        print(f"[ERROR] 导入失败: {e}")
        raise

    # 验证
    print("\n[验证] 测试检索...")
    test_queries = [
        "高血压降压目标",
        "糖尿病用药方案",
        "急性心梗 PCI",
        "COPD 急性加重",
        "脑梗死溶栓",
    ]

    for query in test_queries:
        results = vectorstore.search(
            query=query,
            collection_name="clinical_guidelines",
            n_results=2,
        )
        if results:
            top = results[0]
            print(f"  Q: {query}")
            print(f"  -> {top['metadata'].get('title', '?')} (score: {top['score']:.3f})")
        else:
            print(f"  Q: {query} -> 无结果")

    print("\n" + "=" * 50)
    print("知识库导入完成!")
    print("=" * 50)


if __name__ == "__main__":
    main()
