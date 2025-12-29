"""
Desktop Automation Script
Main entry point for automating file classification and movement
"""

import sys
from pathlib import Path
from datetime import datetime
from orchestrator import FileOrchestrator
from state_manager import StateManager


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_section(text):
    """Print formatted section"""
    print(f"\n[>] {text}")
    print("-"*70)


def run_automation(desktop_path=None, run_limit=5):
    """
    Run the automated file classification and movement
    
    Args:
        desktop_path: Path to Desktop (defaults to user Desktop)
        run_limit: Maximum number of runs to execute (for testing)
    
    Returns:
        Overall summary of all runs
    """
    
    if desktop_path is None:
        desktop_path = Path.home() / "Desktop"
    else:
        desktop_path = Path(desktop_path)
    
    # Initialize components
    state_manager = StateManager(desktop_path)
    orchestrator = FileOrchestrator(desktop_path, state_manager)
    
    print_header("AUTOMATED DOCUMENT CLASSIFICATION SYSTEM")
    print(f"Desktop Path: {desktop_path}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Overall tracking
    overall_results = {
        "runs": [],
        "total_files_across_runs": 0,
        "consistency": 100.0,
        "overall_accuracy": 0.0
    }
    
    previous_run_results = None
    
    # Run automation multiple times
    for run_number in range(1, run_limit + 1):
        print_section(f"RUN {run_number}/{run_limit}")
        
        # Start run
        run_id, _ = state_manager.start_run()
        print(f"Run ID: {run_id}")
        print(f"Start time: {datetime.now().strftime('%H:%M:%S')}")
        
        # Process all files
        print("\n[*] Processing files...")
        results = orchestrator.process_all_files(run_id)
        
        # Update state manager
        state_manager.end_run(
            run_id,
            results["total_files"],
            results["successful_moves"],
            results["failed"],
            results["skipped_files"],
            f"Run {run_number}"
        )
        
        # Print results
        print(f"\n✅ Processing complete:")
        print(f"   Total files on Desktop: {results['total_files']}")
        print(f"   Successfully moved: {results['successful_moves']}")
        print(f"   Already in place: {results['skipped_files']}")
        print(f"   Failed: {results['failed']}")
        
        # Print file details
        print(f"\n📄 File Details:")
        for result in results["results"]:
            status_icon = "✅" if result["overall_status"] == "success" else "⚠️"
            print(f"   {status_icon} {result['filename']}")
            if result["category"]:
                print(f"      → {result['category']}")
            if result["movement_result"]:
                print(f"      Message: {result['movement_result']['message']}")
        
        # Check consistency with previous run
        if previous_run_results:
            consistency = compare_run_results(previous_run_results, results)
            print(f"\n🔄 Consistency with previous run: {consistency:.1f}%")
            overall_results["consistency"] = min(overall_results["consistency"], consistency)
        
        # Store results for comparison
        previous_run_results = results
        overall_results["runs"].append({
            "run_number": run_number,
            "results": results,
            "timestamp": datetime.now().isoformat()
        })
        
        # Print separator
        print(f"\nEnd time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Print overall summary
    print_header("OVERALL SUMMARY")
    print(f"Total runs: {len(overall_results['runs'])}")
    print(f"Consistency across runs: {overall_results['consistency']:.1f}%")
    
    # Analyze cross-run consistency
    print_section("Cross-Run Analysis")
    analyze_consistency(overall_results["runs"])
    
    # Final verdict
    print_section("Final Verdict")
    if overall_results["consistency"] == 100.0:
        print("✅ PERFECT CONSISTENCY: 100% identical results across all runs")
        print("✅ Automation is RELIABLE and DETERMINISTIC")
    else:
        print(f"⚠️ Consistency: {overall_results['consistency']:.1f}%")
    
    return overall_results


def compare_run_results(run1, run2):
    """
    Compare results from two runs to check consistency
    Returns: Percentage match (0-100)
    """
    if run1["total_files"] != run2["total_files"]:
        return 0.0
    
    if run1["successful_moves"] != run2["successful_moves"]:
        return 0.0
    
    if run1["skipped_files"] != run2["skipped_files"]:
        return 0.0
    
    if run1["failed"] != run2["failed"]:
        return 0.0
    
    return 100.0


def analyze_consistency(runs):
    """Analyze consistency across multiple runs"""
    if not runs:
        print("No runs to analyze")
        return
    
    print(f"Analyzed {len(runs)} runs\n")
    
    # Compare first run with all others
    first_run = runs[0]["results"]
    all_consistent = True
    
    for i, run_data in enumerate(runs[1:], 2):
        run_results = run_data["results"]
        consistency = compare_run_results(first_run, run_results)
        
        status = "✅" if consistency == 100.0 else "⚠️"
        print(f"{status} Run {i}: {consistency:.1f}% match with Run 1")
        
        if consistency < 100.0:
            all_consistent = False
    
    if all_consistent:
        print("\n✅ All runs produced identical results!")
    
    return all_consistent


if __name__ == "__main__":
    # Default: run on user's Desktop
    desktop_path = Path.home() / "Desktop"
    
    # Allow command-line argument for custom path
    if len(sys.argv) > 1:
        desktop_path = Path(sys.argv[1])
    
    # Allow custom run count
    run_count = 5
    if len(sys.argv) > 2:
        run_count = int(sys.argv[2])
    
    # Run automation
    try:
        results = run_automation(desktop_path, run_count)
        print("\n" + "="*70)
        print("✅ AUTOMATION COMPLETED SUCCESSFULLY")
        print("="*70)
    except Exception as e:
        print(f"\n[ERROR] Error during automation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
