"""Test query-related methods"""

import pytest
import warnings
from unittest.mock import Mock, patch
from jupiterone.client import JupiterOneClient
from jupiterone.errors import JupiterOneApiError


class TestQueryMethods:
    """Test query-related methods"""

    def setup_method(self):
        """Set up test fixtures"""
        self.client = JupiterOneClient(account="test-account", token="test-token")

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_cursor_query_single_page(self, mock_execute_query):
        """Test _cursor_query method with single page"""
        mock_response = {
            "data": {
                "queryV1": {
                    "data": [{"id": "1"}, {"id": "2"}],
                    "cursor": None
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client._cursor_query("FIND Host")

        assert result == {"data": [{"id": "1"}, {"id": "2"}]}
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_cursor_query_multiple_pages(self, mock_execute_query):
        """Test _cursor_query method with multiple pages"""
        # First page
        first_response = {
            "data": {
                "queryV1": {
                    "data": [{"id": "1"}],
                    "cursor": "cursor-1"
                }
            }
        }
        
        # Second page
        second_response = {
            "data": {
                "queryV1": {
                    "data": [{"id": "2"}],
                    "cursor": None
                }
            }
        }
        
        mock_execute_query.side_effect = [first_response, second_response]

        result = self.client._cursor_query("FIND Host")

        assert result == {"data": [{"id": "1"}, {"id": "2"}]}
        assert mock_execute_query.call_count == 2

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_cursor_query_tree_result(self, mock_execute_query):
        """Test _cursor_query method with tree result"""
        mock_response = {
            "data": {
                "queryV1": {
                    "data": {
                        "vertices": [{"id": "1"}],
                        "edges": [{"id": "edge-1"}]
                    }
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client._cursor_query("FIND Host")

        assert result == {"vertices": [{"id": "1"}], "edges": [{"id": "edge-1"}]}
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_cursor_query_with_limit(self, mock_execute_query):
        """Test _cursor_query method with inline LIMIT"""
        # First page
        first_response = {
            "data": {
                "queryV1": {
                    "data": [{"id": "1"}],
                    "cursor": "cursor-1"
                }
            }
        }
        
        # Second page
        second_response = {
            "data": {
                "queryV1": {
                    "data": [{"id": "2"}],
                    "cursor": "cursor-2"
                }
            }
        }
        
        mock_execute_query.side_effect = [first_response, second_response]

        result = self.client._cursor_query("FIND Host LIMIT 2")

        assert result == {"data": [{"id": "1"}, {"id": "2"}]}
        assert mock_execute_query.call_count == 2

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_cursor_query_with_include_deleted(self, mock_execute_query):
        """Test _cursor_query method with include_deleted parameter"""
        mock_response = {
            "data": {
                "queryV1": {
                    "data": [{"id": "1"}],
                    "cursor": None
                }
            }
        }
        mock_execute_query.return_value = mock_response

        self.client._cursor_query("FIND Host", include_deleted=True)

        # Verify includeDeleted was passed
        call_args = mock_execute_query.call_args
        assert call_args[1]["variables"]["includeDeleted"] is True

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_limit_and_skip_query_single_page(self, mock_execute_query):
        """Test _limit_and_skip_query method with single page"""
        mock_response = {
            "data": {
                "queryV1": {
                    "data": [{"id": "1"}, {"id": "2"}]
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client._limit_and_skip_query("FIND Host")

        assert result == {"data": [{"id": "1"}, {"id": "2"}]}
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_limit_and_skip_query_multiple_pages(self, mock_execute_query):
        """Test _limit_and_skip_query method with multiple pages"""
        # First page
        first_response = {
            "data": {
                "queryV1": {
                    "data": [{"id": "1"}, {"id": "2"}]
                }
            }
        }
        
        # Second page (less than skip count)
        second_response = {
            "data": {
                "queryV1": {
                    "data": [{"id": "3"}]
                }
            }
        }
        
        mock_execute_query.side_effect = [first_response, second_response]

        result = self.client._limit_and_skip_query("FIND Host")

        # The method should return all data from both pages
        assert result == {"data": [{"id": "1"}, {"id": "2"}, {"id": "3"}]}
        assert mock_execute_query.call_count == 2

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_limit_and_skip_query_tree_result(self, mock_execute_query):
        """Test _limit_and_skip_query method with tree result"""
        mock_response = {
            "data": {
                "queryV1": {
                    "data": {
                        "vertices": [{"id": "1"}],
                        "edges": [{"id": "edge-1"}]
                    }
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client._limit_and_skip_query("FIND Host")

        assert result == {"vertices": [{"id": "1"}], "edges": [{"id": "edge-1"}]}
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._limit_and_skip_query')
    def test_query_v1_with_skip_limit(self, mock_limit_skip_query):
        """Test query_v1 method with skip and limit parameters"""
        mock_limit_skip_query.return_value = {"data": [{"id": "1"}]}

        with warnings.catch_warnings(record=True) as w:
            result = self.client.query_v1("FIND Host", skip=10, limit=20)
            
            # Verify deprecation warning was issued
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "limit and skip pagination is no longer a recommended method" in str(w[0].message)

        assert result == {"data": [{"id": "1"}]}
        mock_limit_skip_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._cursor_query')
    def test_query_v1_without_skip_limit(self, mock_cursor_query):
        """Test query_v1 method without skip and limit parameters"""
        mock_cursor_query.return_value = {"data": [{"id": "1"}]}

        result = self.client.query_v1("FIND Host")

        assert result == {"data": [{"id": "1"}]}
        mock_cursor_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._cursor_query')
    def test_query_v1_with_cursor(self, mock_cursor_query):
        """Test query_v1 method with cursor parameter"""
        mock_cursor_query.return_value = {"data": [{"id": "1"}]}

        result = self.client.query_v1("FIND Host", cursor="test-cursor")

        assert result == {"data": [{"id": "1"}]}
        mock_cursor_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._cursor_query')
    def test_query_v1_with_include_deleted(self, mock_cursor_query):
        """Test query_v1 method with include_deleted parameter"""
        mock_cursor_query.return_value = {"data": [{"id": "1"}]}

        result = self.client.query_v1("FIND Host", include_deleted=True)

        assert result == {"data": [{"id": "1"}]}
        mock_cursor_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_cursor_query_with_parallel_processing(self, mock_execute_query):
        """Test _cursor_query method with parallel processing"""
        # First page
        first_response = {
            "data": {
                "queryV1": {
                    "data": [{"id": "1"}],
                    "cursor": "cursor-1"
                }
            }
        }
        
        # Second page
        second_response = {
            "data": {
                "queryV1": {
                    "data": [{"id": "2"}],
                    "cursor": None
                }
            }
        }
        
        mock_execute_query.side_effect = [first_response, second_response]

        result = self.client._cursor_query("FIND Host", max_workers=2)

        assert result == {"data": [{"id": "1"}, {"id": "2"}]}
        assert mock_execute_query.call_count == 2

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_cursor_query_with_limit_in_query(self, mock_execute_query):
        """Test _cursor_query method with LIMIT in the query string"""
        # First page
        first_response = {
            "data": {
                "queryV1": {
                    "data": [{"id": "1"}],
                    "cursor": "cursor-1"
                }
            }
        }
        
        # Second page (should not be called due to LIMIT)
        second_response = {
            "data": {
                "queryV1": {
                    "data": [{"id": "2"}],
                    "cursor": "cursor-2"
                }
            }
        }
        
        mock_execute_query.side_effect = [first_response, second_response]

        result = self.client._cursor_query("FIND Host LIMIT 1")

        assert result == {"data": [{"id": "1"}]}
        assert mock_execute_query.call_count == 1  # Should stop after first page due to LIMIT 