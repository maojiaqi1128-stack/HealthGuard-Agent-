import sys
sys.path.insert(0, "src")

from healthguard.config import get_settings

s = get_settings()
print("provider:", s.llm_provider)
print("model:", s.llm_model)
print("api_base:", s.openai_api_base)
print("api_key_set:", bool(s.openai_api_key))
print("All config loaded OK!")
