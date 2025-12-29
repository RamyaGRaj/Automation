"""
Reset Desktop and Run Automation
Moves all files back to root and runs 5-run test
"""

import os
import shutil
from pathlib import Path

DESKTOP_PATH = Path.home() / "Desktop"

print("🔄 Resetting Desktop...\n")

# Move files from folders back to root
folders = ["UNIVERSITY_DOCS", "TECHNICAL_WORK", "CAPSTONE_WORK"]
for folder in folders:
    folder_path = DESKTOP_PATH / folder
    if folder_path.exists():
        for file in folder_path.glob("*"):
            if file.is_file():
                dest = DESKTOP_PATH / file.name
                shutil.move(str(file), str(dest))
                print(f"↩️  Moved: {file.name}")

# Remove database
db_path = DESKTOP_PATH / "automation.db"
if db_path.exists():
    db_path.unlink()
    print("🗑️  Removed old database\n")

# Show files on Desktop
print("=" * 70)
print("✅ FILES READY ON DESKTOP ROOT:")
print("=" * 70)

files = sorted([
    f.name for f in DESKTOP_PATH.glob("*")
    if f.is_file() and f.suffix in [".pdf", ".docx", ".xlsx", ".pptx", ".md", ".txt"]
])

for i, file in enumerate(files, 1):
    print(f"{i:2d}. {file}")

print(f"\nTotal: {len(files)} files\n")

print("=" * 70)
print("🚀 Running automation (5 runs)...")
print("=" * 70 + "\n")

# Now run automation
import subprocess
import sys

cmd = [sys.executable, "desktop_automation.py", str(DESKTOP_PATH), "5"]
subprocess.run(cmd)
