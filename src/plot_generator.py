"""
Dynamic Plot Generation Module using Plotly
Automatically generates appropriate visualizations based on query results
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Dict, Any, Optional
import re
import numpy as np
import json

class PlotGenerator:
    """Generates Plotly visualizations from SQL query results"""
    
    def __init__(self):
        self.color_palette = px.colors.qualitative.Set2
    
    def should_visualize(self, query: str, results: List[Dict[str, Any]]) -> bool:
        """
        Determine if query results should be visualized
        
        Args:
            query: SQL query string
            results: Query results as list of dictionaries
            
        Returns:
            True if visualization is appropriate
        """
        if not results or len(results) == 0:
            return False
        
        # Don't visualize single row results (unless it's a single metric)
        if len(results) == 1 and len(results[0]) > 2:
            return False
        
        # Don't visualize SELECT * queries
        if re.search(r'SELECT\s+\*', query, re.IGNORECASE):
            return False
        
        # Check if query has aggregations or GROUP BY
        has_aggregation = bool(re.search(
            r'\b(COUNT|SUM|AVG|MAX|MIN|GROUP BY)\b', 
            query, 
            re.IGNORECASE
        ))
        
        # Check if query has time-based columns
        has_time = self._has_time_column(results)
        
        return has_aggregation or has_time or len(results) > 1
    
    def _has_time_column(self, results: List[Dict[str, Any]]) -> bool:
        """
        Check if results have time-series data by analyzing actual values.
        Works on any database schema without hardcoded keywords.
        """
        if not results or len(results) == 0:
            return False

        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(results)

        # Check each column for temporal patterns
        for col in df.columns:
            if self._is_temporal_column(df[col]):
                return True

        return False

    def _is_temporal_column(self, series: pd.Series) -> bool:
        """
        Detect if a pandas Series contains temporal data by analyzing patterns.
        Returns True if the column appears to be temporal (dates, timestamps, periods).
        """
        # Skip numeric-only columns (likely not temporal)
        if pd.api.types.is_numeric_dtype(series):
            return False

        # Try to parse as datetime
        try:
            # Sample first few non-null values
            sample = series.dropna().head(10)
            if len(sample) == 0:
                return False

            # Attempt to parse as datetime
            parsed = pd.to_datetime(sample, errors='coerce')

            # If >80% of samples parsed successfully, it's likely temporal
            success_rate = parsed.notna().sum() / len(sample)
            if success_rate > 0.8:
                return True

            # Check for common date patterns (YYYY-MM, YYYY-MM-DD, etc.)
            # This catches formatted strings that to_datetime might miss
            str_values = sample.astype(str)
            date_pattern = r'^\d{4}[-/]\d{1,2}(?:[-/]\d{1,2})?$|^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}$'
            matches = str_values.str.match(date_pattern)
            if matches.sum() / len(sample) > 0.8:
                return True

        except (ValueError, TypeError):
            pass

        return False
    
    def _detect_chart_type(self, df: pd.DataFrame, query: str) -> str:
        """
        Detect appropriate chart type based on data characteristics.
        Uses data-driven analysis instead of hardcoded keywords.

        Returns:
            Chart type: 'bar', 'line', 'pie', 'scatter', 'heatmap'
        """
        if len(df) == 0:
            return 'bar'

        # Detect temporal columns by analyzing data patterns
        temporal_cols = [col for col in df.columns if self._is_temporal_column(df[col])]

        # If we have temporal data with enough points, use line chart
        if temporal_cols and len(df) > 2:
            return 'line'

        # Detect percentage/ratio data by analyzing numeric values
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

        # Check if numeric values are percentages (0-100 or 0-1 range)
        for col in numeric_cols:
            values = df[col].dropna()
            if len(values) > 0:
                min_val, max_val = values.min(), values.max()
                # If values are in 0-1 or 0-100 range and we have few categories, use pie chart
                if ((0 <= min_val <= 1 and 0 <= max_val <= 1) or
                    (0 <= min_val <= 100 and 0 <= max_val <= 100)) and len(df) <= 10:
                    return 'pie'

        # Check for categorical + numeric pattern (good for bar charts)
        if len(df.columns) == 2 and len(df) <= 20:
            numeric_cols = df.select_dtypes(include=['number']).columns
            categorical_cols = df.select_dtypes(exclude=['number']).columns
            if len(numeric_cols) == 1 and len(categorical_cols) == 1:
                return 'bar'

        # Default to bar chart
        return 'bar'
    
    def generate_plot(self, query: str, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Generate Plotly visualization from query results
        
        Args:
            query: SQL query string
            results: Query results as list of dictionaries
            
        Returns:
            Plotly figure as JSON dict, or None if no visualization
        """
        if not self.should_visualize(query, results):
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(results)
        
        # Detect chart type
        chart_type = self._detect_chart_type(df, query)
        
        # Generate appropriate chart
        if chart_type == 'line':
            fig = self._create_line_chart(df, query)
        elif chart_type == 'pie':
            fig = self._create_pie_chart(df, query)
        elif chart_type == 'scatter':
            fig = self._create_scatter_chart(df, query)
        else:  # default to bar
            fig = self._create_bar_chart(df, query)
        
        # Apply common styling
        self._apply_styling(fig)
        
        # Convert to dict and ensure JSON serializable
        plot_dict = fig.to_dict()
        return self._make_json_serializable(plot_dict)
    
    def _create_bar_chart(self, df: pd.DataFrame, query: str) -> go.Figure:
        """Create bar chart with horizontal orientation for better readability"""
        # Find numeric and categorical columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(exclude=['number']).columns.tolist()
        
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            # Categorical on Y-axis (horizontal bars)
            category_col = categorical_cols[0]
            value_col = numeric_cols[0]
        elif len(df.columns) >= 2:
            category_col = df.columns[0]
            value_col = df.columns[1]
        else:
            return go.Figure()
        
        # Sort by value for better visualization (descending)
        df_sorted = df.sort_values(by=value_col, ascending=True)  # ascending=True for horizontal bars
        
        # Determine if values are integers or floats for formatting
        is_integer = df_sorted[value_col].dtype in ['int64', 'int32'] or (df_sorted[value_col] == df_sorted[value_col].astype(int)).all()
        
        # Format text labels directly
        if is_integer:
            text_labels = [f'{int(val):,}' for val in df_sorted[value_col]]
        else:
            text_labels = [f'{val:,.2f}' for val in df_sorted[value_col]]
        
        # Create HORIZONTAL bar chart (x=values, y=categories)
        fig = go.Figure(data=[
            go.Bar(
                x=df_sorted[value_col].tolist(),  # Convert to list to avoid numpy serialization
                y=df_sorted[category_col].tolist(),  # Convert to list to avoid numpy serialization
                orientation='h',  # Horizontal orientation
                marker_color=self.color_palette[0],
                text=text_labels,
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            xaxis_title=value_col.replace('_', ' ').title(),
            yaxis_title=category_col.replace('_', ' ').title(),
            showlegend=False,
            height=max(400, len(df_sorted) * 40)  # Dynamic height based on number of categories
        )
        
        return fig
    
    def _create_line_chart(self, df: pd.DataFrame, query: str) -> go.Figure:
        """
        Create line chart for time series.
        Uses data-driven temporal detection instead of hardcoded keywords.
        """
        # Detect temporal columns by analyzing data patterns
        temporal_cols = [col for col in df.columns if self._is_temporal_column(df[col])]

        if not temporal_cols:
            return self._create_bar_chart(df, query)

        x_col = temporal_cols[0]
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

        fig = go.Figure()

        # Add line for each numeric column
        for i, y_col in enumerate(numeric_cols):
            fig.add_trace(go.Scatter(
                x=df[x_col].tolist(),  # Convert to list to avoid numpy serialization
                y=df[y_col].tolist(),  # Convert to list to avoid numpy serialization
                mode='lines+markers',
                name=y_col.replace('_', ' ').title(),
                line=dict(color=self.color_palette[i % len(self.color_palette)], width=3),
                marker=dict(size=8)
            ))

        fig.update_layout(
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title='Value',
            hovermode='x unified'
        )

        return fig
    
    def _create_pie_chart(self, df: pd.DataFrame, query: str) -> go.Figure:
        """Create pie chart"""
        if len(df.columns) < 2:
            return self._create_bar_chart(df, query)
        
        # Use first column as labels, second as values
        labels_col = df.columns[0]
        values_col = df.columns[1]
        
        fig = go.Figure(data=[
            go.Pie(
                labels=df[labels_col].tolist(),  # Convert to list to avoid numpy serialization
                values=df[values_col].tolist(),  # Convert to list to avoid numpy serialization
                marker=dict(colors=self.color_palette),
                textinfo='label+percent',
                textposition='auto',
                hovertemplate='<b>%{label}</b><br>Value: %{value}<br>Percent: %{percent}<extra></extra>'
            )
        ])
        
        return fig
    
    def _create_scatter_chart(self, df: pd.DataFrame, query: str) -> go.Figure:
        """Create scatter plot"""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if len(numeric_cols) < 2:
            return self._create_bar_chart(df, query)
        
        x_col = numeric_cols[0]
        y_col = numeric_cols[1]
        
        fig = go.Figure(data=[
            go.Scatter(
                x=df[x_col].tolist(),  # Convert to list to avoid numpy serialization
                y=df[y_col].tolist(),  # Convert to list to avoid numpy serialization
                mode='markers',
                marker=dict(
                    size=10,
                    color=self.color_palette[0],
                    opacity=0.7
                )
            )
        ])
        
        fig.update_layout(
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title()
        )
        
        return fig
    
    def _apply_styling(self, fig: go.Figure):
        """Apply consistent styling to all charts"""
        fig.update_layout(
            template='plotly_white',
            font=dict(family='Inter, system-ui, sans-serif', size=12),
            title_font=dict(size=16, family='Inter, system-ui, sans-serif'),
            margin=dict(l=50, r=50, t=50, b=50),
            height=400,
            hovermode='closest'
        )
        
        # Update axes
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0,0,0,0.1)',
            showline=True,
            linewidth=1,
            linecolor='rgba(0,0,0,0.2)'
        )
        
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(0,0,0,0.1)',
            showline=True,
            linewidth=1,
            linecolor='rgba(0,0,0,0.2)'
        )
    
    def _make_json_serializable(self, obj: Any) -> Any:
        """Recursively convert numpy arrays and other non-serializable types to JSON-compatible types"""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(self._make_json_serializable(item) for item in obj)
        else:
            return obj


def test_plot_generator():
    """Test the plot generator with sample data"""
    generator = PlotGenerator()
    
    # Test 1: Bar chart data
    query1 = "SELECT country, COUNT(*) as count FROM account GROUP BY country"
    results1 = [
        {'country': 'USA', 'count': 1500},
        {'country': 'UK', 'count': 1200},
        {'country': 'Canada', 'count': 800},
        {'country': 'Germany', 'count': 600}
    ]
    
    plot1 = generator.generate_plot(query1, results1)
    print("Test 1 (Bar chart):", "✓ Generated" if plot1 else "✗ Failed")
    
    # Test 2: Time series data
    query2 = "SELECT month, COUNT(*) as subscriptions FROM subscription GROUP BY month"
    results2 = [
        {'month': '2024-01', 'subscriptions': 100},
        {'month': '2024-02', 'subscriptions': 150},
        {'month': '2024-03', 'subscriptions': 200},
        {'month': '2024-04', 'subscriptions': 180}
    ]
    
    plot2 = generator.generate_plot(query2, results2)
    print("Test 2 (Line chart):", "✓ Generated" if plot2 else "✗ Failed")
    
    # Test 3: Pie chart data
    query3 = "SELECT product, SUM(mrr) as revenue FROM subscription GROUP BY product"
    results3 = [
        {'product': 'Basic', 'revenue': 10000},
        {'product': 'Premium', 'revenue': 25000},
        {'product': 'Enterprise', 'revenue': 50000}
    ]
    
    plot3 = generator.generate_plot(query3, results3)
    print("Test 3 (Pie chart):", "✓ Generated" if plot3 else "✗ Failed")


if __name__ == '__main__':
    test_plot_generator()
