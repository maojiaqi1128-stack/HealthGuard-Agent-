"""HealthGuard-Agent Web Server"""
import os
import sys

# 切换到项目目录（必须在 import 之前，确保所有相对路径正确）
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_DIR)
sys.path.insert(0, os.path.join(PROJECT_DIR, "src"))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_DIR, ".env"))

# 清除 settings 缓存，确保使用最新的绝对路径
from healthguard.config import get_settings
get_settings.cache_clear()

print("=" * 55)
print("  HealthGuard-Agent Web 界面")
print("=" * 55)
print()
print("  访问地址: http://localhost:8001")
print("  API 文档: http://localhost:8001/docs")
print()
print("  在浏览器中打开上面的地址，输入病历开始分析")
print()
print("  按 Ctrl+C 停止服务器")
print("=" * 55)
print()

# 验证 ChromaDB 数据
try:
    vs = get_settings()
    from pathlib import Path
    chroma_path = str(Path(vs.chroma_persist_dir).resolve())
    print(f"  ChromaDB 路径: {chroma_path}")
    from healthguard.rag.vectorstore import VectorStoreManager
    VectorStoreManager._instance = None  # 重置单例，确保用最新路径
    vm = VectorStoreManager()
    col = vm.get_or_create_collection("clinical_guidelines")
    count = col.count()
    print(f"  知识库文档数: {count} 条")
    if count == 0:
        print("  [警告] 知识库为空！请先运行: python import_knowledge.py")
    else:
        print(f"  知识库状态: 正常")
    print()
except Exception as e:
    print(f"  [警告] 知识库检查失败: {e}")
    print()

import uvicorn

uvicorn.run(
    "healthguard.main:app",
    host="0.0.0.0",
    port=8001,
    reload=False,
    log_level="warning",
)
