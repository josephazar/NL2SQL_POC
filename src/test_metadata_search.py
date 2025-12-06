#!/usr/bin/env python3
"""Test metadata search"""

from metadata_ingestion import MetadataIngestion

ingestion = MetadataIngestion()

question = "What is the churn rate?"
print(f"Question: {question}\n")

tables = ingestion.search_tables(question, n_results=3)
print(f"Tables type: {type(tables)}")
print(f"Tables: {tables}\n")

queries = ingestion.search_queries(question, n_results=5)
print(f"Queries type: {type(queries)}")
print(f"Queries: {queries}\n")

context = {'tables': tables, 'queries': queries}
print(f"Context: {context}")
