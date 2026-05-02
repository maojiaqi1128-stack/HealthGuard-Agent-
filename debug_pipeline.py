"""Debug script: run pipeline via LangGraph (proper state merging)."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from healthguard.agents.graph import ClinicalPipeline


async def main():
    pipeline = ClinicalPipeline()

    result = await pipeline.analyze(
        patient_id="P001",
        clinical_note=(
            "患者男性，72岁，因间歇性胸痛2周入院。"
            "疼痛位于胸骨后，劳累时加重，休息后缓解。"
            "既往高血压病史10年。BP 150/95 mmHg，心率82次/分。"
            "心电图示V1-V4导联ST段压低0.1mV。"
            "cTnI 0.8 ng/mL。初步诊断：冠心病，不稳定型心绞痛。"
        ),
        request_id="debug-001",
    )

    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
