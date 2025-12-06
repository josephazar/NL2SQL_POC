# Contributing to NL2SQL POC

## Adding Your Own Database

This guide explains how to adapt the NL2SQL system to work with your own database.

### Step 1: Prepare Your Database

The system works with SQLite by default, but can be adapted to any SQL database.

1. **Create or connect your database**
   ```python
   # For SQLite
   DATABASE_PATH=data/your_database.db
   
   # For other databases, modify src/database_connector.py
   ```

2. **Ensure your database has proper schema**
   - Tables with clear names
   - Columns with descriptive names
   - Foreign key relationships defined

### Step 2: Create Table Metadata

For each table in your database, create a JSON file in `metadata/tables/`:

**Example: `metadata/tables/customers.json`**
```json
{
  "table": "customers",
  "datasource": "your_database",
  "description": "Customer information including demographics and contact details. Use this table for customer-related queries, segmentation, and demographic analysis.",
  "columns": [
    {
      "name": "id",
      "type": "INTEGER",
      "description": "Unique customer identifier (primary key)"
    },
    {
      "name": "name",
      "type": "TEXT",
      "description": "Customer full name"
    },
    {
      "name": "email",
      "type": "TEXT",
      "description": "Customer email address"
    },
    {
      "name": "country",
      "type": "TEXT",
      "description": "Customer country. Use for geographic analysis and segmentation by region."
    },
    {
      "name": "created_at",
      "type": "TEXT",
      "description": "Customer registration date (ISO 8601 format). Use for cohort analysis and time-based queries."
    }
  ]
}
```

**Important Tips:**
- Use rich, semantic descriptions
- Mention use cases in descriptions (e.g., "Use for geographic analysis")
- Include data format details (e.g., "ISO 8601 format")
- Describe relationships to other tables

### Step 3: Create Example Queries

Create example queries in `metadata/queries/` to guide the AI:

**Example: `metadata/queries/customers_by_country.json`**
```json
{
  "question": "How many customers do we have by country?",
  "datasource": "your_database",
  "query": "SELECT country, COUNT(*) as customer_count FROM customers GROUP BY country ORDER BY customer_count DESC LIMIT 100;",
  "reasoning": "This query groups customers by country and counts them. The results are sorted by count in descending order to show countries with the most customers first."
}
```

**Query Guidelines:**
- Include diverse query types (simple SELECT, JOINs, aggregations, GROUP BY)
- Add queries for common business questions
- Include time-based queries if you have temporal data
- Show examples of multi-table JOINs

### Step 4: Update Datasources Configuration

Edit `metadata/datasources.json`:

```json
{
  "datasources": [
    {
      "name": "your_database",
      "type": "sqlite",
      "connection_string": "data/your_database.db",
      "description": "Your database description"
    }
  ]
}
```

### Step 5: Ingest Metadata into ChromaDB

Run the metadata ingestion script to vectorize your table and query definitions:

```bash
cd src
python metadata_ingestion.py
```

This will:
- Load all table definitions from `metadata/tables/`
- Load all example queries from `metadata/queries/`
- Create embeddings using Azure OpenAI
- Store in ChromaDB for semantic search

### Step 6: Test Your Setup

Start the web application and test with questions:

```bash
cd webapp
python app.py
```

Try questions like:
- "How many [records] do I have?"
- "Show me [metric] by [dimension]"
- "What is the [calculation] for [entity]?"

### Step 7: Iterate and Improve

Monitor the generated SQL queries and:

1. **Add more example queries** if the AI generates incorrect SQL
2. **Enhance table descriptions** if wrong tables are selected
3. **Add column descriptions** if wrong columns are used
4. **Re-run metadata ingestion** after changes

## Metadata Best Practices

### Table Descriptions
- Explain what the table contains
- Mention primary use cases
- Describe relationships to other tables
- Include business context

### Column Descriptions
- Describe the data and its meaning
- Specify format (dates, numbers, enums)
- Mention valid values or ranges
- Explain when to use this column

### Example Queries
- Cover common question patterns
- Show proper JOIN syntax
- Include aggregations and GROUP BY
- Demonstrate date/time handling

## ChromaDB Configuration

The system uses ChromaDB for semantic search. Configuration in `.env`:

```bash
# ChromaDB Configuration
CHROMADB_PATH=data/chromadb
CHROMADB_COLLECTION_TABLES=nl2sql_tables
CHROMADB_COLLECTION_QUERIES=nl2sql_queries
```

### How It Works

1. **Metadata Ingestion**: Table and query definitions are embedded using Azure OpenAI
2. **Semantic Search**: When a question is asked, ChromaDB finds the top-K most relevant tables and queries
3. **Context Building**: Retrieved metadata is used to build the prompt for SQL generation
4. **SQL Generation**: The LLM generates SQL based on relevant context

### Tuning Semantic Search

In `src/nl2sql_agent_mapreduce.py`, adjust the `n_results` parameter:

```python
# Retrieve more tables/queries for complex domains
relevant_tables = self.metadata.search_tables(question, n_results=10)
relevant_queries = self.metadata.search_queries(question, n_results=10)
```

## Database Connector Customization

For non-SQLite databases, modify `src/database_connector.py`:

```python
import psycopg2  # For PostgreSQL
import pymysql   # For MySQL
import pyodbc    # For SQL Server

class DatabaseConnector:
    def __init__(self, connection_string):
        # Customize based on your database
        self.conn = psycopg2.connect(connection_string)
```

## Troubleshooting

### SQL Generation Issues
- **Wrong tables selected**: Improve table descriptions with more semantic context
- **Wrong columns used**: Add detailed column descriptions
- **Incorrect JOINs**: Add example queries showing proper JOIN syntax
- **Wrong aggregations**: Add example queries with GROUP BY patterns

### Performance Issues
- **Slow queries**: Add indexes to your database
- **Slow semantic search**: Reduce `n_results` parameter
- **High API costs**: Cache common queries

## Need Help?

Open an issue on GitHub with:
- Your table/query metadata
- The question you're asking
- The generated SQL (if incorrect)
- Expected SQL (if known)
