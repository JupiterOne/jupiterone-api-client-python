#!/usr/bin/env python3
"""
JupiterOne Sync Job Workflow Example

This example demonstrates the core synchronization job workflow:
1. Start a sync job
2. Upload entities batch
3. Finalize the sync job

This is a standalone script that can be run independently to test
the sync job functionality.

Note: This example uses PATCH sync mode, which is suitable for entity-only
uploads. If you need to upload relationships, use DIFF sync mode instead.
See: https://docs.jupiterone.io/reference/pipeline-upgrade#patch-sync-jobs-cannot-target-relationships
"""

import os
import sys
from jupiterone.client import JupiterOneClient

def main():
    """Main function to demonstrate sync job workflow."""
    
    # Initialize JupiterOne client
    # You can set these as environment variables or replace with your values
    api_token = os.getenv('JUPITERONE_API_TOKEN')
    account_id = os.getenv('JUPITERONE_ACCOUNT_ID')
    
    if not api_token or not account_id:
        print("Error: Please set JUPITERONE_API_TOKEN and JUPITERONE_ACCOUNT_ID environment variables")
        print("Example:")
        print("  export JUPITERONE_API_TOKEN='your-api-token'")
        print("  export JUPITERONE_ACCOUNT_ID='your-account-id'")
        sys.exit(1)
    
    # Create JupiterOne client
    j1 = JupiterOneClient(token=api_token, account=account_id)
    
    print("=== JupiterOne Sync Job Workflow Example ===\n")
    
    # You'll need to replace this with an actual integration instance ID
    instance_id = os.getenv('JUPITERONE_INSTANCE_ID')
    if not instance_id:
        print("Error: Please set JUPITERONE_INSTANCE_ID environment variable")
        print("Example:")
        print("  export JUPITERONE_INSTANCE_ID='your-integration-instance-id'")
        sys.exit(1)
    
    try:
        # Step 1: Start sync job
        print("1. Starting synchronization job...")
        print("   Note: Using PATCH mode (entities only). Use DIFF mode if uploading relationships.")
        sync_job = j1.start_sync_job(
            instance_id=instance_id,
            sync_mode="PATCH",
            source="integration-external"
        )
        
        sync_job_id = sync_job['job'].get('id')
        print(f"✓ Started sync job: {sync_job_id}")
        print(f"  Status: {sync_job['job']['status']}")
        print()
        
        # Step 2: Upload entities batch
        print("2. Uploading entities batch...")
        
        # Sample entities payload
        entities_payload = [
            {
                "_key": "example-server-001",
                "_type": "example_server",
                "_class": "Host",
                "displayName": "Example Server 001",
                "hostname": "server-001.example.com",
                "ipAddress": "192.168.1.100",
                "operatingSystem": "Linux",
                "tag.Environment": "development",
                "tag.Team": "engineering",
                "tag.Purpose": "web_server"
            },
            {
                "_key": "example-server-002",
                "_type": "example_server",
                "_class": "Host",
                "displayName": "Example Server 002",
                "hostname": "server-002.example.com",
                "ipAddress": "192.168.1.101",
                "operatingSystem": "Linux",
                "tag.Environment": "staging",
                "tag.Team": "engineering",
                "tag.Purpose": "database_server"
            },
            {
                "_key": "example-database-001",
                "_type": "example_database",
                "_class": "Database",
                "displayName": "Example Database 001",
                "databaseName": "app_db",
                "engine": "postgresql",
                "version": "13.4",
                "tag.Environment": "development",
                "tag.Team": "data"
            }
        ]
        
        # Upload entities
        upload_result = j1.upload_entities_batch_json(
            instance_job_id=sync_job_id,
            entities_list=entities_payload
        )
        print(f"✓ Uploaded {len(entities_payload)} entities successfully")
        print(f"  Upload result: {upload_result}")
        print()
        
        # Step 3: Finalize sync job
        print("3. Finalizing synchronization job...")
        finalize_result = j1.finalize_sync_job(instance_job_id=sync_job_id)
        
        finalize_job_id = finalize_result['job'].get('id')
        print(f"✓ Finalized sync job: {finalize_job_id}")
        print(f"  Status: {finalize_result['job']['status']}")
        
        # Check final status
        if finalize_result['job']['status'] == 'COMPLETED':
            print("✓ Sync job completed successfully!")
        elif finalize_result['job']['status'] == 'FAILED':
            error_msg = finalize_result['job'].get('error', 'Unknown error')
            print(f"✗ Sync job failed: {error_msg}")
        else:
            print(f"ℹ Sync job status: {finalize_result['job']['status']}")
        
        print("\n=== Sync Job Workflow Complete ===")
        
    except Exception as e:
        print(f"✗ Error during sync job workflow: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

