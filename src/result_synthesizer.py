"""
Result Synthesizer - Combines multi-query results with unified answer and insights
"""

from typing import Dict, List
from openai import AzureOpenAI
import json
from config_env import Config


class ResultSynthesizer:
    """
    Synthesizes results from multiple sub-queries into a unified answer
    with key insights and recommendations (Reduce phase of Map-Reduce).
    """
    
    def __init__(self, config: Dict[str, str]):
        """Initialize the result synthesizer with Azure OpenAI configuration"""
        self.client = AzureOpenAI(
            api_version=config.get('api_version', '2024-12-01-preview'),
            azure_endpoint=config['endpoint'],
            api_key=config['api_key']
        )
        self.deployment_name = config['deployment_name']
    
    async def synthesize_results(self, question: str, sub_results: List[Dict]) -> Dict:
        """
        Synthesize results from multiple sub-queries.
        
        Args:
            question: Original user question
            sub_results: List of sub-query results
            
        Returns:
            Dictionary with:
            - unified_answer: str
            - key_insights: List[str]
        """
        
        # Build context from sub-results (max rows configured in .env)
        max_rows = Config.SYNTHESIS_MAX_ROWS
        context = ""
        for i, result in enumerate(sub_results, 1):
            context += f"\\n\\nSub-Query {i}: {result['question']}"
            context += f"\\nSQL: {result['sql']}"
            context += f"\\nResults: {json.dumps(result['results'][:max_rows], indent=2)}"
            if len(result['results']) > max_rows:
                context += f"\\n... ({len(result['results'])} total rows)"
        
        prompt = f"""You are a data analyst synthesizing results from multiple database queries.

ORIGINAL QUESTION: {question}

SUB-QUERY RESULTS:{context}

Based on these results, provide:
1. A unified answer that directly answers the original question
2. 3-5 key insights or patterns discovered in the data
3. Actionable recommendations (if applicable)

Respond in JSON format:
{{
    "unified_answer": "A concise summary that answers the original question",
    "key_insights": [
        "Insight 1",
        "Insight 2",
        "Insight 3"
    ]
}}

JSON Response:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are an expert data analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=800
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON if wrapped in code blocks
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            
            return result
        
        except Exception as e:
            # Return basic synthesis on error
            return {
                'unified_answer': f"Results from {len(sub_results)} queries executed successfully.",
                'key_insights': [f"Error synthesizing results: {str(e)}"]
            }

    async def synthesize_simple_result(self, question: str, sql: str, results: List[Dict], columns: List[str]) -> Dict:
        """
        Synthesize results from a single query into a natural language summary.

        Args:
            question: User's original question
            sql: Generated SQL query
            results: Query results
            columns: Column names

        Returns:
            Dictionary with:
            - summary: str (natural language summary)
            - key_insights: List[str] (3-5 insights)
        """

        # If no results, return simple message
        if not results or len(results) == 0:
            return {
                'summary': 'No data found matching your query.',
                'key_insights': []
            }

        # Prepare results (max rows configured in .env)
        max_rows = Config.SYNTHESIS_MAX_ROWS
        result_sample = results[:max_rows]
        total_rows = len(results)

        prompt = f"""You are a data analyst providing clear, concise summaries of database query results.

USER QUESTION: {question}

SQL QUERY: {sql}

RESULTS ({len(result_sample)} of {total_rows} rows shown):
{json.dumps(result_sample, indent=2)}

Provide:
1. A 1-2 sentence natural language summary that directly answers the user's question
2. 3-5 key insights or patterns from the data (if applicable)

Be specific with numbers and trends. If there's only one row, describe that result clearly.

Respond in JSON format:
{{
    "summary": "Clear, direct answer to the user's question with specific numbers",
    "key_insights": [
        "Specific insight with numbers",
        "Another specific observation",
        "Trend or pattern noticed"
    ]
}}

JSON Response:"""

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are an expert data analyst who provides clear, concise summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )

            result_text = response.choices[0].message.content.strip()

            # Extract JSON if wrapped in code blocks
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            result = json.loads(result_text)

            return result

        except Exception as e:
            # Return basic summary on error
            return {
                'summary': f"Query returned {total_rows} row(s).",
                'key_insights': []
            }
