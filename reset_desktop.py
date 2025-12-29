"""
Reset Desktop to Initial State
- Move all files from folders back to Desktop root
- Keep 3 empty folders
- Ready for GUI automation to classify and move them
"""

import os
import shutil
from pathlib import Path

DESKTOP_PATH = Path.home() / "Desktop"

print("🔄 Resetting Desktop to initial state...\n")

# Step 1: Move all files from folders back to root
folders_to_empty = ["UNIVERSITY_DOCS", "TECHNICAL_WORK", "CAPSTONE_WORK", 
                     "University Docs", "Technical Work", "Capstone Work"]

for folder_name in folders_to_empty:
    folder_path = DESKTOP_PATH / folder_name
    if folder_path.exists() and folder_path.is_dir():
        for file in folder_path.glob("*"):
            if file.is_file():
                dest = DESKTOP_PATH / file.name
                try:
                    shutil.move(str(file), str(dest))
                    print(f"↩️  Moved back to root: {file.name}")
                except Exception as e:
                    print(f"⚠️  Could not move {file.name}: {e}")

# Step 2: Ensure we have the correct 3 folders (empty)
correct_folders = ["University Docs", "Technical Work", "Capstone Work"]
for folder_name in correct_folders:
    folder_path = DESKTOP_PATH / folder_name
    if not folder_path.exists():
        folder_path.mkdir()
        print(f"✅ Created folder: {folder_name}")

# Step 3: Remove any duplicate folder names
for old_name in ["UNIVERSITY_DOCS", "TECHNICAL_WORK", "CAPSTONE_WORK"]:
    old_path = DESKTOP_PATH / old_name
    if old_path.exists():
        try:
            shutil.rmtree(old_path)
            print(f"🗑️  Removed duplicate folder: {old_name}")
        except:
            pass

# Step 4: Remove database
db_path = DESKTOP_PATH / "automation.db"
if db_path.exists():
    db_path.unlink()
    print("🗑️  Removed old database")

print("\n" + "=" * 70)
print("✅ DESKTOP RESET COMPLETE!")
print("=" * 70)

# Show current state
print("\n📄 FILES ON DESKTOP ROOT (Ready for classification):\n")
files = sorted([
    f.name for f in DESKTOP_PATH.glob("*")
    if f.is_file() and f.suffix in [".pdf", ".docx", ".xlsx", ".pptx", ".md", ".txt"]
])

for i, file in enumerate(files, 1):
    print(f"{i:2d}. {file}")

print(f"\nTotal: {len(files)} files")

print("\n📂 EMPTY FOLDERS (Ready for automation to move files):\n")
for i, folder_name in enumerate(correct_folders, 1):
    folder_path = DESKTOP_PATH / folder_name
    if folder_path.exists():
        file_count = len([f for f in folder_path.glob("*") if f.is_file()])
        print(f"{i}. {folder_name} ({file_count} files)")

print("\n" + "=" * 70)
print("✅ Ready for GUI automation!")
print("   Launch GUI and it will classify and move these 10 files.")
print("=" * 70)
