"""
HealthGuard-Agent · One-click startup script.

Starts the FastAPI server and prints the access URL.
Usage:
    python start.py            # start server (default port 8001)
    python start.py --port 8000  # custom port
"""
from __future__ import annotations

import argparse
import os
import sys
import time
import webbrowser
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Set PYTHONPATH to src/
os.environ.setdefault("PYTHONPATH", str(PROJECT_ROOT / "src"))


def check_dependencies() -> bool:
    """Check that required packages are installed."""
    missing: list[str] = []
    for pkg, extras in [
        ("fastapi", ""),
        ("uvicorn", ""),
        ("langchain", ""),
        ("langgraph", ""),
        ("chromadb", ""),
        ("duckdb", ""),
    ]:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"[ERROR] Missing packages: {', '.join(missing)}")
        print(f"  Install with: pip install {' '.join(missing)}")
        return False
    return True


def check_env_file() -> bool:
    """Check that .env file exists with required settings."""
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        print(f"[WARN] .env file not found at {env_path}")
        print("  Copy .env.template to .env and fill in your API keys.")
        return False
    # Check for DeepSeek API key
    with open(env_path, "r") as f:
        content = f.read()
    if "OPENAI_API_KEY=" in content and "sk-" not in content:
        print("[WARN] DeepSeek API key may be empty in .env")
        print("  Set OPENAI_API_KEY=sk-... in .env")
    return True


def wait_for_server(host: str, port: int, timeout: int = 30) -> bool:
    """Wait until the server is responding."""
    import urllib.request
    import urllib.error

    url = f"http://{host}:{port}/api/v1/health"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(1)
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Start HealthGuard-Agent server")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0)")
    parser.add_argument("--port", default=8001, type=int, help="Bind port (default: 8001)")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser automatically")
    args = parser.parse_args()

    print("=" * 60)
    print("  HealthGuard-Agent · Clinical Decision Support System")
    print("=" * 60)

    # Step 1: Check dependencies
    print("\n[1/4] Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("  ✅ All dependencies satisfied.")

    # Step 2: Check .env
    print("\n[2/4] Checking configuration...")
    check_env_file()
    print("  ✅ Configuration loaded.")

    # Step 3: Start server
    print(f"\n[3/4] Starting server at http://{args.host}:{args.port} ...")
    import subprocess

    cmd = [
        sys.executable, "-m", "uvicorn",
        "healthguard.main:app",
        "--host", args.host,
        "--port", str(args.port),
        "--reload",
    ]
    # Start server in background process
    proc = subprocess.Popen(
        cmd,
        cwd=str(PROJECT_ROOT),
        env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT / "src")},
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    # Wait for server to be ready
    print("  Waiting for server to start...")
    if wait_for_server(args.host if args.host != "0.0.0.0" else "localhost", args.port):
        print(f"  ✅ Server is running at http://localhost:{args.port}")
    else:
        print("  ⚠️  Server may still be starting. Check the log below.")
        time.sleep(3)

    # Step 4: Open browser
    url = f"http://localhost:{args.port}"
    print(f"\n[4/4] Access URL: {url}")
    if not args.no_browser:
        print("  Opening browser...")
        webbrowser.open(url)

    print("\n" + "=" * 60)
    print("  Server is running. Press Ctrl+C to stop.")
    print("=" * 60 + "\n")

    # Stream server output
    try:
        for line in proc.stdout:
            print(line.rstrip())
    except KeyboardInterrupt:
        print("\nShutting down...")
        proc.terminate()
        proc.wait(timeout=5)


if __name__ == "__main__":
    main()
