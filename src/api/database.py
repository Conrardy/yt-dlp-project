"""
Database module for storing download history using SQLite.
"""

import aiosqlite
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import HistoryEntry

logger = logging.getLogger(__name__)


class Database:
    """SQLite database manager for download history."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize database.
        
        Args:
            db_path: Optional path to database file. Defaults to history.db in current directory.
        """
        self.db_path = db_path or Path("history.db")
        self._initialized = False
    
    async def initialize(self):
        """Initialize database and create tables if they don't exist."""
        if self._initialized:
            return
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS downloads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    title TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    download_date TIMESTAMP NOT NULL,
                    duration TEXT,
                    uploader TEXT,
                    file_size INTEGER,
                    video_id TEXT
                )
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_download_date 
                ON downloads(download_date DESC)
            """)
            await db.commit()
        
        self._initialized = True
        logger.info(f"Database initialized at {self.db_path}")
    
    async def add_download(self, url: str, title: str, filename: str,
                          duration: Optional[str] = None,
                          uploader: Optional[str] = None,
                          file_size: Optional[int] = None,
                          video_id: Optional[str] = None) -> int:
        """
        Add a download entry to the database.
        
        Args:
            url: YouTube URL
            title: Video title
            filename: Downloaded filename
            duration: Video duration
            uploader: Video uploader
            file_size: File size in bytes
            video_id: YouTube video ID
            
        Returns:
            ID of the inserted record
        """
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO downloads 
                (url, title, filename, download_date, duration, uploader, file_size, video_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (url, title, filename, datetime.now(), duration, uploader, file_size, video_id))
            await db.commit()
            return cursor.lastrowid
    
    async def get_history(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get download history.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of download history entries
        """
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM downloads 
                ORDER BY download_date DESC 
                LIMIT ? OFFSET ?
            """, (limit, offset)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_download_by_id(self, download_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a download entry by ID.
        
        Args:
            download_id: Download ID
            
        Returns:
            Download entry or None if not found
        """
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM downloads WHERE id = ?
            """, (download_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def delete_download(self, download_id: int) -> bool:
        """
        Delete a download entry.
        
        Args:
            download_id: Download ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM downloads WHERE id = ?", (download_id,))
            await db.commit()
            return cursor.rowcount > 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get download statistics.
        
        Returns:
            Dictionary with statistics
        """
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            # Total downloads
            async with db.execute("SELECT COUNT(*) FROM downloads") as cursor:
                total = (await cursor.fetchone())[0]
            
            # Total file size
            async with db.execute("SELECT SUM(file_size) FROM downloads WHERE file_size IS NOT NULL") as cursor:
                total_size = (await cursor.fetchone())[0] or 0
            
            return {
                "total_downloads": total,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2) if total_size else 0
            }


# Global database instance
_db_instance: Optional[Database] = None


def get_database(db_path: Optional[Path] = None) -> Database:
    """
    Get or create database instance.
    
    Args:
        db_path: Optional database path
        
    Returns:
        Database instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_path)
    return _db_instance
