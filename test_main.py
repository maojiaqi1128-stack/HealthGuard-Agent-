import sys
sys.path.insert(0, "src")
from healthguard.main import create_app
app = create_app()
print("main.py OK - routes:", [r.path for r in app.routes])
