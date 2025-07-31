"""Test miscellaneous methods"""

import pytest
import responses
from unittest.mock import Mock, patch
from jupiterone.client import JupiterOneClient
from jupiterone.errors import JupiterOneApiError


class TestMiscMethods:
    """Test miscellaneous methods"""

    def setup_method(self):
        """Set up test fixtures"""
        self.client = JupiterOneClient(account="test-account", token="test-token")

    @patch('jupiterone.client.requests.post')
    def test_list_questions(self, mock_post):
        """Test list_questions method"""
        # Mock first page response
        first_response = Mock()
        first_response.json.return_value = {
            "data": {
                "questions": {
                    "questions": [{"id": "question-1", "name": "Test Question"}],
                    "pageInfo": {
                        "hasNextPage": True,
                        "endCursor": "cursor-1"
                    }
                }
            }
        }
        
        # Mock second page response
        second_response = Mock()
        second_response.json.return_value = {
            "data": {
                "questions": {
                    "questions": [{"id": "question-2", "name": "Test Question 2"}],
                    "pageInfo": {
                        "hasNextPage": False,
                        "endCursor": None
                    }
                }
            }
        }
        
        mock_post.side_effect = [first_response, second_response]

        result = self.client.list_questions()

        assert len(result) == 2
        assert result[0]["id"] == "question-1"
        assert result[1]["id"] == "question-2"
        assert mock_post.call_count == 2

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_get_compliance_framework_item_details(self, mock_execute_query):
        """Test get_compliance_framework_item_details method"""
        mock_response = {
            "data": {
                "complianceFrameworkItem": {
                    "id": "item-1",
                    "name": "Test Compliance Item"
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.get_compliance_framework_item_details(item_id="item-1")

        assert result == mock_response
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_get_parameter_details(self, mock_execute_query):
        """Test get_parameter_details method"""
        mock_response = {
            "data": {
                "parameter": {
                    "name": "test_param",
                    "value": "test_value",
                    "secret": False
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.get_parameter_details(name="test_param")

        assert result == mock_response
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.requests.post')
    def test_list_account_parameters(self, mock_post):
        """Test list_account_parameters method"""
        # Mock first page response
        first_response = Mock()
        first_response.json.return_value = {
            "data": {
                "parameterList": {
                    "items": [{"name": "param-1", "value": "value-1"}],
                    "pageInfo": {
                        "hasNextPage": True,
                        "endCursor": "cursor-1"
                    }
                }
            }
        }
        
        # Mock second page response
        second_response = Mock()
        second_response.json.return_value = {
            "data": {
                "parameterList": {
                    "items": [{"name": "param-2", "value": "value-2"}],
                    "pageInfo": {
                        "hasNextPage": False,
                        "endCursor": None
                    }
                }
            }
        }
        
        mock_post.side_effect = [first_response, second_response]

        result = self.client.list_account_parameters()

        assert len(result) == 2
        assert result[0]["name"] == "param-1"
        assert result[1]["name"] == "param-2"
        assert mock_post.call_count == 2

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_create_update_parameter(self, mock_execute_query):
        """Test create_update_parameter method"""
        mock_response = {
            "data": {
                "upsertParameter": {
                    "name": "test_param",
                    "value": "test_value",
                    "secret": False
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.create_update_parameter(
            name="test_param",
            value="test_value",
            secret=False
        )

        assert result == mock_response
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_create_update_parameter_secret(self, mock_execute_query):
        """Test create_update_parameter method with secret parameter"""
        mock_response = {
            "data": {
                "upsertParameter": {
                    "name": "secret_param",
                    "value": "secret_value",
                    "secret": True
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.create_update_parameter(
            name="secret_param",
            value="secret_value",
            secret=True
        )

        assert result == mock_response
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_update_entity_v2(self, mock_execute_query):
        """Test update_entity_v2 method"""
        mock_response = {
            "data": {
                "updateEntityV2": {
                    "id": "entity-1",
                    "displayName": "Updated Entity"
                }
            }
        }
        mock_execute_query.return_value = mock_response

        properties = {
            "displayName": "Updated Entity",
            "tag.environment": "production"
        }

        result = self.client.update_entity_v2(
            entity_id="entity-1",
            properties=properties
        )

        assert result == mock_response["data"]["updateEntityV2"]
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_query_with_deferred_response(self, mock_execute_query):
        """Test query_with_deferred_response method"""
        # Mock the URL response
        url_response = Mock()
        url_response.ok = True
        url_response.json.return_value = {
            'data': {
                'queryV1': {
                    'url': 'https://example.com/download'
                }
            }
        }
        
        # Mock the download response
        download_response = Mock()
        download_response.json.return_value = {
            'status': 'COMPLETED',
            'data': [{'id': 'entity-1'}, {'id': 'entity-2'}]
        }
        
        with patch.object(self.client.session, 'post', return_value=url_response), \
             patch.object(self.client.session, 'get', return_value=download_response):
            
            result = self.client.query_with_deferred_response("FIND Host")

            assert len(result) == 2
            assert result[0]['id'] == 'entity-1'
            assert result[1]['id'] == 'entity-2'

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_query_with_deferred_response_with_cursor(self, mock_execute_query):
        """Test query_with_deferred_response method with cursor"""
        # Mock the URL response
        url_response = Mock()
        url_response.ok = True
        url_response.json.return_value = {
            'data': {
                'queryV1': {
                    'url': 'https://example.com/download'
                }
            }
        }
        
        # Mock the download response with cursor
        download_response = Mock()
        download_response.json.return_value = {
            'status': 'COMPLETED',
            'data': [{'id': 'entity-1'}],
            'cursor': 'next-cursor'
        }
        
        # Mock the second download response (no cursor)
        download_response2 = Mock()
        download_response2.json.return_value = {
            'status': 'COMPLETED',
            'data': [{'id': 'entity-2'}]
        }
        
        with patch.object(self.client.session, 'post', return_value=url_response), \
             patch.object(self.client.session, 'get', side_effect=[download_response, download_response2]):
            
            result = self.client.query_with_deferred_response("FIND Host", cursor="initial-cursor")

            assert len(result) == 2
            assert result[0]['id'] == 'entity-1'
            assert result[1]['id'] == 'entity-2' 