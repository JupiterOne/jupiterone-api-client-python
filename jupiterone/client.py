""" Python SDK for JupiterOne GraphQL API """
import json
from warnings import warn
from typing import Dict, List, Union, Optional
from datetime import datetime
import time
import re
import requests
from requests.adapters import HTTPAdapter, Retry
import concurrent.futures

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
    UPDATE_RELATIONSHIPV2,
    DELETE_RELATIONSHIP,
    CURSOR_QUERY_V1,
    DEFERRED_RESPONSE_QUERY,
    CREATE_INSTANCE,
    INTEGRATION_JOB_VALUES,
    INTEGRATION_INSTANCE_EVENT_VALUES,
    ALL_PROPERTIES,
    GET_ENTITY_RAW_DATA,
    CREATE_SMARTCLASS,
    CREATE_SMARTCLASS_QUERY,
    EVALUATE_SMARTCLASS,
    GET_SMARTCLASS_DETAILS,
    J1QL_FROM_NATURAL_LANGUAGE,
    LIST_RULE_INSTANCES,
    CREATE_RULE_INSTANCE,
    DELETE_RULE_INSTANCE,
    UPDATE_RULE_INSTANCE,
    EVALUATE_RULE_INSTANCE,
    QUESTIONS,
    COMPLIANCE_FRAMEWORK_ITEM,
    LIST_COLLECTION_RESULTS,
    GET_RAW_DATA_DOWNLOAD_URL,
    FIND_INTEGRATION_DEFINITION,
    INTEGRATION_INSTANCES,
    INTEGRATION_INSTANCE,
    UPDATE_INTEGRATION_INSTANCE,
    PARAMETER,
    PARAMETER_LIST,
    UPSERT_PARAMETER,
)

class JupiterOneClient:
    """Python client class for the JupiterOne GraphQL API"""

    # pylint: disable=too-many-instance-attributes

    DEFAULT_URL = "https://graphql.us.jupiterone.io"
    SYNC_API_URL = "https://api.us.jupiterone.io"

    def __init__(
        self,
        account: str = None,
        token: str = None,
        url: str = DEFAULT_URL,
        sync_url: str = SYNC_API_URL,
    ):
        self.account = account
        self.token = token
        self.graphql_url = url
        self.sync_url = sync_url
        self.headers = {
            "Authorization": "Bearer {}".format(self.token),
            "JupiterOne-Account": self.account,
            "Content-Type": "application/json",
        }

        # Initialize session with retry logic
        self.session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 502, 503, 504],
            allowed_methods=["POST", "GET"]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

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
    def _execute_query(self, query: str, variables: Dict = None) -> Dict:
        """Executes query against graphql endpoint"""

        data = {"query": query}
        if variables:
            data.update(variables=variables)

        # Always ask for variableResultSize
        data.update(flags={"variableResultSize": True})

        response = self.session.post(
            self.graphql_url,
            headers=self.headers,
            json=data,
            timeout=60
        )

        # It is still unclear if all responses will have a status
        # code of 200 or if 429 will eventually be used to
        # indicate rate limits being hit.  J1 devs are aware.
        if response.status_code == 200:
            content = response.json()
            if "errors" in content:
                errors = content["errors"]
                if len(errors) == 1 and "429" in errors[0]["message"]:
                    raise JupiterOneApiRetryError(
                        "JupiterOne API rate limit exceeded"
                    )
                raise JupiterOneApiError(content.get("errors"))
            return content

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
                data = response.json()
                content = data.get("error", data.get("errors", content))
            raise JupiterOneApiError("{}:{}".format(response.status_code, content))

    def _cursor_query(
        self,
        query: str,
        cursor: str = None,
        include_deleted: bool = False,
        max_workers: Optional[int] = None
    ) -> Dict:
        """Performs a V1 graph query using cursor pagination with optional parallel processing

        args:
            query (str): Query text
            cursor (str): A pagination cursor for the initial query
            include_deleted (bool): Include recently deleted entities in query/search
            max_workers (int, optional): Maximum number of parallel workers for fetching pages
        """

        # If the query itself includes a LIMIT then we must parse that and check if we've reached
        # or exceeded the required number of results.
        limit_match = re.search(r"(?i)LIMIT\s+(?P<inline_limit>\d+)", query)

        if limit_match:
            result_limit = int(limit_match.group("inline_limit"))
        else:
            result_limit = False

        results: List = []

        def fetch_page(cursor: Optional[str] = None) -> Dict:
            variables = {"query": query, "includeDeleted": include_deleted}
            if cursor is not None:
                variables["cursor"] = cursor
            return self._execute_query(query=CURSOR_QUERY_V1, variables=variables)

        # First page to get initial cursor and data
        response = fetch_page(cursor)
        data = response["data"]["queryV1"]["data"]

        # This means it's a "TREE" query and we have everything
        if "vertices" in data and "edges" in data:
            return data

        results.extend(data)

        # If no cursor or we've hit the limit, return early
        if not response["data"]["queryV1"].get("cursor") or (result_limit and len(results) >= result_limit):
            return {"data": results[:result_limit] if result_limit else results}

        # If parallel processing is enabled and we have more pages to fetch
        if max_workers and max_workers > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_cursor = {
                    executor.submit(fetch_page, response["data"]["queryV1"]["cursor"]):
                    response["data"]["queryV1"]["cursor"]
                }

                while future_to_cursor:
                    # Wait for the next future to complete
                    done, _ = concurrent.futures.wait(
                        future_to_cursor,
                        return_when=concurrent.futures.FIRST_COMPLETED
                    )

                    for future in done:
                        cursor = future_to_cursor.pop(future)
                        try:
                            response = future.result()
                            page_data = response["data"]["queryV1"]["data"]
                            results.extend(page_data)

                            # Check if we need to fetch more pages
                            if (result_limit and len(results) >= result_limit) or \
                               not response["data"]["queryV1"].get("cursor"):
                                # Cancel remaining futures
                                for f in future_to_cursor:
                                    f.cancel()
                                future_to_cursor.clear()
                                break

                            # Schedule next page fetch
                            next_cursor = response["data"]["queryV1"]["cursor"]
                            future_to_cursor[executor.submit(fetch_page, next_cursor)] = next_cursor

                        except Exception as e:
                            # Log error but continue with other pages
                            print(f"Error fetching page with cursor {cursor}: {str(e)}")
        else:
            # Sequential processing
            while True:
                cursor = response["data"]["queryV1"]["cursor"]
                response = fetch_page(cursor)
                data = response["data"]["queryV1"]["data"]
                results.extend(data)

                if result_limit and len(results) >= result_limit:
                    break
                elif not response["data"]["queryV1"].get("cursor"):
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

    def query_with_deferred_response(self, query, cursor=None):
        """
        Execute a J1QL query that returns a deferred response for handling large result sets.

        Args:
            query (str): The J1QL query to execute
            cursor (str, optional): Pagination cursor for subsequent requests

        Returns:
            list: Combined results from all paginated responses
        """
        all_query_results = []
        current_cursor = cursor

        while True:
            variables = {
                "query": query,
                "deferredResponse": "FORCE",
                "cursor": current_cursor,
                "flags": {"variableResultSize": True}
            }

            payload = {
                "query": DEFERRED_RESPONSE_QUERY,
                "variables": variables
            }

            # Use session with retries for reliability
            max_retries = 5
            backoff_factor = 2

            for attempt in range(1, max_retries + 1):

                # Get the download URL
                url_response = self.session.post(
                    self.graphql_url,
                    headers=self.headers,
                    json=payload,
                    timeout=60
                )

                if url_response.status_code == 429:
                    retry_after = int(url_response.headers.get("Retry-After", backoff_factor ** attempt))
                    print(f"Rate limited. Retrying in {retry_after} seconds...")
                    time.sleep(retry_after)
                else:
                    break  # Exit on success or other non-retryable error

            if url_response.ok:

                download_url = url_response.json()['data']['queryV1']['url']

                # Poll the download URL until results are ready
                while True:
                    download_response = self.session.get(download_url, timeout=60).json()
                    status = download_response['status']

                    if status != 'IN_PROGRESS':
                        break

                    time.sleep(0.2)  # Sleep 200 milliseconds between checks

                # Add results to the collection
                all_query_results.extend(download_response['data'])

                # Check for more pages
                if 'cursor' in download_response:
                    current_cursor = download_response['cursor']
                else:
                    break

            else:
                print(f"Request failed after {max_retries} attempts. Status: {url_response.status_code}")

        return all_query_results

    def _execute_syncapi_request(self, endpoint: str, payload: Dict = None) -> Dict:
        """Executes POST request to SyncAPI endpoints"""

        # initiate requests session and implement retry logic of 5 request retries with 1 second between retries
        response = self.session.post(
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
            "relationship": {"_id": kwargs.pop("relationship_id")},
            "timestamp": int(datetime.now().timestamp() * 1000),
        }

        properties = kwargs.pop("properties", None)
        if properties:
            variables["relationship"].update(properties)

        response = self._execute_query(query=UPDATE_RELATIONSHIPV2, variables=variables)
        return response["data"]["updateRelationshipV2"]

    def delete_relationship(self, relationship_id: str = None):
        """Deletes a relationship between two entities.

        args:
            relationship_id (str): The ID of the relationship
        """
        variables = {"relationshipId": relationship_id}

        response = self._execute_query(DELETE_RELATIONSHIP, variables=variables)
        return response["data"]["deleteRelationship"]

    def create_integration_instance(
        self,
        instance_name: str = None,
        instance_description: str = None,
        integration_definition_id: str = "8013680b-311a-4c2e-b53b-c8735fd97a5c",
    ):
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
                "config": {"@tag": {"Production": False, "AccountName": True}},
                "pollingIntervalCronExpression": {},
                "ingestionSourcesOverrides": [],
            }
        }

        response = self._execute_query(CREATE_INSTANCE, variables=variables)
        return response["data"]["createIntegrationInstance"]

    def fetch_all_entity_properties(self):
        """Fetch list of aggregated property keys from all entities in the graph."""

        response = self._execute_query(query=ALL_PROPERTIES)

        return_list = []

        for i in response["data"]["getAllAssetProperties"]:

            if i.startswith(("parameter.", "tag.")) == False:

                return_list.append(i)

        return return_list

    def fetch_all_entity_tags(self):
        """Fetch list of aggregated property keys from all entities in the graph."""

        response = self._execute_query(query=ALL_PROPERTIES)

        return_list = []

        for i in response["data"]["getAllAssetProperties"]:

            if i.startswith(("tag.")) == True:

                return_list.append(i)

        return return_list

    def fetch_entity_raw_data(self, entity_id: str = None):
        """Fetch the contents of raw data for a given entity in a J1 Account."""
        variables = {"entityId": entity_id, "source": "integration-managed"}

        response = self._execute_query(query=GET_ENTITY_RAW_DATA, variables=variables)

        return response

    def start_sync_job(
        self,
        instance_id: str = None,
        sync_mode: str = None,
        source: str = None,
    ):
        """Start a synchronization job.

        args:
            instance_id (str): The "integrationInstanceId" request param for synchronization job
            sync_mode (str): The "syncMode" request body property for synchronization job. "DIFF", "CREATE_OR_UPDATE", or "PATCH"
            source (str): The "source" request body property for synchronization job. "api" or "integration-external"
        """
        endpoint = "/persister/synchronization/jobs"

        data = {
               "source": source,
               "syncMode": sync_mode
        }

        if instance_id is not None:
            data["integrationInstanceId"] = instance_id

        response = self._execute_syncapi_request(endpoint=endpoint, payload=data)

        return response

    def upload_entities_batch_json(
        self, instance_job_id: str = None, entities_list: list = None
    ):
        """Upload batch of entities.

        args:
            instance_job_id (str): The "Job ID" for the Custom Integration job
            entities_list (list): List of Dictionaries containing entities data to upload
        """
        endpoint = f"/persister/synchronization/jobs/{instance_job_id}/entities"

        data = {"entities": entities_list}

        response = self._execute_syncapi_request(endpoint=endpoint, payload=data)

        return response

    def upload_relationships_batch_json(
        self, instance_job_id: str = None, relationships_list: list = None
    ):
        """Upload batch of relationships.

        args:
            instance_job_id (str): The "Job ID" for the Custom Integration job
            relationships_list (list): List of Dictionaries containing relationships data to upload
        """
        endpoint = f"/persister/synchronization/jobs/{instance_job_id}/relationships"

        data = {"relationships": relationships_list}

        response = self._execute_syncapi_request(endpoint=endpoint, payload=data)

        return response

    def upload_combined_batch_json(
        self, instance_job_id: str = None, combined_payload: Dict = None
    ):
        """Upload batch of entities and relationships together.

        args:
            instance_job_id (str): The "Job ID" for the Custom Integration job.
            combined_payload (list): Dictionary containing combined entities and relationships data to upload.
        """
        endpoint = f"/persister/synchronization/jobs/{instance_job_id}/upload"

        response = self._execute_syncapi_request(
            endpoint=endpoint, payload=combined_payload
        )

        return response

    def bulk_delete_entities(
        self, instance_job_id: str = None, entities_list: list = None
    ):
        """Send a request to bulk delete existing entities.

        args:
            instance_job_id (str): The "Job ID" for the Custom Integration job.
            entities_list (list): List of dictionaries containing entities _id's to be deleted.
        """
        endpoint = f"/persister/synchronization/jobs/{instance_job_id}/upload"

        data = {"deleteEntities": entities_list}

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
        variables = {"integrationInstanceId": instance_id, "size": 100}

        response = self._execute_query(INTEGRATION_JOB_VALUES, variables=variables)

        return response["data"]["integrationJobs"]

    def fetch_integration_job_events(
        self, instance_id: str = None, instance_job_id: str = None
    ):
        """Fetch events within an integration job run.

        args:
            instance_id (str): The integration Instance Id of the integration to fetch job events from.
            instance_job_id (str): The integration Job ID of the integration to fetch job events from.
        """
        variables = {
            "integrationInstanceId": instance_id,
            "jobId": instance_job_id,
            "size": 1000,
        }

        response = self._execute_query(
            INTEGRATION_INSTANCE_EVENT_VALUES, variables=variables
        )

        return response["data"]["integrationEvents"]

    def get_integration_definition_details(self, integration_type: str = None):
        """Fetch the Integration Definition Details for a given integration type."""
        variables = {"integrationType": integration_type, "includeConfig": True}

        response = self._execute_query(FIND_INTEGRATION_DEFINITION, variables=variables)
        return response

    def fetch_integration_instances(self, definition_id: str = None):
        """Fetch all configured Instances for a given integration type."""
        variables = {"definitionId": definition_id, "limit": 100}

        response = self._execute_query(INTEGRATION_INSTANCES, variables=variables)
        return response

    def get_integration_instance_details(self, instance_id: str = None):
        """Fetch configuration details for a single configured Integration Instance."""
        variables = {"integrationInstanceId": instance_id}

        response = self._execute_query(INTEGRATION_INSTANCE, variables=variables)
        return response

    def update_integration_instance_config_value(
        self, instance_id: str = None, config_key: str = None, config_value: str = None
    ):
        """Update a single config k:v pair existing on a configured Integration Instance."""

        # fetch existing instance configuration
        instance_config = self.get_integration_instance_details(instance_id=instance_id)
        config_dict = instance_config["data"]["integrationInstance"]["config"]

        if str(config_dict.get(config_key, "Not Found")) != "Not Found":

            # update config key value with new provided value
            config_dict[config_key] = config_value
            instance_config["data"]["integrationInstance"]["config"] = config_dict

            # remove externalId to not include in update payload
            if "externalId" in instance_config["data"]["integrationInstance"]["config"]:
                del instance_config["data"]["integrationInstance"]["config"][
                    "externalId"
                ]

            # prepare variables GraphQL payload for updating config
            instance_details = instance_config["data"]["integrationInstance"]

            variables = {
                "id": instance_details["id"],
                "update": {
                    "pollingInterval": instance_details["pollingInterval"],
                    "config": instance_details["config"],
                    "description": instance_details["description"],
                    "name": instance_details["name"],
                    "collectorPoolId": instance_details["collectorPoolId"],
                    "pollingIntervalCronExpression": instance_details[
                        "pollingIntervalCronExpression"
                    ],
                    "ingestionSourcesOverrides": instance_details[
                        "ingestionSourcesOverrides"
                    ],
                },
            }

            # remove problem fields from previous response
            if variables["update"].get("pollingIntervalCronExpression") is not None:
                if "__typename" in variables["update"]["pollingIntervalCronExpression"]:
                    del variables["update"]["pollingIntervalCronExpression"][
                        "__typename"
                    ]

            ingestion_sources = instance_details.get("ingestionSourcesOverrides", None)
            if ingestion_sources is not None:
                for ingestion_source in instance_details["ingestionSourcesOverrides"]:
                    ingestion_source.pop(
                        "__typename", None
                    )  # Removes key if it exists, ignores if not

            response = self._execute_query(
                UPDATE_INTEGRATION_INSTANCE, variables=variables
            )

            return response

        else:
            return "Provided 'config_key' not found in existing Integration Instance config"

    def create_smartclass(
        self, smartclass_name: str = None, smartclass_description: str = None
    ):
        """Creates a new Smart Class within Assets.

        args:
            smartclass_name (str): The "Smart class name" for Smart Class to be created.
            smartclass_description (str): The "Description" for Smart Class to be created.
        """
        variables = {
            "input": {"tagName": smartclass_name, "description": smartclass_description}
        }

        response = self._execute_query(CREATE_SMARTCLASS, variables=variables)

        return response["data"]["createSmartClass"]

    def create_smartclass_query(
        self,
        smartclass_id: str = None,
        query: str = None,
        query_description: str = None,
    ):
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
                "description": query_description,
            }
        }

        response = self._execute_query(CREATE_SMARTCLASS_QUERY, variables=variables)

        return response["data"]["createSmartClassQuery"]

    def evaluate_smartclass(self, smartclass_id: str = None):
        """Execute an on-demand Evaluation of a defined Smartclass.

        args:
            smartclass_id (str): The unique ID of the Smart Class to trigger the evaluation for.
        """
        variables = {"smartClassId": smartclass_id}

        response = self._execute_query(EVALUATE_SMARTCLASS, variables=variables)

        return response["data"]["evaluateSmartClassRule"]

    def get_smartclass_details(self, smartclass_id: str = None):
        """Fetch config details from defined Smart Class.

        args:
            smartclass_id (str): The unique ID of the Smart Class to fetch details from.
        """
        variables = {"id": smartclass_id}

        response = self._execute_query(GET_SMARTCLASS_DETAILS, variables=variables)

        return response["data"]["smartClass"]

    def generate_j1ql(self, natural_language_prompt: str = None):
        """Generate J1QL query syntax from natural language user input.

        args:
            natural_language_prompt (str): The naturalLanguageQuery prompt input to generate J1QL from.
        """
        variables = {"input": {"naturalLanguageQuery": natural_language_prompt}}

        response = self._execute_query(J1QL_FROM_NATURAL_LANGUAGE, variables=variables)

        return response["data"]["j1qlFromNaturalLanguage"]

    def list_alert_rules(self):
        """List all defined Alert Rules configured in J1 account"""
        results = []

        data = {"query": LIST_RULE_INSTANCES, "flags": {"variableResultSize": True}}

        r = requests.post(
            url=self.graphql_url, headers=self.headers, json=data, verify=True
        ).json()
        results.extend(r["data"]["listRuleInstances"]["questionInstances"])

        while r["data"]["listRuleInstances"]["pageInfo"]["hasNextPage"] == True:

            cursor = r["data"]["listRuleInstances"]["pageInfo"]["endCursor"]

            # cursor query until last page fetched
            data = {
                "query": LIST_RULE_INSTANCES,
                "variables": {"cursor": cursor},
                "flags": {"variableResultSize": True},
            }

            r = requests.post(
                url=self.graphql_url, headers=self.headers, json=data, verify=True
            ).json()
            results.extend(r["data"]["listRuleInstances"]["questionInstances"])

        return results

    def get_alert_rule_details(self, rule_id: str = None):
        """Get details of a single defined Alert Rule configured in J1 account"""
        results = []

        data = {"query": LIST_RULE_INSTANCES, "flags": {"variableResultSize": True}}

        r = requests.post(
            url=self.graphql_url, headers=self.headers, json=data, verify=True
        ).json()
        results.extend(r["data"]["listRuleInstances"]["questionInstances"])

        while r["data"]["listRuleInstances"]["pageInfo"]["hasNextPage"] == True:

            cursor = r["data"]["listRuleInstances"]["pageInfo"]["endCursor"]

            # cursor query until last page fetched
            data = {
                "query": LIST_RULE_INSTANCES,
                "variables": {"cursor": cursor},
                "flags": {"variableResultSize": True},
            }

            r = requests.post(
                url=self.graphql_url, headers=self.headers, json=data, verify=True
            ).json()
            results.extend(r["data"]["listRuleInstances"]["questionInstances"])

        # pick result out of list of results by 'id' key
        item = next((item for item in results if item["id"] == rule_id), None)

        if item:
            return item
        else:
            return "Alert Rule not found for provided ID in configured J1 Account"

    def create_alert_rule(
        self,
        name: str = None,
        description: str = None,
        tags: List[str] = None,
        labels: List[dict] = None,
        polling_interval: str = None,
        severity: str = None,
        j1ql: str = None,
        action_configs: Dict = None,
        resource_group_id: str = None,
    ):
        """Create Alert Rule Configuration in J1 account"""

        variables = {
            "instance": {
                "name": name,
                "description": description,
                "notifyOnFailure": True,
                "triggerActionsOnNewEntitiesOnly": True,
                "ignorePreviousResults": False,
                "operations": [
                    {
                        "when": {
                            "type": "FILTER",
                            "condition": ["AND", ["queries.query0.total", ">", 0]],
                        },
                        "actions": [
                            {
                                "type": "SET_PROPERTY",
                                "targetProperty": "alertLevel",
                                "targetValue": severity,
                            },
                            {"type": "CREATE_ALERT"},
                        ],
                    }
                ],
                "outputs": ["alertLevel"],
                "pollingInterval": polling_interval,
                "question": {
                    "queries": [
                        {
                            "query": j1ql,
                            "name": "query0",
                            "version": "v1",
                            "includeDeleted": False,
                        }
                    ]
                },
                "specVersion": 1,
                "tags": tags,
                "labels": labels,
                "templates": {},
                "resourceGroupId": resource_group_id,
            }
        }

        if action_configs:
            variables["instance"]["operations"][0]["actions"].append(action_configs)

        response = self._execute_query(CREATE_RULE_INSTANCE, variables=variables)

        return response["data"]["createInlineQuestionRuleInstance"]

    def delete_alert_rule(self, rule_id: str = None):
        """Delete a single Alert Rule configured in J1 account"""
        variables = {"id": rule_id}

        response = self._execute_query(DELETE_RULE_INSTANCE, variables=variables)

        return response["data"]["deleteRuleInstance"]

    def update_alert_rule(
        self,
        rule_id: str = None,
        name: str = None,
        description: str = None,
        j1ql: str = None,
        polling_interval: str = None,
        severity: str = None,
        tags: List[str] = None,
        tag_op: str = None,
        labels: List[dict] = None,
        action_configs: List[dict] = None,
        action_configs_op: str = None,
        resource_group_id: str = None,
    ):
        """Update Alert Rule Configuration in J1 account"""
        # fetch existing alert rule
        alert_rule_config = self.get_alert_rule_details(rule_id)

        # increment rule config version
        rule_version = alert_rule_config["version"] + 1

        # fetch current operations config
        operations = alert_rule_config["operations"]
        del operations[0]["__typename"]

        # update name if provided
        if name is not None:
            alert_name = name
        else:
            alert_name = alert_rule_config["name"]

        # update description if provided
        if description is not None:
            alert_description = description
        else:
            alert_description = alert_rule_config["description"]

        # update J1QL query if provided
        if j1ql is not None:
            question_config = alert_rule_config["question"]
            # remove problematic fields
            del question_config["__typename"]
            del question_config["queries"][0]["__typename"]

            # update query string if provided
            question_config["queries"][0]["query"] = j1ql
        else:
            question_config = alert_rule_config["question"]
            # remove problematic fields
            del question_config["__typename"]
            del question_config["queries"][0]["__typename"]

        # update polling_interval if provided
        if polling_interval is not None:
            interval_config = polling_interval
        else:
            interval_config = alert_rule_config["pollingInterval"]

        # update tags list if provided
        if tags is not None:
            if tag_op == "OVERWRITE":
                tags_config = tags
            elif tag_op == "APPEND":
                tags_config = alert_rule_config["tags"] + tags
            else:
                tags_config = alert_rule_config["tags"]
        else:
            tags_config = alert_rule_config["tags"]

        # update labels list if provided
        if labels is not None:
            label_config = labels

        # update action_configs list if provided
        if action_configs is not None:

            if action_configs_op == "OVERWRITE":

                # maintain first item and build new list from input
                alert_action_configs = []
                base_action = alert_rule_config["operations"][0]["actions"][0]
                alert_action_configs.append(base_action)
                alert_action_configs.extend(action_configs)

                # update actions field inside operations payload
                operations[0]["actions"] = alert_action_configs

            elif action_configs_op == "APPEND":

                # update actions field inside operations payload
                operations[0]["actions"].extend(action_configs)

        # update alert severity if provided
        if severity is not None:
            operations[0]["actions"][0]["targetValue"] = severity

        variables = {
            "instance": {
                "id": rule_id,
                "version": rule_version,
                "specVersion": alert_rule_config["specVersion"],
                "name": alert_name,
                "description": alert_description,
                "question": question_config,
                "operations": operations,
                "pollingInterval": interval_config,
                "tags": tags_config,
                "labels": label_config,
                "resourceGroupId": resource_group_id,
            }
        }

        response = self._execute_query(UPDATE_RULE_INSTANCE, variables=variables)

        return response["data"]["updateInlineQuestionRuleInstance"]

    def evaluate_alert_rule(self, rule_id: str = None):
        """Run an Evaluation for a defined Alert Rule configured in J1 account"""
        variables = {"id": rule_id}

        response = self._execute_query(EVALUATE_RULE_INSTANCE, variables=variables)
        return response

    def list_alert_rule_evaluation_results(self, rule_id: str = None):
        """Fetch a list of Evaluation Results for an Alert Rule configured in J1 account"""
        variables = {
            "collectionType": "RULE_EVALUATION",
            "collectionOwnerId": rule_id,
            "beginTimestamp": 0,
            "endTimestamp": round(time.time() * 1000),
            "limit": 40,
        }

        response = self._execute_query(LIST_COLLECTION_RESULTS, variables=variables)
        return response

    def fetch_evaluation_result_download_url(self, raw_data_key: str = None):
        """Fetch evaluation result Download URL for Alert Rule configured in J1 account"""
        variables = {"rawDataKey": raw_data_key}

        response = self._execute_query(GET_RAW_DATA_DOWNLOAD_URL, variables=variables)
        return response

    def fetch_downloaded_evaluation_results(self, download_url: str = None):
        """Return full Alert Rule J1QL results from Download URL"""
        # initiate requests session and implement retry logic of 5 request retries with 1 second between
        try:
            response = self.session.get(download_url, timeout=60)

            return response.json()

        except Exception as e:

            return e

    def list_questions(self):
        """List all defined Questions configured in J1 account Questions Library"""
        results = []

        data = {"query": QUESTIONS, "flags": {"variableResultSize": True}}

        r = requests.post(
            url=self.graphql_url, headers=self.headers, json=data, verify=True
        ).json()
        results.extend(r["data"]["questions"]["questions"])

        while r["data"]["questions"]["pageInfo"]["hasNextPage"] == True:

            cursor = r["data"]["questions"]["pageInfo"]["endCursor"]

            # cursor query until last page fetched
            data = {
                "query": QUESTIONS,
                "variables": {"cursor": cursor},
                "flags": {"variableResultSize": True},
            }

            r = requests.post(
                url=self.graphql_url, headers=self.headers, json=data, verify=True
            ).json()
            results.extend(r["data"]["questions"]["questions"])

        return results

    def get_compliance_framework_item_details(self, item_id: str = None):
        """Fetch Details of a Compliance Framework Requirement configured in J1 account"""
        variables = {"input": {"id": item_id}}

        response = self._execute_query(COMPLIANCE_FRAMEWORK_ITEM, variables=variables)
        return response

    def get_parameter_details(self, name: str = None):
        """Fetch Details of a configured Parameter in J1 account"""
        variables = {"name": name}

        response = self._execute_query(PARAMETER, variables=variables)
        return response

    def list_account_parameters(self):
        """Fetch List of all configured Account Parameters in J1 account"""
        results = []

        data = {"query": PARAMETER_LIST, "flags": {"variableResultSize": True}}

        r = requests.post(
            url=self.graphql_url, headers=self.headers, json=data, verify=True
        ).json()
        results.extend(r["data"]["parameterList"]["items"])

        while r["data"]["parameterList"]["pageInfo"]["hasNextPage"] == True:
            cursor = r["data"]["parameterList"]["pageInfo"]["endCursor"]

            # cursor query until last page fetched
            data = {
                "query": PARAMETER_LIST,
                "variables": {"cursor": cursor},
                "flags": {"variableResultSize": True},
            }

            r = requests.post(
                url=self.graphql_url, headers=self.headers, json=data, verify=True
            ).json()
            results.extend(r["data"]["parameterList"]["items"])

        return results

    def create_update_parameter(
        self,
        name: str = None,
        value: Union[str, int, bool, list] = None,
        secret: bool = False,
    ):
        """Create or Update Account Parameter in J1 account"""
        variables = {"name": name, "value": value, "secret": secret}

        response = self._execute_query(UPSERT_PARAMETER, variables=variables)
        return response
