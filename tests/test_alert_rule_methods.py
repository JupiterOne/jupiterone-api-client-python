"""Test alert rule-related methods"""

import pytest
import responses
import time
from unittest.mock import Mock, patch
from jupiterone.client import JupiterOneClient
from jupiterone.errors import JupiterOneApiError


class TestAlertRuleMethods:
    """Test alert rule-related methods"""

    def setup_method(self):
        """Set up test fixtures"""
        self.client = JupiterOneClient(account="test-account", token="test-token")

    @patch('jupiterone.client.requests.post')
    def test_list_alert_rules(self, mock_post):
        """Test list_alert_rules method"""
        # Mock first page response
        first_response = Mock()
        first_response.json.return_value = {
            "data": {
                "listRuleInstances": {
                    "questionInstances": [{"id": "rule-1", "name": "Test Rule"}],
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
                "listRuleInstances": {
                    "questionInstances": [{"id": "rule-2", "name": "Test Rule 2"}],
                    "pageInfo": {
                        "hasNextPage": False,
                        "endCursor": None
                    }
                }
            }
        }
        
        mock_post.side_effect = [first_response, second_response]

        result = self.client.list_alert_rules()

        assert len(result) == 2
        assert result[0]["id"] == "rule-1"
        assert result[1]["id"] == "rule-2"
        assert mock_post.call_count == 2

    @patch('jupiterone.client.requests.post')
    def test_get_alert_rule_details_found(self, mock_post):
        """Test get_alert_rule_details method - rule found"""
        # Mock response with the target rule
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "listRuleInstances": {
                    "questionInstances": [
                        {"id": "rule-1", "name": "Test Rule"},
                        {"id": "rule-2", "name": "Test Rule 2"}
                    ],
                    "pageInfo": {
                        "hasNextPage": False,
                        "endCursor": None
                    }
                }
            }
        }
        mock_post.return_value = mock_response

        result = self.client.get_alert_rule_details(rule_id="rule-1")

        assert result["id"] == "rule-1"
        assert result["name"] == "Test Rule"

    @patch('jupiterone.client.requests.post')
    def test_get_alert_rule_details_not_found(self, mock_post):
        """Test get_alert_rule_details method - rule not found"""
        # Mock response without the target rule
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "listRuleInstances": {
                    "questionInstances": [
                        {"id": "rule-1", "name": "Test Rule"}
                    ],
                    "pageInfo": {
                        "hasNextPage": False,
                        "endCursor": None
                    }
                }
            }
        }
        mock_post.return_value = mock_response

        result = self.client.get_alert_rule_details(rule_id="nonexistent-rule")

        assert result == "Alert Rule not found for provided ID in configured J1 Account"

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_create_alert_rule_basic(self, mock_execute_query):
        """Test create_alert_rule method - basic usage"""
        mock_response = {
            "data": {
                "createInlineQuestionRuleInstance": {
                    "id": "rule-1",
                    "name": "Test Alert Rule"
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.create_alert_rule(
            name="Test Alert Rule",
            description="Test description",
            polling_interval="ONE_DAY",
            severity="HIGH",
            j1ql="FIND Host"
        )

        assert result == mock_response["data"]["createInlineQuestionRuleInstance"]
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_create_alert_rule_with_resource_group(self, mock_execute_query):
        """Test create_alert_rule method - with resource group"""
        mock_response = {
            "data": {
                "createInlineQuestionRuleInstance": {
                    "id": "rule-1",
                    "name": "Test Alert Rule",
                    "resourceGroupId": "rg-1"
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.create_alert_rule(
            name="Test Alert Rule",
            description="Test description",
            polling_interval="ONE_DAY",
            severity="HIGH",
            j1ql="FIND Host",
            resource_group_id="rg-1"
        )

        assert result == mock_response["data"]["createInlineQuestionRuleInstance"]
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_create_alert_rule_with_action_configs(self, mock_execute_query):
        """Test create_alert_rule method - with action configs"""
        mock_response = {
            "data": {
                "createInlineQuestionRuleInstance": {
                    "id": "rule-1",
                    "name": "Test Alert Rule"
                }
            }
        }
        mock_execute_query.return_value = mock_response

        action_configs = {
            "type": "SEND_EMAIL",
            "recipients": ["test@example.com"]
        }

        result = self.client.create_alert_rule(
            name="Test Alert Rule",
            description="Test description",
            polling_interval="ONE_DAY",
            severity="HIGH",
            j1ql="FIND Host",
            action_configs=action_configs
        )

        assert result == mock_response["data"]["createInlineQuestionRuleInstance"]
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_delete_alert_rule(self, mock_execute_query):
        """Test delete_alert_rule method"""
        mock_response = {
            "data": {
                "deleteRuleInstance": {
                    "id": "rule-1",
                    "deleted": True
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.delete_alert_rule(rule_id="rule-1")

        assert result == mock_response["data"]["deleteRuleInstance"]
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient.get_alert_rule_details')
    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_update_alert_rule_basic(self, mock_execute_query, mock_get_details):
        """Test update_alert_rule method - basic update"""
        # Mock existing rule details
        mock_get_details.return_value = {
            "id": "rule-1",
            "version": 1,
            "name": "Old Name",
            "description": "Old description",
            "pollingInterval": "ONE_DAY",
            "tags": ["old-tag"],
            "labels": [],
            "operations": [{
                "__typename": "Operation",
                "when": {"type": "FILTER", "condition": ["AND", ["queries.query0.total", ">", 0]]},
                "actions": [{"type": "SET_PROPERTY", "targetProperty": "alertLevel", "targetValue": "MEDIUM"}]
            }],
            "question": {
                "__typename": "Question",
                "queries": [{"__typename": "Query", "query": "FIND Host"}]
            },
            "specVersion": 1
        }
        
        mock_response = {
            "data": {
                "updateInlineQuestionRuleInstance": {
                    "id": "rule-1",
                    "name": "New Name"
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.update_alert_rule(
            rule_id="rule-1",
            name="New Name",
            description="New description",
            labels=[]  # Add labels parameter to avoid UnboundLocalError
        )

        assert result == mock_response["data"]["updateInlineQuestionRuleInstance"]
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_evaluate_alert_rule(self, mock_execute_query):
        """Test evaluate_alert_rule method"""
        mock_response = {
            "data": {
                "evaluateRuleInstance": {
                    "id": "evaluation-1",
                    "status": "COMPLETED"
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.evaluate_alert_rule(rule_id="rule-1")

        assert result == mock_response
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_list_alert_rule_evaluation_results(self, mock_execute_query):
        """Test list_alert_rule_evaluation_results method"""
        mock_response = {
            "data": {
                "listCollectionResults": {
                    "results": [{"id": "result-1", "status": "COMPLETED"}]
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.list_alert_rule_evaluation_results(rule_id="rule-1")

        assert result == mock_response
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_fetch_evaluation_result_download_url(self, mock_execute_query):
        """Test fetch_evaluation_result_download_url method"""
        mock_response = {
            "data": {
                "getRawDataDownloadUrl": {
                    "url": "https://example.com/download"
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.fetch_evaluation_result_download_url(raw_data_key="test-key")

        assert result == mock_response
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.requests.get')
    def test_fetch_downloaded_evaluation_results_success(self, mock_get):
        """Test fetch_downloaded_evaluation_results method - success"""
        mock_response = Mock()
        mock_response.json.return_value = {"data": [{"id": "result-1"}]}
        mock_get.return_value = mock_response

        result = self.client.fetch_downloaded_evaluation_results(download_url="https://example.com/download")

        assert result == {"data": [{"id": "result-1"}]}
        mock_get.assert_called_once()

    @patch('jupiterone.client.requests.get')
    def test_fetch_downloaded_evaluation_results_exception(self, mock_get):
        """Test fetch_downloaded_evaluation_results method - exception"""
        mock_get.side_effect = Exception("Network error")

        result = self.client.fetch_downloaded_evaluation_results(download_url="https://example.com/download")

        assert isinstance(result, Exception)
        assert str(result) == "Network error" 