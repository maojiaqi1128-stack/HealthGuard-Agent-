"""
HealthGuard-Agent 简化启动脚本（无 emoji，避免编码问题）
"""
import os
import sys
import time

# 添加 src 到 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# 设置环境变量
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

def main():
    print("=" * 60)
    print("  HealthGuard-Agent - Clinical Decision Support System")
    print("=" * 60)

    # Step 1: Check dependencies
    print("\n[1/3] 检查依赖包...")
    try:
        import fastapi
        import uvicorn
        import langchain
        import chromadb
        print("  [OK] 所有依赖包已安装")
    except ImportError as e:
        print(f"  [ERROR] 缺少依赖: {e}")
        print("  请运行: pip install -r requirements.txt")
        return

    # Step 2: Check .env
    print("\n[2/3] 检查配置文件...")
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_file):
        print("  [WARNING] .env 文件不存在，将使用默认配置")
    else:
        print("  [OK] 配置文件已找到")

    # Step 3: Start server
    print("\n[3/3] 启动服务器...")
    print("  按 Ctrl+C 停止服务器\n")

    import uvicorn
    from healthguard.config import get_settings

    settings = get_settings()
    host = getattr(settings, 'api_host', '0.0.0.0')
    port = getattr(settings, 'api_port', 8001)

    print(f"  服务器地址: http://localhost:{port}")
    print(f"  Web 界面: http://localhost:{port}/")
    print(f"  API 文档: http://localhost:{port}/docs\n")

    # Start uvicorn
    uvicorn.run(
        "healthguard.main:app",
        host=host,
        port=port,
        reload=False,
    )


if __name__ == "__main__":
    main()
