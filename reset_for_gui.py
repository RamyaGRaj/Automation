"""
Complete Reset for GUI Automation
- Clean Desktop (files on root, folders empty)
- Delete old database
- Ready for fresh run
"""

import os
import shutil
from pathlib import Path

DESKTOP_PATH = Path.home() / "Desktop"

print("[*] Complete Reset Starting...\n")

# Step 1: Remove old database
db_path = DESKTOP_PATH / "automation.db"
if db_path.exists():
    db_path.unlink()
    print("[OK] Old database removed")

# Step 2: Move all files from folders back to root
folders = ["University Docs", "Technical Work", "Capstone Work"]
for folder_name in folders:
    folder_path = DESKTOP_PATH / folder_name
    if folder_path.exists():
        for file in folder_path.glob("*"):
            if file.is_file():
                dest = DESKTOP_PATH / file.name
                shutil.move(str(file), str(dest))
                print(f"[OK] Moved {file.name} to Desktop root")

print("\n" + "=" * 70)
print("[OK] DESKTOP RESET COMPLETE!")
print("=" * 70)

# Verify state
print("\nFiles on Desktop root:")
files = sorted([
    f.name for f in DESKTOP_PATH.glob("*")
    if f.is_file() and f.suffix in [".pdf", ".docx", ".xlsx", ".pptx", ".md", ".txt"]
])
for i, f in enumerate(files, 1):
    print(f"  {i:2d}. {f}")

print(f"\nTotal: {len(files)} files")
print("\nFolders (empty):")
for folder in folders:
    print(f"  - {folder}")

print("\n[OK] Ready for GUI automation!")
print("     Click START AUTOMATION to classify and move files")
