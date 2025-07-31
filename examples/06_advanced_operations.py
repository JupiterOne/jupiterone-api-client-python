#!/usr/bin/env python3
"""
JupiterOne Python SDK - Advanced Operations Examples

This file demonstrates how to:
1. Perform bulk operations on entities and relationships
2. Fetch various types of data (properties, tags, raw data)
3. Use advanced query techniques
4. Handle data synchronization and management
5. Work with utility methods and helpers
"""

import os
import time
import json
from jupiterone import JupiterOneClient

def setup_client():
    """Set up JupiterOne client with credentials."""
    return JupiterOneClient(
        account=os.getenv('JUPITERONE_ACCOUNT_ID'),
        token=os.getenv('JUPITERONE_API_TOKEN'),
        url=os.getenv('JUPITERONE_URL', 'https://graphql.us.jupiterone.io'),
        sync_url=os.getenv('JUPITERONE_SYNC_URL', 'https://api.us.jupiterone.io')
    )

def bulk_operations_examples(j1):
    """Demonstrate bulk operations on entities and relationships."""
    
    print("=== Bulk Operations Examples ===\n")
    
    # 1. Bulk entity creation
    print("1. Bulk entity creation:")
    entities_to_create = [
        {
            "entity_key": "bulk-server-001",
            "entity_type": "bulk_test_server",
            "entity_class": "Host",
            "properties": {
                "displayName": "Bulk Test Server 1",
                "ipAddress": "192.168.1.10",
                "tag.Environment": "test",
                "tag.BulkTest": "true"
            }
        },
        {
            "entity_key": "bulk-server-002",
            "entity_type": "bulk_test_server",
            "entity_class": "Host",
            "properties": {
                "displayName": "Bulk Test Server 2",
                "ipAddress": "192.168.1.11",
                "tag.Environment": "test",
                "tag.BulkTest": "true"
            }
        },
        {
            "entity_key": "bulk-database-001",
            "entity_type": "bulk_test_database",
            "entity_class": "Database",
            "properties": {
                "displayName": "Bulk Test Database",
                "engine": "postgres",
                "version": "13.0",
                "tag.Environment": "test",
                "tag.BulkTest": "true"
            }
        }
    ]
    
    created_entities = []
    for entity_data in entities_to_create:
        try:
            entity = j1.create_entity(**entity_data)
            created_entities.append(entity['entity']['_id'])
            print(f"Created entity: {entity['entity']['_id']}")
        except Exception as e:
            print(f"Error creating entity: {e}")
    print()
    
    # 2. Bulk relationship creation
    print("2. Bulk relationship creation:")
    if len(created_entities) >= 2:
        relationships_to_create = [
            {
                "relationship_key": f"{created_entities[0]}:connects:{created_entities[2]}",
                "relationship_type": "host_connects_database",
                "relationship_class": "CONNECTS",
                "from_entity_id": created_entities[0],
                "to_entity_id": created_entities[2],
                "properties": {
                    "port": 5432,
                    "protocol": "tcp",
                    "encrypted": True
                }
            },
            {
                "relationship_key": f"{created_entities[1]}:connects:{created_entities[2]}",
                "relationship_type": "host_connects_database",
                "relationship_class": "CONNECTS",
                "from_entity_id": created_entities[1],
                "to_entity_id": created_entities[2],
                "properties": {
                    "port": 5432,
                    "protocol": "tcp",
                    "encrypted": True
                }
            }
        ]
        
        created_relationships = []
        for rel_data in relationships_to_create:
            try:
                relationship = j1.create_relationship(**rel_data)
                created_relationships.append(relationship['relationship']['_id'])
                print(f"Created relationship: {relationship['relationship']['_id']}")
            except Exception as e:
                print(f"Error creating relationship: {e}")
        print()
        
        # 3. Bulk entity updates
        print("3. Bulk entity updates:")
        for entity_id in created_entities:
            try:
                j1.update_entity(
                    entity_id=entity_id,
                    properties={
                        "lastUpdated": int(time.time()) * 1000,
                        "tag.BulkUpdated": "true",
                        "updateTimestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                )
                print(f"Updated entity: {entity_id}")
            except Exception as e:
                print(f"Error updating entity {entity_id}: {e}")
        print()
        
        # 4. Bulk relationship updates
        print("4. Bulk relationship updates:")
        for rel_id in created_relationships:
            try:
                j1.update_relationship(
                    relationship_id=rel_id,
                    properties={
                        "lastUpdated": int(time.time()) * 1000,
                        "tag.BulkUpdated": "true"
                    }
                )
                print(f"Updated relationship: {rel_id}")
            except Exception as e:
                print(f"Error updating relationship {rel_id}: {e}")
        print()
        
        # 5. Bulk deletion
        print("5. Bulk deletion:")
        # Delete relationships first
        for rel_id in created_relationships:
            try:
                j1.delete_relationship(relationship_id=rel_id)
                print(f"Deleted relationship: {rel_id}")
            except Exception as e:
                print(f"Error deleting relationship {rel_id}: {e}")
        
        # Then delete entities
        for entity_id in created_entities:
            try:
                j1.delete_entity(entity_id=entity_id)
                print(f"Deleted entity: {entity_id}")
            except Exception as e:
                print(f"Error deleting entity {entity_id}: {e}")
        print()

def data_fetching_examples(j1):
    """Demonstrate various data fetching operations."""
    
    print("=== Data Fetching Examples ===\n")
    
    # 1. Fetch all entity properties
    print("1. Fetching all entity properties:")
    try:
        properties = j1.fetch_all_entity_properties()
        print(f"Found {len(properties)} entity properties")
        print("Sample properties:", properties[:10])
    except Exception as e:
        print(f"Error fetching properties: {e}")
    print()
    
    # 2. Fetch all entity tags
    print("2. Fetching all entity tags:")
    try:
        tags = j1.fetch_all_entity_tags()
        print(f"Found {len(tags)} entity tags")
        print("Sample tags:", tags[:10])
    except Exception as e:
        print(f"Error fetching tags: {e}")
    print()
    
    # 3. Fetch entity raw data
    print("3. Fetching entity raw data:")
    try:
        # First, find an entity to get its ID
        entities = j1.query_v1(query='FIND Host LIMIT 1')
        if entities:
            entity_id = entities[0]['_id']
            raw_data = j1.fetch_entity_raw_data(entity_id=entity_id)
            print(f"Raw data keys: {list(raw_data.keys())}")
            
            # Access specific raw data sections
            for key in raw_data.keys():
                if isinstance(raw_data[key], dict):
                    print(f"  {key}: {len(raw_data[key])} items")
                else:
                    print(f"  {key}: {type(raw_data[key])}")
        else:
            print("No entities found to fetch raw data")
    except Exception as e:
        print(f"Error fetching raw data: {e}")
    print()

def advanced_query_examples(j1):
    """Demonstrate advanced query techniques."""
    
    print("=== Advanced Query Examples ===\n")
    
    # 1. Query with variables
    print("1. Query with variables:")
    try:
        variables = {
            "environment": "production",
            "severity": "HIGH"
        }
        
        query_with_vars = """
        FIND Finding 
        WITH severity = $severity 
        AND tag.Environment = $environment
        RETURN displayName, severity, createdOn
        ORDER BY createdOn DESC
        LIMIT 10
        """
        
        results = j1.query_v1(query=query_with_vars, variables=variables)
        print(f"Found {len(results)} findings with variables")
    except Exception as e:
        print(f"Error with variable query: {e}")
    print()
    
    # 2. Query with scope filters
    print("2. Query with scope filters:")
    try:
        scope_filters = [
            {
                "entityType": "aws_ec2_instance",
                "tag.Environment": "production"
            }
        ]
        
        scoped_query = "FIND Host WITH platform = 'linux' LIMIT 5"
        results = j1.query_v1(query=scoped_query, scope_filters=scope_filters)
        print(f"Found {len(results)} hosts with scope filters")
    except Exception as e:
        print(f"Error with scope filters: {e}")
    print()
    
    # 3. Query with flags
    print("3. Query with flags:")
    try:
        flags = {
            "includeDeleted": True,
            "deferredResponse": "DISABLED"
        }
        
        flagged_query = "FIND * WITH _type = 'aws_ec2_instance' LIMIT 5"
        results = j1.query_v1(query=flagged_query, flags=flags)
        print(f"Found {len(results)} entities with flags")
    except Exception as e:
        print(f"Error with flags: {e}")
    print()

def pagination_techniques_examples(j1):
    """Demonstrate different pagination techniques."""
    
    print("=== Pagination Techniques Examples ===\n")
    
    # 1. Cursor-based pagination with custom settings
    print("1. Cursor-based pagination with custom settings:")
    try:
        cursor_results = j1._cursor_query(
            query="FIND (Device | Person)",
            max_workers=5,  # Increase parallel processing
            include_deleted=False
        )
        print(f"Cursor query found {len(cursor_results)} total results")
    except Exception as e:
        print(f"Error with cursor pagination: {e}")
    print()
    
    # 2. Limit and skip pagination with custom values
    print("2. Limit and skip pagination with custom values:")
    try:
        limit_skip_results = j1._limit_and_skip_query(
            query="FIND User",
            skip=10,  # Skip first 10 results
            limit=50,  # Get next 50 results
            include_deleted=False
        )
        print(f"Limit/skip query completed with custom values")
    except Exception as e:
        print(f"Error with limit/skip pagination: {e}")
    print()
    
    # 3. Deferred response with custom polling
    print("3. Deferred response with custom polling:")
    try:
        deferred_results = j1.query_with_deferred_response(
            query="FIND UnifiedDevice",
            polling_interval=60,  # Poll every 60 seconds
            max_retries=5,  # Maximum 5 retries
            timeout=300  # 5 minute timeout
        )
        print(f"Deferred response query completed with {len(deferred_results)} results")
    except Exception as e:
        print(f"Error with deferred response: {e}")
    print()

def data_synchronization_examples(j1):
    """Demonstrate data synchronization operations."""
    
    print("=== Data Synchronization Examples ===\n")
    
    # 1. Create a test entity for sync operations
    print("1. Creating test entity for sync operations:")
    try:
        sync_entity = j1.create_entity(
            entity_key='sync-test-entity',
            entity_type='sync_test_entity',
            entity_class='SyncTestEntity',
            properties={
                'displayName': 'Sync Test Entity',
                'tag.SyncTest': 'true',
                'createdOn': int(time.time()) * 1000
            }
        )
        entity_id = sync_entity['entity']['_id']
        print(f"Created sync test entity: {entity_id}")
    except Exception as e:
        print(f"Error creating sync entity: {e}")
        entity_id = None
    print()
    
    if entity_id:
        # 2. Update entity with sync timestamp
        print("2. Updating entity with sync timestamp:")
        try:
            j1.update_entity(
                entity_id=entity_id,
                properties={
                    'lastSync': int(time.time()) * 1000,
                    'syncVersion': '1.0',
                    'tag.LastSync': time.strftime("%Y-%m-%d %H:%M:%S")
                }
            )
            print("Updated entity with sync information")
        except Exception as e:
            print(f"Error updating sync entity: {e}")
        print()
        
        # 3. Query to verify sync
        print("3. Querying to verify sync:")
        try:
            sync_results = j1.query_v1(
                query=f'FIND * WITH _id = "{entity_id}"'
            )
            if sync_results:
                entity = sync_results[0]
                print(f"Found entity: {entity['displayName']}")
                print(f"Last sync: {entity.get('lastSync')}")
                print(f"Sync version: {entity.get('syncVersion')}")
        except Exception as e:
            print(f"Error querying sync entity: {e}")
        print()
        
        # 4. Clean up sync entity
        print("4. Cleaning up sync entity:")
        try:
            j1.delete_entity(entity_id=entity_id)
            print("Deleted sync test entity")
        except Exception as e:
            print(f"Error deleting sync entity: {e}")
        print()

def utility_methods_examples(j1):
    """Demonstrate utility methods and helpers."""
    
    print("=== Utility Methods Examples ===\n")
    
    # 1. Generate J1QL from natural language
    print("1. Generating J1QL from natural language:")
    natural_queries = [
        "Find all AWS EC2 instances that are running",
        "Show me all databases that are not encrypted",
        "Find users who have admin access",
        "List all applications in production environment"
    ]
    
    for query in natural_queries:
        try:
            result = j1.generate_j1ql(natural_language_prompt=query)
            print(f"Natural: {query}")
            print(f"J1QL: {result['j1ql']}")
            print()
        except Exception as e:
            print(f"Error generating J1QL for '{query}': {e}")
    
    # 2. Test connection
    print("2. Testing connection:")
    try:
        # This would typically be a method to test the connection
        # For now, we'll just try a simple query
        test_result = j1.query_v1(query="FIND * LIMIT 1")
        print("Connection test successful")
    except Exception as e:
        print(f"Connection test failed: {e}")
    print()

def error_handling_examples(j1):
    """Demonstrate error handling patterns."""
    
    print("=== Error Handling Examples ===\n")
    
    # 1. Handle API errors
    print("1. Handling API errors:")
    try:
        # Try to query with invalid syntax
        j1.query_v1(query="INVALID QUERY SYNTAX")
    except Exception as e:
        print(f"Caught API error: {type(e).__name__}: {e}")
    print()
    
    # 2. Handle missing entities
    print("2. Handling missing entities:")
    try:
        # Try to update a non-existent entity
        j1.update_entity(
            entity_id="non-existent-id",
            properties={"test": "value"}
        )
    except Exception as e:
        print(f"Caught missing entity error: {type(e).__name__}: {e}")
    print()
    
    # 3. Handle rate limiting
    print("3. Handling rate limiting:")
    try:
        # Make multiple rapid requests to test rate limiting
        for i in range(10):
            j1.query_v1(query="FIND * LIMIT 1")
            time.sleep(0.1)  # Small delay
        print("Rate limiting test completed")
    except Exception as e:
        print(f"Caught rate limiting error: {type(e).__name__}: {e}")
    print()

def performance_optimization_examples(j1):
    """Demonstrate performance optimization techniques."""
    
    print("=== Performance Optimization Examples ===\n")
    
    # 1. Batch operations for better performance
    print("1. Batch operations for better performance:")
    batch_entities = []
    for i in range(5):
        batch_entities.append({
            "entity_key": f"batch-{i:03d}",
            "entity_type": "batch_test_entity",
            "entity_class": "BatchTestEntity",
            "properties": {
                "displayName": f"Batch Entity {i}",
                "index": i,
                "tag.BatchTest": "true"
            }
        })
    
    # Create entities in batch
    created_batch_entities = []
    for entity_data in batch_entities:
        try:
            entity = j1.create_entity(**entity_data)
            created_batch_entities.append(entity['entity']['_id'])
        except Exception as e:
            print(f"Error creating batch entity: {e}")
    
    print(f"Created {len(created_batch_entities)} batch entities")
    
    # Clean up batch entities
    for entity_id in created_batch_entities:
        try:
            j1.delete_entity(entity_id=entity_id)
        except Exception as e:
            print(f"Error deleting batch entity {entity_id}: {e}")
    
    print("Cleaned up batch entities")
    print()
    
    # 2. Optimized queries
    print("2. Optimized queries:")
    try:
        # Use specific entity types instead of wildcards
        optimized_query = "FIND aws_ec2_instance WITH state = 'running' LIMIT 10"
        results = j1.query_v1(query=optimized_query)
        print(f"Optimized query found {len(results)} results")
    except Exception as e:
        print(f"Error with optimized query: {e}")
    print()

def main():
    """Main function to run all advanced operations examples."""
    
    print("JupiterOne Python SDK - Advanced Operations Examples")
    print("=" * 60)
    
    try:
        # Set up client
        j1 = setup_client()
        print("✓ Client setup successful\n")
        
        # Run examples
        bulk_operations_examples(j1)
        data_fetching_examples(j1)
        advanced_query_examples(j1)
        pagination_techniques_examples(j1)
        data_synchronization_examples(j1)
        utility_methods_examples(j1)
        error_handling_examples(j1)
        performance_optimization_examples(j1)
        
        print("✓ All advanced operations examples completed successfully!")
        print("\nNote: Some examples may require specific data or permissions")
        print("Adjust queries and parameters based on your JupiterOne environment")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nMake sure you have set the following environment variables:")
        print("- JUPITERONE_ACCOUNT_ID")
        print("- JUPITERONE_API_TOKEN")

if __name__ == "__main__":
    main() 