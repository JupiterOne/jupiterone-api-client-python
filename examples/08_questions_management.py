#!/usr/bin/env python3
"""
JupiterOne Python SDK - Questions Management Examples

This file demonstrates how to:
1. Create questions with single and multiple queries
2. Create questions with various configuration options
3. List existing questions in your account
4. Use questions for security monitoring and compliance

NOTE: This example includes robust error handling for the compliance field
to handle potential GraphQL schema mismatches where compliance data might
be returned as a list instead of a dictionary.
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
    # Note: The compliance field access has been made robust to handle potential
    # GraphQL schema mismatches where compliance data might be returned as a list
    # instead of a dictionary. This was causing the original error:
    # "'list' object has no attribute 'get'"
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
        
        # Debug: Show the entire response structure
        print(f"Full question response keys: {list(compliance_mapped_question.keys())}")
        print(f"Question ID: {compliance_mapped_question.get('id', 'No ID')}")
        
        try:
            if 'compliance' in compliance_mapped_question:
                compliance_data = compliance_mapped_question['compliance']
                # Debug: Show the actual structure
                print(f"Compliance data structure: {type(compliance_data)}")
                print(f"Compliance data content: {compliance_data}")
                
                # Handle both list and dictionary responses for compliance
                if isinstance(compliance_data, dict):
                    print(f"Compliance standard: {compliance_data.get('standard', 'Not specified')}")
                    if 'requirements' in compliance_data:
                        reqs = compliance_data['requirements']
                        if isinstance(reqs, list):
                            print(f"Compliance requirements: {', '.join(map(str, reqs))}")
                        else:
                            print(f"Compliance requirements (unexpected type): {type(reqs)} - {reqs}")
                elif isinstance(compliance_data, list):
                    print(f"Compliance data returned as list with {len(compliance_data)} items")
                    # If it's a list, try to access the first item if it exists
                    if compliance_data and isinstance(compliance_data[0], dict):
                        print(f"First compliance item: {compliance_data[0]}")
                else:
                    print(f"Compliance data type: {type(compliance_data)}")
            else:
                print("No compliance field found in response")
        except Exception as compliance_error:
            print(f"Error accessing compliance data: {compliance_error}")
            print(f"Compliance field type: {type(compliance_mapped_question.get('compliance', 'Not present'))}")
            # Show more debugging info
            print(f"Full response for debugging: {compliance_mapped_question}")
        print()
    except Exception as e:
        print(f"Error creating compliance-mapped question: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {str(e)}")
        print()
    
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

def production_environment_examples(j1):
    """Demonstrate questions for production environment monitoring."""
    
    print("=== Production Environment Question Examples ===\n")
    
    print("1. Creating a question for production environment security:")
    try:
        prod_question = j1.create_question(
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
            description="Security checks for production environment resources",
            tags=["production", "security", "critical"],
            pollingInterval="THIRTY_MINUTES"  # More frequent polling for production
        )
        
        print(f"Created production environment question: {prod_question['title']}")
        print(f"Description: {prod_question['description']}")
        print(f"Tags: {', '.join(prod_question.get('tags', []))}")
        print(f"Polling interval: {prod_question.get('pollingInterval', 'Not set')}")
        print()
    except Exception as e:
        print(f"Error creating production environment question: {e}\n")

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
            
        # Demonstrate filtering capabilities
        print("\n=== Filtering Examples ===")
        
        # Search by content
        print("\n1. Searching for security-related questions:")
        security_questions = j1.list_questions(search_query="security")
        print(f"  Found {len(security_questions)} questions with 'security' in title/description")
        if security_questions:
            print(f"  Example: {security_questions[0]['title']}")
        
        # Filter by tags
        print("\n2. Filtering by compliance tags:")
        compliance_questions = j1.list_questions(tags=["compliance"])
        print(f"  Found {len(compliance_questions)} questions tagged with 'compliance'")
        if compliance_questions:
            print(f"  Example: {compliance_questions[0]['title']}")
        
        # Combine search and tags
        print("\n3. Combining search and tags:")
        security_compliance = j1.list_questions(
            search_query="encryption", 
            tags=["security", "compliance"]
        )
        print(f"  Found {len(security_compliance)} questions matching both criteria")
        if security_compliance:
            print(f"  Example: {security_compliance[0]['title']}")
        
        # Search for specific compliance standards
        print("\n4. Searching for CIS compliance questions:")
        cis_questions = j1.list_questions(search_query="CIS")
        print(f"  Found {len(cis_questions)} questions related to CIS")
        if cis_questions:
            print(f"  Example: {cis_questions[0]['title']}")
            
    except Exception as e:
        print(f"Error listing questions: {e}")

def get_question_details_example(j1):
    """Demonstrate getting specific question details."""
    
    print("=== Get Question Details Example ===\n")
    
    print("First, let's get a list of questions to find one to examine:")
    try:
        questions = j1.list_questions()
        
        if questions:
            # Get details of the first question
            first_question = questions[0]
            question_id = first_question['id']
            question_title = first_question['title']
            
            print(f"Getting detailed information for question: {question_title}")
            print(f"Question ID: {question_id}")
            
            # Get full question details
            question_details = j1.get_question_details(question_id=question_id)
            
            print(f"\nDetailed Question Information:")
            print(f"  Title: {question_details['title']}")
            print(f"  ID: {question_details['id']}")
            print(f"  Source ID: {question_details.get('sourceId', 'Not specified')}")
            print(f"  Description: {question_details.get('description', 'No description')}")
            print(f"  Tags: {', '.join(question_details.get('tags', []))}")
            print(f"  Last Updated: {question_details.get('lastUpdatedTimestamp', 'Not specified')}")
            print(f"  Account ID: {question_details.get('accountId', 'Not specified')}")
            print(f"  Show Trend: {question_details.get('showTrend', False)}")
            print(f"  Polling Interval: {question_details.get('pollingInterval', 'Not set')}")
            
            # Display queries
            queries = question_details.get('queries', [])
            print(f"\n  Queries ({len(queries)}):")
            for i, query in enumerate(queries):
                print(f"    Query {i+1}: {query.get('name', 'Unnamed')}")
                print(f"      - Query: {query.get('query', 'No query')}")
                print(f"      - Version: {query.get('version', 'Not specified')}")
                print(f"      - Results Are: {query.get('resultsAre', 'Not specified')}")
            
            # Display compliance information
            compliance = question_details.get('compliance')
            if compliance:
                print(f"\n  Compliance Information:")
                if isinstance(compliance, dict):
                    print(f"    Standard: {compliance.get('standard', 'Not specified')}")
                    requirements = compliance.get('requirements', [])
                    if requirements:
                        print(f"    Requirements: {', '.join(map(str, requirements))}")
                    controls = compliance.get('controls', [])
                    if controls:
                        print(f"    Controls: {', '.join(map(str, controls))}")
                else:
                    print(f"    Compliance data type: {type(compliance)}")
                    print(f"    Compliance content: {compliance}")
            else:
                print(f"\n  Compliance Information: None")
            
            # Display variables
            variables = question_details.get('variables', [])
            if variables:
                print(f"\n  Variables ({len(variables)}):")
                for var in variables:
                    print(f"    - Name: {var.get('name', 'Unnamed')}")
                    print(f"      Required: {var.get('required', False)}")
                    print(f"      Default: {var.get('default', 'None')}")
            else:
                print(f"\n  Variables: None")
                
            # Display integration information
            integration_def_id = question_details.get('integrationDefinitionId')
            if integration_def_id:
                print(f"\n  Integration Definition ID: {integration_def_id}")
            else:
                print(f"\n  Integration Definition ID: None")
                
        else:
            print("No questions found in the account to examine")
            
    except Exception as e:
        print(f"Error getting question details: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {str(e)}")

def update_question_examples(j1):
    """Demonstrate updating existing questions."""
    
    print("=== Update Question Examples ===\n")
    
    # First, let's get a list of questions to find one to update
    print("1. Finding a question to update:")
    try:
        questions = j1.list_questions()
        
        if questions:
            # Get the first question for demonstration
            question_to_update = questions[0]
            question_id = question_to_update['id']
            question_title = question_to_update['title']
            
            print(f"  Found question: {question_title}")
            print(f"  Question ID: {question_id}")
            print(f"  Current tags: {', '.join(question_to_update.get('tags', []))}")
            print(f"  Current description: {question_to_update.get('description', 'No description')[:50]}...")
            print()
            
            # Example 1: Update title and description
            print("2. Updating question title and description:")
            try:
                updated_question = j1.update_question(
                    question_id=question_id,
                    title=f"{question_title} - UPDATED",
                    description="This question has been updated with new information and improved clarity."
                )
                
                print(f"  ✅ Successfully updated question!")
                print(f"  New title: {updated_question['title']}")
                print(f"  New description: {updated_question['description']}")
                print()
                
            except Exception as e:
                print(f"  ❌ Error updating title/description: {e}\n")
            
            # Example 2: Update tags
            print("3. Updating question tags:")
            try:
                current_tags = question_to_update.get('tags', [])
                new_tags = current_tags + ["updated", "maintained", "reviewed"]
                
                updated_question = j1.update_question(
                    question_id=question_id,
                    tags=new_tags
                )
                
                print(f"  ✅ Successfully updated tags!")
                print(f"  New tags: {', '.join(updated_question['tags'])}")
                print()
                
            except Exception as e:
                print(f"  ❌ Error updating tags: {e}\n")
            
            # Example 3: Update queries
            print("4. Updating question queries:")
            try:
                current_queries = question_to_update.get('queries', [])
                if current_queries:
                    # Update the first query with improved version
                    updated_queries = current_queries.copy()
                    if len(updated_queries) > 0:
                        updated_queries[0] = {
                            **updated_queries[0],
                            "query": f"{updated_queries[0].get('query', '')} LIMIT 100",
                            "resultsAre": "INFORMATIVE"
                        }
                    
                    updated_question = j1.update_question(
                        question_id=question_id,
                        queries=updated_queries
                    )
                    
                    print(f"  ✅ Successfully updated queries!")
                    print(f"  Number of queries: {len(updated_question['queries'])}")
                    print(f"  First query updated: {updated_question['queries'][0]['query'][:50]}...")
                    print()
                else:
                    print("  ⚠️  No queries found to update")
                    print()
                    
            except Exception as e:
                print(f"  ❌ Error updating queries: {e}\n")
            
            # Example 4: Comprehensive update
            print("5. Comprehensive question update:")
            try:
                comprehensive_update = j1.update_question(
                    question_id=question_id,
                    title="Comprehensive Security Audit Question - UPDATED",
                    description="This question has been comprehensively updated to include multiple security checks and improved query performance.",
                    tags=["security", "audit", "comprehensive", "updated", "maintained"],
                    showTrend=True,
                    pollingInterval="ONE_DAY"
                )
                
                print(f"  ✅ Successfully completed comprehensive update!")
                print(f"  Final title: {comprehensive_update['title']}")
                print(f"  Final tags: {', '.join(comprehensive_update['tags'])}")
                print(f"  Show trend: {comprehensive_update.get('showTrend', False)}")
                print(f"  Polling interval: {comprehensive_update.get('pollingInterval', 'Not set')}")
                print()
                
            except Exception as e:
                print(f"  ❌ Error in comprehensive update: {e}\n")
            
            # Example 5: Update specific fields only
            print("6. Updating specific fields only:")
            try:
                # Only update the description, leave everything else unchanged
                specific_update = j1.update_question(
                    question_id=question_id,
                    description="This question focuses on specific security controls and compliance requirements."
                )
                
                print(f"  ✅ Successfully updated description only!")
                print(f"  Description updated: {specific_update['description'][:50]}...")
                print(f"  Title remains: {specific_update['title']}")
                print(f"  Tags remain: {', '.join(specific_update['tags'])}")
                print()
                
            except Exception as e:
                print(f"  ❌ Error updating specific fields: {e}\n")
                
        else:
            print("  ⚠️  No questions found in the account to update")
            print()
            
    except Exception as e:
        print(f"  ❌ Error finding questions to update: {e}\n")
    
    # Example 7: Update with compliance metadata
    print("7. Updating question with compliance metadata:")
    try:
        if questions:
            compliance_update = j1.update_question(
                question_id=question_id,
                compliance={
                    "standard": "CIS Controls",
                    "requirements": ["6.1", "6.2"],
                    "controls": ["Data Protection", "Access Control"]
                }
            )
            
            print(f"  ✅ Successfully updated compliance metadata!")
            if 'compliance' in compliance_update:
                compliance_data = compliance_update['compliance']
                if isinstance(compliance_data, dict):
                    print(f"  Standard: {compliance_data.get('standard', 'Not specified')}")
                    print(f"  Requirements: {', '.join(map(str, compliance_data.get('requirements', [])))}")
                    print(f"  Controls: {', '.join(map(str, compliance_data.get('controls', [])))}")
                else:
                    print(f"  Compliance data type: {type(compliance_data)}")
            print()
            
    except Exception as e:
        print(f"  ❌ Error updating compliance metadata: {e}\n")
    
    # Example 8: Update with variables
    print("8. Updating question with variables:")
    try:
        if questions:
            variables_update = j1.update_question(
                question_id=question_id,
                variables=[
                    {
                        "name": "environment",
                        "required": True,
                        "default": "production"
                    },
                    {
                        "name": "severity",
                        "required": False,
                        "default": "high"
                    }
                ]
            )
            
            print(f"  ✅ Successfully updated variables!")
            if 'variables' in variables_update:
                print(f"  Number of variables: {len(variables_update['variables'])}")
                for var in variables_update['variables']:
                    print(f"    - {var['name']} (required: {var.get('required', False)}, default: {var.get('default', 'None')})")
            print()
            
    except Exception as e:
        print(f"  ❌ Error updating variables: {e}\n")

def delete_question_examples(j1):
    """Demonstrate deleting existing questions."""
    
    print("=== Delete Question Examples ===\n")
    
    # Get question ID from user input
    print("1. Enter the question ID to delete:")
    print("   (You can find question IDs by running the list_questions_example first)")
    print()
    
    # For demonstration purposes, use a placeholder ID
    # In a real application, you would use: question_id = input("Enter question ID: ")
    question_id = "your-question-id-here"  # Replace with actual question ID
    
    if question_id == "your-question-id-here":
        print("  ⚠️  Please replace 'your-question-id-here' with an actual question ID")
        print("  Example: question_id = 'fcc0507d-0473-43a2-b083-9d5571b92ae7'")
        print()
        return
    
    print(f"  Question ID to delete: {question_id}")
    print()
    
    # Delete the question
    print("2. Deleting the question:")
    try:
        deleted_question = j1.delete_question(question_id=question_id)
        
        print(f"  ✅ Successfully deleted question!")
        print(f"  Deleted question title: {deleted_question['title']}")
        print(f"  Deleted question ID: {deleted_question['id']}")
        print(f"  Number of queries in deleted question: {len(deleted_question['queries'])}")
        print()
        
    except Exception as e:
        print(f"  ❌ Error deleting question: {e}")
        print()

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
    
    # Use Case 4: Question Maintenance and Updates
    print("\nUse Case 4: Question Maintenance and Updates")
    print("-" * 50)
    print("Maintain and update existing questions:")
    print("""
    # Update question title and description
    updated_question = j1.update_question(
        question_id="existing-question-id",
        title="Updated Security Question Title",
        description="Updated description with new security requirements"
    )
    
    # Update queries for better performance
    updated_question = j1.update_question(
        question_id="existing-question-id",
        queries=[
            {
                "name": "ImprovedQuery",
                "query": "FIND * WITH tag.Security='critical' LIMIT 1000",
                "version": "v2",
                "resultsAre": "BAD"
            }
        ]
    )
    
    # Add compliance metadata
    updated_question = j1.update_question(
        question_id="existing-question-id",
        compliance={
            "standard": "ISO 27001",
            "requirements": ["A.9.1", "A.9.2"],
            "controls": ["Access Control"]
        }
    )
    """)
    
    # Use Case 5: Question Deletion and Cleanup
    print("\nUse Case 5: Question Deletion and Cleanup")
    print("-" * 50)
    print("Delete questions that are no longer needed:")
    print("""
    # Delete a single question
    deleted_question = j1.delete_question(
        question_id="question-id-to-delete"
    )
    print(f"Deleted: {deleted_question['title']}")
    
    # Batch delete deprecated questions
    deprecated_questions = j1.list_questions(tags=["deprecated"])
    for question in deprecated_questions:
        try:
            deleted = j1.delete_question(question_id=question['id'])
            print(f"Deleted deprecated question: {deleted['title']}")
        except Exception as e:
            print(f"Failed to delete {question['title']}: {e}")
    
    # Safe deletion with backup
    question_to_delete = j1.get_question_details(question_id="question-id")
    backup_question = j1.create_question(
        title=f"{question_to_delete['title']} - BACKUP",
        queries=question_to_delete['queries'],
        description=f"Backup before deletion: {question_to_delete.get('description', '')}",
        tags=question_to_delete.get('tags', []) + ["backup"]
    )
    
    # Now delete the original
    j1.delete_question(question_id="question-id")
    print("Original question deleted, backup preserved")
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
    
    production_environment_examples(j1)
    time.sleep(1)
    
    list_questions_example(j1)
    time.sleep(1)

    get_question_details_example(j1)
    time.sleep(1)
    
    update_question_examples(j1)
    time.sleep(1)
    
    delete_question_examples(j1)
    time.sleep(1)
    
    question_use_cases(j1)
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("\nNote: Remember to set your environment variables:")
    print("  - JUPITERONE_ACCOUNT_ID")
    print("  - JUPITERONE_API_TOKEN")

if __name__ == "__main__":
    main()
