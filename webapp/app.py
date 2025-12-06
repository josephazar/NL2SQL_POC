"""
NL2SQL Churn Analytics POC - Main Web Application
FastAPI application with Map-Reduce, Intelligent Visualization & Result Synthesis
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import logging

from config_env import Config
from nl2sql_agent_mapreduce import NL2SQLAgentMapReduce
from database_connector import DatabaseConnector

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="NL2SQL Churn Analytics POC",
    description="Ask questions in natural language - Get SQL queries, results, and visualizations!",
    version="1.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize components
try:
    logger.info("Initializing NL2SQL Agent...")
    agent = NL2SQLAgentMapReduce(Config.get_azure_openai_config())
    db = DatabaseConnector(Config.DATABASE_PATH)
    logger.info("NL2SQL Agent initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize NL2SQL Agent: {e}")
    raise

class QueryRequest(BaseModel):
    question: str

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main page"""
    return templates.TemplateResponse("index_mapreduce.html", {"request": request})

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "nl2sql-mapreduce-poc"}

@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    try:
        stats = db.get_stats()
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/schema")
async def get_schema():
    """Get database schema"""
    try:
        schema = db.get_schema()
        return JSONResponse(content=schema)
    except Exception as e:
        logger.error(f"Error getting schema: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/query")
async def query(request: QueryRequest):
    """Process natural language query"""
    try:
        logger.info(f"Processing query: {request.question}")
        result = await agent.process_question(request.question)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {Config.APP_HOST}:{Config.APP_PORT}")
    uvicorn.run(app, host=Config.APP_HOST, port=Config.APP_PORT)
