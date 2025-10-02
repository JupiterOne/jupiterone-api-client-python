from jupiterone.client import JupiterOneClient
import random
import time
import os
import json

account = os.environ.get("JUPITERONE_ACCOUNT")
token = os.environ.get("JUPITERONE_TOKEN")
url = "https://graphql.us.jupiterone.io"

j1 = JupiterOneClient(account=account, token=token, url=url)

instance_id = "e7113c37-1ea8-4d00-9b82-c24952e70916"

sync_job = j1.start_sync_job(
            instance_id=instance_id,
            sync_mode="PATCH",
            source="integration-external"
        )

print(sync_job)
sync_job_id = sync_job['job'].get('id')

# Prepare entities payload
entities_payload = [
    {
      "_key": "server-001",
      "_type": "aws_ec2_instance",
      "_class": "Host",
      "displayName": "web-server-001",
      "instanceId": "i-1234567890abcdef0",
      "instanceType": "t3.micro",
      "state": "running",
      "tag.Environment": "production",
      "tag.Team": "engineering"
    },
    {
      "_key": "server-002",
      "_type": "aws_ec2_instance",
      "_class": "Host",
      "displayName": "web-server-002",
      "instanceId": "i-0987654321fedcba0",
      "instanceType": "t3.small",
      "state": "running",
      "tag.Environment": "staging",
      "tag.Team": "engineering"
    },
    {
      "_key": "database-001",
      "_type": "aws_rds_instance",
      "_class": "Database",
      "displayName": "prod-database",
      "dbInstanceIdentifier": "prod-db",
      "engine": "postgres",
      "dbInstanceClass": "db.t3.micro",
      "tag.Environment": "production",
      "tag.Team": "data"
    }
]

# Upload entities batch
result = j1.upload_entities_batch_json(
    instance_job_id=sync_job_id,
    entities_list=entities_payload
)
print(f"Uploaded {len(entities_payload)} entities")
print(result)

# Finalize the sync job
result = j1.finalize_sync_job(instance_job_id=sync_job_id)
print(f"Finalized sync job: {result['job']['id']}")

