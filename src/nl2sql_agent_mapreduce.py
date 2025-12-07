"""
NL2SQL Agent with Map-Reduce Architecture
Includes intelligent visualization assessment and result synthesis
"""

import asyncio
from typing import Dict, List, Any, Optional
from openai import AzureOpenAI
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
import logging
import traceback

from config_env import Config
from database_connector import DatabaseConnector
from metadata_ingestion import MetadataIngestion
from plot_generator import PlotGenerator
from query_planner import QueryPlanner
from visualization_assessor import VisualizationAssessor
from result_synthesizer import ResultSynthesizer

logger = logging.getLogger(__name__)


class NL2SQLAgentMapReduce:
    """
    NL2SQL Agent with Map-Reduce architecture for complex multi-part questions.
    
    Features:
    - Query decomposition (Map phase)
    - Parallel sub-query execution
    - Intelligent visualization assessment
    - Result synthesis (Reduce phase)
    """
    
    def __init__(self, config: Dict[str, str]):
        """Initialize the NL2SQL agent with Azure OpenAI configuration"""
        self.config = config
        
        # Initialize Semantic Kernel
        self.kernel = sk.Kernel()
        self.kernel.add_service(
            AzureChatCompletion(
                service_id="chat",
                deployment_name=config['deployment_name'],
                endpoint=config['endpoint'],
                api_key=config['api_key'],
                api_version=config.get('api_version', '2024-12-01-preview')
            )
        )
        
        # Initialize components
        self.db = DatabaseConnector(Config.DATABASE_PATH)
        self.metadata = MetadataIngestion()
        self.plot_generator = PlotGenerator()
        self.planner = QueryPlanner(config)
        self.viz_assessor = VisualizationAssessor(config)
        self.synthesizer = ResultSynthesizer(config)
    
    async def process_question(self, question: str) -> Dict[str, Any]:
        """
        Process a natural language question using Map-Reduce approach.
        
        Args:
            question: Natural language question
            
        Returns:
            Dictionary containing query results, visualizations, and insights
        """
        try:
            # Step 1: Analyze question complexity (Map phase planning)
            analysis = await self.planner.analyze_question(question)
            
            if analysis['is_complex']:
                # Complex query: Execute Map-Reduce
                return await self._execute_map_reduce(question, analysis)
            else:
                # Simple query: Execute directly
                return await self._execute_simple_query(question)
        
        except Exception as e:
            logger.error(f"ERROR in process_question: {e}\n{traceback.format_exc()}")
            return {
                'type': 'error',
                'error': str(e),
                'question': question
            }
    
    async def _execute_map_reduce(self, question: str, analysis: Dict) -> Dict[str, Any]:
        """
        Execute Map-Reduce for complex multi-part questions.
        Each sub-query is treated as a full simple query with:
        - RAG retrieval for similar tables and queries
        - Retry pattern for self-correction
        """

        # MAP PHASE: Execute each sub-query as a standalone simple query with full RAG + retry
        sub_queries = analysis['sub_queries']  # List of question strings
        tasks = [self._execute_single_query(sq) for sq in sub_queries]  # sq is already a string
        sub_results = await asyncio.gather(*tasks)

        # REDUCE PHASE: Synthesize results
        synthesis = await self.synthesizer.synthesize_results(
            question=question,
            sub_results=sub_results
        )
        
        return {
            'type': 'complex',
            'question': question,
            'execution_plan': analysis['reasoning'],
            'sub_queries_count': len(sub_queries),
            'sub_queries': sub_results,
            'unified_answer': synthesis['unified_answer'],
            'key_insights': synthesis['key_insights']
        }
    
    async def _execute_simple_query(self, question: str) -> Dict[str, Any]:
        """Execute a simple single-part query with synthesis"""
        result = await self._execute_single_query(question)

        # Generate synthesis for simple queries too
        synthesis = await self.synthesizer.synthesize_simple_result(
            question=question,
            sql=result['sql'],
            results=result['results'],
            columns=result['columns']
        )

        return {
            'type': 'simple',
            'question': question,
            'sql': result['sql'],
            'reasoning': result['reasoning'],
            'results': result['results'],
            'columns': result['columns'],
            'plot': result.get('plot'),
            'visualization_assessment': result.get('visualization_assessment'),
            'summary': synthesis.get('summary'),  # Natural language summary
            'key_insights': synthesis.get('key_insights', [])  # Bullet points
        }
    
    async def _execute_single_query(self, question: str, max_retries: int = 2) -> Dict[str, Any]:
        """
        Execute a single SQL query from natural language with self-correction retry.

        Args:
            question: Natural language question
            max_retries: Maximum number of retry attempts (default: 2)

        Returns:
            Dictionary with results or error information
        """

        # Retrieve relevant context from metadata using configured top-k values
        relevant_tables = self.metadata.search_tables(question, n_results=Config.RAG_TOP_K_TABLES)
        relevant_queries = self.metadata.search_queries(question, n_results=Config.RAG_TOP_K_QUERIES)

        # Track execution history for self-correction
        execution_history = []

        for attempt in range(max_retries + 1):
            # Build prompt for SQL generation (with error feedback on retries)
            if attempt == 0:
                # First attempt: normal prompt
                prompt = self._build_sql_prompt(question, relevant_tables, relevant_queries)
            else:
                # Retry attempt: include error feedback for self-correction
                prompt = self._build_sql_correction_prompt(
                    question,
                    relevant_tables,
                    relevant_queries,
                    execution_history
                )

            # Generate SQL using Semantic Kernel
            sql, reasoning = await self._generate_sql(prompt)

            # Execute SQL
            results, error = self.db.execute_query(sql)

            # Record this attempt
            execution_history.append({
                'attempt': attempt + 1,
                'sql': sql,
                'error': error
            })

            if not error:
                # Success! Extract columns from results
                columns = list(results[0].keys()) if results else []

                # Assess whether to visualize
                viz_assessment = self.viz_assessor.should_visualize(
                    question=question,
                    sql=sql,
                    results=results,
                    columns=columns
                )

                # Generate plot if recommended
                plot = None
                if viz_assessment['should_visualize']:
                    plot = self.plot_generator.generate_plot(sql, results)

                return {
                    'question': question,
                    'sql': sql,
                    'reasoning': reasoning,
                    'results': results,
                    'columns': columns,
                    'plot': plot,
                    'visualization_assessment': viz_assessment,
                    'attempts': attempt + 1  # Track how many attempts it took
                }

            # If error and not last attempt, continue to retry
            if attempt < max_retries:
                print(f"⚠️ Attempt {attempt + 1} failed: {error}. Retrying with self-correction...")

        # All retries exhausted - return error
        return {
            'question': question,
            'sql': sql,
            'reasoning': reasoning,
            'error': f"Failed after {max_retries + 1} attempts. Last error: {error}",
            'results': [],
            'columns': [],
            'execution_history': execution_history
        }
    
    def _build_sql_prompt(self, question: str, tables: List[Dict], queries: List[Dict]) -> str:
        """Build prompt for SQL generation"""
        
        prompt = f"""You are an expert SQL query generator. Generate a SQL query to answer the user's question.

USER QUESTION: {question}

AVAILABLE TABLES:
"""
        
        for table in tables:
            prompt += f"\n{table['document']}\n"
        
        if queries:
            prompt += "\n\nEXAMPLE QUERIES:\n"
            for query in queries:
                prompt += f"\nQuestion: {query.get('question', 'N/A')}\n"
                prompt += f"SQL: {query.get('query', 'N/A')}\n"
                prompt += f"Reasoning: {query.get('reasoning', 'N/A')}\n"
        
        prompt += """

INSTRUCTIONS:
1. Generate a valid SQLite query
2. Use proper JOINs based on table relationships
3. Follow the patterns from example queries when applicable
4. Keep the query simple and efficient
5. Return ONLY the SQL query, no explanations

SQL Query:"""
        
        return prompt

    def _build_sql_correction_prompt(self, question: str, tables: List[Dict], queries: List[Dict], execution_history: List[Dict]) -> str:
        """
        Build prompt for SQL correction after failed attempts.
        This implements the ReAct pattern - the agent reasons about its errors and corrects them.
        """

        prompt = f"""You are an expert SQL query generator with self-correction capabilities.

USER QUESTION: {question}

AVAILABLE TABLES:
"""

        for table in tables:
            prompt += f"\n{table['document']}\n"

        if queries:
            prompt += "\n\nEXAMPLE QUERIES:\n"
            for query in queries:
                prompt += f"\nQuestion: {query.get('question', 'N/A')}\n"
                prompt += f"SQL: {query.get('query', 'N/A')}\n"
                prompt += f"Reasoning: {query.get('reasoning', 'N/A')}\n"

        # Add execution history for self-correction
        prompt += "\n\n⚠️ PREVIOUS ATTEMPTS AND ERRORS:\n"
        for attempt in execution_history:
            prompt += f"\nAttempt {attempt['attempt']}:\n"
            prompt += f"SQL: {attempt['sql']}\n"
            prompt += f"Error: {attempt['error']}\n"

        prompt += """

🔧 SELF-CORRECTION INSTRUCTIONS:
1. Analyze the errors from previous attempts carefully
2. Common SQL errors to fix:
   - Column name typos or case sensitivity issues
   - Incorrect table names or missing table aliases
   - Wrong JOIN conditions or missing JOINs
   - Invalid aggregation without GROUP BY
   - Syntax errors (missing commas, parentheses, quotes)
   - Using columns not in GROUP BY clause
3. Generate a CORRECTED SQL query that fixes the errors
4. Double-check column names match the table schemas exactly
5. Ensure all JOINs use correct foreign key relationships
6. Return ONLY the corrected SQL query, no explanations

CORRECTED SQL Query:"""

        return prompt

    async def _generate_sql(self, prompt: str) -> tuple[str, str]:
        """Generate SQL using Semantic Kernel"""
        
        chat_function = self.kernel.add_function(
            plugin_name="SQLGenerator",
            function_name="generate",
            prompt=prompt,
            description="Generate SQL query from natural language"
        )
        
        result = await self.kernel.invoke(chat_function)
        sql = str(result).strip()
        
        # Extract SQL if wrapped in code blocks
        if "```sql" in sql:
            sql = sql.split("```sql")[1].split("```")[0].strip()
        elif "```" in sql:
            sql = sql.split("```")[1].split("```")[0].strip()
        
        reasoning = "Generated SQL query based on available tables and example patterns."
        
        return sql, reasoning


# Test code (only runs when script is executed directly)
if __name__ == "__main__":
    async def test():
        agent = NL2SQLAgentMapReduce(Config.get_azure_openai_config())
        
        # Test simple query
        print("\\n=== Test 1: Simple Query ===")
        result = await agent.process_question("How many total customers do I have?")
        print(f"Type: {result['type']}")
        print(f"SQL: {result.get('sql', 'N/A')}")
        print(f"Results: {result.get('results', [])}")
        
        # Test complex query
        print("\\n=== Test 2: Complex Query ===")
        result = await agent.process_question(
            "How many customers do I have in total and what is the churn rate per country?"
        )
        print(f"Type: {result['type']}")
        print(f"Unified Answer: {result.get('unified_answer', 'N/A')}")
        print(f"Sub-queries: {result.get('sub_queries_count', 0)}")
    
    asyncio.run(test())
