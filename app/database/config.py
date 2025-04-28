from pydantic_settings import BaseSettings

from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

from typing import Generator
import urllib.parse
from sqlalchemy import create_engine




# ================= Configuration =================
class Settings(BaseSettings):
    DATABASE_SERVER: str
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_DRIVER: str = "ODBC Driver 17 for SQL Server"
    PDF_BASE_PATH: str = 'D:/order_pdfs'
    MODE: str

    class Config:
        env_file = ".env"

    @property
    def sqlalchemy_database_url(self) -> str:
        params = urllib.parse.quote_plus(
            f"DRIVER={self.DATABASE_DRIVER};"
            f"SERVER={self.DATABASE_SERVER};"
            f"DATABASE={self.DATABASE_NAME};"
            f"UID={self.DATABASE_USER};"
            f"PWD={self.DATABASE_PASSWORD};"
            f"TrustServerCertificate=yes;"
            f"MARS_Connection=Yes;"
            f"CHARSET=UTF8;"
        )
        return f"mssql+pyodbc:///?odbc_connect={params}"

settings = Settings()
