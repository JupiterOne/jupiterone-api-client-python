from jupiterone.client import JupiterOneClient
import random
import time
import os

account = os.environ.get("JUPITERONE_ACCOUNT")
token = os.environ.get("JUPITERONE_TOKEN")

j1 = JupiterOneClient(account=account, token=token)

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

# create_integration_instance
create_integration_instance_r = j1.create_integration_instance(instance_name="testInstanceName",
                                                               instance_description="testInstanceDescription")
print("create_integration_instance()")
print(create_integration_instance_r)

# start_sync_job
start_sync_job_r = j1.start_sync_job(instance_id=create_integration_instance_r['id'])
print("start_sync_job()")
print(start_sync_job_r)

# upload_entities_batch_json
entity_payload = [
    {
      "_key": "1",
      "_type": "jupiterone-api-client-python",
      "_class": "API",
      "propertyName": "value"
    },
    {
      "_key": "2",
      "_type": "jupiterone-api-client-python",
      "_class": "API",
      "propertyName": "value"
    },
    {
      "_key": "3",
      "_type": "jupiterone-api-client-python",
      "_class": "API",
      "propertyName": "value"
    }
  ]

upload_entities_batch_json_r = j1.upload_entities_batch_json(instance_job_id=start_sync_job_r['job']['id'],
                                                             entities_list=entity_payload)
print("upload_entities_batch_json()")
print(upload_entities_batch_json_r)

# fetch_integration_jobs
fetch_integration_jobs_r = j1.fetch_integration_jobs(instance_id=create_integration_instance_r['id'])
print("fetch_integration_jobs()")
print(fetch_integration_jobs_r)

# fetch_integration_job_events
fetch_integration_job_events_r = j1.fetch_integration_job_events(instance_id=create_integration_instance_r['id'],
                                                                 instance_job_id=fetch_integration_jobs_r['jobs'][0]['id'])
print("fetch_integration_job_events()")
print(fetch_integration_job_events_r)

# finalize_sync_job
finalize_sync_job_r = j1.finalize_sync_job(instance_job_id=start_sync_job_r['job']['id'])
print("finalize_sync_job()")
print(finalize_sync_job_r)

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

# list_configured_alert_rules
list_configured_alert_rules_r = j1.list_configured_alert_rules()
print("list_configured_alert_rules()")
print(list_configured_alert_rules_r)

# generate_j1ql
generate_j1ql_r = j1.generate_j1ql(natural_language_prompt="show me all Users containing 'jupiterone' in their email address")
print("generate_j1ql()")
print(generate_j1ql_r)
