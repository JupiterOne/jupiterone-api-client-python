"""Test update_relationship method"""

import json
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from jupiterone.client import JupiterOneClient
from jupiterone.constants import UPDATE_RELATIONSHIP
from jupiterone.errors import JupiterOneApiError


class TestUpdateRelationship:
    """Test update_relationship method"""

    def setup_method(self):
        """Set up test fixtures"""
        self.client = JupiterOneClient(account="test-account", token="test-token")

    @patch.object(JupiterOneClient, '_execute_query')
    def test_update_relationship_basic(self, mock_execute_query):
        """Test basic relationship update"""
        mock_response = {
            "data": {
                "updateRelationship": {
                    "relationship": {
                        "_id": "rel-123",
                        "_type": "test_relationship",
                        "_class": "TestRelationship",
                        "_fromEntityId": "entity-1",
                        "_toEntityId": "entity-2",
                        "displayName": "test relationship"
                    },
                    "edge": {
                        "id": "edge-123",
                        "toVertexId": "entity-2",
                        "fromVertexId": "entity-1",
                        "properties": {"status": "active", "updated": True}
                    }
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.update_relationship(
            relationship_id="rel-123",
            from_entity_id="entity-1",
            to_entity_id="entity-2",
            properties={"status": "active", "updated": True}
        )

        # Verify the method was called with correct parameters
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        assert call_args[1]['query'] == UPDATE_RELATIONSHIP
        
        variables = call_args[1]['variables']
        assert variables["relationshipId"] == "rel-123"
        assert variables["fromEntityId"] == "entity-1"
        assert variables["toEntityId"] == "entity-2"
        assert variables["properties"]["status"] == "active"
        assert variables["properties"]["updated"] is True
        assert "timestamp" in variables
        
        # Verify the result
        assert result == mock_response["data"]["updateRelationship"]

    @patch.object(JupiterOneClient, '_execute_query')
    def test_update_relationship_without_properties(self, mock_execute_query):
        """Test relationship update without properties"""
        mock_response = {
            "data": {
                "updateRelationship": {
                    "relationship": {
                        "_id": "rel-123",
                        "_fromEntityId": "entity-1",
                        "_toEntityId": "entity-2"
                    },
                    "edge": {
                        "id": "edge-123",
                        "fromVertexId": "entity-1",
                        "toVertexId": "entity-2"
                    }
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.update_relationship(
            relationship_id="rel-123",
            from_entity_id="entity-1",
            to_entity_id="entity-2"
        )

        # Verify the method was called with correct parameters
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        variables = call_args[1]['variables']
        assert variables["relationshipId"] == "rel-123"
        assert variables["fromEntityId"] == "entity-1"
        assert variables["toEntityId"] == "entity-2"
        assert variables["properties"] is None
        assert "timestamp" in variables

        # Verify the result
        assert result == mock_response["data"]["updateRelationship"]

    @patch.object(JupiterOneClient, '_execute_query')
    def test_update_relationship_with_complex_properties(self, mock_execute_query):
        """Test relationship update with complex property types"""
        mock_response = {
            "data": {
                "updateRelationship": {
                    "relationship": {
                        "_id": "rel-123",
                        "_fromEntityId": "entity-1",
                        "_toEntityId": "entity-2"
                    },
                    "edge": {
                        "id": "edge-123",
                        "fromVertexId": "entity-1",
                        "toVertexId": "entity-2",
                        "properties": {
                            "nested": {"key": "value"},
                            "list": [1, 2, 3],
                            "boolean": True,
                            "number": 42
                        }
                    }
                }
            }
        }
        mock_execute_query.return_value = mock_response

        properties = {
            "nested": {"key": "value"},
            "list": [1, 2, 3],
            "boolean": True,
            "number": 42
        }

        result = self.client.update_relationship(
            relationship_id="rel-123",
            from_entity_id="entity-1",
            to_entity_id="entity-2",
            properties=properties
        )

        # Verify the method was called with correct parameters
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        variables = call_args[1]['variables']
        assert variables["relationshipId"] == "rel-123"
        assert variables["fromEntityId"] == "entity-1"
        assert variables["toEntityId"] == "entity-2"
        assert variables["properties"]["nested"] == {"key": "value"}
        assert variables["properties"]["list"] == [1, 2, 3]
        assert variables["properties"]["boolean"] is True
        assert variables["properties"]["number"] == 42

        # Verify the result
        assert result == mock_response["data"]["updateRelationship"]

    @patch.object(JupiterOneClient, '_execute_query')
    def test_update_relationship_timestamp_generation(self, mock_execute_query):
        """Test that timestamp is properly generated"""
        mock_response = {
            "data": {
                "updateRelationship": {
                    "relationship": {"_id": "rel-123"}
                }
            }
        }
        mock_execute_query.return_value = mock_response

        # Mock datetime to have a predictable timestamp
        with patch('jupiterone.client.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
            
            self.client.update_relationship(
                relationship_id="rel-123",
                from_entity_id="entity-1",
                to_entity_id="entity-2",
                properties={"test": "value"}
            )

        # Verify timestamp was generated correctly
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        variables = call_args[1]['variables']
        
        # Timestamp should be milliseconds since epoch for 2023-01-01 12:00:00
        expected_timestamp = int(datetime(2023, 1, 1, 12, 0, 0).timestamp() * 1000)
        assert variables["timestamp"] == expected_timestamp

    @patch.object(JupiterOneClient, '_execute_query')
    def test_update_relationship_api_error(self, mock_execute_query):
        """Test handling of API errors"""
        mock_execute_query.side_effect = JupiterOneApiError("API Error")

        with pytest.raises(JupiterOneApiError, match="API Error"):
            self.client.update_relationship(
                relationship_id="rel-123",
                from_entity_id="entity-1",
                to_entity_id="entity-2",
                properties={"test": "value"}
            )

    def test_update_relationship_missing_relationship_id(self):
        """Test that missing relationship_id is handled properly"""
        # The method should still work with None relationship_id
        # as it will be passed to the API which will handle the error
        with patch.object(self.client, '_execute_query') as mock_execute_query:
            mock_execute_query.side_effect = JupiterOneApiError("Invalid relationship ID")
            
            with pytest.raises(JupiterOneApiError):
                self.client.update_relationship(
                    relationship_id=None,
                    from_entity_id="entity-1",
                    to_entity_id="entity-2",
                    properties={"test": "value"}
                )

    @patch.object(JupiterOneClient, '_execute_query')
    def test_update_relationship_empty_properties(self, mock_execute_query):
        """Test relationship update with empty properties dict"""
        mock_response = {
            "data": {
                "updateRelationship": {
                    "relationship": {"_id": "rel-123"}
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.update_relationship(
            relationship_id="rel-123",
            from_entity_id="entity-1",
            to_entity_id="entity-2",
            properties={}
        )

        # Verify the method was called with correct parameters
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        variables = call_args[1]['variables']
        assert variables["relationshipId"] == "rel-123"
        assert variables["fromEntityId"] == "entity-1"
        assert variables["toEntityId"] == "entity-2"
        assert variables["properties"] == {}

        # Verify the result
        assert result == mock_response["data"]["updateRelationship"]

    @patch.object(JupiterOneClient, '_execute_query')
    def test_update_relationship_with_none_properties(self, mock_execute_query):
        """Test relationship update with None properties"""
        mock_response = {
            "data": {
                "updateRelationship": {
                    "relationship": {"_id": "rel-123"}
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.update_relationship(
            relationship_id="rel-123",
            from_entity_id="entity-1",
            to_entity_id="entity-2",
            properties=None
        )

        # Verify the method was called with correct parameters
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        variables = call_args[1]['variables']
        assert variables["relationshipId"] == "rel-123"
        assert variables["fromEntityId"] == "entity-1"
        assert variables["toEntityId"] == "entity-2"
        assert variables["properties"] is None

        # Verify the result
        assert result == mock_response["data"]["updateRelationship"] 