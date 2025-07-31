"""Test integration-related methods"""

import pytest
import responses
from unittest.mock import Mock, patch
from jupiterone.client import JupiterOneClient
from jupiterone.errors import JupiterOneApiError


class TestIntegrationMethods:
    """Test integration-related methods"""

    def setup_method(self):
        """Set up test fixtures"""
        self.client = JupiterOneClient(account="test-account", token="test-token")

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_fetch_all_entity_properties(self, mock_execute_query):
        """Test fetch_all_entity_properties method"""
        mock_response = {
            "data": {
                "getAllAssetProperties": [
                    "property1",
                    "property2",
                    "parameter.secret",
                    "tag.environment",
                    "normal_property"
                ]
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.fetch_all_entity_properties()

        assert result == ["property1", "property2", "normal_property"]
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_fetch_all_entity_tags(self, mock_execute_query):
        """Test fetch_all_entity_tags method"""
        mock_response = {
            "data": {
                "getAllAssetProperties": [
                    "property1",
                    "tag.environment",
                    "tag.owner",
                    "normal_property"
                ]
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.fetch_all_entity_tags()

        assert result == ["tag.environment", "tag.owner"]
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_fetch_entity_raw_data(self, mock_execute_query):
        """Test fetch_entity_raw_data method"""
        mock_response = {
            "data": {
                "getEntityRawData": {
                    "rawData": "test raw data"
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.fetch_entity_raw_data(entity_id="test-entity-id")

        assert result == mock_response
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_syncapi_request')
    def test_start_sync_job(self, mock_syncapi_request):
        """Test start_sync_job method"""
        mock_response = {"jobId": "test-job-id"}
        mock_syncapi_request.return_value = mock_response

        result = self.client.start_sync_job(
            instance_id="test-instance-id",
            sync_mode="DIFF",
            source="api"
        )

        assert result == mock_response
        mock_syncapi_request.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_syncapi_request')
    def test_upload_entities_batch_json(self, mock_syncapi_request):
        """Test upload_entities_batch_json method"""
        mock_response = {"status": "success"}
        mock_syncapi_request.return_value = mock_response

        entities_list = [
            {"_key": "1", "_type": "test", "_class": "Test"}
        ]

        result = self.client.upload_entities_batch_json(
            instance_job_id="test-job-id",
            entities_list=entities_list
        )

        assert result == mock_response
        mock_syncapi_request.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_syncapi_request')
    def test_upload_relationships_batch_json(self, mock_syncapi_request):
        """Test upload_relationships_batch_json method"""
        mock_response = {"status": "success"}
        mock_syncapi_request.return_value = mock_response

        relationships_list = [
            {"_key": "1:2", "_class": "RELATES_TO", "_fromEntityKey": "1", "_toEntityKey": "2"}
        ]

        result = self.client.upload_relationships_batch_json(
            instance_job_id="test-job-id",
            relationships_list=relationships_list
        )

        assert result == mock_response
        mock_syncapi_request.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_syncapi_request')
    def test_upload_combined_batch_json(self, mock_syncapi_request):
        """Test upload_combined_batch_json method"""
        mock_response = {"status": "success"}
        mock_syncapi_request.return_value = mock_response

        combined_payload = {
            "entities": [{"_key": "1", "_type": "test", "_class": "Test"}],
            "relationships": [{"_key": "1:2", "_class": "RELATES_TO"}]
        }

        result = self.client.upload_combined_batch_json(
            instance_job_id="test-job-id",
            combined_payload=combined_payload
        )

        assert result == mock_response
        mock_syncapi_request.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_syncapi_request')
    def test_bulk_delete_entities(self, mock_syncapi_request):
        """Test bulk_delete_entities method"""
        mock_response = {"status": "success"}
        mock_syncapi_request.return_value = mock_response

        entities_list = [{"_id": "entity-1"}, {"_id": "entity-2"}]

        result = self.client.bulk_delete_entities(
            instance_job_id="test-job-id",
            entities_list=entities_list
        )

        assert result == mock_response
        mock_syncapi_request.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_syncapi_request')
    def test_finalize_sync_job(self, mock_syncapi_request):
        """Test finalize_sync_job method"""
        mock_response = {"status": "finalized"}
        mock_syncapi_request.return_value = mock_response

        result = self.client.finalize_sync_job(instance_job_id="test-job-id")

        assert result == mock_response
        mock_syncapi_request.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_fetch_integration_jobs(self, mock_execute_query):
        """Test fetch_integration_jobs method"""
        mock_response = {
            "data": {
                "integrationJobs": {
                    "jobs": [{"id": "job-1", "status": "COMPLETED"}]
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.fetch_integration_jobs(instance_id="test-instance-id")

        assert result == mock_response["data"]["integrationJobs"]
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_fetch_integration_job_events(self, mock_execute_query):
        """Test fetch_integration_job_events method"""
        mock_response = {
            "data": {
                "integrationEvents": {
                    "events": [{"id": "event-1", "name": "test_event"}]
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.fetch_integration_job_events(
            instance_id="test-instance-id",
            instance_job_id="test-job-id"
        )

        assert result == mock_response["data"]["integrationEvents"]
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_get_integration_definition_details(self, mock_execute_query):
        """Test get_integration_definition_details method"""
        mock_response = {
            "data": {
                "findIntegrationDefinition": {
                    "id": "def-1",
                    "title": "Test Integration"
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.get_integration_definition_details(integration_type="test")

        assert result == mock_response
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_fetch_integration_instances(self, mock_execute_query):
        """Test fetch_integration_instances method"""
        mock_response = {
            "data": {
                "integrationInstances": {
                    "instances": [{"id": "instance-1", "name": "test"}]
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.fetch_integration_instances(definition_id="test-def-id")

        assert result == mock_response
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_get_integration_instance_details(self, mock_execute_query):
        """Test get_integration_instance_details method"""
        mock_response = {
            "data": {
                "integrationInstance": {
                    "id": "instance-1",
                    "name": "test",
                    "config": {"key": "value"}
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.get_integration_instance_details(instance_id="test-instance-id")

        assert result == mock_response
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient.get_integration_instance_details')
    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_update_integration_instance_config_value_success(self, mock_execute_query, mock_get_details):
        """Test update_integration_instance_config_value method - success case"""
        mock_get_details.return_value = {
            "data": {
                "integrationInstance": {
                    "id": "instance-1",
                    "config": {"existing_key": "old_value"},
                    "pollingInterval": "DISABLED",
                    "description": "test",
                    "name": "test",
                    "collectorPoolId": "pool-1",
                    "pollingIntervalCronExpression": {},
                    "ingestionSourcesOverrides": []
                }
            }
        }
        
        mock_response = {"data": {"updateIntegrationInstance": {"id": "instance-1"}}}
        mock_execute_query.return_value = mock_response

        result = self.client.update_integration_instance_config_value(
            instance_id="test-instance-id",
            config_key="existing_key",
            config_value="new_value"
        )

        assert result == mock_response
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient.get_integration_instance_details')
    def test_update_integration_instance_config_value_key_not_found(self, mock_get_details):
        """Test update_integration_instance_config_value method - key not found"""
        mock_get_details.return_value = {
            "data": {
                "integrationInstance": {
                    "id": "instance-1",
                    "config": {"existing_key": "old_value"}
                }
            }
        }

        result = self.client.update_integration_instance_config_value(
            instance_id="test-instance-id",
            config_key="nonexistent_key",
            config_value="new_value"
        )

        assert result == "Provided 'config_key' not found in existing Integration Instance config" 