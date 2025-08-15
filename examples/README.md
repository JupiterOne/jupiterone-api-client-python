# JupiterOne Python SDK Examples

This directory contains comprehensive examples demonstrating how to use the JupiterOne Python SDK for various operations and use cases.

## 📁 Example Files Overview

### 1. **01_client_setup_and_queries.py**
**Purpose**: Basic client setup and query operations
- Client initialization with environment variables
- Basic J1QL queries with filtering
- Relationship traversal queries
- Pagination methods (cursor-based, limit/skip, deferred response)
- Complex query patterns
- Natural language to J1QL conversion

**Key Methods Demonstrated**:
- `JupiterOneClient()` - Client initialization
- `query_v1()` - Basic queries
- `_cursor_query()` - Cursor-based pagination
- `_limit_and_skip_query()` - Limit/skip pagination
- `query_with_deferred_response()` - Deferred response for large datasets
- `generate_j1ql()` - Natural language to J1QL

### 2. **02_entity_management.py**
**Purpose**: Complete entity lifecycle management
- Entity creation with various property types
- Entity updates and modifications
- Entity deletion and cleanup
- Entity data fetching (properties, tags, raw data)
- Complete entity lifecycle workflows
- Bulk entity operations

**Key Methods Demonstrated**:
- `create_entity()` - Entity creation
- `update_entity()` - Entity updates
- `delete_entity()` - Entity deletion
- `fetch_all_entity_properties()` - Fetch all properties
- `fetch_all_entity_tags()` - Fetch all tags
- `fetch_entity_raw_data()` - Fetch raw entity data

### 3. **03_relationship_management.py**
**Purpose**: Relationship creation and management
- Relationship creation with properties
- Relationship updates and modifications
- Relationship deletion
- Complex relationship scenarios
- Network-style relationships
- Access control relationships

**Key Methods Demonstrated**:
- `create_relationship()` - Relationship creation
- `update_relationship()` - Relationship updates
- `delete_relationship()` - Relationship deletion

### 4. **04_integration_management.py**
**Purpose**: Integration instance and sync job management
- Integration instance creation
- Integration definition management
- Synchronization job operations
- Batch upload operations (entities, relationships, combined)
- Integration job monitoring and events
- Bulk delete operations

**Key Methods Demonstrated**:
- `create_integration_instance()` - Create integration instances
- `get_integration_definition_details()` - Get integration definitions
- `start_sync_job()` - Start synchronization jobs
- `upload_entities_batch_json()` - Batch entity uploads
- `upload_relationships_batch_json()` - Batch relationship uploads
- `upload_combined_batch_json()` - Combined batch uploads
- `bulk_delete_entities()` - Bulk entity deletion

### 5. **05_alert_rules_and_smartclasses.py**
**Purpose**: Alert rules and SmartClass operations
- Alert rule creation with various configurations
- Alert rules with action configurations (webhooks, tags, Jira)
- Alert rule management and evaluation
- SmartClass creation and management
- Natural language to J1QL conversion
- Compliance framework operations

**Key Methods Demonstrated**:
- `create_alert_rule()` - Create alert rules
- `get_alert_rule_details()` - Get rule details
- `list_alert_rules()` - List all rules
- `update_alert_rule()` - Update rules
- `evaluate_alert_rule()` - Evaluate rules
- `create_smartclass()` - Create SmartClasses
- `create_smartclass_query()` - Add queries to SmartClasses
- `evaluate_smartclass()` - Evaluate SmartClasses

### 6. **06_advanced_operations.py**
**Purpose**: Advanced operations and optimization
- Bulk operations on entities and relationships
- Advanced query techniques (variables, scope filters, flags)
- Performance optimization techniques
- Error handling patterns
- Data synchronization workflows
- Utility methods and helpers

**Key Methods Demonstrated**:
- Bulk entity/relationship operations
- Advanced query parameters
- Error handling patterns
- Performance optimization techniques
- Data synchronization workflows

### 7. **07_account_parameters_list_example.py**
**Purpose**: Account parameter management
- List all account parameters
- Create/update account parameters
- Fetch parameter details
- Secret parameter handling

**Key Methods Demonstrated**:
- `list_account_parameters()` - List all parameters
- `create_update_parameter()` - Create or update parameters
- `get_parameter_details()` - Get parameter details

### 8. **08_questions_management.py**
**Purpose**: Questions creation and management
- Create questions with single and multiple queries
- Configure question properties (tags, compliance, variables)
- Create questions for security monitoring and compliance
- List existing questions in the account
- Advanced question features (parameterization, resource groups)

**Key Methods Demonstrated**:
- `create_question()` - Create questions with J1QL queries
- `list_questions()` - List all questions in the account

### 9. **examples.py**
**Purpose**: Comprehensive examples of all major SDK methods
- Client setup and basic operations
- Entity and relationship management
- Integration and sync job operations
- Alert rules and SmartClass operations
- Questions management and analysis
- Account parameter operations

**Key Methods Demonstrated**:
- All major SDK methods including:
- `list_questions()` - List and analyze all questions in the account
- `create_question()` - Create questions with various configurations
- Entity lifecycle management methods
- Relationship management methods
- Integration and sync job methods
- Alert rule and SmartClass methods

## 🚀 Getting Started

### Prerequisites
1. Python 3.6 or higher
2. JupiterOne account with API access
3. JupiterOne Python SDK installed (`pip install jupiterone`)

### Environment Setup
Set the following environment variables:
```bash
export JUPITERONE_ACCOUNT_ID="your-account-id"
export JUPITERONE_API_TOKEN="your-api-token"
export JUPITERONE_URL="https://graphql.us.jupiterone.io"  # Optional
export JUPITERONE_SYNC_URL="https://api.us.jupiterone.io"  # Optional
```

### Running Examples
Each example file can be run independently:

```bash
# Run client setup and query examples
python 01_client_setup_and_queries.py

# Run entity management examples
python 02_entity_management.py

# Run relationship management examples
python 03_relationship_management.py

# Run integration management examples
python 04_integration_management.py

# Run alert rules and SmartClass examples
python 05_alert_rules_and_smartclasses.py

# Run advanced operations examples
python 06_advanced_operations.py

# Run account parameters examples
python 07_account_parameters_list_example.py

# Run questions management examples
python 08_questions_management.py
```

## 📋 Example Categories

### 🔍 Query Operations
- Basic entity queries
- Relationship traversal
- Property filtering
- Aggregation queries
- Time-based queries
- Complex multi-step queries

### 📊 Questions Management
- Question creation with J1QL queries
- Question listing and analysis
- Compliance metadata management
- Question categorization and filtering
- Question lifecycle management

### 🏗️ Entity Management
- Entity creation with various property types
- Entity updates and modifications
- Entity deletion and cleanup
- Entity lifecycle management
- Bulk entity operations

### 🔗 Relationship Management
- Relationship creation with properties
- Relationship updates and modifications
- Relationship deletion
- Network-style relationships
- Access control relationships

### 🔧 Integration Management
- Integration instance creation
- Synchronization job management
- Batch upload operations
- Integration monitoring
- Bulk operations

### 🚨 Alert Rules & SmartClasses
- Alert rule creation and configuration
- Action configurations (webhooks, tags, Jira)
- SmartClass creation and management
- Natural language to J1QL conversion
- Compliance framework operations

### ⚡ Advanced Operations
- Bulk operations
- Performance optimization
- Error handling patterns
- Data synchronization
- Advanced query techniques

## 🛠️ Common Patterns

### Error Handling
All examples include proper error handling:
```python
try:
    result = j1.some_operation()
    print("Operation successful")
except Exception as e:
    print(f"Error: {e}")
```

### Cleanup Operations
Examples that create test data include cleanup:
```python
# Create test data
entity = j1.create_entity(...)

# ... perform operations ...

# Clean up
j1.delete_entity(entity_id=entity['entity']['_id'])
```

### Environment Variable Usage
Examples use environment variables for configuration:
```python
j1 = JupiterOneClient(
    account=os.getenv('JUPITERONE_ACCOUNT_ID'),
    token=os.getenv('JUPITERONE_API_TOKEN'),
    url=os.getenv('JUPITERONE_URL', 'https://graphql.us.jupiterone.io'),
    sync_url=os.getenv('JUPITERONE_SYNC_URL', 'https://api.us.jupiterone.io')
)
```

### Questions Analysis
Examples show how to analyze questions data:
```python
# List all questions
questions = j1.list_questions()

# Analyze by compliance standards
compliance_standards = {}
for question in questions:
    if 'compliance' in question and question['compliance']:
        compliance = question['compliance']
        if isinstance(compliance, dict) and 'standard' in compliance:
            standard = compliance['standard']
            compliance_standards[standard] = compliance_standards.get(standard, 0) + 1

# Find questions by tags
security_questions = [q for q in questions if 'tags' in q and q['tags'] and any('security' in tag.lower() for tag in q['tags'])]
```

## 📝 Notes

### Placeholder Values
Some examples use placeholder values that need to be replaced:
- `"your-account-id"` - Replace with actual JupiterOne account ID
- `"your-api-token"` - Replace with actual API token
- `"your-integration-definition-id"` - Replace with actual integration definition ID
- `"your-resource-group-id"` - Replace with actual resource group ID

### Permissions
Some examples require specific permissions in your JupiterOne account:
- Entity creation/deletion permissions
- Integration management permissions
- Alert rule creation permissions
- SmartClass creation permissions

### Data Requirements
Some examples assume the presence of certain data types:
- AWS entities (for cloud-specific examples)
- User entities (for access control examples)
- Finding entities (for security examples)

## 🔧 Customization

### Modifying Examples
You can modify examples to suit your needs:
1. Change entity types and properties
2. Modify query filters
3. Adjust pagination parameters
4. Customize error handling
5. Add your own business logic

### Extending Examples
Examples can be extended with:
- Additional error handling
- Logging and monitoring
- Custom data processing
- Integration with other systems
- Automated workflows

## 📚 Additional Resources

- [JupiterOne API Documentation](https://docs.jupiterone.io/reference)
- [J1QL Query Language Guide](https://docs.jupiterone.io/docs/j1ql)
- [JupiterOne Python SDK Documentation](https://github.com/JupiterOne/jupiterone-client-python)
- [JupiterOne Community](https://community.jupiterone.io/)

## 🤝 Contributing

When adding new examples:
1. Follow the existing naming convention
2. Include proper error handling
3. Add cleanup operations for test data
4. Document the purpose and key methods
5. Update this README with new examples

## 📄 License

These examples are provided under the same license as the JupiterOne Python SDK. 