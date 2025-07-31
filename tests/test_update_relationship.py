"""Test update_relationship method"""

import json
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from jupiterone.client import JupiterOneClient
from jupiterone.constants import UPDATE_RELATIONSHIPV2
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
                "updateRelationshipV2": {
                    "relationship": {
                        "_id": "rel-123",
                        "_type": "test_relationship",
                        "_class": "TestRelationship"
                    },
                    "edge": {
                        "id": "edge-123",
                        "toVertexId": "entity-2",
                        "fromVertexId": "entity-1"
                    }
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.update_relationship(
            relationship_id="rel-123",
            properties={"status": "active", "updated": True}
        )

        # Verify the method was called with correct parameters
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        assert call_args[1]['query'] == UPDATE_RELATIONSHIPV2
        
        variables = call_args[1]['variables']
        assert variables["relationship"]["_id"] == "rel-123"
        assert variables["relationship"]["status"] == "active"
        assert variables["relationship"]["updated"] is True
        assert "timestamp" in variables
        
        # Verify the result
        assert result == mock_response["data"]["updateRelationshipV2"]

    @patch.object(JupiterOneClient, '_execute_query')
    def test_update_relationship_without_properties(self, mock_execute_query):
        """Test relationship update without properties"""
        mock_response = {
            "data": {
                "updateRelationshipV2": {
                    "relationship": {
                        "_id": "rel-123"
                    },
                    "edge": {
                        "id": "edge-123"
                    }
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.update_relationship(relationship_id="rel-123")

        # Verify the method was called with correct parameters
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        variables = call_args[1]['variables']
        assert variables["relationship"]["_id"] == "rel-123"
        assert len(variables["relationship"]) == 1  # Only _id should be present
        assert "timestamp" in variables

        # Verify the result
        assert result == mock_response["data"]["updateRelationshipV2"]

    @patch.object(JupiterOneClient, '_execute_query')
    def test_update_relationship_with_complex_properties(self, mock_execute_query):
        """Test relationship update with complex property types"""
        mock_response = {
            "data": {
                "updateRelationshipV2": {
                    "relationship": {
                        "_id": "rel-123",
                        "nested": {"key": "value"},
                        "list": [1, 2, 3],
                        "boolean": True,
                        "number": 42
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
            properties=properties
        )

        # Verify the method was called with correct parameters
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        variables = call_args[1]['variables']
        assert variables["relationship"]["_id"] == "rel-123"
        assert variables["relationship"]["nested"] == {"key": "value"}
        assert variables["relationship"]["list"] == [1, 2, 3]
        assert variables["relationship"]["boolean"] is True
        assert variables["relationship"]["number"] == 42

        # Verify the result
        assert result == mock_response["data"]["updateRelationshipV2"]

    @patch.object(JupiterOneClient, '_execute_query')
    def test_update_relationship_timestamp_generation(self, mock_execute_query):
        """Test that timestamp is properly generated"""
        mock_response = {
            "data": {
                "updateRelationshipV2": {
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
                    properties={"test": "value"}
                )

    @patch.object(JupiterOneClient, '_execute_query')
    def test_update_relationship_empty_properties(self, mock_execute_query):
        """Test relationship update with empty properties dict"""
        mock_response = {
            "data": {
                "updateRelationshipV2": {
                    "relationship": {"_id": "rel-123"}
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.update_relationship(
            relationship_id="rel-123",
            properties={}
        )

        # Verify the method was called with correct parameters
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        variables = call_args[1]['variables']
        assert variables["relationship"]["_id"] == "rel-123"
        assert len(variables["relationship"]) == 1  # Only _id should be present

        # Verify the result
        assert result == mock_response["data"]["updateRelationshipV2"]

    @patch.object(JupiterOneClient, '_execute_query')
    def test_update_relationship_with_none_properties(self, mock_execute_query):
        """Test relationship update with None properties"""
        mock_response = {
            "data": {
                "updateRelationshipV2": {
                    "relationship": {"_id": "rel-123"}
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.update_relationship(
            relationship_id="rel-123",
            properties=None
        )

        # Verify the method was called with correct parameters
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        variables = call_args[1]['variables']
        assert variables["relationship"]["_id"] == "rel-123"
        assert len(variables["relationship"]) == 1  # Only _id should be present

        # Verify the result
        assert result == mock_response["data"]["updateRelationshipV2"] 