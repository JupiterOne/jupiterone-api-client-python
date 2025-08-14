# Create Question Method Documentation

## Overview

The `create_question` method allows you to programmatically create questions in your JupiterOne account. Questions are saved queries that can be run on-demand or on a schedule to monitor your infrastructure and security posture.

## Method Signature

```python
def create_question(
    self,
    title: str,
    queries: List[Dict],
    resource_group_id: str = None,
    **kwargs
)
```

## Parameters

### Required Parameters

- **`title`** (str): The title of the question. This is required and cannot be empty.

- **`queries`** (List[Dict]): A list of query objects. At least one query is required. Each query object can contain:
  - **`query`** (str, required): The J1QL query string
  - **`name`** (str, optional): Name for the query. Defaults to "Query{index}"
  - **`version`** (str, optional): Query version (e.g., "v1")
  - **`resultsAre`** (str, optional): Query result type. Defaults to "INFORMATIVE". Options include:
    - "INFORMATIVE" - Neutral information
    - "GOOD" - Positive/expected results
    - "BAD" - Negative/unexpected results
    - "UNKNOWN" - Unknown state

### Optional Parameters

- **`resource_group_id`** (str): ID of the resource group to associate the question with

### Additional Keyword Arguments (**kwargs)

- **`description`** (str): Description of the question
- **`tags`** (List[str]): List of tags to apply to the question
- **`compliance`** (Dict): Compliance metadata containing:
  - `standard` (str): Compliance standard name
  - `requirements` (List[str]): List of requirement IDs
  - `controls` (List[str]): List of control names
- **`variables`** (List[Dict]): Variable definitions for parameterized queries
- **`showTrend`** (bool): Whether to show trend data for the question results
- **`pollingInterval`** (str): How often to run the queries (e.g., "ONE_HOUR", "ONE_DAY")
- **`integrationDefinitionId`** (str): Integration definition ID if the question is integration-specific

## Return Value

Returns a dictionary containing the created question object with fields like:
- `id`: Unique identifier for the question
- `title`: The question title
- `description`: The question description
- `queries`: List of query objects
- `tags`: Applied tags
- And other metadata fields

## Examples

### Basic Question

```python
from jupiterone import JupiterOneClient

j1_client = JupiterOneClient(
    account="your-account-id",
    token="your-api-token"
)

# Create a simple question
question = j1_client.create_question(
    title="Find All Open Hosts",
    queries=[{
        "query": "FIND Host WITH open=true",
        "name": "OpenHosts"
    }]
)
```

### Question with Multiple Queries

```python
# Create a question with multiple queries for comprehensive checks
question = j1_client.create_question(
    title="Security Compliance Check",
    queries=[
        {
            "query": "FIND Host WITH open=true",
            "name": "OpenHosts",
            "resultsAre": "BAD"
        },
        {
            "query": "FIND User WITH mfaEnabled=false",
            "name": "UsersWithoutMFA",
            "resultsAre": "BAD"
        },
        {
            "query": "FIND DataStore WITH encrypted=false",
            "name": "UnencryptedDataStores",
            "resultsAre": "BAD"
        }
    ],
    description="Comprehensive security compliance check",
    tags=["security", "compliance", "audit"]
)
```

### Advanced Question with All Options

```python
# Create a question with all optional parameters
question = j1_client.create_question(
    title="AWS Security Audit",
    queries=[{
        "query": "FIND aws_instance WITH publicIpAddress!=undefined",
        "name": "PublicInstances",
        "version": "v1",
        "resultsAre": "INFORMATIVE"
    }],
    resource_group_id="resource-group-123",
    description="Audit AWS instances with public IP addresses",
    tags=["aws", "security", "network"],
    showTrend=True,
    pollingInterval="ONE_DAY",
    compliance={
        "standard": "CIS",
        "requirements": ["2.1", "2.2"],
        "controls": ["Network Security"]
    },
    variables=[
        {
            "name": "environment",
            "required": False,
            "default": "production"
        }
    ]
)
```

### Minimal Question

```python
# Create a question with only required parameters
# The query name will default to "Query0" and resultsAre to "INFORMATIVE"
question = j1_client.create_question(
    title="Simple Query",
    queries=[{
        "query": "FIND User LIMIT 10"
    }]
)
```

## Error Handling

The method includes validation for required fields and will raise `ValueError` exceptions for:
- Missing or empty `title`
- Missing or empty `queries` list
- Invalid query format (not a dictionary)
- Missing required `query` field in query objects

```python
try:
    question = j1_client.create_question(
        title="",  # This will raise an error
        queries=[]
    )
except ValueError as e:
    print(f"Error: {e}")
```

## GraphQL Mutation

The method uses the following GraphQL mutation internally:

```graphql
mutation CreateQuestion($question: CreateQuestionInput!) {
    createQuestion(question: $question) {
        id
        title
        description
        tags
        queries {
            name
            query
            version
            resultsAre
        }
        # ... other fields
    }
}
```
