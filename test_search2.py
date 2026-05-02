"""分步骤测试：先只测试 ChromaDB 搜索（不调用 LLM）"""
import os, sys, json, asyncio, warnings
warnings.filterwarnings("ignore")
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_DIR)
sys.path.insert(0, os.path.join(PROJECT_DIR, "src"))

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_DIR, ".env"))

from healthguard.config import get_settings
get_settings.cache_clear()

from healthguard.rag.vectorstore import VectorStoreManager
VectorStoreManager._instance = None

settings = get_settings()
from pathlib import Path
chroma_path = str(Path(settings.chroma_persist_dir).resolve())
print(f"ChromaDB 路径: {chroma_path}")

vm = VectorStoreManager()
col = vm.get_or_create_collection("clinical_guidelines")
print(f"文档数: {col.count()}")

# 直接搜索
results = vm.search(
    query="高血压 胸闷气短 糖尿病 降压 心绞痛",
    collection_name="clinical_guidelines",
    n_results=3
)
print(f"\n搜索结果: {len(results)} 条")
for r in results:
    title = r.get("metadata", {}).get("title", "?")
    score = r.get("score", 0)
    print(f"  [{score:.3f}] {title}")

if not results:
    print("\n[ERR] 搜索返回空！排查中...")
    # 直接看 collection 里有什么
    peek = col.peek(5)
    print("  collection.peek(5):")
    for doc, meta in zip(peek.get("documents", []), peek.get("metadatas", [])):
        print(f"    title={meta.get('title','?')} | {doc[:50]}")
