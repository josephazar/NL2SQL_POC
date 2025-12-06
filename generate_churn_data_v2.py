#!/usr/bin/env python3
"""
Enhanced Churn Data Simulation - Complete ChurnSim Schema
Generates data for all 9 tables matching the original churnsim structure
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Configuration
NUM_ACCOUNTS = 5000
NUM_SUBSCRIPTIONS = 6000
NUM_EVENTS = 50000
NUM_METRICS = 10000
NUM_OBSERVATIONS = 5000

# Seed for reproducibility
np.random.seed(42)
random.seed(42)

# Reference data
COUNTRIES = ['USA', 'UK', 'Canada', 'Germany', 'France', 'Australia']
CHANNELS = ['organic', 'paid_search', 'social_media', 'referral', 'direct', 'email']
PRODUCTS = ['Basic', 'Standard', 'Premium', 'Enterprise']
PRODUCT_MRR = {'Basic': 9.99, 'Standard': 29.99, 'Premium': 49.99, 'Enterprise': 99.99}
BILLING_PERIODS = [1, 3, 6, 12]  # months

EVENT_TYPES = [
    'login', 'logout', 'feature_usage', 'support_ticket', 
    'settings_change', 'invite', 'payment', 'upgrade',
    'downgrade', 'content_view', 'export', 'api_call'
]

METRIC_NAMES = [
    'login_rate', 'feature_usage_count', 'session_duration',
    'support_tickets', 'user_count', 'api_calls',
    'content_views', 'exports', 'engagement_score', 'health_score'
]

def generate_accounts(n):
    """Generate account data"""
    print(f"Generating {n} accounts...")
    accounts = []
    
    for i in range(1, n + 1):
        account = {
            'id': i,
            'channel': random.choice(CHANNELS),
            'date_of_birth': (datetime(1950, 1, 1) + timedelta(days=random.randint(0, 25000))).date(),
            'country': random.choice(COUNTRIES)
        }
        accounts.append(account)
    
    return pd.DataFrame(accounts)

def generate_subscriptions(accounts_df, n):
    """Generate subscription data"""
    print(f"Generating {n} subscriptions...")
    subscriptions = []
    
    # Some accounts can have multiple subscriptions
    for i in range(n):
        account_id = random.choice(accounts_df['id'].tolist())
        product = random.choice(PRODUCTS)
        mrr = PRODUCT_MRR[product]
        bill_period = random.choice(BILLING_PERIODS)
        
        # Random start date in the past 2 years
        start_date = datetime.now() - timedelta(days=random.randint(0, 730))
        
        # 25% chance of churn
        is_churned = random.random() < 0.25
        if is_churned:
            # Churned between 1 and 365 days after start
            days_active = random.randint(1, 365)
            end_date = start_date + timedelta(days=days_active)
        else:
            end_date = None
        
        # Some subscriptions have discounts
        discount = random.choice([0, 0, 0, 0.1, 0.15, 0.2, 0.25])
        
        subscription = {
            'account_id': account_id,
            'product': product,
            'start_date': start_date.date(),
            'end_date': end_date.date() if end_date else None,
            'mrr': mrr * (1 - discount),
            'quantity': random.choice([1, 1, 1, 2, 3, 5]),
            'units': random.choice(['seats', 'users', 'licenses']),
            'bill_period_months': bill_period,
            'discount': discount
        }
        subscriptions.append(subscription)
    
    return pd.DataFrame(subscriptions)

def generate_event_types():
    """Generate event_type lookup table"""
    print("Generating event types...")
    event_types = []
    for i, event_type in enumerate(EVENT_TYPES, 1):
        event_types.append({
            'event_type_id': i,
            'event_type_name': event_type
        })
    return pd.DataFrame(event_types)

def generate_events(subscriptions_df, event_types_df, n):
    """Generate event data"""
    print(f"Generating {n} events...")
    events = []
    
    # Get active subscriptions for event generation
    active_subs = subscriptions_df[subscriptions_df['end_date'].isna()]
    
    for i in range(n):
        if len(active_subs) > 0:
            sub = active_subs.sample(1).iloc[0]
            account_id = sub['account_id']
            start_date = pd.to_datetime(sub['start_date'])
            
            # Event occurred between subscription start and now
            days_range = (datetime.now() - start_date).days
            if days_range > 0:
                event_date = start_date + timedelta(days=random.randint(0, days_range))
            else:
                event_date = start_date
            
            # Random event type
            event_type_id = random.choice(event_types_df['event_type_id'].tolist())
            
            # Some events have user_id (multi-user accounts)
            user_id = random.randint(1, 10) if random.random() < 0.3 else None
            
            # Some events have values
            event_value = round(random.uniform(1, 100), 2) if random.random() < 0.5 else None
            
            event = {
                'account_id': account_id,
                'event_time': event_date,
                'event_type_id': event_type_id,
                'user_id': user_id,
                'event_value': event_value
            }
            events.append(event)
    
    return pd.DataFrame(events)

def generate_metric_names():
    """Generate metric_name lookup table"""
    print("Generating metric names...")
    metric_names = []
    for i, metric_name in enumerate(METRIC_NAMES, 1):
        metric_names.append({
            'metric_name_id': i,
            'metric_name': metric_name
        })
    return pd.DataFrame(metric_names)

def generate_metrics(subscriptions_df, metric_names_df, n):
    """Generate calculated metrics"""
    print(f"Generating {n} metrics...")
    metrics = []
    
    active_subs = subscriptions_df[subscriptions_df['end_date'].isna()]
    
    for i in range(n):
        if len(active_subs) > 0:
            sub = active_subs.sample(1).iloc[0]
            account_id = sub['account_id']
            
            # Metric calculated in the past 90 days
            metric_time = datetime.now() - timedelta(days=random.randint(0, 90))
            
            metric_name_id = random.choice(metric_names_df['metric_name_id'].tolist())
            metric_value = round(random.uniform(0, 100), 2)
            
            metric = {
                'account_id': account_id,
                'metric_time': metric_time,
                'metric_name_id': metric_name_id,
                'metric_value': metric_value
            }
            metrics.append(metric)
    
    return pd.DataFrame(metrics)

def generate_active_periods(subscriptions_df):
    """Generate active period tracking"""
    print("Generating active periods...")
    active_periods = []
    
    for _, sub in subscriptions_df.iterrows():
        account_id = sub['account_id']
        start_date = pd.to_datetime(sub['start_date'])
        end_date = pd.to_datetime(sub['end_date']) if pd.notna(sub['end_date']) else datetime.now()
        
        # Create monthly active periods
        current = start_date
        while current < end_date:
            period_end = min(current + timedelta(days=30), end_date)
            active_periods.append({
                'account_id': account_id,
                'start_date': current.date(),
                'end_date': period_end.date()
            })
            current = period_end + timedelta(days=1)
    
    return pd.DataFrame(active_periods)

def generate_active_weeks(subscriptions_df):
    """Generate weekly activity tracking"""
    print("Generating active weeks...")
    active_weeks = []
    
    # Sample some subscriptions for weekly tracking
    sample_subs = subscriptions_df.sample(min(1000, len(subscriptions_df)))
    
    for _, sub in sample_subs.iterrows():
        account_id = sub['account_id']
        start_date = pd.to_datetime(sub['start_date'])
        end_date = pd.to_datetime(sub['end_date']) if pd.notna(sub['end_date']) else datetime.now()
        
        # Create weekly periods
        current = start_date
        while current < end_date:
            week_end = min(current + timedelta(days=7), end_date)
            active_weeks.append({
                'account_id': account_id,
                'start_date': current.date(),
                'end_date': week_end.date()
            })
            current = week_end + timedelta(days=1)
    
    return pd.DataFrame(active_weeks)

def generate_observations(subscriptions_df, n):
    """Generate ML training observations"""
    print(f"Generating {n} observations...")
    observations = []
    
    for i in range(n):
        sub = subscriptions_df.sample(1).iloc[0]
        account_id = sub['account_id']
        
        # Observation date is random date during subscription
        start_date = pd.to_datetime(sub['start_date'])
        if pd.notna(sub['end_date']):
            end_date = pd.to_datetime(sub['end_date'])
            days_range = (end_date - start_date).days
        else:
            days_range = (datetime.now() - start_date).days
        
        if days_range > 0:
            observation_date = start_date + timedelta(days=random.randint(0, days_range))
        else:
            observation_date = start_date
        
        # is_churn is True if subscription ended after observation
        is_churn = pd.notna(sub['end_date'])
        
        observations.append({
            'account_id': account_id,
            'observation_date': observation_date.date(),
            'is_churn': is_churn
        })
    
    return pd.DataFrame(observations)

def create_database(db_path):
    """Create SQLite database with all tables"""
    print(f"\nCreating database at {db_path}...")
    
    # Generate all data
    accounts_df = generate_accounts(NUM_ACCOUNTS)
    subscriptions_df = generate_subscriptions(accounts_df, NUM_SUBSCRIPTIONS)
    event_types_df = generate_event_types()
    events_df = generate_events(subscriptions_df, event_types_df, NUM_EVENTS)
    metric_names_df = generate_metric_names()
    metrics_df = generate_metrics(subscriptions_df, metric_names_df, NUM_METRICS)
    active_periods_df = generate_active_periods(subscriptions_df)
    active_weeks_df = generate_active_weeks(subscriptions_df)
    observations_df = generate_observations(subscriptions_df, NUM_OBSERVATIONS)
    
    # Create database
    conn = sqlite3.connect(db_path)
    
    print("\nInserting data into database...")
    accounts_df.to_sql('account', conn, if_exists='replace', index=False)
    subscriptions_df.to_sql('subscription', conn, if_exists='replace', index=False)
    event_types_df.to_sql('event_type', conn, if_exists='replace', index=False)
    events_df.to_sql('event', conn, if_exists='replace', index=False)
    metric_names_df.to_sql('metric_name', conn, if_exists='replace', index=False)
    metrics_df.to_sql('metric', conn, if_exists='replace', index=False)
    active_periods_df.to_sql('active_period', conn, if_exists='replace', index=False)
    active_weeks_df.to_sql('active_week', conn, if_exists='replace', index=False)
    observations_df.to_sql('observation', conn, if_exists='replace', index=False)
    
    # Create indexes
    print("Creating indexes...")
    cursor = conn.cursor()
    
    # Account indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_account_id ON account(id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_account_country ON account(country)')
    
    # Subscription indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_subscription_account ON subscription(account_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_subscription_dates ON subscription(start_date, end_date)')
    
    # Event indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_account ON event(account_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_time ON event(event_time)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON event(event_type_id)')
    
    # Metric indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_metric_account ON metric(account_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_metric_time ON metric(metric_time)')
    
    # Observation indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_observation_account ON observation(account_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_observation_date ON observation(observation_date)')
    
    conn.commit()
    
    # Print statistics
    print("\n" + "="*50)
    print("Database Statistics:")
    print("="*50)
    cursor.execute('SELECT COUNT(*) FROM account')
    print(f"Total Accounts: {cursor.fetchone()[0]}")
    
    cursor.execute('SELECT COUNT(*) FROM subscription')
    print(f"Total Subscriptions: {cursor.fetchone()[0]}")
    
    cursor.execute('SELECT COUNT(*) FROM subscription WHERE end_date IS NULL')
    print(f"Active Subscriptions: {cursor.fetchone()[0]}")
    
    cursor.execute('SELECT COUNT(*) FROM subscription WHERE end_date IS NOT NULL')
    print(f"Churned Subscriptions: {cursor.fetchone()[0]}")
    
    cursor.execute('SELECT COUNT(*) FROM event')
    print(f"Total Events: {cursor.fetchone()[0]}")
    
    cursor.execute('SELECT COUNT(*) FROM event_type')
    print(f"Event Types: {cursor.fetchone()[0]}")
    
    cursor.execute('SELECT COUNT(*) FROM metric')
    print(f"Total Metrics: {cursor.fetchone()[0]}")
    
    cursor.execute('SELECT COUNT(*) FROM metric_name')
    print(f"Metric Names: {cursor.fetchone()[0]}")
    
    cursor.execute('SELECT COUNT(*) FROM active_period')
    print(f"Active Periods: {cursor.fetchone()[0]}")
    
    cursor.execute('SELECT COUNT(*) FROM active_week')
    print(f"Active Weeks: {cursor.fetchone()[0]}")
    
    cursor.execute('SELECT COUNT(*) FROM observation')
    print(f"Observations: {cursor.fetchone()[0]}")
    
    cursor.execute('SELECT ROUND(SUM(mrr), 2) FROM subscription WHERE end_date IS NULL')
    print(f"Total MRR: ${cursor.fetchone()[0]}")
    
    conn.close()
    
    # Save CSV exports
    print("\nSaving CSV files...")
    csv_dir = db_path.replace('churn.db', '')
    accounts_df.to_csv(f'{csv_dir}account.csv', index=False)
    subscriptions_df.to_csv(f'{csv_dir}subscription.csv', index=False)
    events_df.to_csv(f'{csv_dir}event.csv', index=False)
    event_types_df.to_csv(f'{csv_dir}event_type.csv', index=False)
    metrics_df.to_csv(f'{csv_dir}metric.csv', index=False)
    metric_names_df.to_csv(f'{csv_dir}metric_name.csv', index=False)
    observations_df.to_csv(f'{csv_dir}observation.csv', index=False)
    
    print(f"\n✓ Database created successfully at {db_path}")
    print(f"✓ CSV files saved in {csv_dir}")

if __name__ == '__main__':
    import os
    
    print("Starting enhanced churn data simulation...")
    print("="*50)
    
    db_path = '/home/ubuntu/nl2sql_churn_poc/data/churn.db'
    create_database(db_path)
    
    print("\n" + "="*50)
    print("✓ Enhanced churn data generation complete!")
    print("="*50)
