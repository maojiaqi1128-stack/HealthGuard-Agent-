"""快速测试 API 返回的数据结构"""
import asyncio
import json
import os
import sys
import traceback

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from dotenv import load_dotenv
load_dotenv()

import warnings
warnings.filterwarnings("ignore")

async def main():
    try:
        from healthguard.agents.graph import ClinicalPipeline

        pipeline = ClinicalPipeline()
        result = await pipeline.analyze(
            patient_id="P001",
            clinical_note="患者男性，65岁，主诉胸闷气短3天。既往高血压10年，糖尿病5年。BP 150/95 mmHg。",
        )

        with open("E:\\HealthGuard-Agent\\api_debug.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)

        print("SUCCESS - 结果已写入 api_debug.json")
        print("guideline_results:", len(result.get("results", {}).get("guideline_results") or []))
        print("results keys:", list(result.get("results", {}).keys()))

    except Exception as e:
        with open("E:\\HealthGuard-Agent\\api_error.txt", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        print("ERROR:", str(e))
        print("详情已写入 api_error.txt")

asyncio.run(main())
