# Churn Rate Query Issue

## Problem
The second sub-query "What is the churn rate per country?" is still returning 0 rows even after adding example queries to metadata.

## Generated SQL (Still Wrong)
```sql
SELECT 
    c.country AS country, 
    COUNT(s.account_id) AS total_accounts, 
    SUM(CASE WHEN o.is_churn = 1 THEN 1 ELSE 0 END) AS churned_accounts,
    (SUM(CASE WHEN o.is_churn = 1 THEN 1 ELSE 0 END) * 1.0 / COUNT(s.account_id)) * 100 AS churn_rate
FROM 
    subscription s
JOIN 
    observation o ON s.account_id = o.account_id
JOIN 
    account c ON s.account_id = c.account_id
WHERE 
    o.observation_date = (SELECT MAX(observation_date) FROM observation WHERE account_id = o.account_id)
GROUP BY 
    c.country
ORDER BY 
    churn_rate DESC
LIMIT 100;
```

**Issue**: The WHERE clause with subquery is likely causing the problem. The LLM is still not using the example query we provided.

## Correct SQL (That Works)
```sql
SELECT 
    a.country,
    COUNT(CASE WHEN o.is_churn = 1 THEN 1 END) AS churned_accounts,
    COUNT(o.account_id) AS total_observations,
    ROUND(COUNT(CASE WHEN o.is_churn = 1 THEN 1 END) * 100.0 / COUNT(o.account_id), 2) AS churn_rate
FROM account a
JOIN observation o ON a.id = o.account_id
GROUP BY a.country
ORDER BY churn_rate DESC
LIMIT 100;
```

**Results**:
- Canada: 26.26%
- UK: 24.57%
- USA: 24.57%
- France: 23.39%
- Germany: 23.24%

## Root Cause
The semantic search is not returning the "churn rate by country" example query with high enough relevance, so the LLM is generating its own (incorrect) SQL.

## Solution Needed
1. Improve the semantic search relevance
2. Add more specific metadata to guide the LLM
3. Possibly add a SQL validation/correction step
4. Consider using few-shot examples in the prompt itself
