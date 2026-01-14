"""Database manager for reminder storage using SQLite"""
import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Optional, Tuple


class ReminderDB:
    """Manages SQLite database operations for train ticket reminders"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection
        
        Args:
            db_path: Path to SQLite database file. If None, uses default location
        """
        if db_path is None:
            # Use app's data directory on Android, local directory otherwise
            try:
                from android.storage import app_storage_path
                db_dir = app_storage_path()
            except ImportError:
                db_dir = os.path.dirname(os.path.abspath(__file__))
            
            db_path = os.path.join(db_dir, 'train_reminders.db')
        
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Create database tables if they don't exist"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_date TEXT NOT NULL,
                reminder_date TEXT NOT NULL,
                reminder_time TEXT DEFAULT '07:45',
                note TEXT,
                alarm_id INTEGER UNIQUE,
                is_triggered INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def add_reminder(self, event_date: str, note: str, alarm_id: int) -> int:
        """Add a new reminder to the database
        
        Args:
            event_date: Date of train journey (YYYY-MM-DD format)
            note: User's reminder note
            alarm_id: Unique ID for AlarmManager
        
        Returns:
            Database row ID of inserted reminder
        """
        # Calculate reminder date (60 days before event)
        event_dt = datetime.strptime(event_date, '%Y-%m-%d')
        reminder_dt = event_dt - timedelta(days=60)
        reminder_date = reminder_dt.strftime('%Y-%m-%d')
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO reminders (event_date, reminder_date, note, alarm_id)
            VALUES (?, ?, ?, ?)
        ''', (event_date, reminder_date, note, alarm_id))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_all_reminders(self) -> List[Tuple]:
        """Get all reminders from database
        
        Returns:
            List of tuples containing reminder data
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, event_date, reminder_date, note, alarm_id, is_triggered
            FROM reminders
            ORDER BY event_date ASC
        ''')
        return cursor.fetchall()
    
    def get_pending_reminders(self) -> List[Tuple]:
        """Get all non-triggered reminders
        
        Returns:
            List of tuples containing pending reminder data
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, event_date, reminder_date, reminder_time, note, alarm_id
            FROM reminders
            WHERE is_triggered = 0
            ORDER BY reminder_date ASC
        ''')
        return cursor.fetchall()
    
    def get_reminder_by_alarm_id(self, alarm_id: int) -> Optional[Tuple]:
        """Get reminder by alarm ID
        
        Args:
            alarm_id: The alarm ID to search for
        
        Returns:
            Tuple containing reminder data or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, event_date, reminder_date, note, alarm_id, is_triggered
            FROM reminders
            WHERE alarm_id = ?
        ''', (alarm_id,))
        return cursor.fetchone()
    
    def mark_as_triggered(self, alarm_id: int) -> bool:
        """Mark a reminder as triggered
        
        Args:
            alarm_id: The alarm ID to mark as triggered
        
        Returns:
            True if successful, False otherwise
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE reminders
            SET is_triggered = 1
            WHERE alarm_id = ?
        ''', (alarm_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete_reminder(self, reminder_id: int) -> bool:
        """Delete a reminder from database
        
        Args:
            reminder_id: Database ID of the reminder to delete
        
        Returns:
            True if successful, False otherwise
        """
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
