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
print(create_r)

properties = {
        'customProperty': 'customValUpdated'
    }

# update_entity
update_r = j1.update_entity(
    entity_id='{}'.format(create_r['entity']['_id']),
    properties=properties
)
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
print(create_r_2)

# create_relationship
create_relationship_r = j1.create_relationship(
    relationship_key='{}:{}'.format(create_r['entity']['_id'], create_r_2['entity']['_id']),
    relationship_type='jupiterone-api-client-python:create_relationship',
    relationship_class='HAS',
    from_entity_id=create_r['entity']['_id'],
    to_entity_id=create_r_2['entity']['_id']
)
print(create_relationship_r)

# delete_relationship
delete_relationship_r = j1.delete_relationship(relationship_id=create_relationship_r['relationship']['_id'])
print(delete_relationship_r)

# delete_entity
delete_entity_r1 = j1.delete_entity(entity_id=create_r['entity']['_id'])
print(delete_entity_r1)

delete_entity_r2 = j1.delete_entity(entity_id=create_r_2['entity']['_id'])
print(delete_entity_r2)


q = "FIND (Device | Person)"
cursor_query_r = j1._cursor_query(q)
print(cursor_query_r)
print(len(cursor_query_r['data']))
