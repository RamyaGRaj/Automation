"""
State Manager Module
Manages database for tracking file processing across multiple runs
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime


class StateManager:
    """Manages state of processed files in SQLite database"""
    
    def __init__(self, desktop_path):
        """
        Initialize state manager
        
        Args:
            desktop_path: Path to Desktop directory
        """
        self.desktop_path = Path(desktop_path)
        self.db_path = self.desktop_path / "automation.db"
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=5.0, check_same_thread=False)
            conn.isolation_level = None  # Autocommit mode
            cursor = conn.cursor()
            
            # Create files table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processed_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL,
                    confidence_score REAL,
                    file_path TEXT,
                    destination_path TEXT,
                    status TEXT,
                    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    moved_timestamp TIMESTAMP
                )
            ''')
            
            # Create runs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_number INTEGER NOT NULL,
                    run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_files INTEGER,
                    successful_moves INTEGER,
                    failed_moves INTEGER,
                    skipped_files INTEGER,
                    notes TEXT
                )
            ''')
            
            # Create run_details table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS run_details (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    classification_result TEXT,
                    action_taken TEXT,
                    action_status TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(run_id) REFERENCES runs(id)
                )
            ''')
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()
            
            print(f"[OK] Database initialized - {len(tables)} tables ready")
        except Exception as e:
            print(f"Error initializing database: {e}")
    
    def get_run_number(self):
        """Get the next run number"""
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=5.0)
            cursor = conn.cursor()
            cursor.execute('SELECT MAX(run_number) FROM runs')
            result = cursor.fetchone()[0]
            conn.close()
            return (result or 0) + 1
        except Exception as e:
            print(f"Error getting run number: {e}")
            return 1
    
    def start_run(self):
        """Start a new run and return run_id"""
        try:
            run_number = self.get_run_number()
            conn = sqlite3.connect(str(self.db_path), timeout=5.0)
            conn.isolation_level = None
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO runs (run_number) VALUES (?)',
                (run_number,)
            )
            run_id = cursor.lastrowid
            conn.close()
            return run_id, run_number
        except Exception as e:
            print(f"Error starting run: {e}")
            return None, None
    
    def end_run(self, run_id, total_files, successful_moves, failed_moves, skipped_files, notes=""):
        """Complete a run with summary statistics"""
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=5.0)
            conn.isolation_level = None
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE runs 
                SET total_files = ?, successful_moves = ?, failed_moves = ?, skipped_files = ?, notes = ?
                WHERE id = ?
            ''', (total_files, successful_moves, failed_moves, skipped_files, notes, run_id))
            conn.close()
        except Exception as e:
            print(f"Error ending run: {e}")
    
    def is_file_processed(self, filename):
        """Check if a file has already been processed"""
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=5.0)
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM processed_files WHERE filename = ?', (filename,))
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception as e:
            print(f"Error checking file processed: {e}")
            return False
    
    def record_file_movement(self, filename, category, confidence_score, 
                            source_path, destination_path, status="moved"):
        """Record a file movement in the database"""
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=5.0)
            conn.isolation_level = None
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO processed_files 
                (filename, category, confidence_score, file_path, destination_path, status, moved_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (filename, category, confidence_score, str(source_path), 
                  str(destination_path), status, datetime.now().isoformat()))
            conn.close()
        except Exception as e:
            print(f"Error recording file movement: {e}")
    
    def record_run_detail(self, run_id, filename, classification_result, action_taken, action_status):
        """Record details of an action taken during a run"""
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=5.0)
            conn.isolation_level = None
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO run_details 
                (run_id, filename, classification_result, action_taken, action_status)
                VALUES (?, ?, ?, ?, ?)
            ''', (run_id, filename, json.dumps(classification_result), action_taken, action_status))
            conn.close()
        except Exception as e:
            print(f"Error recording run detail: {e}")
    
    def get_all_processed_files(self):
        """Get all processed files from database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM processed_files')
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_run_summary(self, run_number):
        """Get summary for a specific run"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM runs WHERE run_number = ?', (run_number,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def get_all_runs_summary(self):
        """Get summary for all runs"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM runs ORDER BY run_number')
        results = cursor.fetchall()
        conn.close()
        return results
    
    def clear_database(self):
        """Clear all data from database (use with caution!)"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('DELETE FROM run_details')
        cursor.execute('DELETE FROM runs')
        cursor.execute('DELETE FROM processed_files')
        conn.commit()
        conn.close()
        print("⚠️  Database cleared")


if __name__ == "__main__":
    # Test state manager
    desktop = Path.home() / "Desktop"
    manager = StateManager(desktop)
    
    print("✅ State Manager initialized")
    print(f"Database path: {manager.db_path}")
    
    # Test start run
    run_id, run_number = manager.start_run()
    print(f"Started run {run_number} (ID: {run_id})")
    
    # Test record file
    manager.record_file_movement(
        "test_file.pdf",
        "UNIVERSITY_DOCS",
        0.95,
        desktop / "test_file.pdf",
        desktop / "University Docs" / "test_file.pdf"
    )
    print("Recorded file movement")
    
    # Test end run
    manager.end_run(run_id, 1, 1, 0, 0, "Test run")
    print("Ended run")
    
    # Test retrieve summary
    summary = manager.get_run_summary(run_number)
    print(f"Run summary: {summary}")
