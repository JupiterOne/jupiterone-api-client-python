#!/usr/bin/env python3
"""
JupiterOne Python SDK - Questions Management Examples

This file demonstrates how to:
1. Create questions with single and multiple queries
2. Create questions with various configuration options
3. List existing questions in your account
4. Use questions for security monitoring and compliance
"""

import os
import json
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

def basic_question_examples(j1):
    """Demonstrate basic question creation."""
    
    print("=== Basic Question Examples ===\n")
    
    # 1. Create a simple question
    print("1. Creating a simple question:")
    try:
        question = j1.create_question(
            title="Show All Public S3 Buckets",
            queries=[{
                "query": "FIND aws_s3_bucket WITH public=true",
                "name": "PublicBuckets",
                "resultsAre": "BAD"
            }],
            description="Identifies S3 buckets that are publicly accessible",
            tags=["aws", "security", "s3"]
        )
        print(f"Created question: {question['title']} (ID: {question['id']})")
        print(f"Query: {question['queries'][0]['query']}")
        print()
    except Exception as e:
        print(f"Error creating question: {e}\n")
    
    # 2. Create a question with minimal parameters
    print("2. Creating a minimal question:")
    try:
        minimal_question = j1.create_question(
            title="List Recent Users",
            queries=[{
                "query": "FIND User WITH createdOn > date.now - 7 days"
            }]
        )
        print(f"Created minimal question: {minimal_question['title']}")
        print(f"Auto-generated query name: {minimal_question['queries'][0]['name']}")
        print()
    except Exception as e:
        print(f"Error creating minimal question: {e}\n")

def multi_query_question_examples(j1):
    """Demonstrate questions with multiple queries."""
    
    print("=== Multi-Query Question Examples ===\n")
    
    # Create a comprehensive security compliance question
    print("1. Creating a comprehensive security compliance question:")
    try:
        compliance_question = j1.create_question(
            title="Security Compliance Dashboard",
            queries=[
                {
                    "query": "FIND User WITH mfaEnabled=false",
                    "name": "UsersWithoutMFA",
                    "resultsAre": "BAD"
                },
                {
                    "query": "FIND Host WITH encryptionEnabled=false",
                    "name": "UnencryptedHosts",
                    "resultsAre": "BAD"
                },
                {
                    "query": "FIND DataStore WITH public=true",
                    "name": "PublicDataStores",
                    "resultsAre": "BAD"
                },
                {
                    "query": "FIND aws_iam_user THAT !HAS aws_iam_access_key",
                    "name": "UsersWithoutAccessKeys",
                    "resultsAre": "GOOD"
                }
            ],
            description="Comprehensive security compliance checks across users, hosts, and data stores",
            tags=["security", "compliance", "audit", "dashboard"],
            showTrend=True
        )
        
        print(f"Created compliance question: {compliance_question['title']}")
        print(f"Number of queries: {len(compliance_question['queries'])}")
        for idx, query in enumerate(compliance_question['queries']):
            print(f"  Query {idx + 1}: {query['name']} - Results are {query['resultsAre']}")
        print()
    except Exception as e:
        print(f"Error creating compliance question: {e}\n")
    
    # Create an AWS security audit question
    print("2. Creating an AWS security audit question:")
    try:
        aws_audit_question = j1.create_question(
            title="AWS Infrastructure Security Audit",
            queries=[
                {
                    "query": "FIND aws_instance WITH publicIpAddress!=undefined",
                    "name": "PublicInstances",
                    "version": "v1",
                    "resultsAre": "INFORMATIVE"
                },
                {
                    "query": "FIND aws_security_group THAT ALLOWS * WITH ipProtocol='tcp' AND fromPort<=22 AND toPort>=22",
                    "name": "SSHOpenToWorld",
                    "version": "v1",
                    "resultsAre": "BAD"
                },
                {
                    "query": "FIND aws_s3_bucket WITH (lifecycleEnabled=false OR lifecycleEnabled=undefined)",
                    "name": "BucketsWithoutLifecycle",
                    "version": "v1",
                    "resultsAre": "INFORMATIVE"
                }
            ],
            description="Audit AWS infrastructure for security best practices",
            tags=["aws", "security", "network", "audit"],
            pollingInterval="ONE_DAY"
        )
        
        print(f"Created AWS audit question: {aws_audit_question['title']}")
        print(f"Polling interval: {aws_audit_question.get('pollingInterval', 'Not set')}")
        print()
    except Exception as e:
        print(f"Error creating AWS audit question: {e}\n")

def advanced_question_examples(j1):
    """Demonstrate advanced question features."""
    
    print("=== Advanced Question Examples ===\n")
    
    # 1. Question with compliance metadata
    print("1. Creating a question with compliance metadata:")
    try:
        compliance_mapped_question = j1.create_question(
            title="CIS AWS Foundations Benchmark 2.3",
            queries=[{
                "query": "FIND aws_cloudtrail WITH isMultiRegionTrail!=true",
                "name": "SingleRegionTrails",
                "resultsAre": "BAD"
            }],
            description="Ensure CloudTrail is enabled in all regions (CIS AWS Foundations Benchmark 2.3)",
            tags=["cis", "aws", "cloudtrail", "compliance"],
            compliance={
                "standard": "CIS AWS Foundations Benchmark",
                "requirements": ["2.3"],
                "controls": ["Logging and Monitoring"]
            },
            showTrend=True,
            pollingInterval="ONE_HOUR"
        )
        
        print(f"Created compliance-mapped question: {compliance_mapped_question['title']}")
        if 'compliance' in compliance_mapped_question:
            print(f"Compliance standard: {compliance_mapped_question['compliance'].get('standard')}")
        print()
    except Exception as e:
        print(f"Error creating compliance-mapped question: {e}\n")
    
    # 2. Question with variables (parameterized queries)
    print("2. Creating a parameterized question with variables:")
    try:
        parameterized_question = j1.create_question(
            title="Environment-Specific Resource Audit",
            queries=[{
                "query": "FIND * WITH tag.Environment={{environment}} AND tag.CostCenter={{costCenter}}",
                "name": "EnvironmentResources",
                "resultsAre": "INFORMATIVE"
            }],
            description="Audit resources by environment and cost center tags",
            tags=["audit", "tagging", "cost-management"],
            variables=[
                {
                    "name": "environment",
                    "required": True,
                    "default": "production"
                },
                {
                    "name": "costCenter",
                    "required": False,
                    "default": "engineering"
                }
            ]
        )
        
        print(f"Created parameterized question: {parameterized_question['title']}")
        if 'variables' in parameterized_question:
            print(f"Number of variables: {len(parameterized_question['variables'])}")
            for var in parameterized_question['variables']:
                print(f"  Variable: {var['name']} (required: {var.get('required', False)})")
        print()
    except Exception as e:
        print(f"Error creating parameterized question: {e}\n")

def resource_group_question_examples(j1):
    """Demonstrate questions with resource group associations."""
    
    print("=== Resource Group Question Examples ===\n")
    
    # Note: You'll need to have a resource group ID for this example
    # This is just a demonstration - replace with your actual resource group ID
    resource_group_id = "your-resource-group-id"  # Replace with actual ID
    
    print("1. Creating a question associated with a resource group:")
    try:
        rg_question = j1.create_question(
            title="Production Environment Security Check",
            queries=[
                {
                    "query": "FIND Host WITH tag.Environment='production' AND encrypted!=true",
                    "name": "UnencryptedProdHosts",
                    "resultsAre": "BAD"
                },
                {
                    "query": "FIND Database WITH tag.Environment='production' AND backupEnabled!=true",
                    "name": "ProdDatabasesWithoutBackup",
                    "resultsAre": "BAD"
                }
            ],
            resource_group_id=resource_group_id,  # Associate with resource group
            description="Security checks for production environment resources",
            tags=["production", "security", "critical"],
            pollingInterval="THIRTY_MINUTES"  # More frequent polling for production
        )
        
        print(f"Created resource group question: {rg_question['title']}")
        print(f"Resource group ID: {resource_group_id}")
        print()
    except Exception as e:
        print(f"Note: Resource group example requires valid resource group ID\n")

def list_questions_example(j1):
    """Demonstrate listing existing questions."""
    
    print("=== List Questions Example ===\n")
    
    print("Fetching existing questions in the account...")
    try:
        questions = j1.list_questions()
        
        print(f"Total questions found: {len(questions)}")
        
        # Display first 5 questions
        for idx, question in enumerate(questions[:5]):
            print(f"\nQuestion {idx + 1}:")
            print(f"  Title: {question['title']}")
            print(f"  ID: {question['id']}")
            print(f"  Tags: {', '.join(question.get('tags', []))}")
            print(f"  Number of queries: {len(question.get('queries', []))}")
            if question.get('description'):
                print(f"  Description: {question['description'][:50]}...")
        
        if len(questions) > 5:
            print(f"\n... and {len(questions) - 5} more questions")
            
    except Exception as e:
        print(f"Error listing questions: {e}")

def question_use_cases(j1):
    """Demonstrate real-world use cases for questions."""
    
    print("\n=== Question Use Cases ===\n")
    
    # Use Case 1: Daily Security Report
    print("Use Case 1: Daily Security Report Question")
    print("-" * 50)
    print("Create a question that runs daily to generate a security report:")
    print("""
    question = j1.create_question(
        title="Daily Security Report",
        queries=[
            {"query": "FIND Finding WITH createdOn > date.now - 1 day", "name": "NewFindings"},
            {"query": "FIND User WITH createdOn > date.now - 1 day", "name": "NewUsers"},
            {"query": "FIND * WITH _class='Vulnerability' AND open=true", "name": "OpenVulnerabilities"}
        ],
        description="Daily security report showing new findings, users, and open vulnerabilities",
        tags=["daily-report", "security"],
        pollingInterval="ONE_DAY"
    )
    """)
    
    # Use Case 2: Compliance Monitoring
    print("\nUse Case 2: Continuous Compliance Monitoring")
    print("-" * 50)
    print("Create questions for continuous compliance monitoring:")
    print("""
    question = j1.create_question(
        title="PCI-DSS Compliance Checks",
        queries=[
            {"query": "FIND User WITH privileged=true AND lastAuthenticationOn < date.now - 90 days", "name": "InactivePrivilegedUsers", "resultsAre": "BAD"},
            {"query": "FIND DataStore WITH classification='payment' AND encrypted!=true", "name": "UnencryptedPaymentData", "resultsAre": "BAD"}
        ],
        compliance={"standard": "PCI-DSS", "requirements": ["8.1.4", "3.4"]},
        pollingInterval="FOUR_HOURS"
    )
    """)
    
    # Use Case 3: Cost Optimization
    print("\nUse Case 3: Cloud Cost Optimization")
    print("-" * 50)
    print("Create questions to identify cost optimization opportunities:")
    print("""
    question = j1.create_question(
        title="Unused Cloud Resources",
        queries=[
            {"query": "FIND aws_instance WITH state='stopped' AND stoppedOn < date.now - 30 days", "name": "LongStoppedInstances"},
            {"query": "FIND aws_ebs_volume THAT !RELATES TO aws_instance", "name": "UnattachedVolumes"},
            {"query": "FIND aws_eip THAT !RELATES TO aws_instance", "name": "UnassociatedElasticIPs"}
        ],
        tags=["cost-optimization", "aws"],
        pollingInterval="ONE_WEEK"
    )
    """)

def main():
    """Run all question management examples."""
    j1 = setup_client()
    
    print("JupiterOne Questions Management Examples")
    print("=" * 50)
    print()
    
    # Run examples
    basic_question_examples(j1)
    time.sleep(1)  # Small delay between API calls
    
    multi_query_question_examples(j1)
    time.sleep(1)
    
    advanced_question_examples(j1)
    time.sleep(1)
    
    resource_group_question_examples(j1)
    time.sleep(1)
    
    list_questions_example(j1)
    
    question_use_cases(j1)
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("\nNote: Remember to set your environment variables:")
    print("  - JUPITERONE_ACCOUNT_ID")
    print("  - JUPITERONE_API_TOKEN")

if __name__ == "__main__":
    main()
