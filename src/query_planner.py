"""
Query Planner - Analyzes question complexity and decomposes into sub-queries
"""

from typing import Dict, List
from openai import AzureOpenAI
import json


class QueryPlanner:
    """
    Analyzes natural language questions to determine complexity and decompose
    complex questions into independent sub-queries for Map-Reduce processing.
    """
    
    def __init__(self, config: Dict[str, str]):
        """Initialize the query planner with Azure OpenAI configuration"""
        self.client = AzureOpenAI(
            api_version=config.get('api_version', '2024-12-01-preview'),
            azure_endpoint=config['endpoint'],
            api_key=config['api_key']
        )
        self.deployment_name = config['deployment_name']
    
    async def analyze_question(self, question: str) -> Dict:
        """
        Analyze a question to determine if it's complex and needs decomposition.
        
        Args:
            question: Natural language question
            
        Returns:
            Dictionary with:
            - is_complex: bool
            - reasoning: str
            - sub_queries: List[str] (if complex)
        """
        
        prompt = f"""Analyze the following user question and determine if it requires multiple independent SQL queries to answer.

USER QUESTION: {question}

A question is COMPLEX if it asks for:
1. Multiple distinct metrics or calculations (e.g., "total customers AND churn rate by country")
2. Information from different time periods or segments that can't be combined in a single query
3. Multiple unrelated aggregations

A question is SIMPLE if it asks for:
1. A single metric or calculation
2. Data that can be retrieved with one SQL query
3. Related information that can be JOINed in a single query

If the question is COMPLEX, break it down into 2-4 independent sub-questions that can be executed in parallel.

Respond in JSON format:
{{
    "is_complex": true/false,
    "reasoning": "Explanation of why the question is complex or simple",
    "sub_queries": ["sub-question 1", "sub-question 2", ...]  // Only if complex
}}

JSON Response:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing database questions."},
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
            
            # Ensure sub_queries is empty list if not complex
            if not result.get('is_complex'):
                result['sub_queries'] = []
            
            return result
        
        except Exception as e:
            # Default to simple query on error
            return {
                'is_complex': False,
                'reasoning': f"Error analyzing question: {str(e)}. Treating as simple query.",
                'sub_queries': []
            }
