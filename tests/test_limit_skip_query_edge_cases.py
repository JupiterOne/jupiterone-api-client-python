"""Test _limit_and_skip_query method edge cases"""

import pytest
from unittest.mock import Mock, patch

from jupiterone.client import JupiterOneClient
from jupiterone.constants import J1QL_SKIP_COUNT, J1QL_LIMIT_COUNT


class TestLimitAndSkipQueryEdgeCases:
    """Test _limit_and_skip_query method edge cases"""

    def setup_method(self):
        """Set up test fixtures"""
        self.client = JupiterOneClient(account="test-account", token="test-token")

    @patch.object(JupiterOneClient, '_execute_query')
    def test_limit_and_skip_query_tree_result(self, mock_execute_query):
        """Test limit and skip query with tree result (no pagination)"""
        mock_response = {
            "data": {
                "queryV1": {
                    "data": {
                        "vertices": [
                            {"id": "1", "entity": {"_id": "1", "name": "entity1"}},
                            {"id": "2", "entity": {"_id": "2", "name": "entity2"}}
                        ],
                        "edges": [
                            {"id": "edge1", "fromVertexId": "1", "toVertexId": "2"}
                        ]
                    }
                }
            }
        }

        mock_execute_query.return_value = mock_response

        result = self.client._limit_and_skip_query("FIND * LIMIT 10")

        # Should only call once for tree result
        mock_execute_query.assert_called_once()
        
        # Verify the result is returned as-is for tree queries
        assert result == mock_response["data"]["queryV1"]["data"]

    @patch.object(JupiterOneClient, '_execute_query')
    def test_limit_and_skip_query_single_page_exact_skip_count(self, mock_execute_query):
        """Test limit and skip query with exactly skip_count results"""
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

        result = self.client._limit_and_skip_query("FIND * LIMIT 10")

        # Should only call once since we got exactly skip_count results
        mock_execute_query.assert_called_once()
        
        # Verify the result
        assert result == {"data": [
            {"id": "1", "name": "entity1"},
            {"id": "2", "name": "entity2"}
        ]}

    @patch.object(JupiterOneClient, '_execute_query')
    def test_limit_and_skip_query_multiple_pages_with_break(self, mock_execute_query):
        """Test limit and skip query with multiple pages and early break"""
        # First page response
        mock_response1 = {
            "data": {
                "queryV1": {
                    "data": [
                        {"id": "1", "name": "entity1"},
                        {"id": "2", "name": "entity2"}
                    ]
                }
            }
        }
        
        # Second page response (fewer than skip_count, should break)
        mock_response2 = {
            "data": {
                "queryV1": {
                    "data": [
                        {"id": "3", "name": "entity3"}
                    ]
                }
            }
        }

        mock_execute_query.side_effect = [mock_response1, mock_response2]

        result = self.client._limit_and_skip_query("FIND * LIMIT 10")

        # Should call twice, but break on second page
        assert mock_execute_query.call_count == 2
        
        # Verify the result
        assert result == {"data": [
            {"id": "1", "name": "entity1"},
            {"id": "2", "name": "entity2"},
            {"id": "3", "name": "entity3"}
        ]}

    @patch.object(JupiterOneClient, '_execute_query')
    def test_limit_and_skip_query_with_custom_skip_limit(self, mock_execute_query):
        """Test limit and skip query with custom skip and limit values"""
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

        result = self.client._limit_and_skip_query(
            "FIND * LIMIT 10",
            skip=50,
            limit=25
        )

        # Verify the query was called with custom skip/limit
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        query = call_args[0][0]
        assert "SKIP 0 LIMIT 25" in query  # First page starts at 0

        # Verify the result
        assert result == {"data": [
            {"id": "1", "name": "entity1"}
        ]}

    @patch.object(JupiterOneClient, '_execute_query')
    def test_limit_and_skip_query_multiple_pages_with_custom_values(self, mock_execute_query):
        """Test limit and skip query with multiple pages and custom values"""
        # First page response
        mock_response1 = {
            "data": {
                "queryV1": {
                    "data": [
                        {"id": "1", "name": "entity1"},
                        {"id": "2", "name": "entity2"}
                    ]
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
                }
            }
        }

        mock_execute_query.side_effect = [mock_response1, mock_response2]

        result = self.client._limit_and_skip_query(
            "FIND * LIMIT 10",
            skip=10,
            limit=10
        )

        # Should call twice
        assert mock_execute_query.call_count == 2
        
        # Verify the queries were called with correct skip values
        call_args_list = mock_execute_query.call_args_list
        assert "SKIP 0 LIMIT 10" in call_args_list[0][0][0]  # First page
        assert "SKIP 10 LIMIT 10" in call_args_list[1][0][0]  # Second page

        # Verify the result
        assert result == {"data": [
            {"id": "1", "name": "entity1"},
            {"id": "2", "name": "entity2"},
            {"id": "3", "name": "entity3"}
        ]}

    @patch.object(JupiterOneClient, '_execute_query')
    def test_limit_and_skip_query_with_include_deleted_true(self, mock_execute_query):
        """Test limit and skip query with include_deleted=True"""
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

        result = self.client._limit_and_skip_query(
            "FIND * LIMIT 10",
            include_deleted=True
        )

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
    def test_limit_and_skip_query_with_include_deleted_false(self, mock_execute_query):
        """Test limit and skip query with include_deleted=False"""
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

        result = self.client._limit_and_skip_query(
            "FIND * LIMIT 10",
            include_deleted=False
        )

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
    def test_limit_and_skip_query_empty_result(self, mock_execute_query):
        """Test limit and skip query with empty result"""
        mock_response = {
            "data": {
                "queryV1": {
                    "data": []
                }
            }
        }

        mock_execute_query.return_value = mock_response

        result = self.client._limit_and_skip_query("FIND * LIMIT 10")

        # Should only call once since empty result
        mock_execute_query.assert_called_once()
        
        # Verify the result
        assert result == {"data": []}

    @patch.object(JupiterOneClient, '_execute_query')
    def test_limit_and_skip_query_complex_query(self, mock_execute_query):
        """Test limit and skip query with complex J1QL query"""
        mock_response = {
            "data": {
                "queryV1": {
                    "data": [
                        {"_id": "1", "_type": "aws_instance", "name": "instance-1"}
                    ]
                }
            }
        }

        mock_execute_query.return_value = mock_response

        complex_query = """
        FIND aws_instance 
        THAT RELATES TO aws_vpc 
        WITH tag.Environment = 'production'
        RETURN _id, _type, name, tag.Environment
        """

        result = self.client._limit_and_skip_query(complex_query)

        # Verify the query was called with the complex query
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        query = call_args[0][0]
        assert "FIND aws_instance" in query
        assert "THAT RELATES TO aws_vpc" in query
        assert "WITH tag.Environment = 'production'" in query
        assert "SKIP 0 LIMIT" in query  # Should have skip/limit added

        # Verify the result
        assert result == {"data": [
            {"_id": "1", "_type": "aws_instance", "name": "instance-1"}
        ]}

    @patch.object(JupiterOneClient, '_execute_query')
    def test_limit_and_skip_query_pagination_math(self, mock_execute_query):
        """Test limit and skip query pagination math"""
        # First page response
        mock_response1 = {
            "data": {
                "queryV1": {
                    "data": [
                        {"id": "1", "name": "entity1"},
                        {"id": "2", "name": "entity2"}
                    ]
                }
            }
        }
        
        # Second page response
        mock_response2 = {
            "data": {
                "queryV1": {
                    "data": [
                        {"id": "3", "name": "entity3"},
                        {"id": "4", "name": "entity4"}
                    ]
                }
            }
        }
        
        # Third page response
        mock_response3 = {
            "data": {
                "queryV1": {
                    "data": [
                        {"id": "5", "name": "entity5"}
                    ]
                }
            }
        }

        mock_execute_query.side_effect = [mock_response1, mock_response2, mock_response3]

        result = self.client._limit_and_skip_query("FIND * LIMIT 10")

        # Should call three times
        assert mock_execute_query.call_count == 3
        
        # Verify the pagination math
        call_args_list = mock_execute_query.call_args_list
        assert "SKIP 0 LIMIT" in call_args_list[0][0][0]  # Page 0: SKIP 0
        assert "SKIP 100 LIMIT" in call_args_list[1][0][0]  # Page 1: SKIP 100
        assert "SKIP 200 LIMIT" in call_args_list[2][0][0]  # Page 2: SKIP 200

        # Verify the result
        assert result == {"data": [
            {"id": "1", "name": "entity1"},
            {"id": "2", "name": "entity2"},
            {"id": "3", "name": "entity3"},
            {"id": "4", "name": "entity4"},
            {"id": "5", "name": "entity5"}
        ]}

    @patch.object(JupiterOneClient, '_execute_query')
    def test_limit_and_skip_query_default_constants(self, mock_execute_query):
        """Test limit and skip query uses default constants correctly"""
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

        result = self.client._limit_and_skip_query("FIND *")

        # Verify the query was called with default constants
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        query = call_args[0][0]
        assert f"SKIP 0 LIMIT {J1QL_LIMIT_COUNT}" in query

        # Verify the result
        assert result == {"data": [
            {"id": "1", "name": "entity1"}
        ]}

    @patch.object(JupiterOneClient, '_execute_query')
    def test_limit_and_skip_query_tree_result_with_vertices_and_edges(self, mock_execute_query):
        """Test limit and skip query with tree result containing vertices and edges"""
        mock_response = {
            "data": {
                "queryV1": {
                    "data": {
                        "vertices": [
                            {"id": "1", "entity": {"_id": "1", "name": "entity1"}},
                            {"id": "2", "entity": {"_id": "2", "name": "entity2"}}
                        ],
                        "edges": [
                            {
                                "id": "edge1",
                                "fromVertexId": "1",
                                "toVertexId": "2",
                                "relationship": {"_id": "rel1", "_type": "HAS"}
                            }
                        ]
                    }
                }
            }
        }

        mock_execute_query.return_value = mock_response

        result = self.client._limit_and_skip_query("FIND * LIMIT 10")

        # Should only call once for tree result
        mock_execute_query.assert_called_once()
        
        # Verify the result is returned as-is for tree queries
        assert result == mock_response["data"]["queryV1"]["data"]
        assert "vertices" in result
        assert "edges" in result
        assert len(result["vertices"]) == 2
        assert len(result["edges"]) == 1 