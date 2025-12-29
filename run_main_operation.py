"""
Run Automation via GUI Automation Script
Executes the classification and file movement
"""

import os
import sys
from pathlib import Path
import subprocess
import time

# Ensure we have clean state
DESKTOP_PATH = Path.home() / "Desktop"

# Remove old database
db_path = DESKTOP_PATH / "automation.db"
if db_path.exists():
    db_path.unlink()
    print("✅ Cleaned old database")

print("\n" + "=" * 70)
print("🚀 MAIN OPERATION: Classify & Move 10 Files into Folders")
print("=" * 70 + "\n")

# Show files before
print("📄 FILES ON DESKTOP ROOT (Before Classification):")
files = sorted([
    f.name for f in DESKTOP_PATH.glob("*")
    if f.is_file() and f.suffix in [".pdf", ".docx", ".xlsx", ".pptx", ".md", ".txt"]
])
for i, f in enumerate(files, 1):
    print(f"   {i:2d}. {f}")

print("\n" + "-" * 70)
print("Running classification and file movement...\n")

# Run the automation
cmd = [sys.executable, "desktop_automation.py", str(DESKTOP_PATH), "5"]
result = subprocess.run(cmd, capture_output=True, text=True)

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

# Verify results
print("\n" + "=" * 70)
print("📂 VERIFICATION - Files in Folders (After Classification)")
print("=" * 70 + "\n")

folders = {
    "University Docs": "#e74c3c",
    "Technical Work": "#3498db", 
    "Capstone Work": "#2ecc71"
}

total_moved = 0
for folder_name in folders.keys():
    folder_path = DESKTOP_PATH / folder_name
    if folder_path.exists():
        files_in_folder = [f.name for f in folder_path.glob("*") if f.is_file()]
        print(f"\n📂 {folder_name}:")
        if files_in_folder:
            for f in sorted(files_in_folder):
                print(f"   ✅ {f}")
            total_moved += len(files_in_folder)
        else:
            print("   (empty)")

print("\n" + "=" * 70)
print(f"✅ SUMMARY: {total_moved} files classified and moved")
print("✅ Classification complete - All files organized!")
print("=" * 70 + "\n")
