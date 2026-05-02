"""Fix all import paths: replace 'from src.healthguard' with 'from healthguard'."""
import os
import re

root = r"E:\HealthGuard-Agent\src\healthguard"
count = 0

for dirpath, _, filenames in os.walk(root):
    for fn in filenames:
        if not fn.endswith(".py"):
            continue
        fp = os.path.join(dirpath, fn)
        with open(fp, "r", encoding="utf-8") as f:
            content = f.read()
        new_content = content.replace("from src.healthguard", "from healthguard")
        if new_content != content:
            with open(fp, "w", encoding="utf-8") as f:
                f.write(new_content)
            count += 1
            print(f"Fixed: {os.path.relpath(fp, root)}")

print(f"\nTotal files fixed: {count}")
