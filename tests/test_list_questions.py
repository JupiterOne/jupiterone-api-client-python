"""Test list_questions method"""

import pytest
from unittest.mock import patch, Mock
from jupiterone.client import JupiterOneClient
from jupiterone.constants import QUESTIONS
from typing import List
from jupiterone.errors import JupiterOneApiError


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

    @patch('jupiterone.client.requests.post')
    def test_list_questions_with_search_query(self, mock_post):
        """Test questions listing with search query parameter"""
        # Mock response for search query
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "questions": {
                    "questions": [
                        {
                            "id": "question-1",
                            "title": "Security Compliance Check",
                            "description": "Check for security compliance issues",
                            "tags": ["security", "compliance"],
                            "queries": [{"name": "SecurityQuery", "query": "FIND Finding WITH severity='HIGH'"}],
                            "compliance": None,
                            "variables": [],
                            "accountId": "test-account",
                            "showTrend": False,
                            "pollingInterval": "ONE_DAY",
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

        # Call list_questions with search query
        result = self.client.list_questions(search_query="security")

        # Verify result
        assert len(result) == 1
        assert result[0]['title'] == "Security Compliance Check"
        assert "security" in result[0]['tags']

        # Verify API call with search query
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]['json']['variables']['searchQuery'] == "security"

    @patch('jupiterone.client.requests.post')
    def test_list_questions_with_tags_filter(self, mock_post):
        """Test questions listing with tags filter parameter"""
        # Mock response for tags filter
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "questions": {
                    "questions": [
                        {
                            "id": "question-1",
                            "title": "CIS AWS Compliance",
                            "description": "CIS AWS Foundations compliance checks",
                            "tags": ["cis", "aws", "compliance"],
                            "queries": [{"name": "CISQuery", "query": "FIND aws_instance WITH encrypted=false"}],
                            "compliance": {
                                "standard": "CIS AWS Foundations",
                                "requirements": ["2.1", "2.2"],
                                "controls": ["Data Protection"]
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

        # Call list_questions with tags filter
        result = self.client.list_questions(tags=["cis", "aws"])

        # Verify result
        assert len(result) == 1
        assert result[0]['title'] == "CIS AWS Compliance"
        assert "cis" in result[0]['tags']
        assert "aws" in result[0]['tags']

        # Verify API call with tags filter
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]['json']['variables']['tags'] == ["cis", "aws"]

    @patch('jupiterone.client.requests.post')
    def test_list_questions_with_search_and_tags(self, mock_post):
        """Test questions listing with both search query and tags filter"""
        # Mock response for combined search and tags
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "questions": {
                    "questions": [
                        {
                            "id": "question-1",
                            "title": "Encryption Security Check",
                            "description": "Check for encryption compliance in security context",
                            "tags": ["security", "compliance", "encryption"],
                            "queries": [{"name": "EncryptionQuery", "query": "FIND DataStore WITH encrypted=false"}],
                            "compliance": {
                                "standard": "PCI-DSS",
                                "requirements": ["3.4"],
                                "controls": ["Data Protection"]
                            },
                            "variables": [],
                            "accountId": "test-account",
                            "showTrend": False,
                            "pollingInterval": "ONE_DAY",
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

        # Call list_questions with both search query and tags
        result = self.client.list_questions(
            search_query="encryption",
            tags=["security", "compliance"]
        )

        # Verify result
        assert len(result) == 1
        assert result[0]['title'] == "Encryption Security Check"
        assert "encryption" in result[0]['tags']
        assert "security" in result[0]['tags']
        assert "compliance" in result[0]['tags']

        # Verify API call with both parameters
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        variables = call_args[1]['json']['variables']
        assert variables['searchQuery'] == "encryption"
        assert variables['tags'] == ["security", "compliance"]

    @patch('jupiterone.client.requests.post')
    def test_list_questions_with_pagination_and_filters(self, mock_post):
        """Test questions listing with filters and pagination"""
        # Mock first page response with filters
        first_response = Mock()
        first_response.json.return_value = {
            "data": {
                "questions": {
                    "questions": [
                        {
                            "id": "question-1",
                            "title": "Security Question 1",
                            "tags": ["security"],
                            "queries": [{"name": "SecurityQuery1", "query": "FIND Host"}],
                            "compliance": None,
                            "variables": [],
                            "accountId": "test-account",
                            "showTrend": False,
                            "pollingInterval": "ONE_DAY",
                            "lastUpdatedTimestamp": "2024-01-01T00:00:00Z"
                        }
                    ],
                    "totalHits": 2,
                    "pageInfo": {
                        "endCursor": "cursor-1",
                        "hasNextPage": True
                    }
                }
            }
        }

        # Mock second page response with filters
        second_response = Mock()
        second_response.json.return_value = {
            "data": {
                "questions": {
                    "questions": [
                        {
                            "id": "question-2",
                            "title": "Security Question 2",
                            "tags": ["security"],
                            "queries": [{"name": "SecurityQuery2", "query": "FIND User"}],
                            "compliance": None,
                            "variables": [],
                            "accountId": "test-account",
                            "showTrend": False,
                            "pollingInterval": "ONE_DAY",
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

        # Set up mock to return different responses for each call
        mock_post.side_effect = [first_response, second_response]

        # Call list_questions with filters
        result = self.client.list_questions(
            search_query="security",
            tags=["security"]
        )

        # Verify result
        assert len(result) == 2
        assert result[0]['title'] == "Security Question 1"
        assert result[1]['title'] == "Security Question 2"

        # Verify API calls (2 calls for 2 pages)
        assert mock_post.call_count == 2

        # Check first call with filters
        first_call = mock_post.call_args_list[0]
        first_variables = first_call[1]['json']['variables']
        assert first_variables['searchQuery'] == "security"
        assert first_variables['tags'] == ["security"]

        # Check second call with filters and cursor
        second_call = mock_post.call_args_list[1]
        second_variables = second_call[1]['json']['variables']
        assert second_variables['searchQuery'] == "security"
        assert second_variables['tags'] == ["security"]
        assert second_variables['cursor'] == "cursor-1"

    @patch('jupiterone.client.requests.post')
    def test_list_questions_no_parameters(self, mock_post):
        """Test questions listing with no parameters (default behavior)"""
        # Mock response for no parameters
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "questions": {
                    "questions": [
                        {
                            "id": "question-1",
                            "title": "Default Question",
                            "tags": ["default"],
                            "queries": [{"name": "DefaultQuery", "query": "FIND *"}],
                            "compliance": None,
                            "variables": [],
                            "accountId": "test-account",
                            "showTrend": False,
                            "pollingInterval": "ONE_DAY",
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

        # Call list_questions with no parameters
        result = self.client.list_questions()

        # Verify result
        assert len(result) == 1
        assert result[0]['title'] == "Default Question"

        # Verify API call with no variables
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]['json']['variables'] == {}

    @patch('jupiterone.client.requests.post')
    def test_list_questions_empty_search_results(self, mock_post):
        """Test questions listing with search that returns no results"""
        # Mock empty response for search
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

        # Call list_questions with search query
        result = self.client.list_questions(search_query="nonexistent")

        # Verify result
        assert len(result) == 0
        assert result == []

        # Verify API call with search query
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]['json']['variables']['searchQuery'] == "nonexistent"

    @patch('jupiterone.client.requests.post')
    def test_list_questions_empty_tags_results(self, mock_post):
        """Test questions listing with tags filter that returns no results"""
        # Mock empty response for tags filter
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

        # Call list_questions with tags filter
        result = self.client.list_questions(tags=["nonexistent_tag"])

        # Verify result
        assert len(result) == 0
        assert result == []

        # Verify API call with tags filter
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]['json']['variables']['tags'] == ["nonexistent_tag"]

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

    def test_list_questions_parameter_validation(self):
        """Test that list_questions method accepts the correct parameter types"""
        # Test that method exists with new signature
        assert hasattr(self.client, 'list_questions')
        method = getattr(self.client, 'list_questions')
        
        # Test that method can be called with different parameter combinations
        import inspect
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())
        
        # Should have self, search_query, and tags parameters
        assert 'search_query' in params
        assert 'tags' in params
        
        # Check parameter types
        search_query_param = sig.parameters['search_query']
        tags_param = sig.parameters['tags']
        
        # search_query should be optional string
        assert search_query_param.default is None
        assert search_query_param.annotation == str or search_query_param.annotation == 'str'
        
        # tags should be optional List[str]
        assert tags_param.default is None
        assert tags_param.annotation == List[str] or 'List[str]' in str(tags_param.annotation)

    def test_list_questions_docstring_updated(self):
        """Test that list_questions method documentation includes new parameters"""
        method = getattr(self.client, 'list_questions')
        docstring = method.__doc__
        
        assert docstring is not None
        assert "search_query" in docstring
        assert "tags" in docstring
        assert "searchQuery" in docstring or "search query" in docstring
        assert "List[str]" in docstring or "List of tags" in docstring


class TestGetQuestionDetails:
    """Test get_question_details method"""

    def setup_method(self):
        """Set up test fixtures"""
        self.client = JupiterOneClient(account="test-account", token="test-token")

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_get_question_details_success(self, mock_execute):
        """Test successful retrieval of question details"""
        # Mock response
        mock_execute.return_value = {
            "data": {
                "question": {
                    "id": "question-123",
                    "sourceId": "source-123",
                    "title": "Test Question",
                    "description": "Test question description",
                    "tags": ["test", "security"],
                    "lastUpdatedTimestamp": "2024-01-01T00:00:00Z",
                    "queries": [
                        {
                            "name": "TestQuery",
                            "query": "FIND Host WITH open=true",
                            "version": "v1",
                            "resultsAre": "BAD"
                        }
                    ],
                    "compliance": {
                        "standard": "CIS",
                        "requirements": ["2.1", "2.2"],
                        "controls": ["Network Security"]
                    },
                    "variables": [
                        {
                            "name": "environment",
                            "required": True,
                            "default": "production"
                        }
                    ],
                    "accountId": "test-account",
                    "integrationDefinitionId": "integration-123",
                    "showTrend": True,
                    "pollingInterval": "ONE_HOUR"
                }
            }
        }

        # Call get_question_details
        result = self.client.get_question_details(question_id="question-123")

        # Verify result
        assert result['id'] == "question-123"
        assert result['title'] == "Test Question"
        assert result['description'] == "Test question description"
        assert result['tags'] == ["test", "security"]
        assert result['sourceId'] == "source-123"
        assert result['accountId'] == "test-account"
        assert result['showTrend'] is True
        assert result['pollingInterval'] == "ONE_HOUR"

        # Verify queries
        queries = result['queries']
        assert len(queries) == 1
        assert queries[0]['name'] == "TestQuery"
        assert queries[0]['query'] == "FIND Host WITH open=true"
        assert queries[0]['version'] == "v1"
        assert queries[0]['resultsAre'] == "BAD"

        # Verify compliance
        compliance = result['compliance']
        assert compliance['standard'] == "CIS"
        assert compliance['requirements'] == ["2.1", "2.2"]
        assert compliance['controls'] == ["Network Security"]

        # Verify variables
        variables = result['variables']
        assert len(variables) == 1
        assert variables[0]['name'] == "environment"
        assert variables[0]['required'] is True
        assert variables[0]['default'] == "production"

        # Verify API call
        mock_execute.assert_called_once()
        call_args = mock_execute.call_args
        assert call_args[1]['variables']['id'] == "question-123"

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_get_question_details_minimal_response(self, mock_execute):
        """Test question details with minimal response data"""
        # Mock minimal response
        mock_execute.return_value = {
            "data": {
                "question": {
                    "id": "question-456",
                    "title": "Minimal Question",
                    "tags": [],
                    "queries": [],
                    "compliance": None,
                    "variables": [],
                    "accountId": "test-account",
                    "showTrend": False,
                    "pollingInterval": "DISABLED"
                }
            }
        }

        # Call get_question_details
        result = self.client.get_question_details(question_id="question-456")

        # Verify result
        assert result['id'] == "question-456"
        assert result['title'] == "Minimal Question"
        assert result['tags'] == []
        assert result['queries'] == []
        assert result['compliance'] is None
        assert result['variables'] == []
        assert result['showTrend'] is False
        assert result['pollingInterval'] == "DISABLED"

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_get_question_details_with_compliance_list(self, mock_execute):
        """Test question details when compliance is returned as a list"""
        # Mock response with compliance as list (edge case)
        mock_execute.return_value = {
            "data": {
                "question": {
                    "id": "question-789",
                    "title": "List Compliance Question",
                    "tags": ["compliance"],
                    "queries": [{"name": "Query1", "query": "FIND Host"}],
                    "compliance": [
                        {
                            "standard": "CIS",
                            "requirements": ["1.1"],
                            "controls": ["Access Control"]
                        }
                    ],
                    "variables": [],
                    "accountId": "test-account",
                    "showTrend": False,
                    "pollingInterval": "ONE_DAY"
                }
            }
        }

        # Call get_question_details
        result = self.client.get_question_details(question_id="question-789")

        # Verify result
        assert result['id'] == "question-789"
        assert result['title'] == "List Compliance Question"
        
        # Verify compliance (should handle list gracefully)
        compliance = result['compliance']
        assert isinstance(compliance, list)
        assert len(compliance) == 1
        assert compliance[0]['standard'] == "CIS"

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_get_question_details_not_found(self, mock_execute):
        """Test question details when question is not found"""
        # Mock response for question not found
        mock_execute.return_value = {
            "data": {
                "question": None
            }
        }

        # Call get_question_details
        result = self.client.get_question_details(question_id="nonexistent")

        # Verify result
        assert result is None

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_get_question_details_api_error(self, mock_execute):
        """Test question details with API error"""
        # Mock API error response
        mock_execute.side_effect = JupiterOneApiError("Question not found")

        # Call get_question_details and expect error
        with pytest.raises(JupiterOneApiError):
            self.client.get_question_details(question_id="invalid-id")

    def test_get_question_details_no_id(self):
        """Test get_question_details without providing question_id"""
        # Call get_question_details without ID
        with pytest.raises(ValueError, match="question_id is required"):
            self.client.get_question_details()

    def test_get_question_details_empty_id(self):
        """Test get_question_details with empty question_id"""
        # Call get_question_details with empty ID
        with pytest.raises(ValueError, match="question_id is required"):
            self.client.get_question_details(question_id="")

    def test_get_question_details_none_id(self):
        """Test get_question_details with None question_id"""
        # Call get_question_details with None ID
        with pytest.raises(ValueError, match="question_id is required"):
            self.client.get_question_details(question_id=None)

    def test_get_question_details_method_exists(self):
        """Test that get_question_details method exists and is callable"""
        assert hasattr(self.client, 'get_question_details')
        assert callable(self.client.get_question_details)

    def test_get_question_details_docstring(self):
        """Test that get_question_details method has proper documentation"""
        method = getattr(self.client, 'get_question_details')
        docstring = method.__doc__
        
        assert docstring is not None
        assert "Get details of a specific question by ID" in docstring
        assert "question_id" in docstring
        assert "Returns" in docstring
        assert "Example" in docstring
        assert "Raises" in docstring

    def test_get_question_details_parameter_validation(self):
        """Test that get_question_details method accepts the correct parameter types"""
        # Test that method exists with correct signature
        assert hasattr(self.client, 'get_question_details')
        method = getattr(self.client, 'get_question_details')
        
        # Test that method can be called with different parameter combinations
        import inspect
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())
        
        # Should have self and question_id parameters
        assert 'question_id' in params
        
        # Check parameter types
        question_id_param = sig.parameters['question_id']
        
        # question_id should be optional string
        assert question_id_param.default is None
        assert question_id_param.annotation == str or question_id_param.annotation == 'str'
