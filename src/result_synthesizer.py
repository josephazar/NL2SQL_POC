"""
Result Synthesizer - Combines multi-query results with unified answer and insights
"""

from typing import Dict, List
from openai import AzureOpenAI
import json


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
        
        # Build context from sub-results
        context = ""
        for i, result in enumerate(sub_results, 1):
            context += f"\\n\\nSub-Query {i}: {result['question']}"
            context += f"\\nSQL: {result['sql']}"
            context += f"\\nResults: {json.dumps(result['results'][:5], indent=2)}"  # First 5 rows
            if len(result['results']) > 5:
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
