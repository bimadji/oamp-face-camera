#!/usr/bin/env python3
"""
SQL file executor - can be run as standalone script or imported as module
- Executes SQL files in order (oldest first)
- Deletes file if execution is successful
- Retries failed files on next run
- Logs all activities
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import from main.py
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

# Import will be done in functions to avoid circular import when used as module

# Setup logging
LOG_DIR = Path(__file__).parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f'sql_execution_{datetime.now().strftime("%Y%m")}.log'

def log(message):
    """Write log message to file and console"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + '\n')

def execute_sql_file(sql_file_path, get_db_connection_func):
    """
    Execute a SQL file
    Returns True if successful, False otherwise
    
    Args:
        sql_file_path: Path to SQL file
        get_db_connection_func: Function to get database connection
    """
    try:
        import psycopg2
        
        # Read SQL file
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Get database connection
        conn = get_db_connection_func()
        if not conn:
            log(f"ERROR: Cannot connect to database for file {sql_file_path.name}")
            return False
        
        # Execute SQL
        with conn.cursor() as cursor:
            cursor.execute(sql_content)
            conn.commit()
        
        conn.close()
        log(f"SUCCESS: Executed {sql_file_path.name}")
        return True
        
    except Exception as e:
        # Catch all exceptions including psycopg2 errors
        log(f"ERROR executing {sql_file_path.name}: {e}")
        return False

def process_sql_files(get_db_connection_func=None, sql_dir=None):
    """
    Process all SQL files in the cron/sql directory
    
    Args:
        get_db_connection_func: Function to get database connection (optional, will import from main if None)
        sql_dir: Directory containing SQL files (optional, defaults to cron/sql)
    """
    # Import get_db_connection if not provided
    if get_db_connection_func is None:
        try:
            from main import get_db_connection
            get_db_connection_func = get_db_connection
        except ImportError as e:
            log(f"ERROR: Cannot import get_db_connection: {e}")
            return
    
    # Set SQL directory
    if sql_dir is None:
        sql_dir = SCRIPT_DIR / 'sql'
    
    # Create directory if it doesn't exist
    sql_dir.mkdir(exist_ok=True)
    
    # Get all SQL files, sorted by name (which includes timestamp)
    sql_files = sorted(sql_dir.glob('*.sql'))
    
    if not sql_files:
        log("No SQL files to process")
        return
    
    log(f"Found {len(sql_files)} SQL file(s) to process")
    
    success_count = 0
    failed_count = 0
    
    for sql_file in sql_files:
        log(f"Processing: {sql_file.name}")
        
        if execute_sql_file(sql_file, get_db_connection_func):
            # Delete file if successful
            try:
                sql_file.unlink()
                log(f"DELETED: {sql_file.name}")
                success_count += 1
            except Exception as e:
                log(f"WARNING: Could not delete {sql_file.name}: {e}")
        else:
            log(f"FAILED: {sql_file.name} will be retried on next run")
            failed_count += 1
    
    log(f"Summary: {success_count} succeeded, {failed_count} failed")

def main():
    """Main entry point"""
    log("=" * 60)
    log("Starting SQL file execution cronjob")
    
    try:
        process_sql_files()
    except Exception as e:
        log(f"CRITICAL ERROR: {e}")
        import traceback
        log(traceback.format_exc())
    
    log("Cronjob completed")
    log("=" * 60)

if __name__ == '__main__':
    main()
