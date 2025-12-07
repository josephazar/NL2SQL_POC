# NL2SQL with Semantic Kernel

A production-ready Natural Language to SQL system powered by Microsoft Semantic Kernel, featuring Map-Reduce architecture, intelligent visualization, and result synthesis.

## 🎯 Features

- **Semantic Kernel Integration**: LLM orchestration with Azure OpenAI
- **RAG with ChromaDB**: Semantic search for relevant tables and query examples
- **Map-Reduce Architecture**: Handles complex multi-part questions with parallel execution
- **Self-Correction**: Retry pattern with error feedback for robust SQL generation
- **Intelligent Visualization**: Data-driven chart generation (no hardcoded keywords)
- **Result Synthesis**: Natural language summaries with AI-generated insights
- **Configurable RAG**: Tune retrieval and synthesis parameters via `.env`
- **Table Filtering**: Query examples organized by main table

## 🏗️ Architecture

### Components

1. **Query Planner**: LLM-powered analysis of question complexity
2. **Metadata Ingestion**: ChromaDB vectorization of tables and queries
3. **NL2SQL Agent**: Semantic Kernel orchestration with RAG
4. **Visualization Assessor**: LLM-based visualization recommendations
5. **Result Synthesizer**: Multi-query result combination with insights
6. **Plot Generator**: Data-driven Plotly chart creation

### Tech Stack

- **AI Framework**: Semantic Kernel with Azure OpenAI (gpt-4o-mini)
- **Vector Database**: ChromaDB for semantic search with embeddings
- **Database**: SQLite (easily adaptable to PostgreSQL, MySQL, etc.)
- **Web Framework**: FastAPI with Bootstrap 5 UI
- **Visualization**: Plotly for interactive charts
- **Language**: Python 3.11+

### Data Flow

```
User Question
    ↓
Query Planner (LLM) → Simple or Complex?
    ↓
┌─────────────────────┬──────────────────────┐
│    Simple Path      │    Complex Path      │
│                     │    (Map-Reduce)      │
│  1. RAG Search      │  1. Decompose Query  │
│     - Top-K Tables  │  2. Parallel Exec    │
│     - Top-K Queries │     (Each with RAG)  │
│  2. SQL Generation  │  3. Reduce/Synthesize│
│  3. Self-Correction │  4. Visualize        │
│  4. Execute Query   │                      │
│  5. Visualize       │                      │
│  6. Synthesize      │                      │
└─────────────────────┴──────────────────────┘
         ↓
    Results + Insights + Visualizations
```

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- Azure OpenAI API access
- Git

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/josephazar/NL2SQL_POC.git
cd NL2SQL_POC

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

# 5. Generate sample data
python src/generate_churn_data.py

# 6. Ingest metadata
python src/metadata_ingestion.py

# 7. Start web application
cd webapp
uvicorn app:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000

## ⚙️ Configuration

Edit `.env` to customize behavior:

```bash
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002

# RAG Configuration
RAG_TOP_K_TABLES=5          # Number of similar tables to retrieve
RAG_TOP_K_QUERIES=5         # Number of example queries to retrieve

# Result Synthesis
SYNTHESIS_MAX_ROWS=50       # Max rows to send to LLM for synthesis
```

## 🚀 Usage

### Example Queries

**Simple Queries:**
- "How many customers do we have?"
- "What is our total MRR?"
- "Show me churn rate by country"

**Complex Queries (Map-Reduce):**
- "Show me subscriptions over time and churn rate by product"
- "What is our total MRR and which customers have the highest event activity?"

**Time-Series:**
- "Show me subscriptions over time"
- "Show me churns by month"

### API Usage

```python
from nl2sql_agent_mapreduce import NL2SQLAgentMapReduce
from config_env import Config

# Initialize agent
agent = NL2SQLAgentMapReduce(Config.get_azure_openai_config())

# Process question
result = await agent.process_question("What is our churn rate?")

print(f"Type: {result['type']}")  # 'simple' or 'complex'
print(f"SQL: {result['sql']}")
print(f"Summary: {result['summary']}")
print(f"Insights: {result['key_insights']}")
```

### Filter Queries by Table

```python
from metadata_ingestion import MetadataIngestion

meta = MetadataIngestion()

# Get all queries for a specific table
queries = meta.get_queries_by_table('subscription')

# Search with table filter
queries = meta.search_queries(
    'churn rate',
    main_table='subscription',
    n_results=5
)
```

## 📁 Project Structure

```
NL2SQL_POC/
├── src/                          # Core modules
│   ├── config_env.py            # Environment configuration
│   ├── database_connector.py    # Database operations
│   ├── metadata_ingestion.py    # ChromaDB RAG setup
│   ├── nl2sql_agent_mapreduce.py # Main agent with SK
│   ├── query_planner.py         # Question decomposition
│   ├── visualization_assessor.py # Viz recommendations
│   ├── result_synthesizer.py    # Result synthesis
│   └── plot_generator.py        # Data-driven charts
├── webapp/                       # Web application
│   ├── app.py                   # FastAPI app
│   ├── templates/               # Bootstrap 5 UI
│   └── static/                  # CSS/JS
├── metadata/                     # Metadata definitions
│   ├── tables/                  # Table schemas (JSON)
│   └── queries/                 # Example queries (JSON)
│       ├── accounts.json        # Account queries
│       ├── churn.json           # Churn queries
│       ├── subscriptions.json   # Subscription queries
│       ├── revenue.json         # Revenue queries
│       └── events_and_metrics.json
├── data/                         # Generated data
│   ├── churn.db                 # SQLite database
│   └── chromadb/                # Vector embeddings
├── .env                          # Configuration
├── requirements.txt              # Dependencies
└── README.md
```

## 🎨 Key Features Explained

### 1. RAG (Retrieval-Augmented Generation)

**Before SQL generation**, the system retrieves:
- **Top-K relevant tables** based on semantic similarity
- **Top-K example queries** as few-shot learning

This context is injected into the LLM prompt for accurate SQL generation.

**Configuration:**
```bash
RAG_TOP_K_TABLES=5      # More tables = better context
RAG_TOP_K_QUERIES=5     # More examples = better patterns
```

### 2. Map-Reduce for Complex Questions

**Example:** "Show me subscriptions over time and churn rate by country"

**MAP Phase:**
- Decomposes into 2 sub-questions
- Each executes with **full RAG retrieval**
- Each has **retry pattern** for self-correction
- Executes in **parallel** for speed

**REDUCE Phase:**
- Synthesizes results into unified answer
- Generates insights across all sub-queries
- Creates visualizations where appropriate

### 3. Data-Driven Visualization

**No hardcoded keywords!** Chart type detection based on:

- **Temporal detection**: Tries `pd.to_datetime()` on actual values
- **Range detection**: Checks if numeric values are percentages (0-100)
- **Cardinality**: Number of unique values vs row count

Works on **any database schema**.

### 4. Result Synthesis

Every query (simple or complex) gets:
- **Summary**: Natural language answer
- **Key Insights**: 3-5 AI-generated observations
- **Visualization**: Auto-generated charts when valuable

**Configuration:**
```bash
SYNTHESIS_MAX_ROWS=50   # Balance between detail and token cost
```

## 📊 Sample Database

Churn analytics database with 9 tables:

- **account**: 5,000 customer accounts
- **subscription**: 6,000+ subscriptions (Basic, Standard, Premium, Enterprise)
- **event**: 50,000+ customer events
- **metric**: 300,000+ usage metrics
- **observation**: 5,000 ML training observations

## 📝 Adding Your Own Database

### 1. Create Table Metadata

`metadata/tables/your_table.json`:
```json
{
  "table": "your_table",
  "datasource": "your_db",
  "description": "Table description",
  "columns": [
    {
      "name": "column_name",
      "type": "TEXT",
      "description": "Column description",
      "examples": ["value1", "value2"]
    }
  ]
}
```

### 2. Add Example Queries

`metadata/queries/your_topic.json`:
```json
{
  "datasource": "your_db",
  "main_table": "your_table",
  "queries": [
    {
      "question": "Your question?",
      "query": "SELECT ... FROM your_table",
      "reasoning": "Explanation"
    }
  ]
}
```

### 3. Re-ingest Metadata

```bash
python src/metadata_ingestion.py
```

## 🧪 Testing

```bash
# Test metadata ingestion
python src/metadata_ingestion.py

# Test agent
cd src
python nl2sql_agent_mapreduce.py

# Test web app
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What is our churn rate?"}'
```

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)**: 5-minute setup guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Detailed architecture
- **[DATA_FLOW_AND_TOKENS.md](DATA_FLOW_AND_TOKENS.md)**: Token usage analysis

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- Built with **Microsoft Semantic Kernel**
- Vector search powered by **ChromaDB**
- Inspired by RAG-based SQL generation patterns

---

**Built with Semantic Kernel, ChromaDB, and FastAPI** 🚀
