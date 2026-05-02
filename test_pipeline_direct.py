"""Test the full pipeline directly (no server needed)."""
import asyncio
import sys
sys.path.insert(0, "src")

from healthguard.agents.graph import ClinicalPipeline

async def main():
    pipeline = ClinicalPipeline()
    print("Pipeline built with LLM:", pipeline.llm.__class__.__name__)
    print("Model:", pipeline.llm.model_name if hasattr(pipeline.llm, 'model_name') else "unknown")
    print("\n--- Running full pipeline ---\n")

    result = await pipeline.analyze(
        patient_id="P001",
        clinical_note=(
            "Patient is a 65-year-old male with chief complaint of chest tightness "
            "and shortness of breath for 3 days. "
            "Past medical history: hypertension for 10 years. "
            "Vitals: BP 150/95 mmHg, HR 82 bpm."
        ),
    )

    import json
    print(json.dumps(result, indent=2, default=str, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
