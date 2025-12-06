"""
Configuration Module - Loads settings from environment variables
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    """Configuration class that loads settings from environment variables"""
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4o-mini')
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT', 'text-embedding-ada-002')
    
    # Database Configuration
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/churn.db')
    
    # ChromaDB Configuration
    CHROMADB_PATH = os.getenv('CHROMADB_PATH', 'data/chromadb')
    CHROMADB_COLLECTION_TABLES = os.getenv('CHROMADB_COLLECTION_TABLES', 'nl2sql_tables')
    CHROMADB_COLLECTION_QUERIES = os.getenv('CHROMADB_COLLECTION_QUERIES', 'nl2sql_queries')
    
    # Application Configuration
    APP_HOST = os.getenv('APP_HOST', '0.0.0.0')
    APP_PORT = int(os.getenv('APP_PORT', '8000'))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls):
        """Validate that required environment variables are set"""
        required_vars = [
            'AZURE_OPENAI_API_KEY',
            'AZURE_OPENAI_ENDPOINT',
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                f"Please copy .env.example to .env and fill in your credentials."
            )
    
    @classmethod
    def get_azure_openai_config(cls):
        """Get Azure OpenAI configuration as a dictionary"""
        return {
            'api_key': cls.AZURE_OPENAI_API_KEY,
            'endpoint': cls.AZURE_OPENAI_ENDPOINT,
            'api_version': cls.AZURE_OPENAI_API_VERSION,
            'deployment_name': cls.AZURE_OPENAI_DEPLOYMENT_NAME,
            'embedding_deployment': cls.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        }
    
    @classmethod
    def get_database_config(cls):
        """Get database configuration as a dictionary"""
        return {
            'database_path': cls.DATABASE_PATH,
        }
    
    @classmethod
    def get_chromadb_config(cls):
        """Get ChromaDB configuration as a dictionary"""
        return {
            'persist_directory': cls.CHROMADB_PATH,
            'collection_tables': cls.CHROMADB_COLLECTION_TABLES,
            'collection_queries': cls.CHROMADB_COLLECTION_QUERIES,
        }

# Validate configuration on import
Config.validate()
