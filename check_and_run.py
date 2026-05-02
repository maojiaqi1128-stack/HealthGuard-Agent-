import urllib.request, time, sys, subprocess, os

# Step 1: Kill old process on port 8001
print("=== HealthGuard-Agent ===")
print("[1] Checking port 8001...")

try:
    result = subprocess.run(
        ["netstat", "-ano"],
        capture_output=True, text=True, timeout=10
    )
    for line in result.stdout.splitlines():
        if ":8001" in line and "LISTENING" in line:
            pid = line.strip().split()[-1]
            print(f"[1] Killing old process PID {pid}...")
            subprocess.run(["taskkill", "/f", "/pid", pid], capture_output=True, timeout=5)
            time.sleep(1)
            break
    else:
        print("[1] Port 8001 is free")
except Exception as e:
    print(f"[1] Port check skipped: {e}")

# Step 2: Start server
print("[2] Starting server...")
env = os.environ.copy()
env["PYTHONPATH"] = "E:\\HealthGuard-Agent\\src"

server_proc = subprocess.Popen(
    ["E:\\HealthGuard-Agent\\.venv\\Scripts\\python.exe", "-m", "uvicorn",
     "healthguard.main:app", "--host", "0.0.0.0", "--port", "8001"],
    cwd="E:\\HealthGuard-Agent",
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

# Step 3: Wait for server to be ready
print("[3] Waiting for server to start...")
for i in range(12):
    time.sleep(3)
    try:
        r = urllib.request.urlopen("http://localhost:8001/", timeout=3)
        if r.status == 200:
            print(f"\n{'='*40}")
            print(f"  Server is running!")
            print(f"  Open browser: http://localhost:8001")
            print(f"{'='*40}")
            # Keep server alive
            print("\n[Server output]")
            try:
                for line in server_proc.stdout:
                    print(line.decode("utf-8", errors="replace"), end="")
            except KeyboardInterrupt:
                pass
            sys.exit(0)
    except Exception:
        pass

print("FAILED: Server did not start in 36 seconds")
print("Last server output:")
try:
    server_proc.kill()
    output = server_proc.stdout.read().decode("utf-8", errors="replace")
    print(output[-2000:] if len(output) > 2000 else output)
except:
    pass
sys.exit(1)
