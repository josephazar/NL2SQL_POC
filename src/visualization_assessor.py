"""
Intelligent Visualization Assessor
Determines whether a visualization adds value for a given query result.
"""

class VisualizationAssessor:
    """Assesses whether a visualization is beneficial for query results."""
    
    def __init__(self, azure_openai_config):
        """Initialize with Azure OpenAI configuration."""
        self.config = azure_openai_config
    
    def should_visualize(self, question: str, sql: str, results: list, columns: list) -> dict:
        """
        Determine if visualization adds value.
        
        Args:
            question: The user's question
            sql: The generated SQL query
            results: Query results as list of dicts
            columns: Column names
            
        Returns:
            dict with 'should_visualize' (bool), 'reason' (str), 'chart_type' (str or None)
        """
        # Rule 1: No results = no visualization
        if not results or len(results) == 0:
            return {
                "should_visualize": False,
                "reason": "No data returned from query",
                "chart_type": None
            }
        
        # Rule 2: Single scalar value (1 row, 1 column) = no visualization
        if len(results) == 1 and len(columns) == 1:
            return {
                "should_visualize": False,
                "reason": "Single scalar value - better displayed as text",
                "chart_type": None,
                "display_format": "scalar"
            }
        
        # Rule 3: Single row with multiple columns = no visualization (usually)
        # Exception: If columns represent categories (e.g., revenue by product in columns)
        if len(results) == 1 and len(columns) > 1:
            # Check if this looks like a pivot/cross-tab
            if self._looks_like_pivot(columns):
                return {
                    "should_visualize": True,
                    "reason": "Single row with multiple category columns - good for bar chart",
                    "chart_type": "bar"
                }
            else:
                return {
                    "should_visualize": False,
                    "reason": "Single row with mixed columns - better as table",
                    "chart_type": None
                }
        
        # Rule 4: Multiple rows with 2 columns (category + value) = good for visualization
        if len(results) >= 2 and len(columns) == 2:
            return {
                "should_visualize": True,
                "reason": "Multiple rows with category-value pairs - ideal for charts",
                "chart_type": "auto"  # Let PlotGenerator decide
            }
        
        # Rule 5: Multiple rows with 3+ columns = depends on content
        if len(results) >= 2 and len(columns) >= 3:
            # Check if there's a clear time column
            if self._has_time_column(columns):
                return {
                    "should_visualize": True,
                    "reason": "Time-series data detected - good for line chart",
                    "chart_type": "line"
                }
            # Check if there's a clear category + multiple metrics
            elif self._has_category_and_metrics(columns, results):
                return {
                    "should_visualize": True,
                    "reason": "Category with multiple metrics - good for grouped bar chart",
                    "chart_type": "bar"
                }
            else:
                return {
                    "should_visualize": False,
                    "reason": "Complex multi-column data - better as table",
                    "chart_type": None
                }
        
        # Default: Don't visualize if unsure
        return {
            "should_visualize": False,
            "reason": "Data structure not suitable for standard visualizations",
            "chart_type": None
        }
    
    def _looks_like_pivot(self, columns: list) -> bool:
        """Check if columns look like pivot categories (e.g., Q1, Q2, Q3, Q4)."""
        # Simple heuristic: if all columns except first are similar (e.g., all start with same prefix)
        if len(columns) < 3:
            return False
        
        # Check for common pivot patterns
        pivot_keywords = ['q1', 'q2', 'q3', 'q4', 'jan', 'feb', 'mar', 'apr', 'may', 'jun',
                          'jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'product', 'region']
        
        col_lower = [c.lower() for c in columns]
        matches = sum(1 for col in col_lower if any(kw in col for kw in pivot_keywords))
        
        return matches >= 2
    
    def _has_time_column(self, columns: list) -> bool:
        """Check if there's a time-related column."""
        time_keywords = ['date', 'time', 'year', 'month', 'day', 'week', 'quarter',
                         'period', 'timestamp', 'created', 'updated']
        
        col_lower = [c.lower() for c in columns]
        return any(any(kw in col for kw in time_keywords) for col in col_lower)
    
    def _has_category_and_metrics(self, columns: list, results: list) -> bool:
        """Check if first column is categorical and rest are numeric metrics."""
        if len(columns) < 2 or len(results) == 0:
            return False
        
        # Check if first column has string values (category)
        first_col = columns[0]
        first_values = [row.get(first_col) for row in results if row.get(first_col) is not None]
        
        if not first_values:
            return False
        
        # If first column has strings and other columns have numbers, it's category + metrics
        first_is_string = isinstance(first_values[0], str)
        
        if first_is_string and len(columns) >= 2:
            # Check if at least one other column is numeric
            for col in columns[1:]:
                values = [row.get(col) for row in results if row.get(col) is not None]
                if values and isinstance(values[0], (int, float)):
                    return True
        
        return False


# Test the assessor
if __name__ == "__main__":
    assessor = VisualizationAssessor({})
    
    # Test 1: Single scalar (total customers)
    test1 = assessor.should_visualize(
        "How many customers?",
        "SELECT COUNT(*) as total FROM account",
        [{"total_customers": 5000}],
        ["total_customers"]
    )
    print("Test 1 (scalar):", test1)
    assert test1["should_visualize"] == False
    
    # Test 2: Category + value (churn by country)
    test2 = assessor.should_visualize(
        "Churn rate by country?",
        "SELECT country, churn_rate FROM ...",
        [{"country": "USA", "churn_rate": 24.5}, {"country": "UK", "churn_rate": 23.1}],
        ["country", "churn_rate"]
    )
    print("Test 2 (category+value):", test2)
    assert test2["should_visualize"] == True
    
    # Test 3: Time series
    test3 = assessor.should_visualize(
        "Revenue over time?",
        "SELECT month, revenue FROM ...",
        [{"month": "2024-01", "revenue": 1000}, {"month": "2024-02", "revenue": 1200}],
        ["month", "revenue"]
    )
    print("Test 3 (time series):", test3)
    assert test3["should_visualize"] == True
    
    print("\n✅ All tests passed!")
