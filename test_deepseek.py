import sys
sys.path.insert(0, "src")

from healthguard.config import get_settings
from healthguard.agents.graph import _build_llm

settings = get_settings()
print("Building LLM with provider:", settings.llm_provider)

llm = _build_llm(settings)
print("LLM type:", type(llm).__name__)

# Quick test call
from langchain_core.messages import HumanMessage
try:
    response = llm.invoke([HumanMessage(content="Say 'hello' in one word")])
    print("API test OK:", response.content[:50])
except Exception as e:
    print("API test FAILED:", e)
