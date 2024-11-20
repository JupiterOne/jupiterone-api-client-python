from jupiterone.client import JupiterOneClient
import random
import time
import os

account = os.environ.get("JUPITERONE_ACCOUNT")
token = os.environ.get("JUPITERONE_TOKEN")
url = "https://graphql.us.jupiterone.io"

j1 = JupiterOneClient(account=account, token=token, url=url)

# query_v1
q = "FIND jupiterone_user"
query_r = j1.query_v1(q)
print("query_v1()")
print(query_r)

# create_entity
num1 = random.randrange(1, 999, 1)

# create_entity
properties = {
        'displayName': 'test{}'.format(num1),
        'customProperty': 'customVal',
        'tag.Production': 'false',
        'owner': 'user.name@jupiterone.com'
    }

create_r = j1.create_entity(
    entity_key='jupiterone-api-client-python:{}'.format(num1),
    entity_type='python_client_create_entity',
    entity_class='Record',
    properties=properties,
    timestamp=int(time.time()) * 1000  # Optional, defaults to current datetime
)
print("create_entity()")
print(create_r)

properties = {
        'customProperty': 'customValUpdated'
    }

# update_entity
update_r = j1.update_entity(
    entity_id='{}'.format(create_r['entity']['_id']),
    properties=properties
)
print("update_entity()")
print(update_r)

# create_entity_2
num2 = random.randrange(1, 999, 1)

properties = {
        'displayName': 'test{}'.format(num2),
        'customProperty': 'customVal',
        'tag.Production': 'false',
        'owner': 'user.name@jupiterone.com'
    }

create_r_2 = j1.create_entity(
    entity_key='jupiterone-api-client-python:{}'.format(num2),
    entity_type='python_client_create_entity',
    entity_class='Record',
    properties=properties,
    timestamp=int(time.time()) * 1000  # Optional, defaults to current datetime
)
print("create_entity()")
print(create_r_2)

# create_relationship
create_relationship_r = j1.create_relationship(
    relationship_key='{}:{}'.format(create_r['entity']['_id'], create_r_2['entity']['_id']),
    relationship_type='jupiterone-api-client-python:create_relationship',
    relationship_class='HAS',
    from_entity_id=create_r['entity']['_id'],
    to_entity_id=create_r_2['entity']['_id'],
)
print("create_relationship()")
print(create_relationship_r)

# delete_relationship
delete_relationship_r = j1.delete_relationship(relationship_id=create_relationship_r['relationship']['_id'])
print("delete_relationship()")
print(delete_relationship_r)

# delete_entity
delete_entity_r1 = j1.delete_entity(entity_id=create_r['entity']['_id'])
print("delete_entity()")
print(delete_entity_r1)

delete_entity_r2 = j1.delete_entity(entity_id=create_r_2['entity']['_id'])
print("delete_entity()")
print(delete_entity_r2)

# cursor_query
q = "FIND Person"
cursor_query_r = j1._cursor_query(q)
print("cursor_query()")
print(cursor_query_r)

# fetch_all_entity_properties
fetch_all_entity_properties_r = j1.fetch_all_entity_properties()
print("fetch_all_entity_properties()")
print(fetch_all_entity_properties_r)

# fetch_all_entity_tags
fetch_all_entity_tags_r = j1.fetch_all_entity_tags()
print("fetch_all_entity_tags()")
print(fetch_all_entity_tags_r)

# fetch_entity_raw_data
fetch_entity_raw_data_r = j1.fetch_entity_raw_data(entity_id="<GUID>")
print("fetch_entity_raw_data()")
print(json.dumps(fetch_entity_raw_data_r, indent=1))

# create_integration_instance
create_integration_instance_r = j1.create_integration_instance(instance_name="pythonclient-customintegration",
                                                               instance_description="dev-testing")
print("create_integration_instance()")
print(create_integration_instance_r)

integration_instance_id = "<GUID>"

# start_sync_job
# sync_mode can be "DIFF", "CREATE_OR_UPDATE", or "PATCH"
start_sync_job_r = j1.start_sync_job(instance_id=integration_instance_id,
                                     sync_mode='CREATE_OR_UPDATE',
                                     source='integration-external')
print("start_sync_job()")
print(start_sync_job_r)

# upload_entities_batch_json
rand_val_range = [x / 10.0 for x in range(0, 100)]
rand_val = random.choice(rand_val_range)

epoch_now = round(time.time() * 1000)

entity_payload = [
    {
      "_key": "1",
      "_type": "pythonclient",
      "_class": "API",
      "displayName": "pythonclient1",
      "propertyName": "value",
      "relationshipProperty": "source",
      "value": rand_val,
      "bulkUploadedOn": epoch_now
    },
    {
      "_key": "2",
      "_type": "pythonclient",
      "_class": "API",
      "displayName": "pythonclient2",
      "propertyName": "value",
      "relationshipProperty": "source",
      "value": rand_val,
      "bulkUploadedOn": epoch_now
    }
]

# update_entities_batch_json
upload_entities_batch_json_r = j1.upload_entities_batch_json(instance_job_id=start_sync_job_r['job']['id'],
                                                             entities_list=entity_payload)
print("upload_entities_batch_json()")
print(upload_entities_batch_json_r)

# upload_relationships_batch_json
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

# update_relationships_batch_json
upload_relationships_batch_json_r = j1.upload_relationships_batch_json(instance_job_id=start_sync_job_r['job']['id'],
                                                                       relationships_list=relationships_payload)
print("upload_relationships_batch_json()")
print(upload_relationships_batch_json_r)

# upload_entities_batch_json
combined_payload = {
    "entities": [
    {
      "_key": "4",
      "_type": "pythonclient",
      "_class": "API",
      "displayName": "pythonclient4",
      "enrichProp": "value1"
    },
    {
      "_key": "5",
      "_type": "pythonclient",
      "_class": "API",
      "displayName": "pythonclient5",
      "enrichProp": "value2"
    },
    {
      "_key": "6",
      "_type": "pythonclient",
      "_class": "API",
      "displayName": "pythonclient6",
      "enrichProp": "value3"
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

# upload_combined_batch_json
upload_combined_batch_json_r = j1.upload_combined_batch_json(instance_job_id=start_sync_job_r['job']['id'],
                                                             combined_payload=combined_payload)
print("upload_combined_batch_json()")
print(upload_combined_batch_json_r)

# finalize_sync_job
finalize_sync_job_r = j1.finalize_sync_job(instance_job_id=start_sync_job_r['job']['id'])
print("finalize_sync_job()")
print(finalize_sync_job_r)

# fetch_integration_jobs
fetch_integration_jobs_r = j1.fetch_integration_jobs(instance_id=integration_instance_id)
print("fetch_integration_jobs()")
print(fetch_integration_jobs_r)

while j1.fetch_integration_jobs(instance_id=integration_instance_id)['jobs'][0]['status'] == "IN_PROGRESS":

    fetch_integration_jobs_r = j1.fetch_integration_jobs(instance_id=integration_instance_id)

    print("fetch_integration_jobs()")
    print(fetch_integration_jobs_r)

# fetch_integration_job_events
fetch_integration_job_events_r = j1.fetch_integration_job_events(instance_id=integration_instance_id,
                                                                 instance_job_id=fetch_integration_jobs_r['jobs'][0]['id'])
print("fetch_integration_job_events()")
print(fetch_integration_job_events_r)

# create_smartclass
create_smartclass_r = j1.create_smartclass(smartclass_name="SmartClass1",
                                           smartclass_description="Created via create_smartclass() method")
print("create_smartclass()")
print(create_smartclass_r)

# create_smartclass_query
create_smartclass_query_r = j1.create_smartclass_query(smartclass_id=create_smartclass_r['id'],
                                                       query="FIND (Device|Host) with osType ~= \'Windows\'",
                                                       query_description="all windows devices and hosts")
print("create_smartclass_query()")
print(create_smartclass_query_r)

# evaluate_smartclass
evaluate_smartclass_r = j1.evaluate_smartclass(smartclass_id=create_smartclass_query_r['smartClassId'])
print("evaluate_smartclass()")
print(evaluate_smartclass_r)

# get_smartclass_details
get_smartclass_details_r = j1.get_smartclass_details(smartclass_id=create_smartclass_query_r['smartClassId'])
print("get_smartclass_details()")
print(get_smartclass_details_r)

# generate_j1ql
generate_j1ql_r = j1.generate_j1ql(natural_language_prompt="show me all Users containing 'jupiterone' in their email address")
print("generate_j1ql()")
print(generate_j1ql_r)

# list_alert_rules
list_alert_rules_r = j1.list_alert_rules()
print("list_configured_alert_rules()")
print(list_alert_rules_r)
print(len(list_alert_rules_r))

# get_alert_rule_details
get_alert_rule_details_r = j1.get_alert_rule_details(rule_id="<GUID>")
print("get_alert_rule_details()")
print(get_alert_rule_details_r)

# create_alert_rule
# polling_interval can be DISABLED, THIRTY_MINUTES, ONE_HOUR, FOUR_HOURS, EIGHT_HOURS, TWELVE_HOURS, ONE_DAY, or ONE_WEEK
# severity can be INFO, LOW, MEDIUM, HIGH, or CRITICAL
webhook_token = "<SECRET>"

webhook_action_config = {
            "type": "WEBHOOK",
            "endpoint": "https://webhook.domain.here/endpoint",
            "headers": {
              "Authorization": "Bearer {}".format(webhook_token),
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

create_alert_rule_r = j1.create_alert_rule(name="create_alert_rule-name",
                                           description="create_alert_rule-description",
                                           tags=['tag1', 'tag2'],
                                           polling_interval="DISABLED",
                                           severity="INFO",
                                           j1ql="find jupiterone_user")
print("create_alert_rule()")
print(create_alert_rule_r)

# delete_alert_rule
delete_alert_rule_r = j1.delete_alert_rule(rule_id="<GUID>")
print("delete_alert_rule()")
print(delete_alert_rule_r)

# update_alert_rule
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

# polling_interval can be DISABLED, THIRTY_MINUTES, ONE_HOUR, FOUR_HOURS, EIGHT_HOURS, TWELVE_HOURS, ONE_DAY, or ONE_WEEK
# tag_op can be OVERWRITE or APPEND
# severity can be INFO, LOW, MEDIUM, HIGH, or CRITICAL
# action_configs_op can be OVERWRITE or APPEND

update_alert_rule_r = j1.update_alert_rule(rule_id="GUID>",
                                           name="Updated Alert Rule Name",
                                           description="Updated Alert Rule Description",
                                           j1ql="find jupiterone_user",
                                           polling_interval="ONE_WEEK",
                                           tags=['tag1', 'tag2', 'tag3'],
                                           tag_op="OVERWRITE",
                                           severity="INFO",
                                           action_configs=alert_rule_config_tag,
                                           action_configs_op="OVERWRITE")
print("update_alert_rule()")
print(json.dumps(update_alert_rule_r, indent=1))

# evaluate_alert_rule
evaluate_alert_rule_r = j1.evaluate_alert_rule(rule_id="<GUID>")
print("evaluate_alert_rule()")
print(json.dumps(evaluate_alert_rule_r, indent=1))

# get_compliance_framework_item_details
r = j1.get_compliance_framework_item_details(item_id="<GUID>")
print("get_compliance_framework_item_details()")
print(json.dumps(r, indent=1))

# list alert rule evaluation results
r = j1.list_alert_rule_evaluation_results(rule_id="<GUID>")
print("list_alert_rule_evaluation_results()")
print(json.dumps(r, indent=1))

# fetch_evaluation_result_download_url
r = j1.fetch_evaluation_result_download_url(raw_data_key="RULE_EVALUATION/<GUID>/query0.json")
print("fetch_evaluation_result_download_url()")
print(json.dumps(r, indent=1))

# fetch_downloaded_evaluation_results
r = j1.fetch_downloaded_evaluation_results(download_url="https://download.us.jupiterone.io/<GUID>%2FRULE_EVALUATION%2F<GUID>%2F<epoch>%2Fquery0.json?token=<TOKEN>&Expires=<epoch>")
print("fetch_downloaded_evaluation_results()")
print(json.dumps(r, indent=1))


