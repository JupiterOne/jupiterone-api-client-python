"""Test smartclass-related methods"""

import pytest
import responses
from unittest.mock import Mock, patch
from jupiterone.client import JupiterOneClient
from jupiterone.errors import JupiterOneApiError


class TestSmartclassMethods:
    """Test smartclass-related methods"""

    def setup_method(self):
        """Set up test fixtures"""
        self.client = JupiterOneClient(account="test-account", token="test-token")

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_create_smartclass(self, mock_execute_query):
        """Test create_smartclass method"""
        mock_response = {
            "data": {
                "createSmartClass": {
                    "id": "smartclass-1",
                    "tagName": "test_smartclass",
                    "description": "Test smart class"
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.create_smartclass(
            smartclass_name="test_smartclass",
            smartclass_description="Test smart class"
        )

        assert result == mock_response["data"]["createSmartClass"]
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_create_smartclass_query(self, mock_execute_query):
        """Test create_smartclass_query method"""
        mock_response = {
            "data": {
                "createSmartClassQuery": {
                    "id": "query-1",
                    "smartClassId": "smartclass-1",
                    "query": "FIND Host",
                    "description": "Test query"
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.create_smartclass_query(
            smartclass_id="smartclass-1",
            query="FIND Host",
            query_description="Test query"
        )

        assert result == mock_response["data"]["createSmartClassQuery"]
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_evaluate_smartclass(self, mock_execute_query):
        """Test evaluate_smartclass method"""
        mock_response = {
            "data": {
                "evaluateSmartClassRule": {
                    "id": "evaluation-1",
                    "status": "COMPLETED"
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.evaluate_smartclass(smartclass_id="smartclass-1")

        assert result == mock_response["data"]["evaluateSmartClassRule"]
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_get_smartclass_details(self, mock_execute_query):
        """Test get_smartclass_details method"""
        mock_response = {
            "data": {
                "smartClass": {
                    "id": "smartclass-1",
                    "tagName": "test_smartclass",
                    "description": "Test smart class",
                    "queries": [{"id": "query-1", "query": "FIND Host"}]
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.get_smartclass_details(smartclass_id="smartclass-1")

        assert result == mock_response["data"]["smartClass"]
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_generate_j1ql(self, mock_execute_query):
        """Test generate_j1ql method"""
        mock_response = {
            "data": {
                "j1qlFromNaturalLanguage": {
                    "query": "FIND Host",
                    "naturalLanguageQuery": "find all hosts"
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.generate_j1ql(natural_language_prompt="find all hosts")

        assert result == mock_response["data"]["j1qlFromNaturalLanguage"]
        mock_execute_query.assert_called_once() 