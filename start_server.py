"""Start FastAPI server programmatically."""
import sys
import uvicorn

sys.path.insert(0, "src")

if __name__ == "__main__":
    uvicorn.run(
        "healthguard.main:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
    )
