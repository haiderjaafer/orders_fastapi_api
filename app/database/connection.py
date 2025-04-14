# app/database_connection.py
import pyodbc
import time  # Added this import
from app.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseConnection:
    _instance: Optional['DatabaseConnection'] = None
    _connection: Optional[pyodbc.Connection] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._initialize_connection()
        return cls._instance

    def _initialize_connection(self) -> None:
        """Initialize the database connection with retry logic."""
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                connection_string = (
                    f"DRIVER={{{settings.DATABASE_DRIVER}}};"
                    f"SERVER={settings.DATABASE_SERVER};"
                    f"DATABASE={settings.DATABASE_NAME};"
                    f"UID={settings.DATABASE_USER};"
                    f"PWD={settings.DATABASE_PASSWORD};"
                    "Encrypt=yes;"  # Recommended for security
                    "TrustServerCertificate=yes;"  # Only for development
                )
                
                self._connection = pyodbc.connect(connection_string)
                self._connection.autocommit = True
                
                # Test the connection
                with self._connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                
                logger.info("Database connection established successfully")
                break
            except pyodbc.Error as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(retry_delay)

    def get_connection(self) -> pyodbc.Connection:
        """Get the database connection.
        
        Returns:
            pyodbc.Connection: The active database connection
            
        Raises:
            RuntimeError: If connection is not established
        """
        if self._connection is None:
            raise RuntimeError("Database connection is not established")
        return self._connection

    def close_connection(self) -> None:
        """Close the database connection and reset the singleton instance."""
        if self._connection:
            try:
                self._connection.close()
                logger.info("Database connection closed successfully")
            except pyodbc.Error as e:
                logger.error(f"Error closing connection: {str(e)}")
            finally:
                self._connection = None
                DatabaseConnection._instance = None

    def __del__(self):
        """Ensure connection is closed when instance is garbage collected."""
        self.close_connection()

    @classmethod
    def test_connection(cls) -> bool:
        """Test if the database connection is alive.
        
        Returns:
            bool: True if connection is alive, False otherwise
        """
        try:
            instance = cls()
            with instance.get_connection().cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return True
        except Exception:
            return False