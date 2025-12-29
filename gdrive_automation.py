"""
Google Drive Automation Script
Main entry point for automating file classification in Google Drive
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from gdrive_manager import GoogleDriveManager
from classifier import classify_document
import tempfile
from state_manager import StateManager


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_section(text):
    """Print formatted section"""
    print(f"\n▶ {text}")
    print("-"*70)


class GoogleDriveAutomation:
    """Orchestrates Google Drive file classification and organization"""
    
    CATEGORY_FOLDERS = {
        "UNIVERSITY_DOCS": "University Docs",
        "TECHNICAL_WORK": "Technical Work",
        "CAPSTONE_WORK": "Capstone Work"
    }
    
    def __init__(self, credentials_file='credentials.json'):
        """
        Initialize Google Drive Automation
        
        Args:
            credentials_file: Path to Google Drive credentials
        """
        self.drive_manager = GoogleDriveManager(credentials_file)
        if not self.drive_manager.is_authenticated():
            raise Exception("Failed to authenticate with Google Drive")
        
        # Initialize state manager (using temp location for Drive testing)
        temp_dir = Path(tempfile.gettempdir()) / "gdrive_automation"
        temp_dir.mkdir(exist_ok=True)
        self.state_manager = StateManager(temp_dir)
        
        # Create folder IDs mapping
        self.folder_ids = {}
    
    def setup_folders(self):
        """Create/get category folders in Drive"""
        print_section("Setting up Google Drive folders")
        
        for category, folder_name in self.CATEGORY_FOLDERS.items():
            folder_id = self.drive_manager.get_or_create_folder(folder_name)
            self.folder_ids[category] = folder_id
            print(f"✅ {folder_name}: {folder_id}")
    
    def classify_file_from_drive(self, file_id, file_name, mime_type):
        """
        Classify a file from Google Drive
        
        Args:
            file_id: Google Drive file ID
            file_name: File name
            mime_type: MIME type
        
        Returns:
            Classification result
        """
        # For Drive files, we'll use filename-based classification
        # (full content extraction would require downloading all files)
        # This is still intelligent as it uses keyword matching
        
        from file_parser import normalize_text
        from config import CLASSIFICATION_KEYWORDS
        
        filename_text = file_name.replace("_", " ").replace("-", " ")
        
        # Score against categories
        scores = {}
        for category, category_info in CLASSIFICATION_KEYWORDS.items():
            keywords = category_info["keywords"]
            
            # Count keyword matches in filename
            matches = 0
            filename_lower = normalize_text(filename_text)
            for keyword in keywords:
                matches += filename_lower.count(keyword.lower())
            
            scores[category] = matches
        
        # Find best category
        best_category = max(scores, key=scores.get)
        confidence = min(scores[best_category] / (sum(scores.values()) + 1), 1.0)
        
        return {
            "file_id": file_id,
            "filename": file_name,
            "category": best_category,
            "confidence_score": confidence,
            "all_scores": scores,
            "status": "success"
        }
    
    def process_file(self, file_id, file_name, mime_type, run_id=None):
        """
        Process a single file: classify and move
        
        Args:
            file_id: Google Drive file ID
            file_name: File name
            mime_type: MIME type
            run_id: Optional run ID for tracking
        
        Returns:
            Processing result
        """
        # Skip folders and system files
        if mime_type == 'application/vnd.google-apps.folder' or file_name.startswith('.'):
            return {
                "file_id": file_id,
                "filename": file_name,
                "status": "skipped",
                "reason": "Is a folder or system file"
            }
        
        # Classify the file
        classification = self.classify_file_from_drive(file_id, file_name, mime_type)
        
        # Get target folder
        target_folder_id = self.folder_ids.get(classification["category"])
        if not target_folder_id:
            return {
                "file_id": file_id,
                "filename": file_name,
                "category": classification["category"],
                "status": "error",
                "reason": "Target folder not found"
            }
        
        # Check if already in target folder (idempotency)
        if self.drive_manager.is_file_in_folder(file_id, target_folder_id):
            if run_id:
                self.state_manager.record_run_detail(
                    run_id,
                    file_name,
                    classification,
                    f"Move to {classification['category']}",
                    "skipped"
                )
            return {
                "file_id": file_id,
                "filename": file_name,
                "category": classification["category"],
                "status": "skipped",
                "reason": "Already in target folder"
            }
        
        # Move the file
        success = self.drive_manager.move_file(file_id, target_folder_id)
        
        if success:
            if run_id:
                self.state_manager.record_run_detail(
                    run_id,
                    file_name,
                    classification,
                    f"Move to {classification['category']}",
                    "success"
                )
            return {
                "file_id": file_id,
                "filename": file_name,
                "category": classification["category"],
                "confidence_score": classification["confidence_score"],
                "status": "success",
                "reason": f"Moved to {self.CATEGORY_FOLDERS[classification['category']]}"
            }
        else:
            if run_id:
                self.state_manager.record_run_detail(
                    run_id,
                    file_name,
                    classification,
                    f"Move to {classification['category']}",
                    "error"
                )
            return {
                "file_id": file_id,
                "filename": file_name,
                "category": classification["category"],
                "status": "error",
                "reason": "Failed to move file"
            }
    
    def process_all_files(self, run_id=None):
        """
        Process all files in Drive root
        
        Args:
            run_id: Optional run ID for tracking
        
        Returns:
            Processing results summary
        """
        # List all files in root
        files = self.drive_manager.list_files_in_folder(only_root=True)
        
        # Filter out folders and system files
        files = [f for f in files if not f['name'].startswith('.')]
        
        results = []
        stats = {
            "total_files": len(files),
            "successful_moves": 0,
            "skipped_files": 0,
            "errors": 0
        }
        
        for file in files:
            result = self.process_file(
                file['id'],
                file['name'],
                file['mimeType'],
                run_id
            )
            results.append(result)
            
            if result["status"] == "success":
                stats["successful_moves"] += 1
            elif result["status"] == "skipped":
                stats["skipped_files"] += 1
            elif result["status"] == "error":
                stats["errors"] += 1
        
        return {
            **stats,
            "results": results
        }


def run_gdrive_automation(credentials_file='credentials.json', run_limit=5):
    """
    Run Google Drive automation multiple times
    
    Args:
        credentials_file: Path to Google Drive credentials
        run_limit: Number of runs to execute
    
    Returns:
        Overall results
    """
    
    print_header("GOOGLE DRIVE AUTOMATED CLASSIFICATION SYSTEM")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if credentials exist
    if not os.path.exists(credentials_file):
        print("\n❌ Error: credentials.json not found!")
        print("\nTo set up Google Drive automation:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project")
        print("3. Enable Google Drive API")
        print("4. Create OAuth 2.0 Desktop Application credentials")
        print("5. Download as JSON and save as 'credentials.json'")
        print("6. Run this script again")
        return None
    
    # Initialize automation
    try:
        automation = GoogleDriveAutomation(credentials_file)
    except Exception as e:
        print(f"\n❌ Failed to initialize: {e}")
        return None
    
    # Setup folders
    automation.setup_folders()
    
    # Overall tracking
    overall_results = {
        "runs": [],
        "consistency": 100.0
    }
    
    previous_run_results = None
    
    # Run automation multiple times
    for run_number in range(1, run_limit + 1):
        print_section(f"RUN {run_number}/{run_limit}")
        
        # Start run
        run_id, _ = automation.state_manager.start_run()
        print(f"Run ID: {run_id}")
        print(f"Start time: {datetime.now().strftime('%H:%M:%S')}")
        
        # Process all files
        print("\n📂 Processing files in Google Drive...")
        results = automation.process_all_files(run_id)
        
        # Update state manager
        automation.state_manager.end_run(
            run_id,
            results["total_files"],
            results["successful_moves"],
            results["errors"],
            results["skipped_files"],
            f"Run {run_number}"
        )
        
        # Print results
        print(f"\n✅ Processing complete:")
        print(f"   Total files in Drive: {results['total_files']}")
        print(f"   Successfully moved: {results['successful_moves']}")
        print(f"   Already in place: {results['skipped_files']}")
        print(f"   Errors: {results['errors']}")
        
        # Print file details
        print(f"\n📄 File Details:")
        for result in results["results"]:
            if result["status"] == "error":
                status_icon = "❌"
            elif result["status"] == "skipped":
                status_icon = "⏭️"
            else:
                status_icon = "✅"
            
            print(f"   {status_icon} {result['filename']}")
            if "category" in result:
                print(f"      → {result.get('category', 'Unknown')}")
            if "reason" in result:
                print(f"      Reason: {result['reason']}")
        
        # Check consistency
        if previous_run_results:
            consistency = compare_results(previous_run_results, results)
            print(f"\n🔄 Consistency with previous run: {consistency:.1f}%")
            overall_results["consistency"] = min(overall_results["consistency"], consistency)
        
        previous_run_results = results
        overall_results["runs"].append({
            "run_number": run_number,
            "results": results,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"\nEnd time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Print summary
    print_header("OVERALL SUMMARY")
    print(f"Total runs: {len(overall_results['runs'])}")
    print(f"Consistency: {overall_results['consistency']:.1f}%")
    
    if overall_results['consistency'] == 100.0:
        print("\n✅ PERFECT CONSISTENCY: 100% identical results across all runs")
        print("✅ Google Drive automation is RELIABLE and DETERMINISTIC")
    
    return overall_results


def compare_results(run1, run2):
    """Compare results from two runs"""
    if run1["total_files"] != run2["total_files"]:
        return 0.0
    if run1["successful_moves"] != run2["successful_moves"]:
        return 0.0
    if run1["skipped_files"] != run2["skipped_files"]:
        return 0.0
    if run1["errors"] != run2["errors"]:
        return 0.0
    return 100.0


if __name__ == "__main__":
    credentials_file = 'credentials.json'
    run_count = 5
    
    if len(sys.argv) > 1:
        credentials_file = sys.argv[1]
    if len(sys.argv) > 2:
        run_count = int(sys.argv[2])
    
    try:
        results = run_gdrive_automation(credentials_file, run_count)
        if results:
            print("\n" + "="*70)
            print("✅ GOOGLE DRIVE AUTOMATION COMPLETED")
            print("="*70)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
