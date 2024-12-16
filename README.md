# JupiterOne Python SDK

[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)


A Python library for the [JupiterOne API](https://docs.jupiterone.io/reference).

## Installation

Requires Python 3.6+

`pip install jupiterone`

## Usage

##### Create a new client:

```python
from jupiterone import JupiterOneClient

j1 = JupiterOneClient(
    account='<yourAccountId>',
    token='<yourApiToken>',
    url='https://graphql.us.jupiterone.io',
    sync_url='https://api.us.jupiterone.io'
)

```

## Regional or Custom Tenant Support

For users with J1 accounts in the EU region for example, 
the 'url' parameter will need to be updated to "https://graphql.eu.jupiterone.io"
and the 'sync_url' parameter will need to be updated to "https://api.eu.jupiterone.io".

If no 'url' parameter is passed, 
the default of "https://graphql.us.jupiterone.io" is used,
and if no 'sync_url' parameter is passed,
the default of "https://api.us.jupiterone.io" is used.

## Method Examples:

### *See the examples/examples.py for full usage example documentation

##### Execute a query:

```python
QUERY = 'FIND Host'
query_result = j1.query_v1(QUERY)

# Including deleted entities
query_result = j1.query_v1(QUERY, include_deleted=True)

# Tree query
QUERY = 'FIND Host RETURN TREE'
query_result = j1.query_v1(QUERY)

# Using cursor graphQL variable to return full set of paginated results
QUERY = "FIND (Device | Person)"
cursor_query_r = j1._cursor_query(QUERY)

```

##### Create an entity:

Note that the CreateEntity mutation behaves like an upsert, so a non-existent entity will be created or an existing entity will be updated.

```python
properties = {
    'myProperty': 'myValue',
    'tag.myTagProperty': 'value_will_be_a_tag'
}

entity = j1.create_entity(
   entity_key='my-unique-key',
   entity_type='my_type',
   entity_class='MyClass',
   properties=properties,
   timestamp=int(time.time()) * 1000 # Optional, defaults to current datetime
)
print(entity['entity'])

```


#### Update an existing entity:
Only send in properties you want to add or update, other existing properties will not be modified.

```python
properties = {
    'newProperty': 'newPropertyValue'
}

j1.update_entity(
    entity_id='<id-of-entity-to-update>',
    properties=properties
)

```


#### Delete an entity:

```python
j1.delete_entity(entity_id='<id-of-entity-to-delete>')
```

##### Create a relationship

```python
j1.create_relationship(
    relationship_key='this_entity_relates_to_that_entity',
    relationship_type='my_relationship_type',
    relationship_class='MYRELATIONSHIP',
    from_entity_id='<id-of-source-entity>',
    to_entity_id='<id-of-destination-entity>'
)

```

##### Delete a relationship

```python
j1.delete_relationship(relationship_id='<id-of-relationship-to-delete>')

```

##### Fetch Graph Entity Properties

```python
j1.fetch_all_entity_properties()

```

##### Fetch Graph Entity Tags

```python
j1.fetch_all_entity_tags()

```

##### Fetch Entity Raw Data

```python
j1.fetch_entity_raw_data(entity_id='<id-of-entity>')

```

##### Create Integration Instance

```python
j1.create_integration_instance(
    instance_name="Integration Name", 
    instance_description="Description Text")

```

##### Start Synchronization Job

```python
j1.start_sync_job(instance_id='<id-of-integration-instance>')

```

##### Upload Batch of Entities

```python
entities_payload = [
    {
      "_key": "1",
      "_type": "pythonclient",
      "_class": "API",
      "displayName": "pythonclient1",
      "propertyName": "value"
    },
    {
      "_key": "2",
      "_type": "pythonclient",
      "_class": "API",
      "displayName": "pythonclient2",
      "propertyName": "value"
    },
    {
      "_key": "3",
      "_type": "pythonclient",
      "_class": "API",
      "displayName": "pythonclient3",
      "propertyName": "value"
    }
]

j1.upload_entities_batch_json(instance_job_id='<id-of-integration-sync-job>',
                              entities_list=entities_payload)

```

##### Upload Batch of Relationships

```python
relationships_payload = [
    {
      "_key": "1:2",
      "_class": "EXTENDS",
      "_type": "pythonclient_extends_pythonclient",
      "_fromEntityKey": "1",
      "_toEntityKey": "2",
      "relationshipProperty": "value"
    },
    {
      "_key": "2:3",
      "_class": "EXTENDS",
      "_type": "pythonclient_extends_pythonclient",
      "_fromEntityKey": "2",
      "_toEntityKey": "3",
      "relationshipProperty": "value"
    }
]

j1.upload_relationships_batch_json(instance_job_id='<id-of-integration-sync-job>',
                                   relationships_list=relationships_payload)

```

##### Upload Batch of Entities and Relationships

```python
combined_payload = {
    "entities": [
    {
      "_key": "4",
      "_type": "pythonclient",
      "_class": "API",
      "displayName": "pythonclient4",
      "propertyName": "value"
    },
    {
      "_key": "5",
      "_type": "pythonclient",
      "_class": "API",
      "displayName": "pythonclient5",
      "propertyName": "value"
    },
    {
      "_key": "6",
      "_type": "pythonclient",
      "_class": "API",
      "displayName": "pythonclient6",
      "propertyName": "value"
    }
],
    "relationships": [
    {
      "_key": "4:5",
      "_class": "EXTENDS",
      "_type": "pythonclient_extends_pythonclient",
      "_fromEntityKey": "4",
      "_toEntityKey": "5",
      "relationshipProperty": "value"
    },
    {
      "_key": "5:6",
      "_class": "EXTENDS",
      "_type": "pythonclient_extends_pythonclient",
      "_fromEntityKey": "5",
      "_toEntityKey": "6",
      "relationshipProperty": "value"
    }
]
}

j1.upload_combined_batch_json(instance_job_id='<id-of-integration-sync-job>',
                              combined_payload=combined_payload)

```

##### Finalize Synchronization Job

```python
j1.finalize_sync_job(instance_job_id='<id-of-integration-sync-job>')

```

##### Fetch Integration Instance Jobs

```python

j1.fetch_integration_jobs(instance_id='<id-of-integration-instance>')
```

##### Fetch Integration Instance Job Events

```python
j1.fetch_integration_job_events(instance_id='<id-of-integration-instance>',
                                instance_job_id='<id-of-integration-instance-job>')

```

##### Create SmartClass

```python
j1.create_smartclass(smartclass_name='SmartClassName',
                     smartclass_description='SmartClass Description Text')

```

##### Create SmartClass Query

```python
j1.create_smartclass_query(smartclass_id='<id-of-smartclass>',
                           query='<J1QL-query-to-be-added>',
                           query_description='Query Description Text')

```

##### Run SmartClass Evaluation

```python
j1.evaluate_smartclass(smartclass_id='<id-of-smartclass>')

```

##### Get SmartClass Details

```python
j1.get_smartclass_details(smartclass_id='<id-of-smartclass>')

```

##### Generate J1QL from Natural Language Prompt

```python
j1.generate_j1ql(natural_language_prompt='<natural-language-input-text>')

```

##### List Alert Rules

```python
j1.list_alert_rules()

```

##### Get Alert Rule Details

```python
j1.get_alert_rule_details(rule_id='<id-of-alert-rule>')

```

##### Create Alert Rule

```python
# polling_interval can be DISABLED, THIRTY_MINUTES, ONE_HOUR, FOUR_HOURS, EIGHT_HOURS, TWELVE_HOURS, ONE_DAY, or ONE_WEEK
# severity can be INFO, LOW, MEDIUM, HIGH, or CRITICAL

j1.create_alert_rule(name="create_alert_rule-name",
                     description="create_alert_rule-description",
                     tags=['tag1', 'tag2'],
                     polling_interval="DISABLED",
                     severity="INFO",
                     j1ql="find jupiterone_user")

```

##### Create Alert Rule with Action Config

```python

webhook_action_config = {
            "type": "WEBHOOK",
            "endpoint": "https://webhook.domain.here/endpoint",
            "headers": {
              "Authorization": "Bearer <SECRET>",
            },
            "method": "POST",
            "body": {
              "queryData": "{{queries.query0.data}}"
            }
}

tag_entities_action_config = {
            "type": "TAG_ENTITIES",
            "entities": "{{queries.query0.data}}",
            "tags": [
              {
                "name": "tagKey",
                "value": "tagValue"
              }
            ]
}

j1.create_alert_rule(name="create_alert_rule-name",
                    description="create_alert_rule-description",
                    tags=['tag1', 'tag2'],
                    polling_interval="DISABLED",
                    severity="INFO",
                    j1ql="find jupiterone_user",
                    action_configs=webhook_action_config)

```

##### Delete Alert Rule

```python

j1.delete_alert_rule(rule_id='<id-of-alert-rule')

```

##### Update Alert Rule

```python

# polling_interval can be DISABLED, THIRTY_MINUTES, ONE_HOUR, FOUR_HOURS, EIGHT_HOURS, TWELVE_HOURS, ONE_DAY, or ONE_WEEK
# tag_op can be OVERWRITE or APPEND
# severity can be INFO, LOW, MEDIUM, HIGH, or CRITICAL
# action_configs_op can be OVERWRITE or APPEND

alert_rule_config_alert = [
    {
        "type": "CREATE_ALERT"
    }
]

alert_rule_config_tag = [
    {
        "type": "TAG_ENTITIES",
        "entities": "{{queries.query0.data}}",
        "tags": [
            {
                "name": "tagName",
                "value": "tagValue"
            }
        ]
    }
]

alert_rule_config_webhook = [
    {
        "type": "WEBHOOK",
        "endpoint": "https://webhook.example",
        "headers": {
            "Authorization": "Bearer <TOKEN>"
        },
        "method": "POST",
        "body": {
            "queryData": "{{queries.query0.data}}"
        }
    }
]

alert_rule_config_multiple = [
    {
        "type": "WEBHOOK",
        "endpoint": "https://webhook.example",
        "headers": {
            "Authorization": "Bearer <TOKEN>"
        },
        "method": "POST",
        "body": {
            "queryData": "{{queries.query0.data}}"
        }
    },
    {
        "type": "TAG_ENTITIES",
        "entities": "{{queries.query0.data}}",
        "tags": [
            {
                "name": "tagName",
                "value": "tagValue"
            }
        ]
    }
]

j1.update_alert_rule(rule_id="<id-of-alert-rule>",
                     name="Updated Alert Rule Name",
                     description="Updated Alert Rule Description",
                     j1ql="find jupiterone_user",
                     polling_interval="ONE_WEEK",
                     tags=['tag1', 'tag2', 'tag3'],
                     tag_op="OVERWRITE",
                     severity="INFO",
                     action_configs=alert_rule_config_tag,
                     action_configs_op="OVERWRITE")

j1.update_alert_rule(rule_id='<id-of-alert-rule>',
                     tags=['newTag1', 'newTag1'],
                     tag_op="OVERWRITE")

j1.update_alert_rule(rule_id='<id-of-alert-rule>',
                     tags=['additionalTag1', 'additionalTag2'],
                     tag_op="APPEND")

```

##### Evaluate Alert Rule

```python

j1.evaluate_alert_rule(rule_id='<id-of-alert-rule>')

```

##### Get Compliance Framework Item

```python

j1.get_compliance_framework_item_details(item_id="<id-of-item>")

```

##### List Alert Rule Evaluation Results

```python

j1.list_alert_rule_evaluation_results(rule_id="<id-of-rule>")

```

##### Fetch Evaluation Result Download URL

```python

j1.fetch_evaluation_result_download_url(raw_data_key="RULE_EVALUATION/<id-of-evaluation>/query0.json")

```

##### Fetch Evaluation Result Download URL

```python

j1.fetch_evaluation_result_download_url(raw_data_key="RULE_EVALUATION/<id-of-evaluation>/query0.json")

```

##### Fetch Downloaded Evaluation Results

```python

j1.fetch_downloaded_evaluation_results(download_url="https://download.us.jupiterone.io/<id-of-rule>/RULE_EVALUATION/<id-of-evaluation>/<epoch>/query0.json?token=<TOKEN>&Expires=<epoch>")

```

##### Get Integration Definition Details

```python

# examples: 'aws', 'azure', 'google_cloud'

j1.get_integration_definition_details(integration_type="<integration-type>")

```

##### Fetch Integration Instances

```python

j1.fetch_integration_instances(definition_id="<id-of-definition>")


```

##### Fetch Integration Instance Details

```python

j1.get_integration_instance_details(instance_id="<id-of-integration-instance>")


```

##### Get Account Parameter Details

```python

j1.get_parameter_details(name="ParameterName")


```

##### List Account Parameters

```python

j1.list_account_parameters()


```

##### Create or Update Acount Parameter

```python

j1.create_update_parameter(name="ParameterName", value="stored_value", secret=False)


```