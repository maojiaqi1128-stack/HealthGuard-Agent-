import urllib.request, time, sys

for attempt in range(6):
    time.sleep(5)
    try:
        r = urllib.request.urlopen("http://localhost:8001/", timeout=5)
        print(f"SUCCESS - HTTP {r.status}")
        sys.exit(0)
    except Exception as e:
        print(f"Attempt {attempt+1}/6: {e}")

print("FAILED - Service did not start in 30 seconds")
sys.exit(1)
