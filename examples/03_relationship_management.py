#!/usr/bin/env python3
"""
JupiterOne Python SDK - Relationship Management Examples

This file demonstrates how to:
1. Create relationships with various properties
2. Update existing relationships
3. Delete relationships
4. Work with complex relationship scenarios
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

def create_test_entities(j1):
    """Create test entities for relationship examples."""
    
    print("Creating test entities for relationship examples...")
    
    # Create source entity
    source_entity = j1.create_entity(
        entity_key='relationship-test-source',
        entity_type='test_source_entity',
        entity_class='TestSourceEntity',
        properties={
            'displayName': 'Test Source Entity',
            'tag.Test': 'true'
        }
    )
    
    # Create target entity
    target_entity = j1.create_entity(
        entity_key='relationship-test-target',
        entity_type='test_target_entity',
        entity_class='TestTargetEntity',
        properties={
            'displayName': 'Test Target Entity',
            'tag.Test': 'true'
        }
    )
    
    print(f"Created source entity: {source_entity['entity']['_id']}")
    print(f"Created target entity: {target_entity['entity']['_id']}\n")
    
    return source_entity['entity']['_id'], target_entity['entity']['_id']

def create_relationship_examples(j1, from_entity_id, to_entity_id):
    """Demonstrate relationship creation with various property types."""
    
    print("=== Relationship Creation Examples ===\n")
    
    # 1. Basic relationship creation
    print("1. Creating a basic relationship:")
    basic_relationship = j1.create_relationship(
        relationship_key=f'{from_entity_id}:basic_connects:{to_entity_id}',
        relationship_type='basic_connects',
        relationship_class='CONNECTS',
        from_entity_id=from_entity_id,
        to_entity_id=to_entity_id
    )
    print(f"Created basic relationship: {basic_relationship['relationship']['_id']}\n")
    
    # 2. Relationship with properties
    print("2. Creating a relationship with properties:")
    relationship_with_props = j1.create_relationship(
        relationship_key=f'{from_entity_id}:user_accesses_application:{to_entity_id}',
        relationship_type='user_accesses_application',
        relationship_class='ACCESSES',
        from_entity_id=from_entity_id,
        to_entity_id=to_entity_id,
        properties={
            'accessLevel': 'read',
            'grantedOn': int(time.time()) * 1000,
            'grantedBy': 'admin@company.com',
            'permissions': ['read', 'execute']
        }
    )
    print(f"Created relationship with properties: {relationship_with_props['relationship']['_id']}\n")
    
    # 3. Relationship with complex properties
    print("3. Creating a relationship with complex properties:")
    complex_relationship = j1.create_relationship(
        relationship_key=f'{from_entity_id}:host_installed_software:{to_entity_id}',
        relationship_type='host_installed_software',
        relationship_class='INSTALLED',
        from_entity_id=from_entity_id,
        to_entity_id=to_entity_id,
        properties={
            'installedOn': int(time.time()) * 1000,
            'version': '2.1.0',
            'installPath': '/usr/local/bin/software',
            'permissions': ['read', 'execute'],
            'metadata': {
                'installer': 'package_manager',
                'verified': True,
                'checksum': 'sha256:abc123...'
            },
            'tag.InstallationType': 'automated',
            'tag.Verified': 'true'
        }
    )
    print(f"Created complex relationship: {complex_relationship['relationship']['_id']}\n")
    
    return basic_relationship, relationship_with_props, complex_relationship

def update_relationship_examples(j1, relationship_id):
    """Demonstrate relationship update operations."""
    
    print("=== Relationship Update Examples ===\n")
    
    # 1. Basic property update
    print("1. Updating basic relationship properties:")
    basic_update = j1.update_relationship(
        relationship_id=relationship_id,
        properties={
            'accessLevel': 'write',
            'lastModified': int(time.time()) * 1000
        }
    )
    print(f"Updated relationship: {basic_update['relationship']['_id']}\n")
    
    # 2. Update with complex properties
    print("2. Updating with complex properties:")
    complex_update = j1.update_relationship(
        relationship_id=relationship_id,
        properties={
            'accessLevel': 'admin',
            'lastModified': int(time.time()) * 1000,
            'modifiedBy': 'security_team',
            'expiresOn': int(time.time() + 86400) * 1000,  # 24 hours from now
            'auditLog': {
                'previousLevel': 'write',
                'reason': 'promotion_requested',
                'approvedBy': 'security_manager'
            }
        }
    )
    print(f"Updated with complex properties\n")
    
    # 3. Update with tags
    print("3. Updating relationship tags:")
    tag_update = j1.update_relationship(
        relationship_id=relationship_id,
        properties={
            'tag.Status': 'active',
            'tag.Priority': 'high',
            'tag.ReviewRequired': 'true',
            'tag.LastReview': '2024-01-01'
        }
    )
    print(f"Updated relationship tags\n")

def delete_relationship_examples(j1, relationship_id):
    """Demonstrate relationship deletion."""
    
    print("=== Relationship Deletion Examples ===\n")
    
    # 1. Basic deletion
    print("1. Deleting a relationship:")
    delete_result = j1.delete_relationship(relationship_id=relationship_id)
    print(f"Deleted relationship: {delete_result['relationship']['_id']}\n")
    
    # 2. Deletion with timestamp
    print("2. Deleting with specific timestamp:")
    timestamp_delete = j1.delete_relationship(
        relationship_id=relationship_id,
        timestamp=int(time.time()) * 1000
    )
    print(f"Deleted with timestamp\n")

def relationship_lifecycle_example(j1, from_entity_id, to_entity_id):
    """Demonstrate complete relationship lifecycle."""
    
    print("=== Complete Relationship Lifecycle Example ===\n")
    
    # 1. Create relationship
    print("1. Creating lifecycle test relationship:")
    relationship = j1.create_relationship(
        relationship_key=f'{from_entity_id}:lifecycle_test:{to_entity_id}',
        relationship_type='lifecycle_test',
        relationship_class='TESTRELATIONSHIP',
        from_entity_id=from_entity_id,
        to_entity_id=to_entity_id,
        properties={
            'status': 'active',
            'createdOn': int(time.time()) * 1000
        }
    )
    relationship_id = relationship['relationship']['_id']
    print(f"Created: {relationship_id}")
    
    # 2. Update relationship
    print("2. Updating relationship:")
    j1.update_relationship(
        relationship_id=relationship_id,
        properties={
            'status': 'updated',
            'lastModified': int(time.time()) * 1000
        }
    )
    print("Updated successfully")
    
    # 3. Query to verify
    print("3. Querying to verify update:")
    result = j1.query_v1(query=f'FIND * WITH _id = "{relationship_id}"')
    if result:
        print(f"Found relationship: {result[0]['_type']}")
        print(f"Status: {result[0].get('status')}")
    
    # 4. Delete relationship
    print("4. Deleting relationship:")
    j1.delete_relationship(relationship_id=relationship_id)
    print("Deleted successfully")
    
    # 5. Verify deletion
    print("5. Verifying deletion:")
    result = j1.query_v1(query=f'FIND * WITH _id = "{relationship_id}"')
    if not result:
        print("Relationship successfully deleted")
    print()

def network_relationship_example(j1):
    """Demonstrate network-style relationships."""
    
    print("=== Network Relationship Example ===\n")
    
    # Create network entities
    entities = []
    for i in range(3):
        entity = j1.create_entity(
            entity_key=f'network-node-{i:03d}',
            entity_type='network_node',
            entity_class='NetworkNode',
            properties={
                'displayName': f'Network Node {i}',
                'ipAddress': f'192.168.1.{i+1}',
                'tag.Network': 'test_network'
            }
        )
        entities.append(entity['entity']['_id'])
        print(f"Created network node {i}: {entity['entity']['_id']}")
    
    # Create network connections
    relationships = []
    for i in range(len(entities) - 1):
        relationship = j1.create_relationship(
            relationship_key=f'{entities[i]}:network_connects:{entities[i+1]}',
            relationship_type='network_connects',
            relationship_class='CONNECTS',
            from_entity_id=entities[i],
            to_entity_id=entities[i+1],
            properties={
                'protocol': 'tcp',
                'port': 80 + i,
                'encrypted': True,
                'bandwidth': '100Mbps'
            }
        )
        relationships.append(relationship['relationship']['_id'])
        print(f"Created connection {i}: {relationship['relationship']['_id']}")
    
    print(f"Created {len(entities)} nodes with {len(relationships)} connections")
    
    # Clean up
    for relationship_id in relationships:
        j1.delete_relationship(relationship_id=relationship_id)
    for entity_id in entities:
        j1.delete_entity(entity_id=entity_id)
    
    print("Cleaned up network example")
    print()

def access_control_relationship_example(j1):
    """Demonstrate access control relationships."""
    
    print("=== Access Control Relationship Example ===\n")
    
    # Create user and resource entities
    user_entity = j1.create_entity(
        entity_key='test-user-001',
        entity_type='test_user',
        entity_class='User',
        properties={
            'displayName': 'Test User',
            'email': 'test@company.com',
            'role': 'developer'
        }
    )
    
    resource_entity = j1.create_entity(
        entity_key='test-resource-001',
        entity_type='test_resource',
        entity_class='Resource',
        properties={
            'displayName': 'Test Resource',
            'type': 'database',
            'environment': 'development'
        }
    )
    
    # Create access relationship
    access_relationship = j1.create_relationship(
        relationship_key=f'{user_entity["entity"]["_id"]}:user_accesses_resource:{resource_entity["entity"]["_id"]}',
        relationship_type='user_accesses_resource',
        relationship_class='ACCESSES',
        from_entity_id=user_entity['entity']['_id'],
        to_entity_id=resource_entity['entity']['_id'],
        properties={
            'accessLevel': 'read',
            'grantedOn': int(time.time()) * 1000,
            'grantedBy': 'admin@company.com',
            'expiresOn': int(time.time() + 30*24*60*60) * 1000,  # 30 days
            'reason': 'development_work',
            'tag.AccessType': 'temporary',
            'tag.ReviewRequired': 'true'
        }
    )
    
    print(f"Created access control relationship: {access_relationship['relationship']['_id']}")
    
    # Update access level
    j1.update_relationship(
        relationship_id=access_relationship['relationship']['_id'],
        properties={
            'accessLevel': 'write',
            'lastModified': int(time.time()) * 1000,
            'modifiedBy': 'security_team',
            'reason': 'promotion_approved'
        }
    )
    print("Updated access level to write")
    
    # Clean up
    j1.delete_relationship(relationship_id=access_relationship['relationship']['_id'])
    j1.delete_entity(entity_id=user_entity['entity']['_id'])
    j1.delete_entity(entity_id=resource_entity['entity']['_id'])
    
    print("Cleaned up access control example")
    print()

def main():
    """Main function to run all relationship management examples."""
    
    print("JupiterOne Python SDK - Relationship Management Examples")
    print("=" * 60)
    
    try:
        # Set up client
        j1 = setup_client()
        print("✓ Client setup successful\n")
        
        # Create test entities
        from_entity_id, to_entity_id = create_test_entities(j1)
        
        # Run examples
        basic_rel, props_rel, complex_rel = create_relationship_examples(j1, from_entity_id, to_entity_id)
        
        # Update examples (using the relationship with properties)
        update_relationship_examples(j1, props_rel['relationship']['_id'])
        
        # Complete lifecycle example
        relationship_lifecycle_example(j1, from_entity_id, to_entity_id)
        
        # Network relationship example
        network_relationship_example(j1)
        
        # Access control example
        access_control_relationship_example(j1)
        
        # Clean up created entities and relationships
        print("=== Cleanup ===\n")
        relationships_to_clean = [basic_rel, props_rel, complex_rel]
        for rel in relationships_to_clean:
            try:
                j1.delete_relationship(relationship_id=rel['relationship']['_id'])
                print(f"Cleaned up relationship: {rel['relationship']['_id']}")
            except:
                pass
        
        # Clean up entities
        try:
            j1.delete_entity(entity_id=from_entity_id)
            j1.delete_entity(entity_id=to_entity_id)
            print(f"Cleaned up entities")
        except:
            pass
        
        print("\n✓ All relationship management examples completed successfully!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nMake sure you have set the following environment variables:")
        print("- JUPITERONE_ACCOUNT_ID")
        print("- JUPITERONE_API_TOKEN")

if __name__ == "__main__":
    main() 