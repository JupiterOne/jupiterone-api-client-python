"""Test _cursor_query method edge cases"""

import pytest
from unittest.mock import Mock, patch
import concurrent.futures

from jupiterone.client import JupiterOneClient
from jupiterone.errors import JupiterOneApiError


class TestCursorQueryEdgeCases:
    """Test _cursor_query method edge cases"""

    def setup_method(self):
        """Set up test fixtures"""
        self.client = JupiterOneClient(account="test-account", token="test-token")

    @patch.object(JupiterOneClient, '_execute_query')
    def test_cursor_query_with_limit_in_query_exact_match(self, mock_execute_query):
        """Test cursor query with LIMIT in query that matches exactly"""
        # First page response
        mock_response1 = {
            "data": {
                "queryV1": {
                    "data": [
                        {"id": "1", "name": "entity1"},
                        {"id": "2", "name": "entity2"}
                    ],
                    "cursor": "cursor123"
                }
            }
        }
        
        # Second page response (should not be called due to limit)
        mock_response2 = {
            "data": {
                "queryV1": {
                    "data": [
                        {"id": "3", "name": "entity3"}
                    ],
                    "cursor": "cursor456"
                }
            }
        }

        mock_execute_query.side_effect = [mock_response1, mock_response2]

        result = self.client._cursor_query("FIND * LIMIT 2")

        # Should only call once since we hit the limit exactly
        assert mock_execute_query.call_count == 1
        
        # Verify the result
        assert result == {"data": [
            {"id": "1", "name": "entity1"},
            {"id": "2", "name": "entity2"}
        ]}

    @patch.object(JupiterOneClient, '_execute_query')
    def test_cursor_query_with_limit_in_query_under_limit(self, mock_execute_query):
        """Test cursor query with LIMIT in query but fewer results than limit"""
        # Response with fewer results than limit
        mock_response = {
            "data": {
                "queryV1": {
                    "data": [
                        {"id": "1", "name": "entity1"}
                    ]
                    # No cursor since we're under the limit
                }
            }
        }

        mock_execute_query.return_value = mock_response

        result = self.client._cursor_query("FIND * LIMIT 5")

        # Should only call once since no cursor returned
        assert mock_execute_query.call_count == 1
        
        # Verify the result
        assert result == {"data": [
            {"id": "1", "name": "entity1"}
        ]}

    @patch.object(JupiterOneClient, '_execute_query')
    def test_cursor_query_with_limit_in_query_over_limit(self, mock_execute_query):
        """Test cursor query with LIMIT in query but more results than limit"""
        # First page response
        mock_response1 = {
            "data": {
                "queryV1": {
                    "data": [
                        {"id": "1", "name": "entity1"},
                        {"id": "2", "name": "entity2"},
                        {"id": "3", "name": "entity3"}
                    ],
                    "cursor": "cursor123"
                }
            }
        }
        
        # Second page response
        mock_response2 = {
            "data": {
                "queryV1": {
                    "data": [
                        {"id": "4", "name": "entity4"},
                        {"id": "5", "name": "entity5"}
                    ],
                    "cursor": "cursor456"
                }
            }
        }

        mock_execute_query.side_effect = [mock_response1, mock_response2]

        result = self.client._cursor_query("FIND * LIMIT 4")

        # Should call twice but only return 4 results
        assert mock_execute_query.call_count == 2
        
        # Verify the result is limited to 4
        assert len(result["data"]) == 4
        assert result["data"][0]["id"] == "1"
        assert result["data"][3]["id"] == "4"

    @patch.object(JupiterOneClient, '_execute_query')
    def test_cursor_query_parallel_processing_error_handling(self, mock_execute_query):
        """Test cursor query with parallel processing and error handling"""
        # First page response
        mock_response1 = {
            "data": {
                "queryV1": {
                    "data": [
                        {"id": "1", "name": "entity1"}
                    ],
                    "cursor": "cursor123"
                }
            }
        }
        
        # Second page response (will cause error)
        mock_response2 = JupiterOneApiError("API Error")

        mock_execute_query.side_effect = [mock_response1, mock_response2]

        # Use parallel processing with error handling
        result = self.client._cursor_query("FIND * LIMIT 10", max_workers=2)

        # Should handle the error gracefully and return first page
        assert result == {"data": [
            {"id": "1", "name": "entity1"}
        ]}

    @patch.object(JupiterOneClient, '_execute_query')
    def test_cursor_query_parallel_processing_cancel_futures(self, mock_execute_query):
        """Test cursor query with parallel processing and future cancellation"""
        # First page response
        mock_response1 = {
            "data": {
                "queryV1": {
                    "data": [
                        {"id": "1", "name": "entity1"},
                        {"id": "2", "name": "entity2"}
                    ],
                    "cursor": "cursor123"
                }
            }
        }
        
        # Second page response
        mock_response2 = {
            "data": {
                "queryV1": {
                    "data": [
                        {"id": "3", "name": "entity3"}
                    ]
                    # No cursor - final page
                }
            }
        }

        mock_execute_query.side_effect = [mock_response1, mock_response2]

        result = self.client._cursor_query("FIND * LIMIT 2", max_workers=2)

        # Should return only 2 results due to limit
        assert len(result["data"]) == 2
        assert result["data"][0]["id"] == "1"
        assert result["data"][1]["id"] == "2"

    @patch.object(JupiterOneClient, '_execute_query')
    def test_cursor_query_with_include_deleted_true(self, mock_execute_query):
        """Test cursor query with include_deleted=True"""
        mock_response = {
            "data": {
                "queryV1": {
                    "data": [
                        {"id": "1", "name": "entity1", "deleted": True},
                        {"id": "2", "name": "entity2", "deleted": False}
                    ]
                }
            }
        }

        mock_execute_query.return_value = mock_response

        result = self.client._cursor_query("FIND * LIMIT 10", include_deleted=True)

        # Verify the query was called with includeDeleted=True
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        variables = call_args[0][1]
        assert variables["includeDeleted"] is True

        # Verify the result
        assert result == {"data": [
            {"id": "1", "name": "entity1", "deleted": True},
            {"id": "2", "name": "entity2", "deleted": False}
        ]}

    @patch.object(JupiterOneClient, '_execute_query')
    def test_cursor_query_with_include_deleted_false(self, mock_execute_query):
        """Test cursor query with include_deleted=False"""
        mock_response = {
            "data": {
                "queryV1": {
                    "data": [
                        {"id": "1", "name": "entity1"},
                        {"id": "2", "name": "entity2"}
                    ]
                }
            }
        }

        mock_execute_query.return_value = mock_response

        result = self.client._cursor_query("FIND * LIMIT 10", include_deleted=False)

        # Verify the query was called with includeDeleted=False
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        variables = call_args[0][1]
        assert variables["includeDeleted"] is False

        # Verify the result
        assert result == {"data": [
            {"id": "1", "name": "entity1"},
            {"id": "2", "name": "entity2"}
        ]}

    @patch.object(JupiterOneClient, '_execute_query')
    def test_cursor_query_with_initial_cursor(self, mock_execute_query):
        """Test cursor query with initial cursor parameter"""
        mock_response = {
            "data": {
                "queryV1": {
                    "data": [
                        {"id": "3", "name": "entity3"},
                        {"id": "4", "name": "entity4"}
                    ]
                }
            }
        }

        mock_execute_query.return_value = mock_response

        result = self.client._cursor_query("FIND * LIMIT 10", cursor="initial_cursor")

        # Verify the query was called with the initial cursor
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        variables = call_args[0][1]
        assert variables["cursor"] == "initial_cursor"

        # Verify the result
        assert result == {"data": [
            {"id": "3", "name": "entity3"},
            {"id": "4", "name": "entity4"}
        ]}

    @patch.object(JupiterOneClient, '_execute_query')
    def test_cursor_query_no_limit_in_query(self, mock_execute_query):
        """Test cursor query without LIMIT in query"""
        # First page response
        mock_response1 = {
            "data": {
                "queryV1": {
                    "data": [
                        {"id": "1", "name": "entity1"},
                        {"id": "2", "name": "entity2"}
                    ],
                    "cursor": "cursor123"
                }
            }
        }
        
        # Second page response
        mock_response2 = {
            "data": {
                "queryV1": {
                    "data": [
                        {"id": "3", "name": "entity3"}
                    ]
                    # No cursor - final page
                }
            }
        }

        mock_execute_query.side_effect = [mock_response1, mock_response2]

        result = self.client._cursor_query("FIND *")

        # Should call twice and return all results
        assert mock_execute_query.call_count == 2
        
        # Verify the result
        assert result == {"data": [
            {"id": "1", "name": "entity1"},
            {"id": "2", "name": "entity2"},
            {"id": "3", "name": "entity3"}
        ]}

    @patch.object(JupiterOneClient, '_execute_query')
    def test_cursor_query_case_insensitive_limit(self, mock_execute_query):
        """Test cursor query with case insensitive LIMIT matching"""
        mock_response = {
            "data": {
                "queryV1": {
                    "data": [
                        {"id": "1", "name": "entity1"},
                        {"id": "2", "name": "entity2"}
                    ]
                }
            }
        }

        mock_execute_query.return_value = mock_response

        # Test with lowercase 'limit'
        result = self.client._cursor_query("FIND * limit 5")

        # Should still work and return results
        assert result == {"data": [
            {"id": "1", "name": "entity1"},
            {"id": "2", "name": "entity2"}
        ]}

    @patch.object(JupiterOneClient, '_execute_query')
    def test_cursor_query_complex_limit_pattern(self, mock_execute_query):
        """Test cursor query with complex LIMIT pattern in query"""
        mock_response = {
            "data": {
                "queryV1": {
                    "data": [
                        {"id": "1", "name": "entity1"}
                    ]
                }
            }
        }

        mock_execute_query.return_value = mock_response

        # Test with complex query containing LIMIT
        complex_query = """
        FIND aws_instance 
        THAT RELATES TO aws_vpc 
        WITH tag.Environment = 'production'
        RETURN _id, _type, name
        LIMIT 100
        """

        result = self.client._cursor_query(complex_query)

        # Should work with complex queries
        assert result == {"data": [
            {"id": "1", "name": "entity1"}
        ]}

    @patch.object(JupiterOneClient, '_execute_query')
    def test_cursor_query_max_workers_none(self, mock_execute_query):
        """Test cursor query with max_workers=None (sequential processing)"""
        # First page response
        mock_response1 = {
            "data": {
                "queryV1": {
                    "data": [
                        {"id": "1", "name": "entity1"}
                    ],
                    "cursor": "cursor123"
                }
            }
        }
        
        # Second page response
        mock_response2 = {
            "data": {
                "queryV1": {
                    "data": [
                        {"id": "2", "name": "entity2"}
                    ]
                }
            }
        }

        mock_execute_query.side_effect = [mock_response1, mock_response2]

        result = self.client._cursor_query("FIND * LIMIT 10", max_workers=None)

        # Should use sequential processing
        assert mock_execute_query.call_count == 2
        
        # Verify the result
        assert result == {"data": [
            {"id": "1", "name": "entity1"},
            {"id": "2", "name": "entity2"}
        ]}

    @patch.object(JupiterOneClient, '_execute_query')
    def test_cursor_query_max_workers_one(self, mock_execute_query):
        """Test cursor query with max_workers=1 (sequential processing)"""
        # First page response
        mock_response1 = {
            "data": {
                "queryV1": {
                    "data": [
                        {"id": "1", "name": "entity1"}
                    ],
                    "cursor": "cursor123"
                }
            }
        }
        
        # Second page response
        mock_response2 = {
            "data": {
                "queryV1": {
                    "data": [
                        {"id": "2", "name": "entity2"}
                    ]
                }
            }
        }

        mock_execute_query.side_effect = [mock_response1, mock_response2]

        result = self.client._cursor_query("FIND * LIMIT 10", max_workers=1)

        # Should use sequential processing
        assert mock_execute_query.call_count == 2
        
        # Verify the result
        assert result == {"data": [
            {"id": "1", "name": "entity1"},
            {"id": "2", "name": "entity2"}
        ]} 