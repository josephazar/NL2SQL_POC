# Quick Start Guide - NL2SQL with Semantic Kernel

## 🚀 5-Minute Setup

### 1. Configure Environment

Create `.env` file in project root:

```bash
cp .env.example .env
```

Edit `.env` with your Azure OpenAI credentials:
```bash
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
```

### 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Initialize Database and Metadata

```bash
# Generate sample churn database
python src/generate_churn_data.py

# Ingest metadata into ChromaDB
python src/metadata_ingestion.py
```

### 4. Start the Application

```bash
cd webapp
uvicorn app:app --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`

## 📊 Try Example Questions

Open your browser to http://localhost:8000 and try:

### Simple Queries
- "How many customers do we have?"
- "What is our total MRR?"
- "How many active subscriptions do we have?"

### Churn Analysis
- "What is our churn rate?"
- "Show me churn rate by country"
- "What is the churn rate by product?"

### Revenue Analysis
- "Show me total MRR by product"
- "Who are the top 10 customers by MRR?"
- "Show me MRR trends over time"

### Time-Series
- "Show me subscriptions over time"
- "Show me churns by month"

## 🎯 Understanding the Results

Each query returns:

1. **Type**: `simple` (single query) or `complex` (map-reduce)
2. **SQL**: Generated SQL query with syntax highlighting
3. **Results**: Data in formatted table
4. **Visualization**: Auto-generated charts (when appropriate)
5. **Summary**: Natural language answer
6. **Key Insights**: AI-generated insights from the data

## 📁 What's in the Database?

- **5,000 accounts** across 6 countries
- **6,000+ subscriptions** (Basic, Standard, Premium, Enterprise)
- **50,000+ events** (login, feature usage, support tickets)
- **300,000+ metrics** (usage statistics, engagement scores)

## ⚙️ Configuration Options

Edit `.env` to customize:

```bash
# RAG Configuration
RAG_TOP_K_TABLES=5          # Number of similar tables to retrieve
RAG_TOP_K_QUERIES=5         # Number of example queries to retrieve

# Result Synthesis
SYNTHESIS_MAX_ROWS=50       # Max rows to send to LLM for synthesis
```

## 🔧 Advanced Usage

### Add Custom Query Examples

1. Create/edit JSON file in `metadata/queries/`:

```json
{
  "datasource": "churn_db",
  "main_table": "subscription",
  "queries": [
    {
      "question": "Your question here?",
      "query": "SELECT ... FROM ...",
      "reasoning": "Explanation of the query"
    }
  ]
}
```

2. Re-run metadata ingestion:

```bash
python src/metadata_ingestion.py
```

### Filter Queries by Table

```python
from metadata_ingestion import MetadataIngestion

meta = MetadataIngestion()

# Get all queries for subscription table
queries = meta.get_queries_by_table('subscription')

# Search with table filter
queries = meta.search_queries('churn rate', main_table='subscription')
```

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
lsof -ti:8000

# Kill existing process
lsof -ti:8000 | xargs kill -9
```

### ChromaDB errors
```bash
# Reset ChromaDB
rm -rf data/chromadb
python src/metadata_ingestion.py
```

### Azure OpenAI errors
- Verify credentials in `.env`
- Check API key has quota
- Confirm deployment names match your Azure setup

## 🏗️ Architecture Overview

```
User Question
    ↓
Query Planner (LLM) → Simple or Complex?
    ↓
┌─────────────────┬──────────────────┐
│   Simple Path   │   Complex Path    │
│                 │   (Map-Reduce)    │
│  1. RAG Search  │  1. Decompose     │
│  2. SQL Gen     │  2. Parallel Exec │
│  3. Execute     │  3. Synthesize    │
│  4. Visualize   │  4. Visualize     │
│  5. Synthesize  │                   │
└─────────────────┴──────────────────┘
         ↓
    Results + Insights
```

## 💡 Pro Tips

1. **Specific questions work best** - "Show me churn rate by country" > "Tell me about churn"
2. **Use the schema tab** - Understand available tables and columns
3. **Check synthesis** - AI provides insights beyond raw data
4. **Adjust RAG settings** - More examples = better SQL but higher token cost
5. **Add domain examples** - Custom queries improve accuracy for your use case

## 📚 Key Features

✅ **Semantic Kernel** - LLM orchestration framework
✅ **RAG (ChromaDB)** - Retrieves relevant tables & query examples
✅ **Map-Reduce** - Handles complex multi-part questions
✅ **Self-Correction** - Retry pattern with error feedback
✅ **Auto-Visualization** - Data-driven chart generation
✅ **Result Synthesis** - Natural language summaries + insights

---

**Ready to ask questions?** Open http://localhost:8000 and start exploring! 🚀
