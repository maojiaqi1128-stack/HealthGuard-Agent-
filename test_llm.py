"""Test if ChatOllama works with the current config."""
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
import asyncio

async def test():
    llm = ChatOllama(
        base_url="http://localhost:11434",
        model="mistral:7b",
        temperature=0.1,
        num_predict=512,
    )
    print("Testing LLM call...")
    try:
        response = await llm.ainvoke([
            SystemMessage(content="You are a helpful assistant. Reply in JSON."),
            HumanMessage(content="Extract age and gender from: 'Patient is 72-year-old male.' Return JSON only."),
        ])
        print("LLM Response:", response.content)
        print("SUCCESS")
    except Exception as e:
        print("ERROR:", e)

asyncio.run(test())
