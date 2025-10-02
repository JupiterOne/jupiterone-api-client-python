#!/usr/bin/env python3
"""
JupiterOne Python SDK - Integration Management Examples

This file demonstrates how to:
1. Create integration instances
2. Start synchronization jobs
3. Upload entities and relationships in batches
4. Manage integration jobs and events
5. Work with integration definitions
"""

import os
from jupiterone import JupiterOneClient

def setup_client():
    """Set up JupiterOne client with credentials."""
    return JupiterOneClient(
        account=os.getenv('JUPITERONE_ACCOUNT_ID'),
        token=os.getenv('JUPITERONE_API_TOKEN'),
        url=os.getenv('JUPITERONE_URL', 'https://graphql.us.jupiterone.io'),
        sync_url=os.getenv('JUPITERONE_SYNC_URL', 'https://api.us.jupiterone.io')
    )

def create_integration_instance_examples(j1):
    """Demonstrate integration instance creation."""
    
    print("=== Integration Instance Creation Examples ===\n")
    
    # 1. Basic integration instance creation
    print("1. Creating a basic integration instance:")
    basic_instance = j1.create_integration_instance(
        instance_name="AWS Production Account",
        instance_description="Production AWS account integration for security monitoring"
    )
    print(f"Created basic instance: {basic_instance['instance']['_id']}\n")
    
    # 2. Integration instance with resource group
    print("2. Creating integration instance with resource group:")
    resource_group_instance = j1.create_integration_instance(
        instance_name="AWS Development Account",
        instance_description="Development AWS account integration",
        resource_group_id="your-resource-group-id"  # Replace with actual ID
    )
    print(f"Created instance with resource group: {resource_group_instance['instance']['_id']}\n")
    
    # 3. Integration instance with custom definition
    print("3. Creating integration instance with custom definition:")
    custom_instance = j1.create_integration_instance(
        instance_name="Custom Integration",
        instance_description="Custom integration for internal systems",
        integration_definition_id="your-integration-definition-id",  # Replace with actual ID
        resource_group_id="your-resource-group-id"  # Replace with actual ID
    )
    print(f"Created custom instance: {custom_instance['instance']['_id']}\n")
    
    return basic_instance, resource_group_instance, custom_instance

def integration_definition_examples(j1):
    """Demonstrate working with integration definitions."""
    
    print("=== Integration Definition Examples ===\n")
    
    # 1. Get AWS integration definition details
    print("1. Getting AWS integration definition:")
    try:
        aws_details = j1.get_integration_definition_details(integration_type="aws")
        print(f"AWS Integration: {aws_details['definition']['name']}")
        print(f"Description: {aws_details['definition']['description']}")
        
        # Access configuration fields
        if 'configFields' in aws_details['definition']:
            print("AWS Configuration Fields:")
            for field in aws_details['definition']['configFields'][:5]:  # Show first 5
                print(f"  - {field['name']}: {field['type']}")
    except Exception as e:
        print(f"Error getting AWS definition: {e}")
    print()
    
    # 2. Get Azure integration definition details
    print("2. Getting Azure integration definition:")
    try:
        azure_details = j1.get_integration_definition_details(integration_type="azure")
        print(f"Azure Integration: {azure_details['definition']['name']}")
    except Exception as e:
        print(f"Error getting Azure definition: {e}")
    print()
    
    # 3. Get Google Cloud integration definition details
    print("3. Getting Google Cloud integration definition:")
    try:
        gcp_details = j1.get_integration_definition_details(integration_type="google_cloud")
        print(f"Google Cloud Integration: {gcp_details['definition']['name']}")
    except Exception as e:
        print(f"Error getting GCP definition: {e}")
    print()

def integration_instance_management_examples(j1, instance_id):
    """Demonstrate integration instance management."""
    
    print("=== Integration Instance Management Examples ===\n")
    
    # 1. Get integration instance details
    print("1. Getting integration instance details:")
    try:
        instance_details = j1.get_integration_instance_details(instance_id=instance_id)
        print(f"Instance: {instance_details['instance']['name']}")
        print(f"Description: {instance_details['instance']['description']}")
        print(f"Status: {instance_details['instance']['status']}")
        
        # Access configuration
        if 'config' in instance_details['instance']:
            print("Configuration:")
            for key, value in instance_details['instance']['config'].items():
                if key != 'password':  # Don't print sensitive data
                    print(f"  {key}: {value}")
        
        # Access recent jobs
        if 'recentJobs' in instance_details['instance']:
            print("Recent Jobs:")
            for job in instance_details['instance']['recentJobs'][:3]:  # Show first 3
                print(f"  Job ID: {job['_id']}")
                print(f"  Status: {job['status']}")
                print(f"  Started: {job.get('startedOn')}")
    except Exception as e:
        print(f"Error getting instance details: {e}")
    print()
    
    # 2. Fetch integration instances
    print("2. Fetching all integration instances:")
    try:
        instances = j1.fetch_integration_instances(definition_id="your-definition-id")  # Replace with actual ID
        print(f"Found {len(instances)} integration instances")
        for instance in instances[:3]:  # Show first 3
            print(f"  Instance ID: {instance['_id']}")
            print(f"  Name: {instance['name']}")
            print(f"  Status: {instance['status']}")
    except Exception as e:
        print(f"Error fetching instances: {e}")
    print()

def sync_job_examples(j1, instance_id):
    """Demonstrate synchronization job operations."""
    
    print("=== Synchronization Job Examples ===\n")
    
    # 1. Start sync job
    print("1. Starting synchronization job:")
    try:
        sync_job = j1.start_sync_job(
            instance_id=instance_id,
            sync_mode="PATCH",
            source="api"
        )
        job_id = sync_job['job']['_id']
        print(f"Started sync job: {job_id}")
        print(f"Status: {sync_job['job']['status']}")
    except Exception as e:
        print(f"Error starting sync job: {e}")
        job_id = None
    print()
    
    if job_id:
        # 2. Fetch integration jobs
        print("2. Fetching integration jobs:")
        try:
            jobs = j1.fetch_integration_jobs(instance_id=instance_id)
            print(f"Found {len(jobs)} jobs for instance")
            for job in jobs[:3]:  # Show first 3
                print(f"  Job ID: {job['_id']}")
                print(f"  Status: {job['status']}")
                print(f"  Started: {job.get('startedOn')}")
                print(f"  Completed: {job.get('completedOn')}")
        except Exception as e:
            print(f"Error fetching jobs: {e}")
        print()
        
        # 3. Fetch job events
        print("3. Fetching job events:")
        try:
            events = j1.fetch_integration_job_events(
                instance_id=instance_id,
                instance_job_id=job_id
            )
            print(f"Found {len(events)} events for job")
            for event in events[:5]:  # Show first 5
                print(f"  Event: {event.get('event')}")
                print(f"  Timestamp: {event.get('timestamp')}")
                print(f"  Message: {event.get('message')}")
        except Exception as e:
            print(f"Error fetching events: {e}")
        print()
        
        # 4. Finalize sync job
        print("4. Finalizing sync job:")
        try:
            finalize_result = j1.finalize_sync_job(instance_job_id=job_id)
            print(f"Finalized sync job: {finalize_result['job']['_id']}")
            
            # Check job status
            if finalize_result['job']['status'] == 'COMPLETED':
                print("Sync job completed successfully")
            elif finalize_result['job']['status'] == 'FAILED':
                print(f"Sync job failed: {finalize_result['job'].get('error', 'Unknown error')}")
        except Exception as e:
            print(f"Error finalizing job: {e}")
        print()

def batch_upload_examples(j1, job_id):
    """Demonstrate batch upload operations."""
    
    print("=== Batch Upload Examples ===\n")
    
    # 1. Upload entities batch
    print("1. Uploading entities batch:")
    entities_payload = [
        {
            "_key": "server-001",
            "_type": "aws_ec2_instance",
            "_class": "Host",
            "displayName": "web-server-001",
            "instanceId": "i-1234567890abcdef0",
            "instanceType": "t3.micro",
            "state": "running",
            "tag.Environment": "production",
            "tag.Team": "engineering"
        },
        {
            "_key": "server-002",
            "_type": "aws_ec2_instance",
            "_class": "Host",
            "displayName": "web-server-002",
            "instanceId": "i-0987654321fedcba0",
            "instanceType": "t3.small",
            "state": "running",
            "tag.Environment": "staging",
            "tag.Team": "engineering"
        },
        {
            "_key": "database-001",
            "_type": "aws_rds_instance",
            "_class": "Database",
            "displayName": "prod-database",
            "dbInstanceIdentifier": "prod-db",
            "engine": "postgres",
            "dbInstanceClass": "db.t3.micro",
            "tag.Environment": "production",
            "tag.Team": "data"
        }
    ]
    
    try:
        j1.upload_entities_batch_json(
            instance_job_id=job_id,
            entities_list=entities_payload
        )
        print(f"Uploaded {len(entities_payload)} entities successfully")
    except Exception as e:
        print(f"Error uploading entities: {e}")
    print()
    
    # 2. Upload relationships batch
    print("2. Uploading relationships batch:")
    relationships_payload = [
        {
            "_key": "server-001:aws_ec2_instance_connects_aws_rds_instance:database-001",
            "_class": "CONNECTS",
            "_type": "aws_ec2_instance_connects_aws_rds_instance",
            "_fromEntityKey": "server-001",
            "_toEntityKey": "database-001",
            "port": 5432,
            "protocol": "tcp",
            "encrypted": True
        },
        {
            "_key": "server-002:aws_ec2_instance_connects_aws_rds_instance:database-001",
            "_class": "CONNECTS",
            "_type": "aws_ec2_instance_connects_aws_rds_instance",
            "_fromEntityKey": "server-002",
            "_toEntityKey": "database-001",
            "port": 5432,
            "protocol": "tcp",
            "encrypted": True
        }
    ]
    
    try:
        j1.upload_relationships_batch_json(
            instance_job_id=job_id,
            relationships_list=relationships_payload
        )
        print(f"Uploaded {len(relationships_payload)} relationships successfully")
    except Exception as e:
        print(f"Error uploading relationships: {e}")
    print()
    
    # 3. Upload combined batch
    print("3. Uploading combined batch:")
    combined_payload = {
        "entities": [
            {
                "_key": "vpc-001",
                "_type": "aws_vpc",
                "_class": "Network",
                "displayName": "production-vpc",
                "vpcId": "vpc-12345678",
                "cidrBlock": "10.0.0.0/16",
                "state": "available",
                "tag.Environment": "production",
                "tag.Purpose": "web_servers"
            },
            {
                "_key": "subnet-001",
                "_type": "aws_subnet",
                "_class": "Network",
                "displayName": "public-subnet-1a",
                "subnetId": "subnet-12345678",
                "cidrBlock": "10.0.1.0/24",
                "availabilityZone": "us-east-1a",
                "state": "available"
            }
        ],
        "relationships": [
            {
                "_key": "vpc-001:aws_vpc_contains_aws_subnet:subnet-001",
                "_class": "CONTAINS",
                "_type": "aws_vpc_contains_aws_subnet",
                "_fromEntityKey": "vpc-001",
                "_toEntityKey": "subnet-001"
            },
            {
                "_key": "subnet-001:aws_subnet_contains_aws_ec2_instance:server-001",
                "_class": "CONTAINS",
                "_type": "aws_subnet_contains_aws_ec2_instance",
                "_fromEntityKey": "subnet-001",
                "_toEntityKey": "server-001"
            }
        ]
    }
    
    try:
        j1.upload_combined_batch_json(
            instance_job_id=job_id,
            combined_payload=combined_payload
        )
        print(f"Uploaded {len(combined_payload['entities'])} entities and {len(combined_payload['relationships'])} relationships successfully")
    except Exception as e:
        print(f"Error uploading combined batch: {e}")
    print()

def bulk_delete_example(j1, job_id):
    """Demonstrate bulk delete operations."""
    
    print("=== Bulk Delete Example ===\n")
    
    # Create entities to delete
    entities_to_delete = [
        {
            "_key": "delete-test-001",
            "_type": "test_delete_entity",
            "_class": "TestDeleteEntity",
            "displayName": "Test Delete Entity 1"
        },
        {
            "_key": "delete-test-002",
            "_type": "test_delete_entity",
            "_class": "TestDeleteEntity",
            "displayName": "Test Delete Entity 2"
        }
    ]
    
    try:
        # First upload the entities
        j1.upload_entities_batch_json(
            instance_job_id=job_id,
            entities_list=entities_to_delete
        )
        print("Uploaded entities for deletion test")
        
        # Then bulk delete them
        j1.bulk_delete_entities(
            instance_job_id=job_id,
            entities_list=entities_to_delete
        )
        print("Bulk delete completed successfully")
    except Exception as e:
        print(f"Error in bulk delete: {e}")
    print()

def main():
    """Main function to run all integration management examples."""
    
    print("JupiterOne Python SDK - Integration Management Examples")
    print("=" * 60)
    
    try:
        # Set up client
        j1 = setup_client()
        print("✓ Client setup successful\n")
        
        # Run examples
        basic_instance, resource_group_instance, custom_instance = create_integration_instance_examples(j1)
        
        # Integration definition examples
        integration_definition_examples(j1)
        
        # Integration instance management (using the basic instance)
        integration_instance_management_examples(j1, basic_instance['instance']['_id'])
        
        # Sync job examples (using the basic instance)
        sync_job_examples(j1, basic_instance['instance']['_id'])
        
        # Note: For batch upload examples, you would need a real job ID
        # These examples show the structure but won't run without a valid job
        print("=== Batch Upload Examples (Structure Only) ===\n")
        print("Note: These examples require a valid sync job ID to run")
        print("The structure is shown for reference\n")
        
        # Show batch upload structure
        print("Batch upload structure would include:")
        print("- Upload entities batch")
        print("- Upload relationships batch") 
        print("- Upload combined batch")
        print("- Bulk delete entities")
        print()
        
        print("✓ All integration management examples completed successfully!")
        print("\nNote: Some examples require valid integration definition IDs and resource group IDs")
        print("Replace placeholder values with actual IDs when testing")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nMake sure you have set the following environment variables:")
        print("- JUPITERONE_ACCOUNT_ID")
        print("- JUPITERONE_API_TOKEN")

if __name__ == "__main__":
    main() 