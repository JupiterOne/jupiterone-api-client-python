"""Test create_integration_instance method"""

import pytest
from unittest.mock import Mock, patch
from jupiterone.client import JupiterOneClient


class TestCreateIntegrationInstance:
    """Test create_integration_instance method"""

    def setup_method(self):
        """Set up test fixtures"""
        self.client = JupiterOneClient(account="test-account", token="test-token")

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_create_integration_instance_basic(self, mock_execute_query):
        """Test basic integration instance creation without resource_group_id"""
        # Mock response
        mock_response = {
            "data": {
                "createIntegrationInstance": {
                    "id": "test-instance-id",
                    "name": "test-instance",
                    "description": "Test integration instance"
                }
            }
        }
        mock_execute_query.return_value = mock_response

        # Test the method
        result = self.client.create_integration_instance(
            instance_name="test-instance",
            instance_description="Test integration instance"
        )

        # Verify the result
        assert result == mock_response["data"]["createIntegrationInstance"]

        # Verify the query was called with correct variables
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        variables = call_args[1]['variables']
        
        assert variables["instance"]["name"] == "test-instance"
        assert variables["instance"]["description"] == "Test integration instance"
        assert "resourceGroupId" not in variables["instance"]

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_create_integration_instance_with_resource_group_id(self, mock_execute_query):
        """Test integration instance creation with resource_group_id"""
        # Mock response
        mock_response = {
            "data": {
                "createIntegrationInstance": {
                    "id": "test-instance-id",
                    "name": "test-instance",
                    "description": "Test integration instance",
                    "resourceGroupId": "test-resource-group-id"
                }
            }
        }
        mock_execute_query.return_value = mock_response

        # Test the method with resource_group_id
        result = self.client.create_integration_instance(
            instance_name="test-instance",
            instance_description="Test integration instance",
            resource_group_id="test-resource-group-id"
        )

        # Verify the result
        assert result == mock_response["data"]["createIntegrationInstance"]

        # Verify the query was called with correct variables including resourceGroupId
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        variables = call_args[1]['variables']
        
        assert variables["instance"]["name"] == "test-instance"
        assert variables["instance"]["description"] == "Test integration instance"
        assert variables["instance"]["resourceGroupId"] == "test-resource-group-id"

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_create_integration_instance_with_custom_definition_id(self, mock_execute_query):
        """Test integration instance creation with custom definition ID"""
        # Mock response
        mock_response = {
            "data": {
                "createIntegrationInstance": {
                    "id": "test-instance-id",
                    "name": "test-instance",
                    "integrationDefinitionId": "custom-definition-id"
                }
            }
        }
        mock_execute_query.return_value = mock_response

        # Test the method with custom definition ID
        result = self.client.create_integration_instance(
            instance_name="test-instance",
            integration_definition_id="custom-definition-id"
        )

        # Verify the result
        assert result == mock_response["data"]["createIntegrationInstance"]

        # Verify the query was called with correct variables
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        variables = call_args[1]['variables']
        
        assert variables["instance"]["integrationDefinitionId"] == "custom-definition-id"

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_create_integration_instance_all_parameters(self, mock_execute_query):
        """Test integration instance creation with all parameters"""
        # Mock response
        mock_response = {
            "data": {
                "createIntegrationInstance": {
                    "id": "test-instance-id",
                    "name": "test-instance",
                    "description": "Test integration instance",
                    "integrationDefinitionId": "custom-definition-id",
                    "resourceGroupId": "test-resource-group-id"
                }
            }
        }
        mock_execute_query.return_value = mock_response

        # Test the method with all parameters
        result = self.client.create_integration_instance(
            instance_name="test-instance",
            instance_description="Test integration instance",
            integration_definition_id="custom-definition-id",
            resource_group_id="test-resource-group-id"
        )

        # Verify the result
        assert result == mock_response["data"]["createIntegrationInstance"]

        # Verify the query was called with correct variables
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        variables = call_args[1]['variables']
        
        assert variables["instance"]["name"] == "test-instance"
        assert variables["instance"]["description"] == "Test integration instance"
        assert variables["instance"]["integrationDefinitionId"] == "custom-definition-id"
        assert variables["instance"]["resourceGroupId"] == "test-resource-group-id"
        assert variables["instance"]["pollingInterval"] == "DISABLED"
        assert "config" in variables["instance"]
        assert "pollingIntervalCronExpression" in variables["instance"]
        assert "ingestionSourcesOverrides" in variables["instance"] 