#!/usr/bin/env python3
"""
JupiterOne Python SDK - Client Setup and Query Examples

This file demonstrates how to:
1. Set up the JupiterOne client
2. Execute basic queries
3. Use pagination methods
4. Handle deferred responses for large datasets
"""

import os
import time
from jupiterone import JupiterOneClient

def setup_client():
    """Set up JupiterOne client with credentials."""
    
    # Method 1: Using environment variables (recommended for production)
    j1 = JupiterOneClient(
        account=os.getenv('JUPITERONE_ACCOUNT_ID'),
        token=os.getenv('JUPITERONE_API_TOKEN'),
        url=os.getenv('JUPITERONE_URL', 'https://graphql.us.jupiterone.io'),
        sync_url=os.getenv('JUPITERONE_SYNC_URL', 'https://api.us.jupiterone.io')
    )
    
    # Method 2: Direct configuration (for testing/development)
    # j1 = JupiterOneClient(
    #     account='your-account-id',
    #     token='your-api-token',
    #     url='https://graphql.us.jupiterone.io',
    #     sync_url='https://api.us.jupiterone.io'
    # )
    
    return j1

def basic_query_examples(j1):
    """Demonstrate basic query operations."""
    
    print("=== Basic Query Examples ===\n")
    
    # 1. Simple entity query
    print("1. Finding all hosts:")
    hosts = j1.query_v1(query='FIND Host LIMIT 10')
    print(f"Found {len(hosts)} hosts\n")
    
    # 2. Query with property filtering
    print("2. Finding Linux hosts:")
    linux_hosts = j1.query_v1(query='FIND Host WITH platform = "linux" LIMIT 5')
    print(f"Found {len(linux_hosts)} Linux hosts\n")
    
    # 3. Query with relationships
    print("3. Finding hosts with applications:")
    hosts_with_apps = j1.query_v1(
        query='FIND Host AS h THAT HAS Application AS a RETURN h.displayName, a.displayName LIMIT 5'
    )
    print(f"Found {len(hosts_with_apps)} host-application relationships\n")
    
    # 4. Tree query
    print("4. Tree query for host hierarchy:")
    tree_result = j1.query_v1(query='FIND Host RETURN TREE LIMIT 5')
    print(f"Tree query completed\n")
    
    # 5. Query with deleted entities
    print("5. Query including deleted entities:")
    all_hosts = j1.query_v1(query='FIND Host LIMIT 5', include_deleted=True)
    print(f"Found {len(all_hosts)} hosts (including deleted)\n")

def pagination_examples(j1):
    """Demonstrate different pagination methods."""
    
    print("=== Pagination Examples ===\n")
    
    # 1. Cursor-based pagination (recommended for large datasets)
    print("1. Cursor-based pagination:")
    cursor_result = j1._cursor_query(
        query="FIND (Device | Person)",
        max_workers=3  # Parallel processing
    )
    print(f"Cursor query found {len(cursor_result)} total results\n")
    
    # 2. Limit and skip pagination
    print("2. Limit and skip pagination:")
    limit_skip_result = j1._limit_and_skip_query(
        query="FIND User",
        skip=0,
        limit=100
    )
    print(f"Limit/skip query completed\n")
    
    # 3. Deferred response for very large datasets
    print("3. Deferred response for large datasets:")
    deferred_result = j1.query_with_deferred_response(
        query="FIND UnifiedDevice",
        polling_interval=30,  # seconds
        max_retries=10
    )
    print(f"Deferred response query completed with {len(deferred_result)} results\n")

def complex_query_examples(j1):
    """Demonstrate complex query patterns."""
    
    print("=== Complex Query Examples ===\n")
    
    # 1. Multi-step relationship traversal
    print("1. Multi-step relationship query:")
    complex_query = """
    FIND User AS u 
    THAT HAS AccessPolicy AS ap 
    THAT ALLOWS * AS resource 
    WHERE resource.tag.Environment = 'production'
    RETURN u.displayName, ap.displayName, resource.displayName
    LIMIT 10
    """
    complex_result = j1.query_v1(query=complex_query)
    print(f"Complex query found {len(complex_result)} results\n")
    
    # 2. Aggregation query
    print("2. Aggregation query:")
    agg_query = """
    FIND Host AS h 
    RETURN h.platform, count(h) 
    ORDER BY count(h) DESC 
    LIMIT 10
    """
    agg_result = j1.query_v1(query=agg_query)
    print(f"Aggregation query completed\n")
    
    # 3. Time-based query
    print("3. Time-based query:")
    time_query = """
    FIND Finding 
    WITH createdOn > date.now - 7 days 
    RETURN displayName, severity, createdOn 
    ORDER BY createdOn DESC 
    LIMIT 10
    """
    time_result = j1.query_v1(query=time_query)
    print(f"Time-based query found {len(time_result)} recent findings\n")

def natural_language_to_j1ql(j1):
    """Demonstrate natural language to J1QL conversion."""
    
    print("=== Natural Language to J1QL Examples ===\n")
    
    prompts = [
        "Find all AWS EC2 instances that are running and tagged as production",
        "Show me all databases that are not encrypted",
        "Find users who have admin access to production systems",
        "List all applications that haven't been updated in the last 30 days"
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"{i}. Prompt: {prompt}")
        try:
            result = j1.generate_j1ql(natural_language_prompt=prompt)
            print(f"   Generated J1QL: {result['j1ql']}")
        except Exception as e:
            print(f"   Error: {e}")
        print()

def main():
    """Main function to run all examples."""
    
    print("JupiterOne Python SDK - Client Setup and Query Examples")
    print("=" * 60)
    
    try:
        # Set up client
        j1 = setup_client()
        print("✓ Client setup successful\n")
        
        # Run examples
        basic_query_examples(j1)
        pagination_examples(j1)
        complex_query_examples(j1)
        natural_language_to_j1ql(j1)
        
        print("✓ All examples completed successfully!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nMake sure you have set the following environment variables:")
        print("- JUPITERONE_ACCOUNT_ID")
        print("- JUPITERONE_API_TOKEN")
        print("- JUPITERONE_URL (optional)")
        print("- JUPITERONE_SYNC_URL (optional)")

if __name__ == "__main__":
    main() 