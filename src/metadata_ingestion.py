"""
Metadata Ingestion Module
Loads table and query metadata into ChromaDB with embeddings
"""

import json
import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict
import config


class MetadataIngestion:
    """Handles ingestion of table and query metadata into ChromaDB"""
    
    def __init__(self):
        """Initialize ChromaDB client and collections"""
        # Create ChromaDB directory if it doesn't exist
        config.CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client with persistent storage
        self.client = chromadb.PersistentClient(
            path=str(config.CHROMA_DIR),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Create or get collections
        self.tables_collection = self.client.get_or_create_collection(
            name=config.CHROMA_COLLECTION_TABLES,
            metadata={"description": "Table metadata for NL2SQL"}
        )
        
        self.queries_collection = self.client.get_or_create_collection(
            name=config.CHROMA_COLLECTION_QUERIES,
            metadata={"description": "Example queries for NL2SQL"}
        )
    
    def load_table_metadata(self) -> int:
        """Load all table metadata JSON files into ChromaDB"""
        tables_dir = config.METADATA_DIR / "tables"
        count = 0
        
        print(f"Loading table metadata from {tables_dir}...")
        
        for json_file in tables_dir.glob("*.json"):
            with open(json_file, 'r') as f:
                table_data = json.load(f)
            
            # Create document text for embedding
            doc_text = self._create_table_document(table_data)
            
            # Add to ChromaDB
            self.tables_collection.add(
                documents=[doc_text],
                metadatas=[{
                    "table": table_data["table"],
                    "datasource": table_data["datasource"],
                    "description": table_data["description"],
                    "type": "table"
                }],
                ids=[f"table_{table_data['table']}"]
            )
            
            count += 1
            print(f"  ✓ Loaded table: {table_data['table']}")
        
        return count
    
    def load_query_metadata(self) -> int:
        """
        Load all query metadata JSON files into ChromaDB.
        Supports both old and new schema:
        - Old: {datasource, question, query, reasoning}
        - New: {datasource, queries: [{question, query, reasoning}, ...]}
        """
        queries_dir = config.METADATA_DIR / "queries"
        count = 0

        print(f"Loading query metadata from {queries_dir}...")

        for json_file in queries_dir.glob("*.json"):
            with open(json_file, 'r') as f:
                file_data = json.load(f)

            datasource = file_data.get("datasource", "unknown")
            main_table = file_data.get("main_table", "unknown")  # Get main table

            # Determine schema: new (with "queries" array) or old (single query)
            if "queries" in file_data:
                # New schema: multiple queries per file
                queries_list = file_data["queries"]
            else:
                # Old schema: single query per file (backward compatibility)
                queries_list = [{
                    "question": file_data["question"],
                    "query": file_data["query"],
                    "reasoning": file_data.get("reasoning", "")
                }]

            # Add each query to ChromaDB
            for idx, query_data in enumerate(queries_list):
                doc_text = query_data["question"]

                # Create unique ID for each query
                if len(queries_list) == 1:
                    query_id = f"query_{json_file.stem}"
                else:
                    query_id = f"query_{json_file.stem}_{idx}"

                self.queries_collection.add(
                    documents=[doc_text],
                    metadatas=[{
                        "datasource": datasource,
                        "main_table": main_table,  # Store main table
                        "question": query_data["question"],
                        "query": query_data["query"],
                        "reasoning": query_data.get("reasoning", ""),
                        "type": "query"
                    }],
                    ids=[query_id]
                )

                count += 1

            print(f"  ✓ Loaded {len(queries_list)} query(s) from: {json_file.stem}")

        return count
    
    def _create_table_document(self, table_data: Dict) -> str:
        """Create a rich text document from table metadata for embedding"""
        doc_parts = [
            f"Table: {table_data['table']}",
            f"Description: {table_data['description']}",
            "Columns:"
        ]
        
        for col in table_data['columns']:
            col_text = f"  - {col['name']} ({col.get('type', 'unknown')}): {col['description']}"
            if 'examples' in col:
                col_text += f" Examples: {', '.join(map(str, col['examples']))}"
            doc_parts.append(col_text)
        
        return "\n".join(doc_parts)
    
    def search_tables(self, query: str, n_results: int = 3) -> List[Dict]:
        """Search for relevant tables based on natural language query"""
        results = self.tables_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        tables = []
        if results['metadatas'] and len(results['metadatas']) > 0:
            for metadata, document in zip(results['metadatas'][0], results['documents'][0]):
                tables.append({
                    "table": metadata["table"],
                    "description": metadata["description"],
                    "document": document
                })
        
        return tables
    
    def search_queries(self, query: str, n_results: int = 5, datasource: str = None, main_table: str = None) -> List[Dict]:
        """
        Search for similar example queries based on natural language query.

        Args:
            query: Natural language query for semantic search
            n_results: Number of results to return
            datasource: Optional filter by datasource (e.g., "churn_db")
            main_table: Optional filter by main table (e.g., "subscription")

        Returns:
            List of similar query examples
        """
        # Build where filter for ChromaDB
        where_filter = {}
        if datasource:
            where_filter["datasource"] = datasource
        if main_table:
            where_filter["main_table"] = main_table

        # Query with or without filters
        query_params = {
            "query_texts": [query],
            "n_results": n_results
        }
        if where_filter:
            query_params["where"] = where_filter

        results = self.queries_collection.query(**query_params)

        queries = []
        if results['metadatas'] and len(results['metadatas']) > 0:
            for metadata in results['metadatas'][0]:
                queries.append({
                    "question": metadata["question"],
                    "query": metadata["query"],
                    "reasoning": metadata.get("reasoning", ""),
                    "main_table": metadata.get("main_table", "unknown")
                })

        return queries

    def get_queries_by_table(self, table_name: str, n_results: int = 10) -> List[Dict]:
        """
        Get all example queries for a specific table.

        Args:
            table_name: Table name to filter by
            n_results: Maximum number of results

        Returns:
            List of queries for the specified table
        """
        results = self.queries_collection.get(
            where={"main_table": table_name},
            limit=n_results,
            include=['metadatas']
        )

        queries = []
        if results['metadatas']:
            for metadata in results['metadatas']:
                queries.append({
                    "question": metadata["question"],
                    "query": metadata["query"],
                    "reasoning": metadata.get("reasoning", ""),
                    "main_table": metadata.get("main_table", "unknown")
                })

        return queries

    def reset_collections(self):
        """Reset (delete and recreate) all collections"""
        print("Resetting ChromaDB collections...")
        self.client.delete_collection(config.CHROMA_COLLECTION_TABLES)
        self.client.delete_collection(config.CHROMA_COLLECTION_QUERIES)
        
        self.tables_collection = self.client.create_collection(
            name=config.CHROMA_COLLECTION_TABLES,
            metadata={"description": "Table metadata for NL2SQL"}
        )
        
        self.queries_collection = self.client.create_collection(
            name=config.CHROMA_COLLECTION_QUERIES,
            metadata={"description": "Example queries for NL2SQL"}
        )
        print("Collections reset successfully")


def main():
    """Main function to run metadata ingestion"""
    print("=" * 60)
    print("NL2SQL Metadata Ingestion")
    print("=" * 60)
    
    ingestion = MetadataIngestion()
    
    # Reset collections for fresh start
    ingestion.reset_collections()
    
    # Load metadata
    table_count = ingestion.load_table_metadata()
    query_count = ingestion.load_query_metadata()
    
    print("\n" + "=" * 60)
    print(f"Ingestion Complete!")
    print(f"  Tables loaded: {table_count}")
    print(f"  Queries loaded: {query_count}")
    print("=" * 60)
    
    # Test search
    print("\nTesting semantic search...")
    test_query = "Which customers have stopped using our service?"
    
    print(f"\nQuery: '{test_query}'")
    print("\nRelevant tables:")
    tables = ingestion.search_tables(test_query, n_results=2)
    for table in tables:
        print(f"  - {table['table']}: {table['description']}")
    
    print("\nSimilar example queries:")
    queries = ingestion.search_queries(test_query, n_results=3)
    for q in queries:
        print(f"  - {q['question']}")
        print(f"    SQL: {q['query'][:80]}...")


if __name__ == "__main__":
    main()
