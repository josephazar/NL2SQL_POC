"""
Churn Data Simulation Script
Generates realistic customer churn data and saves to SQLite database
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Configuration
NUM_CUSTOMERS = 5000
NUM_SUBSCRIPTIONS = 6000
NUM_EVENTS = 50000
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 12, 31)

def generate_customers(n):
    """Generate customer data"""
    print(f"Generating {n} customers...")
    
    customers = []
    for i in range(1, n + 1):
        signup_date = START_DATE + timedelta(days=random.randint(0, 365))
        
        customer = {
            'customer_id': i,
            'email': f'customer{i}@example.com',
            'name': f'Customer {i}',
            'country': random.choice(['USA', 'UK', 'Canada', 'Germany', 'France', 'Australia']),
            'signup_date': signup_date.strftime('%Y-%m-%d'),
            'age': random.randint(18, 75),
            'account_type': random.choice(['Individual', 'Business', 'Enterprise']),
            'created_at': signup_date.strftime('%Y-%m-%d %H:%M:%S')
        }
        customers.append(customer)
    
    return pd.DataFrame(customers)

def generate_subscriptions(customers_df, n):
    """Generate subscription data"""
    print(f"Generating {n} subscriptions...")
    
    plans = [
        {'plan_id': 1, 'plan_name': 'Basic', 'mrr': 9.99, 'features': 'basic'},
        {'plan_id': 2, 'plan_name': 'Standard', 'mrr': 19.99, 'features': 'standard'},
        {'plan_id': 3, 'plan_name': 'Premium', 'mrr': 49.99, 'features': 'premium'},
        {'plan_id': 4, 'plan_name': 'Enterprise', 'mrr': 99.99, 'features': 'enterprise'}
    ]
    
    subscriptions = []
    for i in range(1, n + 1):
        customer = customers_df.sample(1).iloc[0]
        plan = random.choice(plans)
        
        start_date = datetime.strptime(customer['signup_date'], '%Y-%m-%d') + timedelta(days=random.randint(0, 30))
        
        # Determine if churned
        is_churned = random.random() < 0.25  # 25% churn rate
        
        if is_churned:
            # Churned after 1-12 months
            months_active = random.randint(1, 12)
            end_date = start_date + timedelta(days=months_active * 30)
            if end_date > END_DATE:
                end_date = None
                is_churned = False
        else:
            end_date = None
        
        subscription = {
            'subscription_id': i,
            'customer_id': customer['customer_id'],
            'plan_id': plan['plan_id'],
            'plan_name': plan['plan_name'],
            'mrr': plan['mrr'],
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d') if end_date else None,
            'status': 'churned' if is_churned else 'active',
            'billing_period': random.choice(['monthly', 'annual']),
            'created_at': start_date.strftime('%Y-%m-%d %H:%M:%S')
        }
        subscriptions.append(subscription)
    
    return pd.DataFrame(subscriptions)

def generate_events(subscriptions_df, n):
    """Generate customer event data"""
    print(f"Generating {n} events...")
    
    event_types = [
        'login', 'feature_usage', 'support_ticket', 'download', 
        'upload', 'share', 'invite', 'payment', 'profile_update',
        'settings_change', 'export_data', 'api_call'
    ]
    
    events = []
    for i in range(1, n + 1):
        subscription = subscriptions_df.sample(1).iloc[0]
        
        start = datetime.strptime(subscription['start_date'], '%Y-%m-%d')
        if subscription['end_date']:
            end = datetime.strptime(subscription['end_date'], '%Y-%m-%d')
        else:
            end = END_DATE
        
        # Generate event within subscription period
        event_date = start + timedelta(days=random.randint(0, (end - start).days))
        
        event = {
            'event_id': i,
            'customer_id': subscription['customer_id'],
            'subscription_id': subscription['subscription_id'],
            'event_type': random.choice(event_types),
            'event_date': event_date.strftime('%Y-%m-%d'),
            'event_value': round(random.uniform(0, 100), 2),
            'created_at': event_date.strftime('%Y-%m-%d %H:%M:%S')
        }
        events.append(event)
    
    return pd.DataFrame(events)

def create_database(db_path):
    """Create SQLite database and tables"""
    print(f"Creating database at {db_path}...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            country TEXT,
            signup_date DATE NOT NULL,
            age INTEGER,
            account_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create subscriptions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            subscription_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            plan_id INTEGER NOT NULL,
            plan_name TEXT NOT NULL,
            mrr REAL NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE,
            status TEXT NOT NULL,
            billing_period TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    ''')
    
    # Create events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            event_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            subscription_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            event_date DATE NOT NULL,
            event_value REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id)
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_customer_email ON customers(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_subscription_customer ON subscriptions(customer_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_subscription_status ON subscriptions(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_customer ON events(customer_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_date ON events(event_date)')
    
    conn.commit()
    return conn

def main():
    """Main execution function"""
    print("Starting churn data simulation...")
    
    # Generate data
    customers_df = generate_customers(NUM_CUSTOMERS)
    subscriptions_df = generate_subscriptions(customers_df, NUM_SUBSCRIPTIONS)
    events_df = generate_events(subscriptions_df, NUM_EVENTS)
    
    # Create database
    db_path = 'data/churn.db'
    conn = create_database(db_path)
    
    # Insert data
    print("Inserting customers...")
    customers_df.to_sql('customers', conn, if_exists='replace', index=False)
    
    print("Inserting subscriptions...")
    subscriptions_df.to_sql('subscriptions', conn, if_exists='replace', index=False)
    
    print("Inserting events...")
    events_df.to_sql('events', conn, if_exists='replace', index=False)
    
    # Verify data
    cursor = conn.cursor()
    print("\nDatabase Statistics:")
    total_customers = cursor.execute('SELECT COUNT(*) FROM customers').fetchone()[0]
    total_subscriptions = cursor.execute('SELECT COUNT(*) FROM subscriptions').fetchone()[0]
    active_subscriptions = cursor.execute('SELECT COUNT(*) FROM subscriptions WHERE status = "active"').fetchone()[0]
    churned_subscriptions = cursor.execute('SELECT COUNT(*) FROM subscriptions WHERE status = "churned"').fetchone()[0]
    total_events = cursor.execute('SELECT COUNT(*) FROM events').fetchone()[0]
    
    print(f"Total Customers: {total_customers}")
    print(f"Total Subscriptions: {total_subscriptions}")
    print(f"Active Subscriptions: {active_subscriptions}")
    print(f"Churned Subscriptions: {churned_subscriptions}")
    print(f"Total Events: {total_events}")
    
    conn.close()
    
    # Also save as CSV for reference
    print("\nSaving CSV files...")
    customers_df.to_csv('data/customers.csv', index=False)
    subscriptions_df.to_csv('data/subscriptions.csv', index=False)
    events_df.to_csv('data/events.csv', index=False)
    
    print(f"\n✓ Database created successfully at {db_path}")
    print("✓ CSV files saved in data/")

if __name__ == '__main__':
    main()
