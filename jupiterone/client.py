""" Python SDK for JupiterOne GraphQL API """
# pylint: disable=W0212,no-name-in-module
# see https://github.com/PyCQA/pylint/issues/409

import json
from warnings import warn
from typing import Dict, List
from datetime import datetime

import re
import requests
from requests.adapters import HTTPAdapter, Retry
from retrying import retry

from jupiterone.errors import (
    JupiterOneClientError,
    JupiterOneApiRetryError,
    JupiterOneApiError,
)

from jupiterone.constants import (
    J1QL_SKIP_COUNT,
    J1QL_LIMIT_COUNT,
    QUERY_V1,
    CREATE_ENTITY,
    DELETE_ENTITY,
    UPDATE_ENTITY,
    CREATE_RELATIONSHIP,
    UPDATE_RELATIONSHIP,
    DELETE_RELATIONSHIP,
    CURSOR_QUERY_V1,
    CREATE_INSTANCE,
    INTEGRATION_JOB_VALUES,
    INTEGRATION_INSTANCE_EVENT_VALUES,
    ALL_PROPERTIES,
    CREATE_SMARTCLASS,
    CREATE_SMARTCLASS_QUERY,
    EVALUATE_SMARTCLASS,
    GET_SMARTCLASS_DETAILS,
    LIST_RULE_INSTANCES,
    J1QL_FROM_NATURAL_LANGUAGE
)


def retry_on_429(exc):
    """Used to trigger retry on rate limit"""
    return isinstance(exc, JupiterOneApiRetryError)


class JupiterOneClient:
    """Python client class for the JupiterOne GraphQL API"""

    # pylint: disable=too-many-instance-attributes

    DEFAULT_URL = "https://graphql.us.jupiterone.io"
    SYNC_API_URL = "https://api.us.jupiterone.io"

    RETRY_OPTS = {
        "wait_exponential_multiplier": 1000,
        "wait_exponential_max": 10000,
        "stop_max_delay": 300000,
        "retry_on_exception": retry_on_429,
    }

    def __init__(self, account: str = None, token: str = None, url: str = DEFAULT_URL, sync_url: str = SYNC_API_URL):
        self.account = account
        self.token = token
        self.graphql_url = url
        self.sync_url = sync_url
        self.headers = {
            "Authorization": "Bearer {}".format(self.token),
            "JupiterOne-Account": self.account,
            "Content-Type": "application/json"
        }

    @property
    def account(self):
        """Your JupiterOne account ID"""
        return self._account

    @account.setter
    def account(self, value: str):
        """Your JupiterOne account ID"""
        if not value:
            raise JupiterOneClientError("account is required")
        self._account = value

    @property
    def token(self):
        """Your JupiterOne access token"""
        return self._token

    @token.setter
    def token(self, value: str):
        """Your JupiterOne access token"""
        if not value:
            raise JupiterOneClientError("token is required")
        self._token = value

    # pylint: disable=R1710
    @retry(**RETRY_OPTS)
    def _execute_query(self, query: str, variables: Dict = None) -> Dict:
        """Executes query against graphql endpoint"""

        data = {"query": query}
        if variables:
            data.update(variables=variables)

        # Always ask for variableResultSize
        data.update(flags={"variableResultSize": True})

        # initiate requests session and implement retry logic of 5 request retries with 1 second between
        s = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        response = s.post(
            self.graphql_url, headers=self.headers, json=data, timeout=60
        )

        # It is still unclear if all responses will have a status
        # code of 200 or if 429 will eventually be used to
        # indicate rate limits being hit.  J1 devs are aware.
        if response.status_code == 200:
            if response._content:
                content = json.loads(response._content)
                if "errors" in content:
                    errors = content["errors"]
                    if len(errors) == 1:
                        if "429" in errors[0]["message"]:
                            raise JupiterOneApiRetryError(
                                "JupiterOne API rate limit exceeded"
                            )
                    raise JupiterOneApiError(content.get("errors"))
                return response.json()

        elif response.status_code == 401:
            raise JupiterOneApiError(
                "401: Unauthorized. Please supply a valid account id and API token."
            )

        elif response.status_code in [429, 503]:
            raise JupiterOneApiRetryError("JupiterOne API rate limit exceeded.")

        elif response.status_code in [504]:
            raise JupiterOneApiRetryError("Gateway Timeout.")

        elif response.status_code in [500]:
            raise JupiterOneApiError("JupiterOne API internal server error.")

        else:
            content = response._content
            if isinstance(content, (bytes, bytearray)):
                content = content.decode("utf-8")
            if "application/json" in response.headers.get("Content-Type", "text/plain"):
                data = json.loads(content)
                content = data.get("error", data.get("errors", content))
            raise JupiterOneApiError("{}:{}".format(response.status_code, content))

    def _cursor_query(
        self, query: str, cursor: str = None, include_deleted: bool = False
    ) -> Dict:
        """Performs a V1 graph query using cursor pagination
        args:
            query (str): Query text
            cursor (str): A pagination cursor for the initial query
            include_deleted (bool): Include recently deleted entities in query/search
        """

        # If the query itself includes a LIMIT then we must parse that and check if we've reached
        # or exceeded the required number of results.
        limit_match = re.search(r"(?i)LIMIT\s+(?P<inline_limit>\d+)", query)

        if limit_match:
            result_limit = int(limit_match.group("inline_limit"))
        else:
            result_limit = False

        results: List = []
        while True:
            variables = {"query": query, "includeDeleted": include_deleted}

            if cursor is not None:
                variables["cursor"] = cursor

            response = self._execute_query(query=CURSOR_QUERY_V1, variables=variables)
            data = response["data"]["queryV1"]["data"]

            # This means it's a "TREE" query and we have everything
            if "vertices" in data and "edges" in data:
                return data

            results.extend(data)

            if result_limit and len(results) >= result_limit:
                # We can stop paginating if we've collected enough results based on the requested limit
                break
            elif (
                "cursor" in response["data"]["queryV1"]
                and response["data"]["queryV1"]["cursor"] is not None
            ):
                # We got a cursor and haven't collected enough results
                cursor = response["data"]["queryV1"]["cursor"]
            else:
                # No cursor returned so we're done
                break

        # If we detected an inline LIMIT make sure we only return that many results
        if result_limit:
            return {"data": results[:result_limit]}

        # Return everything
        return {"data": results}

    def _limit_and_skip_query(
        self,
        query: str,
        skip: int = J1QL_SKIP_COUNT,
        limit: int = J1QL_LIMIT_COUNT,
        include_deleted: bool = False,
    ) -> Dict:
        results: List = []
        page: int = 0

        while True:
            variables = {
                "query": f"{query} SKIP {page * skip} LIMIT {limit}",
                "includeDeleted": include_deleted,
            }
            response = self._execute_query(query=QUERY_V1, variables=variables)

            data = response["data"]["queryV1"]["data"]

            # If tree query then no pagination
            if "vertices" in data and "edges" in data:
                return data

            if len(data) < J1QL_SKIP_COUNT:
                results.extend(data)
                break

            results.extend(data)
            page += 1

        return {"data": results}

    def _execute_syncapi_request(self, endpoint: str, payload: Dict = None) -> Dict:
        """Executes POST request to SyncAPI endpoints"""

        # initiate requests session and implement retry logic of 5 request retries with 1 second between
        s = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        response = s.post(
            self.sync_url + endpoint, headers=self.headers, json=payload, timeout=60
        )

        # It is still unclear if all responses will have a status
        # code of 200 or if 429 will eventually be used to
        # indicate rate limits being hit.  J1 devs are aware.
        if response.status_code == 200:
            if response._content:
                content = json.loads(response._content)
                if "errors" in content:
                    errors = content["errors"]
                    if len(errors) == 1:
                        if "429" in errors[0]["message"]:
                            raise JupiterOneApiRetryError(
                                "JupiterOne API rate limit exceeded"
                            )
                    raise JupiterOneApiError(content.get("errors"))
                return response.json()

        elif response.status_code == 401:
            raise JupiterOneApiError(
                "401: Unauthorized. Please supply a valid account id and API token."
            )

        elif response.status_code in [429, 503]:
            raise JupiterOneApiRetryError("JupiterOne API rate limit exceeded.")

        elif response.status_code in [504]:
            raise JupiterOneApiRetryError("Gateway Timeout.")

        elif response.status_code in [500]:
            raise JupiterOneApiError("JupiterOne API internal server error.")

        else:
            content = response._content
            if isinstance(content, (bytes, bytearray)):
                content = content.decode("utf-8")
            if "application/json" in response.headers.get("Content-Type", "text/plain"):
                data = json.loads(content)
                content = data.get("error", data.get("errors", content))
            raise JupiterOneApiError("{}:{}".format(response.status_code, content))

    def query_v1(self, query: str, **kwargs) -> Dict:
        """Performs a V1 graph query
        args:
            query (str): Query text
            skip (int):  Skip entity count
            limit (int): Limit entity count
            cursor (str): A pagination cursor for the initial query
            include_deleted (bool): Include recently deleted entities in query/search
        """
        uses_limit_and_skip: bool = "skip" in kwargs.keys() or "limit" in kwargs.keys()
        skip: int = kwargs.pop("skip", J1QL_SKIP_COUNT)
        limit: int = kwargs.pop("limit", J1QL_LIMIT_COUNT)
        include_deleted: bool = kwargs.pop("include_deleted", False)
        cursor: str = kwargs.pop("cursor", None)

        if uses_limit_and_skip:
            warn(
                "limit and skip pagination is no longer a recommended method for pagination. "
                "To read more about using cursors checkout the JupiterOne documentation: "
                "https://docs.jupiterone.io/features/admin/parameters#query-parameterlist",
                DeprecationWarning,
                stacklevel=2,
            )
            return self._limit_and_skip_query(
                query=query, skip=skip, limit=limit, include_deleted=include_deleted
            )
        else:
            return self._cursor_query(
                query=query, cursor=cursor, include_deleted=include_deleted
            )

    def create_entity(self, **kwargs) -> Dict:
        """Creates an entity in graph.  It will also update an existing entity.

        args:
            entity_key (str): Unique key for the entity
            entity_type (str): Value for _type of entity
            entity_class (str): Value for _class of entity
            timestamp (int): Specify createdOn timestamp
            properties (dict): Dictionary of key/value entity properties
        """
        variables = {
            "entityKey": kwargs.pop("entity_key"),
            "entityType": kwargs.pop("entity_type"),
            "entityClass": kwargs.pop("entity_class"),
        }

        timestamp: int = kwargs.pop("timestamp", None)
        properties: Dict = kwargs.pop("properties", None)

        if timestamp:
            variables.update(timestamp=timestamp)
        if properties:
            variables.update(properties=properties)

        response = self._execute_query(query=CREATE_ENTITY, variables=variables)
        return response["data"]["createEntity"]

    def delete_entity(self, entity_id: str = None) -> Dict:
        """Deletes an entity from the graph.  Note this is a hard delete.

        args:
            entity_id (str): Entity ID for entity to delete
        """
        variables = {"entityId": entity_id}
        response = self._execute_query(DELETE_ENTITY, variables=variables)
        return response["data"]["deleteEntity"]

    def update_entity(self, entity_id: str = None, properties: Dict = None) -> Dict:
        """
        Update an existing entity.

        args:
            entity_id (str): The _id of the entity to update
            properties (dict): Dictionary of key/value entity properties
        """
        variables = {"entityId": entity_id, "properties": properties}
        response = self._execute_query(UPDATE_ENTITY, variables=variables)
        return response["data"]["updateEntity"]

    def create_relationship(self, **kwargs) -> Dict:
        """
        Create a relationship (edge) between two entities (vertices).

        args:
            relationship_key (str): Unique key for the relationship
            relationship_type (str): Value for _type of relationship
            relationship_class (str): Value for _class of relationship
            from_entity_id (str): Entity ID of the source vertex
            to_entity_id (str): Entity ID of the destination vertex
        """
        variables = {
            "relationshipKey": kwargs.pop("relationship_key"),
            "relationshipType": kwargs.pop("relationship_type"),
            "relationshipClass": kwargs.pop("relationship_class"),
            "fromEntityId": kwargs.pop("from_entity_id"),
            "toEntityId": kwargs.pop("to_entity_id"),
        }

        properties = kwargs.pop("properties", None)
        if properties:
            variables["properties"] = properties

        response = self._execute_query(query=CREATE_RELATIONSHIP, variables=variables)
        return response["data"]["createRelationship"]

    def update_relationship(self, **kwargs) -> Dict:
        """
        Update a relationship (edge) between two entities (vertices).

        args:
            relationship_id (str): Unique _id of the relationship
            properties (dict): Dictionary of key/value relationship properties
        """
        now_dt = datetime.now()

        variables = {
            "relationshipId": kwargs.pop("relationship_id"),
            "timestamp": datetime.strptime(str(now_dt), "%Y-%m-%d %H:%M:%S.%f").timestamp()
        }

        properties = kwargs.pop("properties", None)
        if properties:
            variables["properties"] = properties

        response = self._execute_query(query=UPDATE_RELATIONSHIP, variables=variables)
        return response["data"]["updateRelationship"]

    def delete_relationship(self, relationship_id: str = None):
        """Deletes a relationship between two entities.

        args:
            relationship_id (str): The ID of the relationship
        """
        variables = {"relationshipId": relationship_id}

        response = self._execute_query(DELETE_RELATIONSHIP, variables=variables)
        return response["data"]["deleteRelationship"]

    def create_integration_instance(self,
                                    instance_name: str = None,
                                    instance_description: str = None,
                                    integration_definition_id: str = "8013680b-311a-4c2e-b53b-c8735fd97a5c"):
        """Creates a new Custom Integration Instance.

        args:
            instance_name (str): The "Account name" for integration instance
            instance_description (str): The "Description" for integration instance
            integration_definition_id (str): The "Integration definition ID" for integration instance,
            if no parameter is passed, then the Custom Integration definition ID will be used.
        """
        variables = {
                  "instance": {
                    "name": instance_name,
                    "description": instance_description,
                    "integrationDefinitionId": integration_definition_id,
                    "pollingInterval": "DISABLED",
                    "config": {
                      "@tag": {
                        "Production": False,
                        "AccountName": True
                      }
                    },
                    "pollingIntervalCronExpression": {},
                    "ingestionSourcesOverrides": []
                  }
        }

        response = self._execute_query(CREATE_INSTANCE, variables=variables)
        return response['data']['createIntegrationInstance']

    def fetch_all_entity_properties(self):
        """Fetch list of aggregated property keys from all entities in the graph.

        """

        response = self._execute_query(query=ALL_PROPERTIES)

        return_list = []

        for i in response['data']['getAllAssetProperties']:

            if i.startswith(('parameter.', 'tag.')) == False:

                return_list.append(i)

        return return_list

    def fetch_all_entity_tags(self):
        """Fetch list of aggregated property keys from all entities in the graph.

        """

        response = self._execute_query(query=ALL_PROPERTIES)

        return_list = []

        for i in response['data']['getAllAssetProperties']:

            if i.startswith(('tag.')) == True:

                return_list.append(i)

        return return_list

    def start_sync_job(self, instance_id: str = None):
        """Start a synchronization job.

        args:
            instance_id (str): The "integrationInstanceId" request param for synchronization job
        """
        endpoint = "/persister/synchronization/jobs"

        data = {
               "source": "integration-managed",
               "integrationInstanceId": instance_id
               }

        response = self._execute_syncapi_request(endpoint=endpoint, payload=data)

        return response

    def upload_entities_batch_json(self, instance_job_id: str = None, entities_list: list = None):
        """Upload batch of entities.

        args:
            instance_job_id (str): The "Job ID" for the Custom Integration job
            entities_list (list): List of Dictionaries containing entities data to upload
        """
        endpoint = f"/persister/synchronization/jobs/{instance_job_id}/entities"

        data = {
               "entities": entities_list
        }

        response = self._execute_syncapi_request(endpoint=endpoint, payload=data)

        return response

    def upload_relationships_batch_json(self, instance_job_id: str = None, relationships_list: list = None):
        """Upload batch of relationships.

        args:
            instance_job_id (str): The "Job ID" for the Custom Integration job
            relationships_list (list): List of Dictionaries containing relationships data to upload
        """
        endpoint = f"/persister/synchronization/jobs/{instance_job_id}/relationships"

        data = {
               "relationships": relationships_list
        }

        response = self._execute_syncapi_request(endpoint=endpoint, payload=data)

        return response

    def upload_combined_batch_json(self, instance_job_id: str = None, combined_payload: Dict = None):
        """Upload batch of entities and relationships together.

        args:
            instance_job_id (str): The "Job ID" for the Custom Integration job.
            combined_payload (list): Dictionary containing combined entities and relationships data to upload.
        """
        endpoint = f"/persister/synchronization/jobs/{instance_job_id}/upload"

        response = self._execute_syncapi_request(endpoint=endpoint, payload=combined_payload)

        return response

    def bulk_delete_entities(self, instance_job_id: str = None, entities_list: list = None):
        """Send a request to bulk delete existing entities.

        args:
            instance_job_id (str): The "Job ID" for the Custom Integration job.
            entities_list (list): List of dictionaries containing entities _id's to be deleted.
        """
        endpoint = f"/persister/synchronization/jobs/{instance_job_id}/upload"

        data = {
            "deleteEntities": entities_list
        }

        response = self._execute_syncapi_request(endpoint=endpoint, payload=data)

        return response

    def finalize_sync_job(self, instance_job_id: str = None):
        """Start a synchronization job.

        args:
            instance_job_id (str): The "Job ID" for the Custom Integration job
        """
        endpoint = f"/persister/synchronization/jobs/{instance_job_id}/finalize"

        data = {}

        response = self._execute_syncapi_request(endpoint=endpoint, payload=data)

        return response

    def fetch_integration_jobs(self, instance_id: str = None):
        """Fetch Integration Job details from defined integration instance.

        args:
            instance_id (str): The "integrationInstanceId" of the integration to fetch jobs from.
        """
        variables = {
                    "integrationInstanceId": instance_id,
                    "size": 100
        }

        response = self._execute_query(INTEGRATION_JOB_VALUES, variables=variables)

        return response['data']['integrationJobs']

    def fetch_integration_job_events(self, instance_id: str = None, instance_job_id: str = None):
        """Fetch events within an integration job run.

        args:
            instance_id (str): The integration Instance Id of the integration to fetch job events from.
            instance_job_id (str): The integration Job ID of the integration to fetch job events from.
        """
        variables = {
                    "integrationInstanceId": instance_id,
                    "jobId": instance_job_id,
                    "size": 1000
        }

        response = self._execute_query(INTEGRATION_INSTANCE_EVENT_VALUES, variables=variables)

        return response['data']['integrationEvents']

    def create_smartclass(self, smartclass_name: str = None, smartclass_description: str = None):
        """Creates a new Smart Class within Assets.

        args:
            smartclass_name (str): The "Smart class name" for Smart Class to be created.
            smartclass_description (str): The "Description" for Smart Class to be created.
        """
        variables = {
                    "input": {
                        "tagName": smartclass_name,
                        "description": smartclass_description
                    }
        }

        response = self._execute_query(CREATE_SMARTCLASS, variables=variables)

        return response['data']['createSmartClass']

    def create_smartclass_query(self, smartclass_id: str = None, query: str = None, query_description: str = None):
        """Creates a new J1QL Query within a defined Smart Class.

        args:
            smartclass_id (str): The unique ID of the Smart Class the query is created within.
            query (str): The J1QL for the query being created.
            query_description (str): The description of the query being created.
        """
        variables = {
                    "input": {
                        "smartClassId": smartclass_id,
                        "query": query,
                        "description": query_description
                    }
        }

        response = self._execute_query(CREATE_SMARTCLASS_QUERY, variables=variables)

        return response['data']['createSmartClassQuery']

    def evaluate_smartclass(self, smartclass_id: str = None):
        """Execute an on-demand Evaluation of a defined Smartclass.

        args:
            smartclass_id (str): The unique ID of the Smart Class to trigger the evaluation for.
        """
        variables = {
                    "smartClassId": smartclass_id
        }

        response = self._execute_query(EVALUATE_SMARTCLASS, variables=variables)

        return response['data']['evaluateSmartClassRule']

    def get_smartclass_details(self, smartclass_id: str = None):
        """Fetch config details from defined Smart Class.

        args:
            smartclass_id (str): The unique ID of the Smart Class to fetch details from.
        """
        variables = {
                    "id": smartclass_id
        }

        response = self._execute_query(GET_SMARTCLASS_DETAILS, variables=variables)

        return response['data']['smartClass']

    def list_configured_alert_rules(self):
        """List defined Alert Rules configured in J1 account

        """
        variables = {
                    "limit": 100
        }

        response = self._execute_query(LIST_RULE_INSTANCES, variables=variables)

        return response['data']['listRuleInstances']

    def generate_j1ql(self, natural_language_prompt: str = None):
        """Generate J1QL query syntax from natural language user input.

        args:
            natural_language_prompt (str): The naturalLanguageQuery prompt input to generate J1QL from.
        """
        variables = {
            "input": {
                "naturalLanguageQuery": natural_language_prompt
            }
        }

        response = self._execute_query(J1QL_FROM_NATURAL_LANGUAGE, variables=variables)

        return response['data']['j1qlFromNaturalLanguage']
