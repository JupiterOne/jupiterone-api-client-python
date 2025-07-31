"""
Example: Creating Integration Instances with Resource Group Support

This example demonstrates how to use the create_integration_instance method
with the new resource_group_id parameter to assign integration instances
to specific resource groups.
"""

from jupiterone.client import JupiterOneClient
import os


def main():
    """Example of creating integration instances with resource group support"""
    
    # Initialize the JupiterOne client
    # You can set these as environment variables or pass them directly
    account = os.getenv('JUPITERONE_ACCOUNT')
    token = os.getenv('JUPITERONE_API_TOKEN')
    
    if not account or not token:
        print("Please set JUPITERONE_ACCOUNT and JUPITERONE_API_TOKEN environment variables")
        return
    
    j1_client = JupiterOneClient(account=account, token=token)
    
    # Example 1: Create integration instance without resource group
    print("Creating integration instance without resource group...")
    try:
        integration = j1_client.create_integration_instance(
            instance_name="my-integration-no-rg",
            instance_description="Integration without resource group assignment"
        )
        print(f"Created integration instance: {integration['id']}")
        print(f"Name: {integration['name']}")
        print(f"Description: {integration['description']}")
    except Exception as e:
        print(f"Error creating integration instance: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Create integration instance with resource group
    print("Creating integration instance with resource group...")
    try:
        integration_with_rg = j1_client.create_integration_instance(
            instance_name="my-integration-with-rg",
            instance_description="Integration with resource group assignment",
            resource_group_id="your-resource-group-id-here"  # Replace with actual resource group ID
        )
        print(f"Created integration instance: {integration_with_rg['id']}")
        print(f"Name: {integration_with_rg['name']}")
        print(f"Description: {integration_with_rg['description']}")
        print(f"Resource Group ID: {integration_with_rg.get('resourceGroupId', 'Not assigned')}")
    except Exception as e:
        print(f"Error creating integration instance with resource group: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 3: Create integration instance with custom definition and resource group
    print("Creating integration instance with custom definition and resource group...")
    try:
        integration_custom = j1_client.create_integration_instance(
            instance_name="my-custom-integration",
            instance_description="Custom integration with resource group",
            integration_definition_id="your-integration-definition-id-here",  # Replace with actual definition ID
            resource_group_id="your-resource-group-id-here"  # Replace with actual resource group ID
        )
        print(f"Created custom integration instance: {integration_custom['id']}")
        print(f"Name: {integration_custom['name']}")
        print(f"Description: {integration_custom['description']}")
        print(f"Integration Definition ID: {integration_custom.get('integrationDefinitionId')}")
        print(f"Resource Group ID: {integration_custom.get('resourceGroupId', 'Not assigned')}")
    except Exception as e:
        print(f"Error creating custom integration instance: {e}")


if __name__ == "__main__":
    main() 