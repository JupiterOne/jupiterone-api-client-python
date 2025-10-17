#!/usr/bin/env python3
"""
Custom File Transfer (CFT) Integration Example

This script demonstrates how to use the JupiterOne Python client to:
1. Get an upload URL for Custom File Transfer integration
2. Upload a CSV file to the integration
3. Invoke the integration to process the uploaded file

Prerequisites:
- JupiterOne account with API access
- Custom File Transfer integration instance configured
- CSV file to upload

Usage:
    python 09_custom_file_transfer_example.py
"""

import os
import sys

# Add the parent directory to the path so we can import the jupiterone client
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
except NameError:
    # Handle case when __file__ is not available (e.g., when exec'd)
    sys.path.append('..')

from jupiterone.client import JupiterOneClient


def setup_client():
    """Set up the JupiterOne client with credentials."""
    # You can set these as environment variables or replace with your actual values
    account = os.getenv('JUPITERONE_ACCOUNT')
    token = os.getenv('JUPITERONE_API_TOKEN')
    
    if not account or not token:
        print("Error: Please set JUPITERONE_ACCOUNT and JUPITERONE_API_TOKEN environment variables")
        print("Example:")
        print("export JUPITERONE_ACCOUNT='your-account-id'")
        print("export JUPITERONE_API_TOKEN='your-api-token'")
        sys.exit(1)
    
    try:
        client = JupiterOneClient(account=account, token=token)
        print(f"✅ Successfully connected to JupiterOne account: {account}")
        return client
    except Exception as e:
        print(f"❌ Failed to connect to JupiterOne: {e}")
        sys.exit(1)


def get_cft_upload_url_example(client, integration_instance_id, filename, dataset_id):
    """
    Example of getting an upload URL for Custom File Transfer integration.
    
    Args:
        client: JupiterOne client instance
        integration_instance_id: ID of the CFT integration instance
        filename: Name of the file to upload
        dataset_id: Dataset ID for the upload
    """
    print("\n" + "="*60)
    print("1. GETTING CFT UPLOAD URL")
    print("="*60)
    
    try:
        print(f"Requesting upload URL for:")
        print(f"  - Integration Instance ID: {integration_instance_id}")
        print(f"  - Filename: {filename}")
        print(f"  - Dataset ID: {dataset_id}")
        
        upload_info = client.get_cft_upload_url(
            integration_instance_id=integration_instance_id,
            filename=filename,
            dataset_id=dataset_id
        )
        
        print("✅ Upload URL obtained successfully!")
        print(f"  - Upload URL: {upload_info['uploadUrl']}")
        print(f"  - Expires In: {upload_info['expiresIn']} seconds")
        
        return upload_info
        
    except Exception as e:
        print(f"❌ Failed to get upload URL: {e}")
        return None


def upload_cft_file_example(client, upload_url, file_path):
    """
    Example of uploading a CSV file to Custom File Transfer integration.
    
    Args:
        client: JupiterOne client instance
        upload_url: Upload URL obtained from get_cft_upload_url()
        file_path: Local path to the CSV file
    """
    print("\n" + "="*60)
    print("2. UPLOADING CSV FILE")
    print("="*60)
    
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return None
        
        # Check if file is CSV
        if not file_path.lower().endswith('.csv'):
            print(f"❌ File must be a CSV file. Got: {file_path}")
            return None
        
        print(f"Uploading file:")
        print(f"  - File path: {file_path}")
        print(f"  - File size: {os.path.getsize(file_path)} bytes")
        print(f"  - Upload URL: {upload_url}")
        
        # Upload the file
        result = client.upload_cft_file(
            upload_url=upload_url,
            file_path=file_path
        )
        
        print("✅ File upload completed!")
        print(f"  - Status code: {result['status_code']}")
        print(f"  - Success: {result['success']}")
        print(f"  - Response headers: {result['headers']}")
        
        if result['success']:
            print("  - File uploaded successfully to JupiterOne")
        else:
            print(f"  - Upload failed. Response data: {result['response_data']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Failed to upload file: {e}")
        return None


def invoke_cft_integration_example(client, integration_instance_id):
    """
    Example of invoking a Custom File Transfer integration instance.
    
    Args:
        client: JupiterOne client instance
        integration_instance_id: ID of the CFT integration instance
    """
    print("\n" + "="*60)
    print("3. INVOKING CFT INTEGRATION")
    print("="*60)
    
    try:
        print(f"Invoicing integration instance:")
        print(f"  - Integration Instance ID: {integration_instance_id}")
        
        # Invoke the integration
        result = client.invoke_cft_integration(
            integration_instance_id=integration_instance_id
        )
        
        if result == True:
            print("✅ Integration invoked successfully!")
            print("  - The integration is now processing the uploaded file")
        elif result == 'ALREADY_RUNNING':
            print("⚠️  Integration is already running")
            print("  - The integration instance is currently executing")
        else:
            print("❌ Integration invocation failed")
            print("  - Check the integration instance configuration")
        
        return result
        
    except Exception as e:
        print(f"❌ Failed to invoke integration: {e}")
        return None


def complete_workflow_example(client, integration_instance_id, file_path, dataset_id):
    """
    Complete workflow example combining all three methods.
    
    Args:
        client: JupiterOne client instance
        integration_instance_id: ID of the CFT integration instance
        file_path: Local path to the CSV file
        dataset_id: Dataset ID for the upload
    """
    print("\n" + "="*60)
    print("COMPLETE CFT WORKFLOW")
    print("="*60)
    
    print("Starting complete Custom File Transfer workflow...")
    
    # Step 1: Get upload URL
    upload_info = get_cft_upload_url_example(
        client, integration_instance_id, os.path.basename(file_path), dataset_id
    )
    
    if not upload_info:
        print("❌ Workflow failed at step 1: Getting upload URL")
        return False
    
    # Step 2: Upload file
    upload_result = upload_cft_file_example(client, upload_info['uploadUrl'], file_path)
    
    if not upload_result or not upload_result['success']:
        print("❌ Workflow failed at step 2: Uploading file")
        return False
    
    # Step 3: Invoke integration
    invoke_result = invoke_cft_integration_example(client, integration_instance_id)
    
    if invoke_result == True:
        print("\n🎉 Complete workflow successful!")
        print("  - File uploaded successfully")
        print("  - Integration invoked successfully")
        print("  - Data processing has begun")
        return True
    elif invoke_result == 'ALREADY_RUNNING':
        print("\n⚠️  Workflow partially successful")
        print("  - File uploaded successfully")
        print("  - Integration is already running")
        return True
    else:
        print("\n❌ Workflow failed at step 3: Invoking integration")
        return False


def main():
    """Main function demonstrating the CFT methods."""
    print("🚀 JupiterOne Custom File Transfer Integration Examples")
    print("="*60)
    
    # Configuration - Replace these with your actual values
    INTEGRATION_INSTANCE_ID = os.getenv('J1_CFT_INSTANCE_ID', 'your-integration-instance-id')
    DATASET_ID = os.getenv('J1_CFT_DATASET_ID', 'your-dataset-id')
    CSV_FILE_PATH = os.getenv('J1_CSV_FILE_PATH', 'examples/scanned_hosts.csv')
    
    # Check if we have the required configuration
    if INTEGRATION_INSTANCE_ID == 'your-integration-instance-id':
        print("⚠️  Configuration required:")
        print("Set the following environment variables:")
        print("  - J1_CFT_INSTANCE_ID: Your CFT integration instance ID")
        print("  - J1_CFT_DATASET_ID: Your dataset ID")
        print("  - J1_CSV_FILE_PATH: Path to your CSV file (optional, defaults to examples/scanned_hosts.csv)")
        print("\nExample:")
        print("export J1_CFT_INSTANCE_ID='123e4567-e89b-12d3-a456-426614174000'")
        print("export J1_CFT_DATASET_ID='dataset-123'")
        print("export J1_CSV_FILE_PATH='/path/to/your/file.csv'")
        print("\nOr update the variables in this script directly.")
        return
    
    # Set up the client
    client = setup_client()
    
    # Individual method examples
    print("\n📚 INDIVIDUAL METHOD EXAMPLES")
    
    # Example 1: Get upload URL
    upload_info = get_cft_upload_url_example(
        client, INTEGRATION_INSTANCE_ID, os.path.basename(CSV_FILE_PATH), DATASET_ID
    )
    
    if upload_info:
        # Example 2: Upload file
        upload_result = upload_cft_file_example(
            client, upload_info['uploadUrl'], CSV_FILE_PATH
        )
        
        if upload_result and upload_result['success']:
            # Example 3: Invoke integration
            invoke_cft_integration_example(client, INTEGRATION_INSTANCE_ID)
    
    # Complete workflow example
    print("\n🔄 COMPLETE WORKFLOW EXAMPLE")
    complete_workflow_example(client, INTEGRATION_INSTANCE_ID, CSV_FILE_PATH, DATASET_ID)
    
    print("\n" + "="*60)
    print("📖 USAGE PATTERNS")
    print("="*60)
    
    print("""
Common usage patterns:

1. Single file upload and processing:
   upload_info = client.get_cft_upload_url(instance_id, filename, dataset_id)
   upload_result = client.upload_cft_file(upload_info['uploadUrl'], file_path)
   if upload_result['success']:
       client.invoke_cft_integration(instance_id)

2. Batch processing multiple files:
   for file_path in csv_files:
       upload_info = client.get_cft_upload_url(instance_id, filename, dataset_id)
       client.upload_cft_file(upload_info['uploadUrl'], file_path)
   
   # Invoke integration once after all files are uploaded
   client.invoke_cft_integration(instance_id)

3. Error handling and retries:
   try:
       result = client.upload_cft_file(upload_url, file_path)
       if result['success']:
           print("Upload successful")
       else:
           print(f"Upload failed: {result['response_data']}")
   except Exception as e:
       print(f"Upload error: {e}")
    """)


if __name__ == "__main__":
    main()
