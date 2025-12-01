"""Database connection utilities for PostgreSQL"""
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
from typing import Optional, Dict, Any
from contextlib import contextmanager
import os
from dotenv import load_dotenv

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Load environment variables
load_dotenv()


class DatabaseConnection:
    """PostgreSQL database connection manager"""
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Initialize database connection parameters.
        
        Args:
            host: Database host (defaults to localhost or DB_HOST env var)
            port: Database port (defaults to 5432 or DB_PORT env var)
            database: Database name (defaults to 'bank_reviews' or DB_NAME env var)
            user: Database user (defaults to 'postgres' or DB_USER env var)
            password: Database password (defaults to DB_PASSWORD env var)
        """
        self.host = host or os.getenv('DB_HOST', 'localhost')
        self.port = port or int(os.getenv('DB_PORT', 5432))
        self.database = database or os.getenv('DB_NAME', 'bank_reviews')
        self.user = user or os.getenv('DB_USER', 'postgres')
        self.password = password or os.getenv('DB_PASSWORD', '')
        
        self.connection: Optional[psycopg2.extensions.connection] = None
    
    def connect(self) -> psycopg2.extensions.connection:
        """
        Establish database connection.
        
        Returns:
            Database connection object
            
        Raises:
            psycopg2.Error: If connection fails
        """
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            logger.info(f"Connected to database '{self.database}' at {self.host}:{self.port}")
            return self.connection
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Database connection closed")
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        
        Usage:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM banks")
        """
        conn = None
        try:
            conn = self.connect()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if conn:
                self.disconnect()
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> list:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters (for parameterized queries)
            
        Returns:
            List of query results
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """
        Execute an INSERT/UPDATE/DELETE query.
        
        Args:
            query: SQL query string
            params: Query parameters (for parameterized queries)
            
        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.rowcount
    
    def test_connection(self) -> bool:
        """
        Test database connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT version();")
                    version = cursor.fetchone()
                    logger.info(f"PostgreSQL version: {version[0]}")
                    return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

