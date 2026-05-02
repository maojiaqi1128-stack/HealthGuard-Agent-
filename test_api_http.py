"""通过 HTTP API 测试指南检索"""
import json
import urllib.request
import urllib.error

data = json.dumps({
    "patient_id": "P001",
    "clinical_note": "患者男性，65岁，主诉胸闷气短3天。既往高血压10年，糖尿病5年。体格检查：BP 150/95 mmHg，心率82次/分，节律整齐。既往用药：二甲双胍 500mg bid，氨氯地平 5mg qd。"
}).encode("utf-8")

req = urllib.request.Request(
    "http://localhost:8001/api/v1/analyze",
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST",
)

print("正在发送分析请求...")
try:
    with urllib.request.urlopen(req, timeout=300) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        
    print("HTTP 状态: 200 OK")
    print()
    
    results = result.get("results", {})
    gr = results.get("guideline_results") or []
    print(f"指南检索结果数量: {len(gr)}")
    
    for i, g in enumerate(gr, 1):
        print(f"\n  [{i}] {g.get('guideline_title', '?')}")
        print(f"       相关度: {g.get('relevance_score', 0):.0%}")
        recs = g.get('key_recommendations', [])
        for r in recs[:2]:
            print(f"       - {r}")
    
    if not gr:
        print("  [空] guideline_results 仍为空！")
        print("  compliance 警告:", results.get("compliance_report", {}).get("warnings", []))
        print("  processing_time:", result.get("metadata", {}).get("agent_timings", {}))

except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8")
    print(f"HTTP 错误 {e.code}: {body[:500]}")
except Exception as e:
    print(f"请求失败: {e}")
