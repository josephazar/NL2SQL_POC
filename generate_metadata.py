#!/usr/bin/env python3
"""Generate metadata JSON files for all tables"""

import json
import os

METADATA_DIR = 'metadata'

# Table metadata
TABLES = {
    'account': {
        'table': 'account',
        'description': 'Customer account information including demographics and acquisition channel',
        'datasource': 'churn_db',
        'columns': [
            {'name': 'id', 'description': 'Unique account identifier', 'type': 'INTEGER', 'examples': []},
            {'name': 'channel', 'description': 'Acquisition channel (organic, paid_search, social_media, referral, direct, email)', 'type': 'TEXT', 'examples': ['organic', 'paid_search', 'referral']},
            {'name': 'date_of_birth', 'description': 'Customer date of birth', 'type': 'DATE', 'examples': []},
            {'name': 'country', 'description': 'Customer country', 'type': 'TEXT', 'examples': ['USA', 'UK', 'Canada', 'Germany', 'France', 'Australia']}
        ]
    },
    'subscription': {
        'table': 'subscription',
        'description': 'Customer subscription details including product, pricing, and churn status',
        'datasource': 'churn_db',
        'columns': [
            {'name': 'account_id', 'description': 'Foreign key to account table', 'type': 'INTEGER', 'examples': []},
            {'name': 'product', 'description': 'Subscription product/plan name', 'type': 'TEXT', 'examples': ['Basic', 'Standard', 'Premium', 'Enterprise']},
            {'name': 'start_date', 'description': 'Subscription start date', 'type': 'DATE', 'examples': []},
            {'name': 'end_date', 'description': 'Subscription end date (NULL if active)', 'type': 'DATE', 'examples': []},
            {'name': 'mrr', 'description': 'Monthly recurring revenue', 'type': 'REAL', 'examples': []},
            {'name': 'quantity', 'description': 'Number of units/seats', 'type': 'REAL', 'examples': []},
            {'name': 'units', 'description': 'Unit type (seats, users, licenses)', 'type': 'TEXT', 'examples': ['seats', 'users', 'licenses']},
            {'name': 'bill_period_months', 'description': 'Billing period in months', 'type': 'INTEGER', 'examples': [1, 3, 6, 12]},
            {'name': 'discount', 'description': 'Discount percentage applied', 'type': 'REAL', 'examples': []}
        ]
    },
    'event': {
        'table': 'event',
        'description': 'Customer behavioral events and interactions',
        'datasource': 'churn_db',
        'columns': [
            {'name': 'account_id', 'description': 'Foreign key to account table', 'type': 'INTEGER', 'examples': []},
            {'name': 'event_time', 'description': 'Timestamp when event occurred', 'type': 'TIMESTAMP', 'examples': []},
            {'name': 'event_type_id', 'description': 'Foreign key to event_type table', 'type': 'INTEGER', 'examples': []},
            {'name': 'user_id', 'description': 'User ID for multi-user accounts (nullable)', 'type': 'INTEGER', 'examples': []},
            {'name': 'event_value', 'description': 'Numeric value associated with event (nullable)', 'type': 'REAL', 'examples': []}
        ]
    },
    'event_type': {
        'table': 'event_type',
        'description': 'Lookup table for event types',
        'datasource': 'churn_db',
        'columns': [
            {'name': 'event_type_id', 'description': 'Unique event type identifier', 'type': 'INTEGER', 'examples': []},
            {'name': 'event_type_name', 'description': 'Event type name', 'type': 'TEXT', 'examples': ['login', 'logout', 'feature_usage', 'support_ticket', 'settings_change']}
        ]
    },
    'metric': {
        'table': 'metric',
        'description': 'Calculated customer metrics over time',
        'datasource': 'churn_db',
        'columns': [
            {'name': 'account_id', 'description': 'Foreign key to account table', 'type': 'INTEGER', 'examples': []},
            {'name': 'metric_time', 'description': 'Timestamp when metric was calculated', 'type': 'TIMESTAMP', 'examples': []},
            {'name': 'metric_name_id', 'description': 'Foreign key to metric_name table', 'type': 'INTEGER', 'examples': []},
            {'name': 'metric_value', 'description': 'Calculated metric value', 'type': 'REAL', 'examples': []}
        ]
    },
    'metric_name': {
        'table': 'metric_name',
        'description': 'Lookup table for metric names',
        'datasource': 'churn_db',
        'columns': [
            {'name': 'metric_name_id', 'description': 'Unique metric name identifier', 'type': 'INTEGER', 'examples': []},
            {'name': 'metric_name', 'description': 'Metric name', 'type': 'TEXT', 'examples': ['login_rate', 'feature_usage_count', 'session_duration', 'engagement_score']}
        ]
    },
    'active_period': {
        'table': 'active_period',
        'description': 'Monthly active periods for accounts',
        'datasource': 'churn_db',
        'columns': [
            {'name': 'account_id', 'description': 'Foreign key to account table', 'type': 'INTEGER', 'examples': []},
            {'name': 'start_date', 'description': 'Period start date', 'type': 'DATE', 'examples': []},
            {'name': 'end_date', 'description': 'Period end date', 'type': 'DATE', 'examples': []}
        ]
    },
    'active_week': {
        'table': 'active_week',
        'description': 'Weekly activity tracking for accounts',
        'datasource': 'churn_db',
        'columns': [
            {'name': 'account_id', 'description': 'Foreign key to account table', 'type': 'INTEGER', 'examples': []},
            {'name': 'start_date', 'description': 'Week start date', 'type': 'DATE', 'examples': []},
            {'name': 'end_date', 'description': 'Week end date', 'type': 'DATE', 'examples': []}
        ]
    },
    'observation': {
        'table': 'observation',
        'description': 'ML training observations with churn labels',
        'datasource': 'churn_db',
        'columns': [
            {'name': 'account_id', 'description': 'Foreign key to account table', 'type': 'INTEGER', 'examples': []},
            {'name': 'observation_date', 'description': 'Date of observation', 'type': 'DATE', 'examples': []},
            {'name': 'is_churn', 'description': 'Whether account churned (boolean)', 'type': 'BOOLEAN', 'examples': []}
        ]
    }
}

# Query examples
QUERIES = {
    'churn_rate': {
        'datasource': 'churn_db',
        'question': 'What is our current churn rate?',
        'query': 'SELECT ROUND(CAST(SUM(CASE WHEN end_date IS NOT NULL THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 2) as churn_rate_percent FROM subscription',
        'reasoning': 'Calculates the percentage of churned subscriptions out of total subscriptions by counting subscriptions with end_date set.'
    },
    'mrr_by_product': {
        'datasource': 'churn_db',
        'question': 'What is the total MRR by product?',
        'query': 'SELECT product, ROUND(SUM(mrr), 2) as total_mrr FROM subscription WHERE end_date IS NULL GROUP BY product ORDER BY total_mrr DESC',
        'reasoning': 'Sums monthly recurring revenue for active subscriptions grouped by product.'
    },
    'top_customers_by_mrr': {
        'datasource': 'churn_db',
        'question': 'Who are the top 10 customers by MRR?',
        'query': 'SELECT a.id, a.country, ROUND(SUM(s.mrr), 2) as total_mrr FROM account a JOIN subscription s ON a.id = s.account_id WHERE s.end_date IS NULL GROUP BY a.id, a.country ORDER BY total_mrr DESC LIMIT 10',
        'reasoning': 'Joins accounts with active subscriptions and ranks by total MRR.'
    },
    'accounts_by_country': {
        'datasource': 'churn_db',
        'question': 'How many accounts do we have in each country?',
        'query': 'SELECT country, COUNT(*) as account_count FROM account GROUP BY country ORDER BY account_count DESC',
        'reasoning': 'Groups accounts by country and counts them.'
    },
    'event_activity_by_type': {
        'datasource': 'churn_db',
        'question': 'What is the event activity by type?',
        'query': 'SELECT et.event_type_name, COUNT(*) as event_count FROM event e JOIN event_type et ON e.event_type_id = et.event_type_id GROUP BY et.event_type_name ORDER BY event_count DESC',
        'reasoning': 'Counts events grouped by event type using the event_type lookup table.'
    },
    'churn_by_channel': {
        'datasource': 'churn_db',
        'question': 'What is the churn rate by acquisition channel?',
        'query': 'SELECT a.channel, ROUND(CAST(SUM(CASE WHEN s.end_date IS NOT NULL THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 2) as churn_rate FROM account a JOIN subscription s ON a.id = s.account_id GROUP BY a.channel ORDER BY churn_rate DESC',
        'reasoning': 'Calculates churn rate for each acquisition channel by joining accounts and subscriptions.'
    },
    'subscriptions_over_time': {
        'datasource': 'churn_db',
        'question': 'Show me subscription starts by month',
        'query': "SELECT strftime('%Y-%m', start_date) as month, COUNT(*) as new_subscriptions FROM subscription GROUP BY month ORDER BY month",
        'reasoning': 'Groups subscriptions by start month to show growth over time.'
    },
    'churns_over_time': {
        'datasource': 'churn_db',
        'question': 'Show me churns by month',
        'query': "SELECT strftime('%Y-%m', end_date) as month, COUNT(*) as churns FROM subscription WHERE end_date IS NOT NULL GROUP BY month ORDER BY month",
        'reasoning': 'Groups churned subscriptions by end month to show churn trends over time.'
    },
    'avg_metrics_by_account': {
        'datasource': 'churn_db',
        'question': 'What are the average metric values by metric type?',
        'query': 'SELECT mn.metric_name, ROUND(AVG(m.metric_value), 2) as avg_value, COUNT(*) as measurement_count FROM metric m JOIN metric_name mn ON m.metric_name_id = mn.metric_name_id GROUP BY mn.metric_name ORDER BY avg_value DESC',
        'reasoning': 'Calculates average values for each metric type using metric and metric_name tables.'
    },
    'churn_observations': {
        'datasource': 'churn_db',
        'question': 'How many churn observations do we have?',
        'query': 'SELECT is_churn, COUNT(*) as observation_count FROM observation GROUP BY is_churn',
        'reasoning': 'Counts ML training observations grouped by churn status.'
    }
}

def save_table_metadata():
    """Save table metadata JSON files"""
    tables_dir = os.path.join(METADATA_DIR, 'tables')
    for table_name, metadata in TABLES.items():
        filepath = os.path.join(tables_dir, f'{table_name}.json')
        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✓ Created {filepath}")

def save_query_metadata():
    """Save query example JSON files"""
    queries_dir = os.path.join(METADATA_DIR, 'queries')
    for query_name, metadata in QUERIES.items():
        filepath = os.path.join(queries_dir, f'{query_name}.json')
        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✓ Created {filepath}")

def save_datasources():
    """Save datasources.json"""
    datasources = {
        'datasources': [
            {
                'name': 'churn_db',
                'type': 'sqlite',
                'connection_string': 'data/churn.db',
                'description': 'Customer churn database with complete churnsim schema (9 tables)',
                'tables': list(TABLES.keys())
            }
        ]
    }
    filepath = os.path.join(METADATA_DIR, 'datasources.json')
    with open(filepath, 'w') as f:
        json.dump(datasources, f, indent=2)
    print(f"✓ Created {filepath}")

if __name__ == '__main__':
    print("Generating metadata files...")
    print("="*50)
    save_table_metadata()
    print()
    save_query_metadata()
    print()
    save_datasources()
    print("="*50)
    print(f"✓ Generated {len(TABLES)} table metadata files")
    print(f"✓ Generated {len(QUERIES)} query example files")
    print("✓ Generated datasources.json")
