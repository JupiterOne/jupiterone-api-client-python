"""Test list_questions method"""

import pytest
from unittest.mock import patch, Mock
from jupiterone.client import JupiterOneClient
from jupiterone.constants import QUESTIONS


class TestListQuestions:
    """Test list_questions method"""

    def setup_method(self):
        """Set up test fixtures"""
        self.client = JupiterOneClient(account="test-account", token="test-token")

    @patch('jupiterone.client.requests.post')
    def test_list_questions_basic(self, mock_post):
        """Test basic questions listing with single page"""
        # Mock response for single page
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "questions": {
                    "questions": [
                        {
                            "id": "question-1",
                            "title": "Test Question 1",
                            "description": "Test description 1",
                            "tags": ["test", "security"],
                            "queries": [{
                                "name": "Query1",
                                "query": "FIND Host",
                                "version": "v1",
                                "resultsAre": "INFORMATIVE"
                            }],
                            "compliance": {
                                "standard": "CIS",
                                "requirements": ["2.1", "2.2"],
                                "controls": ["Network Security"]
                            },
                            "variables": [],
                            "accountId": "test-account",
                            "showTrend": False,
                            "pollingInterval": "ONE_DAY",
                            "lastUpdatedTimestamp": "2024-01-01T00:00:00Z"
                        },
                        {
                            "id": "question-2",
                            "title": "Test Question 2",
                            "description": "Test description 2",
                            "tags": ["compliance", "audit"],
                            "queries": [{
                                "name": "Query2",
                                "query": "FIND User WITH mfaEnabled=false",
                                "version": "v1",
                                "resultsAre": "BAD"
                            }],
                            "compliance": None,
                            "variables": [
                                {
                                    "name": "environment",
                                    "required": True,
                                    "default": "production"
                                }
                            ],
                            "accountId": "test-account",
                            "showTrend": True,
                            "pollingInterval": "DISABLED",
                            "lastUpdatedTimestamp": "2024-01-02T00:00:00Z"
                        }
                    ],
                    "totalHits": 2,
                    "pageInfo": {
                        "endCursor": None,
                        "hasNextPage": False
                    }
                }
            }
        }
        mock_post.return_value = mock_response

        # Call list_questions
        result = self.client.list_questions()

        # Verify result
        assert len(result) == 2
        assert result[0]['id'] == "question-1"
        assert result[0]['title'] == "Test Question 1"
        assert result[0]['tags'] == ["test", "security"]
        assert result[1]['id'] == "question-2"
        assert result[1]['title'] == "Test Question 2"
        assert result[1]['tags'] == ["compliance", "audit"]

        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        
        # Check the query was called with correct parameters
        assert call_args[1]['json']['query'] == QUESTIONS
        assert call_args[1]['json']['flags']['variableResultSize'] is True

    @patch('jupiterone.client.requests.post')
    def test_list_questions_with_pagination(self, mock_post):
        """Test questions listing with multiple pages"""
        # Mock first page response
        first_response = Mock()
        first_response.json.return_value = {
            "data": {
                "questions": {
                    "questions": [
                        {
                            "id": "question-1",
                            "title": "Test Question 1",
                            "tags": ["test"],
                            "queries": [{"name": "Query1", "query": "FIND Host"}],
                            "compliance": None,
                            "variables": [],
                            "accountId": "test-account",
                            "showTrend": False,
                            "pollingInterval": "ONE_DAY",
                            "lastUpdatedTimestamp": "2024-01-01T00:00:00Z"
                        }
                    ],
                    "totalHits": 3,
                    "pageInfo": {
                        "endCursor": "cursor-1",
                        "hasNextPage": True
                    }
                }
            }
        }

        # Mock second page response
        second_response = Mock()
        second_response.json.return_value = {
            "data": {
                "questions": {
                    "questions": [
                        {
                            "id": "question-2",
                            "title": "Test Question 2",
                            "tags": ["security"],
                            "queries": [{"name": "Query2", "query": "FIND User"}],
                            "compliance": None,
                            "variables": [],
                            "accountId": "test-account",
                            "showTrend": False,
                            "pollingInterval": "ONE_DAY",
                            "lastUpdatedTimestamp": "2024-01-02T00:00:00Z"
                        },
                        {
                            "id": "question-3",
                            "title": "Test Question 3",
                            "tags": ["compliance"],
                            "queries": [{"name": "Query3", "query": "FIND Finding"}],
                            "compliance": None,
                            "variables": [],
                            "accountId": "test-account",
                            "showTrend": False,
                            "pollingInterval": "ONE_DAY",
                            "lastUpdatedTimestamp": "2024-01-03T00:00:00Z"
                        }
                    ],
                    "totalHits": 3,
                    "pageInfo": {
                        "endCursor": None,
                        "hasNextPage": False
                    }
                }
            }
        }

        # Set up mock to return different responses for each call
        mock_post.side_effect = [first_response, second_response]

        # Call list_questions
        result = self.client.list_questions()

        # Verify result
        assert len(result) == 3
        assert result[0]['id'] == "question-1"
        assert result[1]['id'] == "question-2"
        assert result[2]['id'] == "question-3"

        # Verify API calls (2 calls for 2 pages)
        assert mock_post.call_count == 2

        # Check first call
        first_call = mock_post.call_args_list[0]
        assert first_call[1]['json']['query'] == QUESTIONS
        assert first_call[1]['json']['flags']['variableResultSize'] is True

        # Check second call (with cursor)
        second_call = mock_post.call_args_list[1]
        assert second_call[1]['json']['query'] == QUESTIONS
        assert second_call[1]['json']['variables']['cursor'] == "cursor-1"
        assert second_call[1]['json']['flags']['variableResultSize'] is True

    @patch('jupiterone.client.requests.post')
    def test_list_questions_empty_response(self, mock_post):
        """Test questions listing with empty response"""
        # Mock empty response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "questions": {
                    "questions": [],
                    "totalHits": 0,
                    "pageInfo": {
                        "endCursor": None,
                        "hasNextPage": False
                    }
                }
            }
        }
        mock_post.return_value = mock_response

        # Call list_questions
        result = self.client.list_questions()

        # Verify result
        assert len(result) == 0
        assert result == []

        # Verify API call
        mock_post.assert_called_once()

    @patch('jupiterone.client.requests.post')
    def test_list_questions_with_compliance_data(self, mock_post):
        """Test questions listing with compliance metadata"""
        # Mock response with compliance data
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "questions": {
                    "questions": [
                        {
                            "id": "question-1",
                            "title": "CIS Compliance Check",
                            "tags": ["cis", "compliance"],
                            "queries": [{"name": "CISQuery", "query": "FIND Host WITH encrypted=false"}],
                            "compliance": {
                                "standard": "CIS AWS Foundations",
                                "requirements": ["2.1", "2.2", "2.3"],
                                "controls": ["Data Protection", "Network Security"]
                            },
                            "variables": [],
                            "accountId": "test-account",
                            "showTrend": True,
                            "pollingInterval": "ONE_HOUR",
                            "lastUpdatedTimestamp": "2024-01-01T00:00:00Z"
                        }
                    ],
                    "totalHits": 1,
                    "pageInfo": {
                        "endCursor": None,
                        "hasNextPage": False
                    }
                }
            }
        }
        mock_post.return_value = mock_response

        # Call list_questions
        result = self.client.list_questions()

        # Verify result
        assert len(result) == 1
        question = result[0]
        assert question['id'] == "question-1"
        assert question['title'] == "CIS Compliance Check"
        assert question['tags'] == ["cis", "compliance"]
        
        # Verify compliance data
        compliance = question['compliance']
        assert compliance['standard'] == "CIS AWS Foundations"
        assert compliance['requirements'] == ["2.1", "2.2", "2.3"]
        assert compliance['controls'] == ["Data Protection", "Network Security"]

    @patch('jupiterone.client.requests.post')
    def test_list_questions_with_variables(self, mock_post):
        """Test questions listing with variable definitions"""
        # Mock response with variables
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "questions": {
                    "questions": [
                        {
                            "id": "question-1",
                            "title": "Environment-Specific Query",
                            "tags": ["environment", "variables"],
                            "queries": [{"name": "EnvQuery", "query": "FIND * WITH tag.Environment={{env}}"}],
                            "compliance": None,
                            "variables": [
                                {
                                    "name": "env",
                                    "required": True,
                                    "default": "production"
                                },
                                {
                                    "name": "region",
                                    "required": False,
                                    "default": "us-east-1"
                                }
                            ],
                            "accountId": "test-account",
                            "showTrend": False,
                            "pollingInterval": "DISABLED",
                            "lastUpdatedTimestamp": "2024-01-01T00:00:00Z"
                        }
                    ],
                    "totalHits": 1,
                    "pageInfo": {
                        "endCursor": None,
                        "hasNextPage": False
                    }
                }
            }
        }
        mock_post.return_value = mock_response

        # Call list_questions
        result = self.client.list_questions()

        # Verify result
        assert len(result) == 1
        question = result[0]
        assert question['id'] == "question-1"
        assert question['title'] == "Environment-Specific Query"
        
        # Verify variables
        variables = question['variables']
        assert len(variables) == 2
        assert variables[0]['name'] == "env"
        assert variables[0]['required'] is True
        assert variables[0]['default'] == "production"
        assert variables[1]['name'] == "region"
        assert variables[1]['required'] is False
        assert variables[1]['default'] == "us-east-1"

    @patch('jupiterone.client.requests.post')
    def test_list_questions_with_polling_intervals(self, mock_post):
        """Test questions listing with different polling intervals"""
        # Mock response with various polling intervals
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "questions": {
                    "questions": [
                        {
                            "id": "question-1",
                            "title": "Daily Check",
                            "tags": ["daily"],
                            "queries": [{"name": "DailyQuery", "query": "FIND Finding"}],
                            "compliance": None,
                            "variables": [],
                            "accountId": "test-account",
                            "showTrend": False,
                            "pollingInterval": "ONE_DAY",
                            "lastUpdatedTimestamp": "2024-01-01T00:00:00Z"
                        },
                        {
                            "id": "question-2",
                            "title": "Hourly Check",
                            "tags": ["hourly"],
                            "queries": [{"name": "HourlyQuery", "query": "FIND User"}],
                            "compliance": None,
                            "variables": [],
                            "accountId": "test-account",
                            "showTrend": True,
                            "pollingInterval": "ONE_HOUR",
                            "lastUpdatedTimestamp": "2024-01-01T00:00:00Z"
                        },
                        {
                            "id": "question-3",
                            "title": "Disabled Check",
                            "tags": ["disabled"],
                            "queries": [{"name": "DisabledQuery", "query": "FIND Host"}],
                            "compliance": None,
                            "variables": [],
                            "accountId": "test-account",
                            "showTrend": False,
                            "pollingInterval": "DISABLED",
                            "lastUpdatedTimestamp": "2024-01-01T00:00:00Z"
                        }
                    ],
                    "totalHits": 3,
                    "pageInfo": {
                        "endCursor": None,
                        "hasNextPage": False
                    }
                }
            }
        }
        mock_post.return_value = mock_response

        # Call list_questions
        result = self.client.list_questions()

        # Verify result
        assert len(result) == 3
        
        # Verify polling intervals
        assert result[0]['pollingInterval'] == "ONE_DAY"
        assert result[1]['pollingInterval'] == "ONE_HOUR"
        assert result[2]['pollingInterval'] == "DISABLED"
        
        # Verify showTrend settings
        assert result[0]['showTrend'] is False
        assert result[1]['showTrend'] is True
        assert result[2]['showTrend'] is False

    @patch('jupiterone.client.requests.post')
    def test_list_questions_error_handling(self, mock_post):
        """Test questions listing with error handling"""
        # Mock error response
        mock_response = Mock()
        mock_response.json.return_value = {
            "errors": [
                {
                    "message": "Unauthorized access",
                    "extensions": {"code": "UNAUTHORIZED"}
                }
            ]
        }
        mock_post.return_value = mock_response

        # Call list_questions and expect it to handle the error gracefully
        # The method should return an empty list or raise an exception
        with pytest.raises(Exception):
            self.client.list_questions()

    @patch('jupiterone.client.requests.post')
    def test_list_questions_malformed_response(self, mock_post):
        """Test questions listing with malformed response"""
        # Mock malformed response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "questions": {
                    # Missing required fields
                    "questions": [
                        {
                            "id": "question-1",
                            # Missing title
                            "tags": ["test"]
                            # Missing other required fields
                        }
                    ]
                }
            }
        }
        mock_post.return_value = mock_response

        # Call list_questions
        result = self.client.list_questions()

        # Verify result (should still work with missing fields)
        assert len(result) == 1
        question = result[0]
        assert question['id'] == "question-1"
        assert question['tags'] == ["test"]
        # Missing fields should be None or not present
        assert 'title' not in question or question['title'] is None

    def test_list_questions_method_exists(self):
        """Test that list_questions method exists and is callable"""
        assert hasattr(self.client, 'list_questions')
        assert callable(self.client.list_questions)

    def test_list_questions_docstring(self):
        """Test that list_questions method has proper documentation"""
        method = getattr(self.client, 'list_questions')
        assert method.__doc__ is not None
        assert "List all defined Questions" in method.__doc__
        assert "J1 account Questions Library" in method.__doc__
