import json
from pathlib import Path
import requests
import os
import time
from colorama import init, Fore, Style
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

# Initialize colorama
init(autoreset=True)

# Load configuration
 
script_dir = Path(__file__).parent.parent

with open(f'{script_dir}/infra/integrations/integration_outputs.json', 'r') as f:
    config = json.load(f)

# JupiterOne API details
API_URL = 'https://api.us.jupiterone.io/graphql'
HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {os.environ.get("JUPITERONE_API_KEY")}',
    'JupiterOne-Account': os.environ.get("JUPITERONE_ACCOUNT")
}

def get_upload_url(integration_instance_id, filename, dataset_id):
    query = """
    mutation integrationFileTransferUploadUrl(
        $integrationInstanceId: String!
        $filename: String!
        $datasetId: String!
    ) {
        integrationFileTransferUploadUrl(
            integrationInstanceId: $integrationInstanceId
            filename: $filename
            datasetId: $datasetId
        ) {
            uploadUrl
            expiresIn
        }
    }
    """
    variables = {
        "integrationInstanceId": integration_instance_id,
        "filename": filename,
        "datasetId": dataset_id
    }
    response = requests.post(API_URL, json={"query": query, "variables": variables}, headers=HEADERS)
    return response.json()['data']['integrationFileTransferUploadUrl']['uploadUrl']

def upload_file(upload_url, file_path):
    with open(file_path, 'rb') as f:
        response = requests.put(upload_url, data=f, headers={'Content-Type': 'text/csv'})
    return response.status_code

def invoke_integration(integration_instance_id):
    query = """
    mutation InvokeIntegrationInstance(
        $id: String!
    ) {
        invokeIntegrationInstance(
            id: $id
        ) {
            success
            integrationJobId
        }
    }
    """
    variables = {"id": integration_instance_id}
    response = requests.post(API_URL, json={"query": query, "variables": variables}, headers=HEADERS)
    response_json = response.json()
    
    if 'errors' in response_json:
        error = response_json['errors'][0]
        if error.get('extensions', {}).get('code') == 'ALREADY_EXECUTING_ERROR':
            return 'ALREADY_RUNNING'
        else:
            print(f"GraphQL error: {error['message']}")
            return False
    elif 'data' in response_json and response_json['data'] is not None:
        if 'invokeIntegrationInstance' in response_json['data']:
            return response_json['data']['invokeIntegrationInstance']['success']
        else:
            print(f"Unexpected response format: 'invokeIntegrationInstance' not found in data")
            return False
    else:
        print(f"Unexpected response format: {response_json}")
        return False

def print_colored(message, color=Fore.WHITE, style=Style.NORMAL):
    print(f"{style}{color}{message}")

def select_integrations():
    integration_names = list(config.keys())
    integration_names_lower = [name.lower() for name in integration_names]
    completer = WordCompleter(integration_names + ['all'])
    
    print_colored("Available integrations:", Fore.CYAN, Style.BRIGHT)
    for name in integration_names:
        print_colored(f"  - {name}", Fore.CYAN)
    
    while True:
        selection = prompt(
            "Enter integration names to run (comma-separated) or 'all': ",
            completer=completer
        ).strip().lower()
        
        if selection == 'all':
            return integration_names
        
        selected = [name.strip() for name in selection.split(',')]
        valid_selections = []
        invalid = []
        
        for name in selected:
            if name in integration_names_lower:
                valid_selections.append(integration_names[integration_names_lower.index(name)])
            else:
                invalid.append(name)
        
        if invalid:
            print_colored(f"Invalid integrations: {', '.join(invalid)}. Please try again.", Fore.RED)
        else:
            return valid_selections

def main():
    # Check if environment variables are set
    if not os.environ.get("JUPITERONE_API_KEY") or not os.environ.get("JUPITERONE_ACCOUNT"):
        print_colored("Error: JUPITERONE_API_KEY and JUPITERONE_ACCOUNT environment variables must be set.", Fore.RED, Style.BRIGHT)
        return

    selected_integrations = select_integrations()

    for integration_name in selected_integrations:
        integration_data = config[integration_name]
        integration_instance_id = integration_data['integrationInstanceId']
        source_files = integration_data['sourceFiles'].split(',')
        dataset_ids = integration_data['dataSetIds'].split(',')

        print_colored(f"\nProcessing integration: {integration_name}", Fore.GREEN, Style.BRIGHT)

        for filename, dataset_id in zip(source_files, dataset_ids):
            print_colored(f"  Uploading {filename} for dataset {dataset_id}", Fore.YELLOW)
            upload_url = get_upload_url(integration_instance_id, filename, dataset_id)
            
            file_path = os.path.join(script_dir, 'data', filename)
            
            status_code = upload_file(upload_url, file_path)
            if status_code == 200:
                print_colored(f"    ✔ Successfully uploaded {filename}", Fore.GREEN)
            else:
                print_colored(f"    ✘ Failed to upload {filename}. Status code: {status_code}", Fore.RED)

        print_colored(f"  Invoking integration: {integration_name}", Fore.YELLOW)
        try:
            result = invoke_integration(integration_instance_id)
            if result == True:
                print_colored(f"    ✔ Successfully invoked integration: {integration_name}", Fore.GREEN)
            elif result == 'ALREADY_RUNNING':
                print_colored(f"    ⚠ Integration {integration_name} is already running. Skipping.", Fore.YELLOW)
            else:
                print_colored(f"    ✘ Failed to invoke integration: {integration_name}", Fore.RED)
        except Exception as e:
            print_colored(f"    ✘ Error invoking integration {integration_name}: {str(e)}", Fore.RED)

        print()  # Empty line for readability
        time.sleep(5)  # Wait for 5 seconds before the next integration

if __name__ == "__main__":
    main()
