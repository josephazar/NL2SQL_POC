# Quick Start Guide - NL2SQL Churn POC

## 🚀 5-Minute Setup

### 1. Start the Application

```bash
cd /home/ubuntu/nl2sql_churn_poc/webapp
source ../venv/bin/activate
python app.py
```

The server will start on `http://0.0.0.0:8000`

### 2. Access the Web Interface

Open your browser to:
- **Local:** http://localhost:8000
- **Public URL:** https://8000-iiobg734ojo79m1l1mgnq-225270a7.manusvm.computer

### 3. Try Example Questions

Click on any of the example buttons or type your own questions:

#### Simple Questions
- "How many customers do we have?"
- "What is our total revenue?"

#### Churn Analysis
- "What is our churn rate?"
- "Show me customers who churned recently"

#### Customer Insights
- "Who are our top 10 most engaged customers?"
- "Show me the top customers by revenue"

#### Geographic Analysis
- "How many customers do we have in each country?"

### 4. Understanding the Results

Each query returns:
1. **Generated SQL** - The SQL query created from your question
2. **Reasoning** - Explanation of the query logic
3. **Data Results** - Formatted table with query results
4. **Metadata** - Relevant tables and example queries used

## 📊 What's in the Database?

- **5,000 customers** across 6 countries
- **6,000 subscriptions** (4,492 active, 1,508 churned)
- **50,000 customer events** (logins, feature usage, etc.)
- **4 subscription plans** (Basic, Standard, Premium, Enterprise)

## 🔧 Testing the CLI

Want to test without the web interface?

```bash
cd /home/ubuntu/nl2sql_churn_poc/src
source ../venv/bin/activate
python nl2sql_agent.py
```

This will run automated tests with predefined questions.

## 📝 Customization

### Add Your Own Example Queries

1. Create a new JSON file in `metadata/queries/`:

```json
{
  "datasource": "churn_db",
  "question": "Your question here?",
  "query": "SELECT ... FROM ...",
  "reasoning": "Explanation of the query"
}
```

2. Re-run metadata ingestion:

```bash
cd src
python metadata_ingestion.py
```

### Modify Database Schema

1. Edit table metadata in `metadata/tables/*.json`
2. Re-run metadata ingestion
3. Restart the web application

## 🐛 Troubleshooting

### Server won't start
- Check if port 8000 is already in use: `netstat -tuln | grep 8000`
- Kill existing process: `pkill -f "python app.py"`

### ChromaDB errors
- Delete and recreate: `rm -rf data/chromadb`
- Re-run: `python src/metadata_ingestion.py`

### SQL generation errors
- Check Azure OpenAI credentials in `src/config.py`
- Verify API key is valid and has quota

## 📚 Next Steps

1. **Explore the code** - Check out `src/nl2sql_agent.py` for the main logic
2. **Add more data** - Modify `generate_churn_data.py` to create more records
3. **Customize the UI** - Edit `webapp/templates/index.html` and `webapp/static/style.css`
4. **Add new features** - Extend the FastAPI endpoints in `webapp/app.py`

## 💡 Pro Tips

1. **Use specific questions** - The more specific your question, the better the SQL
2. **Check the reasoning** - Understand why the AI generated that particular query
3. **Review the metadata** - See which tables and examples influenced the result
4. **Iterate on questions** - Refine your question if the first result isn't perfect

## 🎯 Example Workflow

1. **Start with simple questions** to understand the system
2. **Review the generated SQL** to learn SQL patterns
3. **Try complex questions** combining multiple tables
4. **Use the schema browser** to understand available data
5. **Add your own examples** to improve accuracy for specific use cases

---

**Ready to explore? Start asking questions!** 🚀
