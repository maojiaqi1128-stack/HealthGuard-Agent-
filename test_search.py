"""测试 ChromaDB 搜索功能"""
import sys
sys.path.insert(0, r'E:\HealthGuard-Agent\src')

from healthguard.rag.vectorstore import VectorStoreManager

# 初始化 vectorstore
v = VectorStoreManager()

# 测试搜索
test_queries = [
    "高血压 降压目标",
    "糖尿病 用药",
    "胸闷气短",
]

print("=" * 50)
print("测试 ChromaDB 搜索功能")
print("=" * 50)

for query in test_queries:
    print(f"\n查询: {query}")
    results = v.search(query=query, collection_name='clinical_guidelines', n_results=3)
    if results:
        print(f"  找到 {len(results)} 个结果:")
        for i, r in enumerate(results, 1):
            title = r['metadata'].get('title', '未知')
            score = r['score']
            print(f"  {i}. {title} (相关度: {score:.3f})")
    else:
        print("  无结果")

print("\n" + "=" * 50)
print("测试完成")
print("=" * 50)
