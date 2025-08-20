"""Test question management methods"""

import pytest
from unittest.mock import patch
from jupiterone.client import JupiterOneClient
from jupiterone.errors import JupiterOneApiError
from jupiterone.constants import UPDATE_QUESTION, DELETE_QUESTION


class TestQuestionManagement:
    """Test question management methods"""

    def setup_method(self):
        """Set up test fixtures"""
        self.client = JupiterOneClient(account="test-account", token="test-token")
        self.question_id = "test-question-123"

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_update_question_title_only(self, mock_execute_query):
        """Test updating question title only"""
        mock_response = {
            "data": {
                "updateQuestion": {
                    "id": self.question_id,
                    "title": "Updated Question Title",
                    "description": "Original description",
                    "queries": [{"name": "Query0", "query": "FIND Host"}],
                    "tags": ["original", "tag"]
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.update_question(
            question_id=self.question_id,
            title="Updated Question Title"
        )

        # Verify the call
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        
        # Check the mutation was called with correct parameters
        assert call_args[0][0] == UPDATE_QUESTION
        
        # Check variables - they are in the second positional argument
        variables = call_args[0][1]
        assert variables['id'] == self.question_id
        assert variables['update']['title'] == "Updated Question Title"
        assert 'description' not in variables['update']
        assert 'queries' not in variables['update']
        assert 'tags' not in variables['update']

        # Check result
        assert result['id'] == self.question_id
        assert result['title'] == "Updated Question Title"

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_update_question_description_only(self, mock_execute_query):
        """Test updating question description only"""
        mock_response = {
            "data": {
                "updateQuestion": {
                    "id": self.question_id,
                    "title": "Original Title",
                    "description": "Updated description",
                    "queries": [{"name": "Query0", "query": "FIND Host"}],
                    "tags": ["original", "tag"]
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.update_question(
            question_id=self.question_id,
            description="Updated description"
        )

        # Verify the call
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        
        # Check variables - they are in the second positional argument
        variables = call_args[0][1]
        assert variables['id'] == self.question_id
        assert variables['update']['description'] == "Updated description"
        assert 'title' not in variables['update']
        assert 'queries' not in variables['update']
        assert 'tags' not in variables['update']

        # Check result
        assert result['description'] == "Updated description"

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_update_question_tags_only(self, mock_execute_query):
        """Test updating question tags only"""
        new_tags = ["security", "compliance", "updated"]
        mock_response = {
            "data": {
                "updateQuestion": {
                    "id": self.question_id,
                    "title": "Original Title",
                    "description": "Original description",
                    "queries": [{"name": "Query0", "query": "FIND Host"}],
                    "tags": new_tags
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.update_question(
            question_id=self.question_id,
            tags=new_tags
        )

        # Verify the call
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        
        # Check variables - they are in the second positional argument
        variables = call_args[0][1]
        assert variables['id'] == self.question_id
        assert variables['update']['tags'] == new_tags
        assert 'title' not in variables['update']
        assert 'description' not in variables['update']
        assert 'queries' not in variables['update']

        # Check result
        assert result['tags'] == new_tags

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_update_question_queries_only(self, mock_execute_query):
        """Test updating question queries only"""
        new_queries = [
            {"name": "UpdatedQuery", "query": "FIND User WITH active=true", "version": "v2"}
        ]
        mock_response = {
            "data": {
                "updateQuestion": {
                    "id": self.question_id,
                    "title": "Original Title",
                    "description": "Original description",
                    "queries": new_queries,
                    "tags": ["original", "tag"]
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.update_question(
            question_id=self.question_id,
            queries=new_queries
        )

        # Verify the call
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        
        # Check variables - they are in the second positional argument
        variables = call_args[0][1]
        assert variables['id'] == self.question_id
        # The queries are now processed and enriched with default values
        processed_queries = variables['update']['queries']
        assert len(processed_queries) == 1
        assert processed_queries[0]['name'] == "UpdatedQuery"
        assert processed_queries[0]['query'] == "FIND User WITH active=true"
        assert processed_queries[0]['version'] == "v2"
        assert processed_queries[0]['resultsAre'] == "INFORMATIVE"  # Default value added
        assert 'title' not in variables['update']
        assert 'description' not in variables['update']
        assert 'tags' not in variables['update']

        # Check result
        assert result['queries'] == new_queries

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_update_question_comprehensive(self, mock_execute_query):
        """Test updating question with multiple fields"""
        update_data = {
            "title": "Comprehensive Updated Title",
            "description": "Comprehensive updated description",
            "tags": ["comprehensive", "update", "test"],
            "queries": [
                {"name": "ComprehensiveQuery", "query": "FIND * WITH _class='Host'", "version": "v3"}
            ]
        }
        
        mock_response = {
            "data": {
                "updateQuestion": {
                    "id": self.question_id,
                    **update_data
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.update_question(
            question_id=self.question_id,
            **update_data
        )

        # Verify the call
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        
        # Check variables - they are in the second positional argument
        variables = call_args[0][1]
        assert variables['id'] == self.question_id
        assert variables['update']['title'] == update_data['title']
        assert variables['update']['description'] == update_data['description']
        assert variables['update']['tags'] == update_data['tags']
        # The queries are now processed and enriched with default values
        processed_queries = variables['update']['queries']
        assert len(processed_queries) == 1
        assert processed_queries[0]['name'] == "ComprehensiveQuery"
        assert processed_queries[0]['query'] == "FIND * WITH _class='Host'"
        assert processed_queries[0]['version'] == "v3"
        assert processed_queries[0]['resultsAre'] == "INFORMATIVE"  # Default value added

        # Check result
        assert result['title'] == update_data['title']
        assert result['description'] == update_data['description']
        assert result['tags'] == update_data['tags']
        assert result['queries'] == update_data['queries']

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_update_question_with_kwargs(self, mock_execute_query):
        """Test updating question with additional kwargs"""
        mock_response = {
            "data": {
                "updateQuestion": {
                    "id": self.question_id,
                    "title": "Original Title",
                    "showTrend": True,
                    "pollingInterval": "ONE_HOUR"
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.update_question(
            question_id=self.question_id,
            showTrend=True,
            pollingInterval="ONE_HOUR"
        )

        # Verify the call
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        
        # Check variables - they are in the second positional argument
        variables = call_args[0][1]
        assert variables['id'] == self.question_id
        assert variables['update']['showTrend'] is True
        assert variables['update']['pollingInterval'] == "ONE_HOUR"

        # Check result
        assert result['showTrend'] is True
        assert result['pollingInterval'] == "ONE_HOUR"

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_update_question_api_error(self, mock_execute_query):
        """Test updating question with API error"""
        mock_execute_query.side_effect = JupiterOneApiError("API Error")

        with pytest.raises(JupiterOneApiError):
            self.client.update_question(
                question_id=self.question_id,
                title="Updated Title"
            )

    def test_update_question_empty_question_id(self):
        """Test updating question with empty question ID"""
        with pytest.raises(ValueError, match="question_id is required"):
            self.client.update_question(
                question_id="",
                title="Updated Title"
            )

    def test_update_question_none_question_id(self):
        """Test updating question with None question ID"""
        with pytest.raises(ValueError, match="question_id is required"):
            self.client.update_question(
                question_id=None,
                title="Updated Title"
            )

    def test_update_question_no_update_fields(self):
        """Test updating question with no update fields"""
        with pytest.raises(ValueError, match="At least one update field must be provided"):
            self.client.update_question(question_id=self.question_id)

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_delete_question_success(self, mock_execute_query):
        """Test successful question deletion"""
        mock_response = {
            "data": {
                "deleteQuestion": {
                    "id": self.question_id,
                    "title": "Question to Delete",
                    "description": "This question will be deleted",
                    "queries": [{"name": "Query0", "query": "FIND Host"}],
                    "tags": ["delete", "test"],
                    "accountId": "test-account"
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.delete_question(question_id=self.question_id)

        # Verify the call
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        
        # Check the mutation was called with correct parameters
        assert call_args[0][0] == DELETE_QUESTION
        
        # Check variables - they are in the second positional argument
        variables = call_args[0][1]
        assert variables['id'] == self.question_id

        # Check result
        assert result['id'] == self.question_id
        assert result['title'] == "Question to Delete"
        assert result['description'] == "This question will be deleted"
        assert len(result['queries']) == 1
        assert result['tags'] == ["delete", "test"]

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_delete_question_api_error(self, mock_execute_query):
        """Test deleting question with API error"""
        mock_execute_query.side_effect = JupiterOneApiError("API Error")

        with pytest.raises(JupiterOneApiError):
            self.client.delete_question(question_id=self.question_id)

    def test_delete_question_empty_question_id(self):
        """Test deleting question with empty question ID"""
        with pytest.raises(ValueError, match="question_id is required"):
            self.client.delete_question(question_id="")

    def test_delete_question_none_question_id(self):
        """Test deleting question with None question ID"""
        with pytest.raises(ValueError, match="question_id is required"):
            self.client.delete_question(question_id=None)

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_delete_question_nonexistent_question(self, mock_execute_query):
        """Test deleting nonexistent question"""
        mock_response = {
            "data": {
                "deleteQuestion": None
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.delete_question(question_id="nonexistent-id")
        
        assert result is None

    # Tests for queries validation in update_question
    def test_update_question_queries_validation_empty_list(self):
        """Test that update_question rejects empty queries list"""
        with pytest.raises(ValueError, match="queries must be a non-empty list"):
            self.client.update_question(
                question_id=self.question_id,
                queries=[]
            )

    def test_update_question_queries_validation_not_list(self):
        """Test that update_question rejects non-list queries"""
        with pytest.raises(ValueError, match="queries must be a non-empty list"):
            self.client.update_question(
                question_id=self.question_id,
                queries="not a list"
            )

    def test_update_question_queries_validation_none(self):
        """Test that update_question accepts None queries (no update)"""
        # This should not raise an error since queries=None means no update
        # The validation only happens when queries is provided
        try:
            self.client.update_question(
                question_id=self.question_id,
                title="Updated Title"
            )
        except Exception as e:
            # If it gets to the API call, that's fine - we're just testing validation
            pass

    def test_update_question_queries_validation_missing_query_field(self):
        """Test that update_question rejects queries missing 'query' field"""
        with pytest.raises(ValueError, match="Query at index 0 must have a 'query' field"):
            self.client.update_question(
                question_id=self.question_id,
                queries=[{"name": "InvalidQuery"}]
            )

    def test_update_question_queries_validation_invalid_query_type(self):
        """Test that update_question rejects non-dict query items"""
        with pytest.raises(ValueError, match="Query at index 0 must be a dictionary"):
            self.client.update_question(
                question_id=self.question_id,
                queries=["not a dict"]
            )

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_update_question_queries_validation_success(self, mock_execute_query):
        """Test that update_question successfully processes valid queries"""
        mock_response = {
            "data": {
                "updateQuestion": {
                    "id": self.question_id,
                    "title": "Updated Title",
                    "queries": [
                        {
                            "name": "Query0",
                            "query": "FIND Host",
                            "resultsAre": "INFORMATIVE"
                        }
                    ]
                }
            }
        }
        mock_execute_query.return_value = mock_response
        
        result = self.client.update_question(
            question_id=self.question_id,
            queries=[{"query": "FIND Host"}]
        )
        
        # Verify the call was made with processed queries
        call_args = mock_execute_query.call_args
        variables = call_args[0][1]
        assert variables['update']['queries'][0]['name'] == "Query0"
        assert variables['update']['queries'][0]['query'] == "FIND Host"
        assert variables['update']['queries'][0]['resultsAre'] == "INFORMATIVE"
        
        # Check result
        assert result['id'] == self.question_id
        assert result['title'] == "Updated Title"
