#!/usr/bin/env python3
"""
JupiterOne Python SDK - Alert Rules and SmartClass Examples

This file demonstrates how to:
1. Create and manage alert rules
2. Work with SmartClasses
3. Generate J1QL from natural language
4. Handle alert rule evaluations
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

def alert_rule_examples(j1):
    """Demonstrate alert rule creation and management."""
    
    print("=== Alert Rule Examples ===\n")
    
    # 1. Basic alert rule creation
    print("1. Creating a basic alert rule:")
    basic_rule = j1.create_alert_rule(
        name="Unencrypted Databases",
        description="Alert when databases are found without encryption",
        tags=['security', 'compliance'],
        polling_interval="ONE_DAY",
        severity="HIGH",
        j1ql="FIND Database WITH encrypted = false"
    )
    print(f"Created basic alert rule: {basic_rule['rule']['_id']}\n")
    
    # 2. Complex alert rule with multiple conditions
    print("2. Creating a complex alert rule:")
    complex_rule = j1.create_alert_rule(
        name="Production Access Violations",
        description="Alert when non-admin users access production resources",
        tags=['security', 'access-control', 'production'],
        polling_interval="THIRTY_MINUTES",
        severity="CRITICAL",
        j1ql="""
        FIND User AS u 
        THAT HAS AccessPolicy AS ap 
        THAT ALLOWS * AS resource 
        WHERE resource.tag.Environment = 'production' 
        AND ap.accessLevel = 'admin' 
        AND u.tag.Role != 'admin'
        """
    )
    print(f"Created complex alert rule: {complex_rule['rule']['_id']}\n")
    
    return basic_rule, complex_rule

def alert_rule_with_actions_examples(j1):
    """Demonstrate alert rules with action configurations."""
    
    print("=== Alert Rules with Actions Examples ===\n")
    
    # 1. Webhook action configuration
    webhook_action_config = {
        "type": "WEBHOOK",
        "endpoint": "https://webhook.example.com/security-alerts",
        "headers": {
            "Authorization": "Bearer your-webhook-token",
            "Content-Type": "application/json"
        },
        "method": "POST",
        "body": {
            "alertType": "security_violation",
            "queryData": "{{queries.query0.data}}",
            "timestamp": "{{timestamp}}"
        }
    }
    
    # 2. Tag entities action configuration
    tag_entities_action_config = {
        "type": "TAG_ENTITIES",
        "entities": "{{queries.query0.data}}",
        "tags": [
            {
                "name": "SecurityViolation",
                "value": "true"
            },
            {
                "name": "ViolationType",
                "value": "unencrypted_database"
            }
        ]
    }
    
    # 3. Jira ticket creation action configuration
    jira_action_config = {
        "integrationInstanceId": "your-jira-integration-id",  # Replace with actual ID
        "type": "CREATE_JIRA_TICKET",
        "entityClass": "Record",
        "summary": "Security Violation Detected",
        "issueType": "Bug",
        "project": "SEC",
        "additionalFields": {
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "{{alertWebLink}}\n\n**Affected Items:**\n\n* {{queries.query0.data|mapProperty('displayName')|join('\n* ')}}"
                            }
                        ]
                    }
                ]
            },
            "labels": ["security", "automated", "jupiterone"]
        }
    }
    
    # Create alert rule with webhook action
    print("1. Creating alert rule with webhook action:")
    webhook_rule = j1.create_alert_rule(
        name="Security Violation Webhook Alert",
        description="Send security violations to webhook endpoint",
        tags=['security', 'automation'],
        polling_interval="ONE_HOUR",
        severity="HIGH",
        j1ql="FIND Finding WITH severity = 'HIGH'",
        action_configs=webhook_action_config
    )
    print(f"Created webhook alert rule: {webhook_rule['rule']['_id']}\n")
    
    # Create alert rule with multiple actions
    print("2. Creating alert rule with multiple actions:")
    multiple_actions = [webhook_action_config, tag_entities_action_config]
    multi_action_rule = j1.create_alert_rule(
        name="Comprehensive Security Alert",
        description="Alert and tag security violations",
        tags=['security', 'compliance'],
        polling_interval="FOUR_HOURS",
        severity="MEDIUM",
        j1ql="FIND Finding WITH severity = ('HIGH' OR 'CRITICAL')",
        action_configs=multiple_actions
    )
    print(f"Created multi-action alert rule: {multi_action_rule['rule']['_id']}\n")
    
    return webhook_rule, multi_action_rule

def alert_rule_management_examples(j1, rule_id):
    """Demonstrate alert rule management operations."""
    
    print("=== Alert Rule Management Examples ===\n")
    
    # 1. Get alert rule details
    print("1. Getting alert rule details:")
    try:
        rule_details = j1.get_alert_rule_details(rule_id=rule_id)
        print(f"Rule: {rule_details['rule']['name']}")
        print(f"Description: {rule_details['rule']['description']}")
        print(f"J1QL: {rule_details['rule']['j1ql']}")
        print(f"Severity: {rule_details['rule']['severity']}")
        print(f"Polling Interval: {rule_details['rule']['pollingInterval']}")
        
        # Check action configurations
        if 'actionConfigs' in rule_details['rule']:
            print("Action Configurations:")
            for action in rule_details['rule']['actionConfigs']:
                print(f"  Type: {action['type']}")
                if action['type'] == 'WEBHOOK':
                    print(f"  Endpoint: {action['endpoint']}")
                elif action['type'] == 'TAG_ENTITIES':
                    print(f"  Tags: {action['tags']}")
    except Exception as e:
        print(f"Error getting rule details: {e}")
    print()
    
    # 2. List all alert rules
    print("2. Listing all alert rules:")
    try:
        alert_rules = j1.list_alert_rules()
        print(f"Found {len(alert_rules)} alert rules")
        for rule in alert_rules[:3]:  # Show first 3
            print(f"  Rule ID: {rule['_id']}")
            print(f"  Name: {rule['name']}")
            print(f"  Severity: {rule['severity']}")
            print(f"  Status: {rule['status']}")
    except Exception as e:
        print(f"Error listing alert rules: {e}")
    print()
    
    # 3. Update alert rule
    print("3. Updating alert rule:")
    try:
        updated_rule = j1.update_alert_rule(
            rule_id=rule_id,
            name="Updated Security Alert Rule",
            description="Updated description for security monitoring",
            j1ql="FIND Finding WITH severity = ('HIGH' OR 'CRITICAL')",
            polling_interval="ONE_WEEK",
            tags=['security', 'compliance', 'updated'],
            tag_op="OVERWRITE",
            severity="INFO"
        )
        print(f"Updated alert rule: {updated_rule['rule']['_id']}")
    except Exception as e:
        print(f"Error updating alert rule: {e}")
    print()
    
    # 4. Evaluate alert rule
    print("4. Evaluating alert rule:")
    try:
        evaluation = j1.evaluate_alert_rule(rule_id=rule_id)
        print(f"Started evaluation: {evaluation['evaluation']['_id']}")
        
        # Check evaluation status
        if evaluation['evaluation']['status'] == 'COMPLETED':
            print("Evaluation completed successfully")
            print(f"Entities found: {evaluation['evaluation'].get('entityCount', 0)}")
        elif evaluation['evaluation']['status'] == 'FAILED':
            print(f"Evaluation failed: {evaluation['evaluation'].get('error', 'Unknown error')}")
    except Exception as e:
        print(f"Error evaluating alert rule: {e}")
    print()

def smartclass_examples(j1):
    """Demonstrate SmartClass operations."""
    
    print("=== SmartClass Examples ===\n")
    
    # 1. Create SmartClass
    print("1. Creating a SmartClass:")
    smartclass = j1.create_smartclass(
        smartclass_name='ProductionServers',
        smartclass_description='All production servers across cloud providers'
    )
    smartclass_id = smartclass['smartclass']['_id']
    print(f"Created SmartClass: {smartclass_id}\n")
    
    # 2. Add queries to SmartClass
    print("2. Adding queries to SmartClass:")
    queries = [
        ('FIND Host WITH tag.Environment = "production"', 'Production hosts'),
        ('FIND Database WITH tag.Environment = "production"', 'Production databases'),
        ('FIND Application WITH tag.Environment = "production"', 'Production applications')
    ]
    
    for query_text, description in queries:
        try:
            smartclass_query = j1.create_smartclass_query(
                smartclass_id=smartclass_id,
                query=query_text,
                query_description=description
            )
            print(f"Added query: {smartclass_query['query']['_id']}")
        except Exception as e:
            print(f"Error adding query: {e}")
    print()
    
    # 3. Get SmartClass details
    print("3. Getting SmartClass details:")
    try:
        smartclass_details = j1.get_smartclass_details(smartclass_id=smartclass_id)
        print(f"SmartClass: {smartclass_details['smartclass']['name']}")
        print(f"Description: {smartclass_details['smartclass']['description']}")
        print(f"Queries: {len(smartclass_details.get('queries', []))}")
        
        # List all queries in the SmartClass
        for query in smartclass_details.get('queries', []):
            print(f"  Query: {query['query']}")
            print(f"  Description: {query['description']}")
    except Exception as e:
        print(f"Error getting SmartClass details: {e}")
    print()
    
    # 4. Evaluate SmartClass
    print("4. Evaluating SmartClass:")
    try:
        evaluation = j1.evaluate_smartclass(smartclass_id=smartclass_id)
        print(f"Started SmartClass evaluation: {evaluation['evaluation']['_id']}")
        
        # Check evaluation status
        if evaluation['evaluation']['status'] == 'COMPLETED':
            print("SmartClass evaluation completed")
            print(f"Entities found: {evaluation['evaluation'].get('entityCount', 0)}")
    except Exception as e:
        print(f"Error evaluating SmartClass: {e}")
    print()
    
    return smartclass_id

def natural_language_to_j1ql_examples(j1):
    """Demonstrate natural language to J1QL conversion."""
    
    print("=== Natural Language to J1QL Examples ===\n")
    
    prompts = [
        "Find all AWS EC2 instances that are running and tagged as production",
        "Show me all databases that are not encrypted",
        "Find users who have admin access to production systems",
        "List all applications that haven't been updated in the last 30 days",
        "Show me all network connections between development and production environments",
        "Find all security findings with high severity from the last week"
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"{i}. Prompt: {prompt}")
        try:
            result = j1.generate_j1ql(natural_language_prompt=prompt)
            print(f"   Generated J1QL: {result['j1ql']}")
        except Exception as e:
            print(f"   Error: {e}")
        print()

def alert_rule_evaluation_examples(j1, rule_id):
    """Demonstrate alert rule evaluation operations."""
    
    print("=== Alert Rule Evaluation Examples ===\n")
    
    # 1. List evaluation results
    print("1. Listing evaluation results:")
    try:
        evaluations = j1.list_alert_rule_evaluation_results(rule_id=rule_id)
        print(f"Found {len(evaluations)} evaluations")
        
        # Process evaluation results
        for evaluation in evaluations[:3]:  # Show first 3
            print(f"  Evaluation ID: {evaluation['_id']}")
            print(f"  Status: {evaluation['status']}")
            print(f"  Started: {evaluation.get('startedOn')}")
            print(f"  Completed: {evaluation.get('completedOn')}")
            print(f"  Entities found: {evaluation.get('entityCount', 0)}")
    except Exception as e:
        print(f"Error listing evaluations: {e}")
    print()
    
    # 2. Fetch evaluation result download URL
    print("2. Fetching evaluation result download URL:")
    try:
        # This would typically use a real evaluation ID
        download_url = j1.fetch_evaluation_result_download_url(
            raw_data_key="RULE_EVALUATION/example-evaluation-id/query0.json"
        )
        print(f"Download URL: {download_url['url']}")
        print(f"URL expires: {download_url.get('expires')}")
    except Exception as e:
        print(f"Error fetching download URL: {e}")
    print()
    
    # 3. Fetch downloaded evaluation results
    print("3. Fetching downloaded evaluation results:")
    try:
        # This would use a real download URL
        download_url = "https://download.us.jupiterone.io/example-url"
        results = j1.fetch_downloaded_evaluation_results(download_url=download_url)
        print(f"Downloaded {len(results)} results")
        
        # Process the results
        for result in results[:3]:  # Show first 3
            print(f"  Entity: {result.get('displayName', result.get('_id'))}")
            print(f"  Type: {result.get('_type')}")
            print(f"  Class: {result.get('_class')}")
    except Exception as e:
        print(f"Error fetching downloaded results: {e}")
    print()

def compliance_framework_examples(j1):
    """Demonstrate compliance framework operations."""
    
    print("=== Compliance Framework Examples ===\n")
    
    # Get compliance framework item details
    print("1. Getting compliance framework item details:")
    try:
        # This would use a real item ID
        item_details = j1.get_compliance_framework_item_details(item_id="example-item-id")
        print(f"Item: {item_details['item']['name']}")
        print(f"Description: {item_details['item']['description']}")
        print(f"Category: {item_details['item']['category']}")
        print(f"Status: {item_details['item']['status']}")
        
        # Access compliance requirements
        if 'requirements' in item_details['item']:
            print("Requirements:")
            for req in item_details['item']['requirements']:
                print(f"  - {req['description']}")
    except Exception as e:
        print(f"Error getting compliance item: {e}")
    print()

def main():
    """Main function to run all alert rules and SmartClass examples."""
    
    print("JupiterOne Python SDK - Alert Rules and SmartClass Examples")
    print("=" * 60)
    
    try:
        # Set up client
        j1 = setup_client()
        print("✓ Client setup successful\n")
        
        # Run examples
        basic_rule, complex_rule = alert_rule_examples(j1)
        webhook_rule, multi_action_rule = alert_rule_with_actions_examples(j1)
        
        # Alert rule management (using the basic rule)
        alert_rule_management_examples(j1, basic_rule['rule']['_id'])
        
        # SmartClass examples
        smartclass_id = smartclass_examples(j1)
        
        # Natural language to J1QL
        natural_language_to_j1ql_examples(j1)
        
        # Alert rule evaluation examples
        alert_rule_evaluation_examples(j1, basic_rule['rule']['_id'])
        
        # Compliance framework examples
        compliance_framework_examples(j1)
        
        print("✓ All alert rules and SmartClass examples completed successfully!")
        print("\nNote: Some examples require valid integration instance IDs and other configuration")
        print("Replace placeholder values with actual IDs when testing")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nMake sure you have set the following environment variables:")
        print("- JUPITERONE_ACCOUNT_ID")
        print("- JUPITERONE_API_TOKEN")

if __name__ == "__main__":
    main() 