# NL2SQL Churn Analytics POC

A production-ready Natural Language to SQL system with Map-Reduce architecture, intelligent visualization assessment, and result synthesis.

## 🎯 Features

- **Generic NL2SQL Engine**: Works with any database through metadata-driven approach
- **Map-Reduce Architecture**: Decomposes complex multi-part questions into parallel sub-queries
- **Intelligent Visualization**: AI-powered assessment of when charts add value
- **Result Synthesis**: Combines multi-query results with unified answers and actionable insights
- **Semantic Search**: ChromaDB-powered retrieval of relevant tables and example queries
- **Dynamic Plotly Charts**: Bar, line, pie, and scatter visualizations
- **FastAPI Web Interface**: Professional UI with real-time query processing

## 🏗️ Architecture

### Components

1. **Query Planner**: Analyzes question complexity and decomposes into sub-queries
2. **Metadata Ingestion**: Vectorizes table and query metadata in ChromaDB
3. **NL2SQL Agent**: Orchestrates SQL generation using Semantic Kernel
4. **Visualization Assessor**: Determines if visualization adds value
5. **Result Synthesizer**: Combines multi-query results with insights
6. **Plot Generator**: Creates appropriate Plotly visualizations

### Tech Stack

- **AI Framework**: Semantic Kernel with Azure OpenAI (gpt-4o-mini)
- **Vector Database**: ChromaDB for semantic search
- **Database**: SQLite (easily adaptable to other databases)
- **Web Framework**: FastAPI with Jinja2 templates
- **Visualization**: Plotly for interactive charts
- **Language**: Python 3.11+

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- Azure OpenAI API access
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/josephazar/NL2SQL_POC.git
   cd NL2SQL_POC
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your Azure OpenAI credentials
   ```

5. **Generate sample data** (optional - uses churn simulation)
   ```bash
   python generate_churn_data_v2.py
   ```

6. **Ingest metadata**
   ```bash
   cd src
   python metadata_ingestion.py
   ```

## 🚀 Usage

### Start the Web Application

```bash
cd webapp
python app.py
```

The application will be available at `http://localhost:8000`

### Example Queries

**Simple Queries** (single SQL query):
- "How many total customers do I have?"
- "What is the churn rate?"
- "Show me events by type"

**Complex Queries** (Map-Reduce with multiple SQL queries):
- "How many customers do I have in total and what is the churn rate per country?"
- "What is the total MRR and show me events by type?"

### API Usage

```python
from nl2sql_agent_mapreduce import NL2SQLAgentMapReduce
from config_env import Config

# Initialize agent
agent = NL2SQLAgentMapReduce(Config.get_azure_openai_config())

# Process question
result = await agent.process_question("How many customers do I have?")

print(result['sql'])
print(result['results'])
```

## 📁 Project Structure

```
NL2SQL_POC/
├── src/                          # Core modules
│   ├── config_env.py            # Environment-based configuration
│   ├── database_connector.py    # Database operations
│   ├── metadata_ingestion.py    # ChromaDB vectorization
│   ├── nl2sql_agent_mapreduce.py # Main NL2SQL agent
│   ├── query_planner.py         # Question decomposition
│   ├── visualization_assessor.py # Intelligent viz decisions
│   ├── result_synthesizer.py    # Multi-query synthesis
│   └── plot_generator.py        # Plotly chart generation
├── webapp/                       # Web application
│   ├── app.py                   # FastAPI application
│   ├── templates/               # Jinja2 HTML templates
│   └── static/                  # CSS and JavaScript
├── metadata/                     # Table and query definitions
│   ├── tables/                  # JSON table metadata
│   ├── queries/                 # JSON example queries
│   └── datasources.json         # Data source configuration
├── data/                         # Database and ChromaDB storage
│   ├── churn.db                 # SQLite database
│   └── chromadb/                # Vector embeddings
├── .env.example                  # Environment variables template
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002

# Database Configuration
DATABASE_PATH=data/churn.db

# ChromaDB Configuration
CHROMADB_PATH=data/chromadb
CHROMADB_COLLECTION_TABLES=nl2sql_tables
CHROMADB_COLLECTION_QUERIES=nl2sql_queries

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO
```

## 📊 Sample Database

The POC includes a churn analytics database with 9 tables:

- **account**: Customer accounts (5,000 records)
- **subscription**: Subscription history (6,000 records)
- **event**: Customer events (50,000 records)
- **event_type**: Event type lookup (12 types)
- **observation**: ML training data (5,000 observations)
- **metric**: Calculated metrics (10,000 metrics)
- **metric_name**: Metric definitions (10 types)
- **active_period**: Activity periods (64,912 records)
- **active_week**: Weekly activity (40,586 records)

## 🎨 Key Features Explained

### 1. Intelligent Visualization Assessment

The system uses AI to decide when visualizations add value:

- **Scalar values** (e.g., "total customers = 5,000"): No chart
- **Categorical data** (e.g., "churn rate by country"): Bar/pie chart
- **Time-series** (e.g., "subscriptions over time"): Line chart
- **Multi-dimensional**: Scatter plot or grouped bar chart

### 2. Map-Reduce for Complex Questions

**Example**: "How many customers do I have in total and what is the churn rate per country?"

**MAP PHASE**:
- Decomposes into 2 sub-questions
- Executes sub-queries in parallel
- Each assessed independently for visualization

**REDUCE PHASE**:
- Generates unified answer
- Extracts key insights
- Provides actionable recommendations

### 3. Semantic Search

Uses ChromaDB to find:
- **Top-K relevant tables** based on question semantics
- **Top-K similar queries** as few-shot examples
- Guides LLM to generate accurate SQL

## 🧪 Testing

Run the test suite:

```bash
cd src
python nl2sql_agent_mapreduce.py
```

## 📝 Adding Your Own Database

1. **Create table metadata** in `metadata/tables/`:
   ```json
   {
     "table": "your_table",
     "description": "Description of the table",
     "columns": [
       {
         "name": "column_name",
         "type": "TEXT",
         "description": "Column description"
       }
     ]
   }
   ```

2. **Add example queries** in `metadata/queries/`:
   ```json
   {
     "question": "Example question?",
     "query": "SELECT * FROM your_table",
     "reasoning": "Explanation of the query"
   }
   ```

3. **Update datasources.json**:
   ```json
   {
     "datasources": [
       {
         "name": "your_database",
         "type": "sqlite",
         "connection_string": "data/your_database.db"
       }
     ]
   }
   ```

4. **Re-ingest metadata**:
   ```bash
   cd src
   python metadata_ingestion.py
   ```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by [GPT-RAG](https://github.com/Azure/GPT-RAG) NL2SQL architecture
- Uses [genaiops-orchestrator](https://github.com/placerda/genaiops-orchestrator-1604) metadata patterns
- Churn data simulation based on [fight-churn-extended](https://github.com/andreaschandra/fight-churn-extended)

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using Semantic Kernel, ChromaDB, and FastAPI**
