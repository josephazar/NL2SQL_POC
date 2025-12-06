"""
Database Connector Module
Handles SQLite database connections and query execution
"""

import sqlite3
import json
from typing import List, Dict, Any, Tuple
from pathlib import Path
import config


class DatabaseConnector:
    """Manages database connections and query execution"""
    
    def __init__(self, db_path: Path = None):
        """Initialize database connector"""
        self.db_path = db_path or config.DB_PATH
        self._datasource_config = self._load_datasource_config()
    
    def _load_datasource_config(self) -> Dict:
        """Load datasource configuration from JSON"""
        datasource_path = config.METADATA_DIR / "datasources.json"
        with open(datasource_path, 'r') as f:
            return json.load(f)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def execute_query(self, sql: str) -> Tuple[List[Dict[str, Any]], str]:
        """
        Execute a SQL query and return results
        
        Args:
            sql: SQL query string
            
        Returns:
            Tuple of (results as list of dicts, error message if any)
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            
            # Fetch results
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            results = []
            if rows:
                columns = [description[0] for description in cursor.description]
                results = [dict(zip(columns, row)) for row in rows]
            
            conn.close()
            return results, None
            
        except Exception as e:
            return [], str(e)
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """
        Get detailed schema information for a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with table schema information
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Get foreign keys
            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            foreign_keys = cursor.fetchall()
            
            # Get indexes
            cursor.execute(f"PRAGMA index_list({table_name})")
            indexes = cursor.fetchall()
            
            conn.close()
            
            schema = {
                "table": table_name,
                "columns": [
                    {
                        "name": col[1],
                        "type": col[2],
                        "not_null": bool(col[3]),
                        "default_value": col[4],
                        "primary_key": bool(col[5])
                    }
                    for col in columns
                ],
                "foreign_keys": [
                    {
                        "column": fk[3],
                        "references_table": fk[2],
                        "references_column": fk[4]
                    }
                    for fk in foreign_keys
                ],
                "indexes": [idx[1] for idx in indexes]
            }
            
            return schema
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_all_tables(self) -> List[str]:
        """Get list of all tables in the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            return tables
        except Exception as e:
            print(f"Error getting tables: {e}")
            return []
    
    def validate_sql(self, sql: str) -> Tuple[bool, str]:
        """
        Validate SQL syntax without executing
        
        Args:
            sql: SQL query string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            # Use EXPLAIN to validate without executing
            cursor.execute(f"EXPLAIN {sql}")
            conn.close()
            return True, ""
        except Exception as e:
            return False, str(e)
    
    def get_sample_data(self, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get sample rows from a table"""
        sql = f"SELECT * FROM {table_name} LIMIT {limit}"
        results, error = self.execute_query(sql)
        if error:
            return []
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {}
        
        try:
            # Total accounts
            results, _ = self.execute_query("SELECT COUNT(*) as count FROM account")
            stats['total_accounts'] = results[0]['count'] if results else 0
            
            # Active subscriptions
            results, _ = self.execute_query("SELECT COUNT(*) as count FROM subscription WHERE end_date IS NULL")
            stats['active_subscriptions'] = results[0]['count'] if results else 0
            
            # Churned subscriptions
            results, _ = self.execute_query("SELECT COUNT(*) as count FROM subscription WHERE end_date IS NOT NULL")
            stats['churned_subscriptions'] = results[0]['count'] if results else 0
            
            # Total MRR
            results, _ = self.execute_query("SELECT ROUND(SUM(mrr), 2) as total FROM subscription WHERE end_date IS NULL")
            stats['total_mrr'] = results[0]['total'] if results and results[0]['total'] else 0
            
            # Total events
            results, _ = self.execute_query("SELECT COUNT(*) as count FROM event")
            stats['total_events'] = results[0]['count'] if results else 0
            
            # Total metrics
            results, _ = self.execute_query("SELECT COUNT(*) as count FROM metric")
            stats['total_metrics'] = results[0]['count'] if results else 0
            
        except Exception as e:
            print(f"Error getting stats: {e}")
        
        return stats
    
    def get_schema(self) -> Dict[str, Any]:
        """Get schema information for all tables"""
        schema = {}
        tables = self.get_all_tables()
        
        for table in tables:
            table_schema = self.get_table_schema(table)
            sample_data = self.get_sample_data(table, limit=1)
            
            schema[table] = {
                'columns': table_schema.get('columns', []),
                'sample_data': sample_data,
                'sample_count': len(sample_data)
            }
        
        return schema

