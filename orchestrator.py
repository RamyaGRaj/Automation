"""
File Orchestrator Module
Handles file movements with safety checks and state management
"""

import shutil
from pathlib import Path
from classifier import classify_document
from state_manager import StateManager


class FileOrchestrator:
    """Orchestrates file movements with safety and state tracking"""
    
    def __init__(self, desktop_path, state_manager=None):
        """
        Initialize orchestrator
        
        Args:
            desktop_path: Path to Desktop directory
            state_manager: Optional StateManager instance
        """
        self.desktop_path = Path(desktop_path)
        self.state_manager = state_manager or StateManager(desktop_path)
    
    def get_target_folder(self, category):
        """
        Get the target folder path for a category
        
        Args:
            category: Classification category (e.g., "UNIVERSITY_DOCS")
        
        Returns:
            Path to target folder
        """
        category_mapping = {
            "UNIVERSITY_DOCS": "University Docs",
            "TECHNICAL_WORK": "Technical Work",
            "CAPSTONE_WORK": "Capstone Work"
        }
        
        folder_name = category_mapping.get(category)
        if not folder_name:
            return None
        
        return self.desktop_path / folder_name
    
    def ensure_folder_exists(self, folder_path):
        """Create folder if it doesn't exist"""
        folder_path = Path(folder_path)
        if not folder_path.exists():
            folder_path.mkdir(parents=True, exist_ok=True)
            return True
        return False
    
    def is_file_in_target(self, file_path, target_folder):
        """Check if file is already in its target folder"""
        file_path = Path(file_path)
        target_folder = Path(target_folder)
        return file_path.parent == target_folder
    
    def move_file(self, file_path, target_folder):
        """
        Safely move a file to target folder
        
        Args:
            file_path: Source file path
            target_folder: Destination folder path
        
        Returns:
            {
                "status": "success" | "skipped" | "error",
                "source": str,
                "destination": str,
                "message": str
            }
        """
        file_path = Path(file_path)
        target_folder = Path(target_folder)
        
        # Check if file exists
        if not file_path.exists():
            return {
                "status": "error",
                "source": str(file_path),
                "destination": str(target_folder),
                "message": f"File not found: {file_path.name}"
            }
        
        # Ensure target folder exists
        self.ensure_folder_exists(target_folder)
        
        # Check if file is already in target folder (idempotency)
        if self.is_file_in_target(file_path, target_folder):
            return {
                "status": "skipped",
                "source": str(file_path),
                "destination": str(target_folder),
                "message": f"File already in target folder: {target_folder.name}"
            }
        
        # Check if file with same name already exists in target
        target_file = target_folder / file_path.name
        if target_file.exists():
            return {
                "status": "error",
                "source": str(file_path),
                "destination": str(target_file),
                "message": f"File already exists in target: {target_file.name}"
            }
        
        # Perform the move
        try:
            shutil.move(str(file_path), str(target_file))
            return {
                "status": "success",
                "source": str(file_path),
                "destination": str(target_file),
                "message": f"Successfully moved to {target_folder.name}"
            }
        except Exception as e:
            return {
                "status": "error",
                "source": str(file_path),
                "destination": str(target_file),
                "message": f"Error moving file: {str(e)}"
            }
    
    def process_file(self, file_path, run_id=None):
        """
        Process a single file: classify and move
        
        Args:
            file_path: Path to file to process
            run_id: Optional run ID for tracking
        
        Returns:
            {
                "filename": str,
                "category": str,
                "classification_status": str,
                "movement_status": str,
                "movement_result": dict,
                "overall_status": str
            }
        """
        file_path = Path(file_path)
        
        # Classify the file
        classification = classify_document(file_path)
        
        # If classification failed, return error
        if classification["status"] == "error":
            return {
                "filename": classification["filename"],
                "category": None,
                "classification_status": "error",
                "movement_status": "skipped",
                "movement_result": None,
                "overall_status": "error",
                "reason": classification["reasoning"]
            }
        
        # Get target folder
        target_folder = self.get_target_folder(classification["category"])
        if not target_folder:
            return {
                "filename": classification["filename"],
                "category": classification["category"],
                "classification_status": "success",
                "movement_status": "error",
                "movement_result": None,
                "overall_status": "error",
                "reason": "Invalid category"
            }
        
        # Move the file
        movement_result = self.move_file(file_path, target_folder)
        
        # Record in state manager if available
        if self.state_manager and movement_result["status"] in ["success", "skipped"]:
            self.state_manager.record_file_movement(
                classification["filename"],
                classification["category"],
                classification["confidence_score"],
                file_path,
                movement_result["destination"],
                movement_result["status"]
            )
        
        # Record run detail if run_id provided
        if run_id and self.state_manager:
            self.state_manager.record_run_detail(
                run_id,
                classification["filename"],
                classification,
                f"Move to {classification['category']}",
                movement_result["status"]
            )
        
        # Determine overall status
        overall_status = "success" if movement_result["status"] in ["success", "skipped"] else "error"
        
        return {
            "filename": classification["filename"],
            "category": classification["category"],
            "confidence_score": classification["confidence_score"],
            "classification_status": classification["status"],
            "movement_status": movement_result["status"],
            "movement_result": movement_result,
            "overall_status": overall_status
        }
    
    def process_all_files(self, run_id=None):
        """
        Process all unprocessed files on Desktop
        
        Args:
            run_id: Optional run ID for tracking
        
        Returns:
            {
                "total_files": int,
                "processed": int,
                "successful_moves": int,
                "skipped_files": int,
                "failed": int,
                "results": list
            }
        """
        # Find all files on Desktop (not in folders)
        files = [f for f in self.desktop_path.iterdir() 
                if f.is_file() and not f.name.startswith(".")]
        
        results = []
        stats = {
            "total_files": len(files),
            "processed": 0,
            "successful_moves": 0,
            "skipped_files": 0,
            "failed": 0
        }
        
        for file_path in files:
            result = self.process_file(file_path, run_id)
            results.append(result)
            
            if result["overall_status"] == "success":
                stats["processed"] += 1
                if result["movement_status"] == "success":
                    stats["successful_moves"] += 1
                elif result["movement_status"] == "skipped":
                    stats["skipped_files"] += 1
            else:
                stats["failed"] += 1
        
        return {
            **stats,
            "results": results
        }


if __name__ == "__main__":
    # Test orchestrator
    desktop = Path.home() / "Desktop"
    orchestrator = FileOrchestrator(desktop)
    
    print("✅ File Orchestrator initialized")
    print(f"Desktop path: {desktop}")
    
    # Test classify and move a single file (if it exists)
    test_file = desktop / "Semester_Transcript_2024.pdf"
    if test_file.exists():
        print(f"\nTesting with: {test_file.name}")
        result = orchestrator.process_file(test_file)
        print(f"Category: {result['category']}")
        print(f"Movement status: {result['movement_status']}")
        print(f"Overall status: {result['overall_status']}")
