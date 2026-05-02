"""重新导入知识库到正确的 ChromaDB 路径"""
import os
import sys
import warnings
warnings.filterwarnings("ignore")

os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_DIR)
sys.path.insert(0, os.path.join(PROJECT_DIR, "src"))

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_DIR, ".env"))

# 清除缓存
from healthguard.config import get_settings
get_settings.cache_clear()

# 重置单例
from healthguard.rag.vectorstore import VectorStoreManager
VectorStoreManager._instance = None

settings = get_settings()
from pathlib import Path
chroma_path = str(Path(settings.chroma_persist_dir).resolve())
print(f"ChromaDB 路径: {chroma_path}")

# 检查当前数量
vm = VectorStoreManager()
col = vm.get_or_create_collection("clinical_guidelines")
current_count = col.count()
print(f"当前文档数: {current_count}")

if current_count > 0:
    print("知识库已有数据，跳过导入")
else:
    print("知识库为空，开始导入...")
    
    # 调用原始导入逻辑
    import json
    import hashlib
    from pathlib import Path
    
    KB_DIR = Path(PROJECT_DIR) / "knowledge_base"
    md_files = list(KB_DIR.glob("*.md"))
    print(f"找到 {len(md_files)} 个指南文件")
    
    def chunk_text(text, chunk_size=800, overlap=100):
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            if end == len(text):
                break
            start += chunk_size - overlap
        return chunks
    
    all_docs, all_metas, all_ids = [], [], []
    
    for md_file in md_files:
        content = md_file.read_text(encoding="utf-8")
        lines = content.split("\n")
        title = lines[0].lstrip("#").strip() if lines else md_file.stem
        
        # 提取元数据
        source = "未知来源"
        for line in lines[:20]:
            if "来源" in line or "source" in line.lower():
                source = line.split("：")[-1].split(":")[-1].strip()
                break
        
        chunks = chunk_text(content)
        for i, chunk in enumerate(chunks):
            chunk_id = hashlib.md5(f"{md_file.stem}_{i}".encode()).hexdigest()
            all_docs.append(chunk)
            all_metas.append({
                "title": title,
                "source": source,
                "file": md_file.name,
                "chunk_index": i,
            })
            all_ids.append(chunk_id)
    
    print(f"准备导入 {len(all_docs)} 个文档块...")
    
    # 分批导入
    BATCH = 20
    for i in range(0, len(all_docs), BATCH):
        batch_docs = all_docs[i:i+BATCH]
        batch_metas = all_metas[i:i+BATCH]
        batch_ids = all_ids[i:i+BATCH]
        vm.add_documents(batch_docs, batch_metas, batch_ids)
        print(f"  已导入 {min(i+BATCH, len(all_docs))}/{len(all_docs)}")
    
    final_count = col.count()
    print(f"\n导入完成！知识库现有 {final_count} 个文档块")
