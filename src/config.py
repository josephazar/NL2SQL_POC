"""
Configuration Module - Simple path-based configuration
"""

from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
METADATA_DIR = BASE_DIR / "metadata"
DATA_DIR = BASE_DIR / "data"

# Database paths
DB_PATH = DATA_DIR / "churn.db"

# ChromaDB configuration
CHROMA_DIR = DATA_DIR / "chromadb"
CHROMA_COLLECTION_TABLES = "nl2sql_tables"
CHROMA_COLLECTION_QUERIES = "nl2sql_queries"
