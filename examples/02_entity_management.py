#!/usr/bin/env python3
"""
JupiterOne Python SDK - Entity Management Examples

This file demonstrates how to:
1. Create entities with various properties
2. Update existing entities
3. Delete entities
4. Fetch entity properties and tags
5. Access entity raw data
"""

import os
import time
from jupiterone import JupiterOneClient

def setup_client():
    """Set up JupiterOne client with credentials."""
    return JupiterOneClient(
        account=os.getenv('JUPITERONE_ACCOUNT_ID'),
        token=os.getenv('JUPITERONE_API_TOKEN'),
        url=os.getenv('JUPITERONE_URL', 'https://graphql.us.jupiterone.io'),
        sync_url=os.getenv('JUPITERONE_SYNC_URL', 'https://api.us.jupiterone.io')
    )

def create_entity_examples(j1):
    """Demonstrate entity creation with various property types."""
    
    print("=== Entity Creation Examples ===\n")
    
    # 1. Basic entity creation
    print("1. Creating a basic application entity:")
    basic_entity = j1.create_entity(
        entity_key='my-app-001',
        entity_type='my_application',
        entity_class='Application',
        properties={
            'displayName': 'My Web Application',
            'version': '1.0.0',
            'status': 'active'
        }
    )
    print(f"Created entity: {basic_entity['entity']['_id']}\n")
    
    # 2. Entity with tags
    print("2. Creating an entity with tags:")
    tagged_entity = j1.create_entity(
        entity_key='prod-server-001',
        entity_type='aws_ec2_instance',
        entity_class='Host',
        properties={
            'displayName': 'Production Web Server',
            'instanceId': 'i-1234567890abcdef0',
            'instanceType': 't3.micro',
            'state': 'running',
            'tag.Environment': 'production',
            'tag.Team': 'engineering',
            'tag.Purpose': 'web_server'
        }
    )
    print(f"Created tagged entity: {tagged_entity['entity']['_id']}\n")
    
    # 3. Entity with complex properties
    print("3. Creating an entity with complex properties:")
    complex_entity = j1.create_entity(
        entity_key='database-001',
        entity_type='aws_rds_instance',
        entity_class='Database',
        properties={
            'displayName': 'Production Database',
            'dbInstanceIdentifier': 'prod-db',
            'engine': 'postgres',
            'dbInstanceClass': 'db.t3.micro',
            'allocatedStorage': 20,
            'encrypted': True,
            'backupRetentionPeriod': 7,
            'tag.Environment': 'production',
            'tag.Team': 'data',
            'metadata': {
                'createdBy': 'terraform',
                'lastBackup': '2024-01-01T00:00:00Z',
                'maintenanceWindow': 'sun:03:00-sun:04:00'
            }
        },
        timestamp=int(time.time()) * 1000
    )
    print(f"Created complex entity: {complex_entity['entity']['_id']}\n")
    
    return basic_entity, tagged_entity, complex_entity

def update_entity_examples(j1, entity_id):
    """Demonstrate entity update operations."""
    
    print("=== Entity Update Examples ===\n")
    
    # 1. Basic property update
    print("1. Updating basic properties:")
    update_result = j1.update_entity(
        entity_id=entity_id,
        properties={
            'status': 'maintenance',
            'lastUpdated': int(time.time()) * 1000
        }
    )
    print(f"Updated entity: {update_result['entity']['_id']}\n")
    
    # 2. Update with tags
    print("2. Updating entity tags:")
    tag_update = j1.update_entity(
        entity_id=entity_id,
        properties={
            'tag.Status': 'maintenance',
            'tag.LastMaintenance': '2024-01-01',
            'tag.MaintenanceReason': 'security_patches'
        }
    )
    print(f"Updated entity tags\n")
    
    # 3. Update with complex properties
    print("3. Updating with complex properties:")
    complex_update = j1.update_entity(
        entity_id=entity_id,
        properties={
            'isActive': False,
            'maintenanceWindow': {
                'start': '2024-01-01T00:00:00Z',
                'end': '2024-01-01T04:00:00Z',
                'reason': 'scheduled_maintenance'
            },
            'metadata': {
                'maintenancePerformedBy': 'admin@company.com',
                'maintenanceType': 'security_patches',
                'estimatedDuration': '4 hours'
            }
        }
    )
    print(f"Updated with complex properties\n")

def delete_entity_examples(j1, entity_id):
    """Demonstrate entity deletion."""
    
    print("=== Entity Deletion Examples ===\n")
    
    # 1. Basic deletion
    print("1. Deleting an entity:")
    delete_result = j1.delete_entity(entity_id=entity_id)
    print(f"Deleted entity: {delete_result['entity']['_id']}\n")
    
    # 2. Deletion with timestamp
    print("2. Deleting with specific timestamp:")
    timestamp_delete = j1.delete_entity(
        entity_id=entity_id,
        timestamp=int(time.time()) * 1000
    )
    print(f"Deleted with timestamp\n")

def fetch_entity_data_examples(j1):
    """Demonstrate fetching entity-related data."""
    
    print("=== Entity Data Fetching Examples ===\n")
    
    # 1. Fetch all entity properties
    print("1. Fetching all entity properties:")
    properties = j1.fetch_all_entity_properties()
    print(f"Found {len(properties)} entity properties")
    print("Sample properties:", properties[:10])
    print()
    
    # 2. Fetch all entity tags
    print("2. Fetching all entity tags:")
    tags = j1.fetch_all_entity_tags()
    print(f"Found {len(tags)} entity tags")
    print("Sample tags:", tags[:10])
    print()
    
    # 3. Fetch entity raw data (if entity exists)
    print("3. Fetching entity raw data:")
    try:
        # First, find an entity to get its ID
        entities = j1.query_v1(query='FIND Host LIMIT 1')
        if entities:
            entity_id = entities[0]['_id']
            raw_data = j1.fetch_entity_raw_data(entity_id=entity_id)
            print(f"Raw data keys: {list(raw_data.keys())}")
            
            # Access specific raw data sections
            if 'aws' in raw_data:
                print("AWS data available")
            if 'azure' in raw_data:
                print("Azure data available")
        else:
            print("No entities found to fetch raw data")
    except Exception as e:
        print(f"Error fetching raw data: {e}")
    print()

def entity_lifecycle_example(j1):
    """Demonstrate complete entity lifecycle."""
    
    print("=== Complete Entity Lifecycle Example ===\n")
    
    # 1. Create entity
    print("1. Creating lifecycle test entity:")
    entity = j1.create_entity(
        entity_key='lifecycle-test-001',
        entity_type='test_entity',
        entity_class='TestEntity',
        properties={
            'displayName': 'Lifecycle Test Entity',
            'status': 'active',
            'tag.Test': 'true'
        }
    )
    entity_id = entity['entity']['_id']
    print(f"Created: {entity_id}")
    
    # 2. Update entity
    print("2. Updating entity:")
    j1.update_entity(
        entity_id=entity_id,
        properties={
            'status': 'updated',
            'lastModified': int(time.time()) * 1000
        }
    )
    print("Updated successfully")
    
    # 3. Query to verify
    print("3. Querying to verify update:")
    result = j1.query_v1(query=f'FIND * WITH _id = "{entity_id}"')
    if result:
        print(f"Found entity: {result[0]['displayName']}")
        print(f"Status: {result[0].get('status')}")
    
    # 4. Delete entity
    print("4. Deleting entity:")
    j1.delete_entity(entity_id=entity_id)
    print("Deleted successfully")
    
    # 5. Verify deletion
    print("5. Verifying deletion:")
    result = j1.query_v1(query=f'FIND * WITH _id = "{entity_id}"')
    if not result:
        print("Entity successfully deleted")
    print()

def bulk_entity_operations(j1):
    """Demonstrate bulk entity operations."""
    
    print("=== Bulk Entity Operations Example ===\n")
    
    # Create multiple entities
    entities = []
    for i in range(3):
        entity = j1.create_entity(
            entity_key=f'bulk-test-{i:03d}',
            entity_type='bulk_test_entity',
            entity_class='BulkTestEntity',
            properties={
                'displayName': f'Bulk Test Entity {i}',
                'index': i,
                'tag.BulkTest': 'true'
            }
        )
        entities.append(entity['entity']['_id'])
        print(f"Created entity {i}: {entity['entity']['_id']}")
    
    print(f"Created {len(entities)} entities")
    
    # Update all entities
    for i, entity_id in enumerate(entities):
        j1.update_entity(
            entity_id=entity_id,
            properties={
                'status': 'bulk_updated',
                'updateIndex': i
            }
        )
    print("Updated all entities")
    
    # Delete all entities
    for entity_id in entities:
        j1.delete_entity(entity_id=entity_id)
    print("Deleted all entities")
    print()

def main():
    """Main function to run all entity management examples."""
    
    print("JupiterOne Python SDK - Entity Management Examples")
    print("=" * 60)
    
    try:
        # Set up client
        j1 = setup_client()
        print("✓ Client setup successful\n")
        
        # Run examples
        basic_entity, tagged_entity, complex_entity = create_entity_examples(j1)
        
        # Update examples (using the basic entity)
        update_entity_examples(j1, basic_entity['entity']['_id'])
        
        # Fetch data examples
        fetch_entity_data_examples(j1)
        
        # Complete lifecycle example
        entity_lifecycle_example(j1)
        
        # Bulk operations
        bulk_entity_operations(j1)
        
        # Clean up created entities
        print("=== Cleanup ===\n")
        for entity in [basic_entity, tagged_entity, complex_entity]:
            try:
                j1.delete_entity(entity_id=entity['entity']['_id'])
                print(f"Cleaned up: {entity['entity']['_id']}")
            except:
                pass
        
        print("\n✓ All entity management examples completed successfully!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nMake sure you have set the following environment variables:")
        print("- JUPITERONE_ACCOUNT_ID")
        print("- JUPITERONE_API_TOKEN")

if __name__ == "__main__":
    main() 