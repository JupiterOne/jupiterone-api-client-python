"""Test create_question method"""

import pytest
from unittest.mock import patch
from jupiterone.client import JupiterOneClient
from jupiterone.constants import CREATE_QUESTION


class TestCreateQuestion:
    """Test create_question method"""

    def setup_method(self):
        """Set up test fixtures"""
        self.client = JupiterOneClient(account="test-account", token="test-token")

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_create_question_basic(self, mock_execute):
        """Test basic question creation with minimal parameters"""
        # Mock response
        mock_execute.return_value = {
            "data": {
                "createQuestion": {
                    "id": "question-123",
                    "title": "Test Question",
                    "description": "Test description",
                    "queries": [{
                        "name": "Query0",
                        "query": "FIND Host",
                        "resultsAre": "INFORMATIVE"
                    }],
                    "tags": [],
                    "accountId": "test-account"
                }
            }
        }

        # Create question
        result = self.client.create_question(
            title="Test Question",
            queries=[{"query": "FIND Host"}]
        )

        # Verify call
        mock_execute.assert_called_once()
        call_args = mock_execute.call_args

        # Check the mutation was called with correct parameters
        assert call_args[0][0] == CREATE_QUESTION

        # Check variables
        variables = call_args[1]['variables']
        assert variables['question']['title'] == "Test Question"
        assert len(variables['question']['queries']) == 1
        assert variables['question']['queries'][0]['query'] == "FIND Host"
        assert variables['question']['queries'][0]['name'] == "Query0"
        assert variables['question']['queries'][0]['resultsAre'] == "INFORMATIVE"

        # Check result
        assert result['id'] == "question-123"
        assert result['title'] == "Test Question"

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_create_question_with_all_options(self, mock_execute):
        """Test question creation with all optional parameters"""
        # Mock response
        mock_execute.return_value = {
            "data": {
                "createQuestion": {
                    "id": "question-456",
                    "title": "Complex Question",
                    "description": "Complex description",
                    "queries": [{
                        "name": "NoMFAUsers",
                        "query": "FIND User WITH mfaEnabled=false",
                        "version": "v1",
                        "resultsAre": "BAD"
                    }],
                    "tags": ["security", "test"],
                    "showTrend": True,
                    "pollingInterval": "ONE_HOUR"
                }
            }
        }

        # Create question with all options
        result = self.client.create_question(
            title="Complex Question",
            queries=[{
                "query": "FIND User WITH mfaEnabled=false",
                "name": "NoMFAUsers",
                "version": "v1",
                "resultsAre": "BAD"
            }],
            description="Complex description",
            tags=["security", "test"],
            showTrend=True,
            pollingInterval="ONE_HOUR"
        )

        # Check variables
        variables = mock_execute.call_args[1]['variables']
        question_input = variables['question']

        assert question_input['title'] == "Complex Question"
        assert question_input['description'] == "Complex description"
        assert question_input['tags'] == ["security", "test"]
        assert question_input['showTrend'] == True
        assert question_input['pollingInterval'] == "ONE_HOUR"

        # Check result
        assert result['id'] == "question-456"
        assert result['showTrend'] == True

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_create_question_with_compliance(self, mock_execute):
        """Test question creation with compliance metadata"""
        # Mock response
        mock_execute.return_value = {
            "data": {
                "createQuestion": {
                    "id": "question-789",
                    "title": "Compliance Question",
                    "compliance": {
                        "standard": "CIS",
                        "requirements": ["2.1", "2.2"],
                        "controls": ["Network Security"]
                    }
                }
            }
        }

        # Create question with compliance
        result = self.client.create_question(
            title="Compliance Question",
            queries=[{
                "query": "FIND Host WITH open=true",
                "name": "OpenHosts",
                "resultsAre": "BAD"
            }],
            compliance={
                "standard": "CIS",
                "requirements": ["2.1", "2.2"],
                "controls": ["Network Security"]
            }
        )

        # Check variables
        variables = mock_execute.call_args[1]['variables']
        question_input = variables['question']

        assert question_input['compliance']['standard'] == "CIS"
        assert question_input['compliance']['requirements'] == ["2.1", "2.2"]
        assert question_input['compliance']['controls'] == ["Network Security"]

        # Check result
        assert result['compliance']['standard'] == "CIS"

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_create_question_with_variables(self, mock_execute):
        """Test question creation with variables"""
        # Mock response
        mock_execute.return_value = {
            "data": {
                "createQuestion": {
                    "id": "question-101",
                    "title": "Variable Question",
                    "variables": [
                        {
                            "name": "environment",
                            "required": True,
                            "default": "production"
                        }
                    ]
                }
            }
        }

        # Create question with variables
        result = self.client.create_question(
            title="Variable Question",
            queries=[{
                "query": "FIND * WITH tag.Environment={{environment}}",
                "name": "EnvResources"
            }],
            variables=[
                {
                    "name": "environment",
                    "required": True,
                    "default": "production"
                }
            ]
        )

        # Check variables
        variables = mock_execute.call_args[1]['variables']
        question_input = variables['question']

        assert len(question_input['variables']) == 1
        assert question_input['variables'][0]['name'] == "environment"
        assert question_input['variables'][0]['required'] == True
        assert question_input['variables'][0]['default'] == "production"

        # Check result
        assert len(result['variables']) == 1

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_create_question_multiple_queries(self, mock_execute):
        """Test question creation with multiple queries"""
        # Mock response
        mock_execute.return_value = {
            "data": {
                "createQuestion": {
                    "id": "question-multi",
                    "title": "Multi Query Question",
                    "queries": [
                        {
                            "name": "Query1",
                            "query": "FIND Host WITH open=true",
                            "resultsAre": "BAD"
                        },
                        {
                            "name": "Query2",
                            "query": "FIND User WITH mfaEnabled=false",
                            "resultsAre": "BAD"
                        }
                    ]
                }
            }
        }

        # Create question with multiple queries
        result = self.client.create_question(
            title="Multi Query Question",
            queries=[
                {
                    "query": "FIND Host WITH open=true",
                    "name": "Query1",
                    "resultsAre": "BAD"
                },
                {
                    "query": "FIND User WITH mfaEnabled=false",
                    "name": "Query2",
                    "resultsAre": "BAD"
                }
            ]
        )

        # Check variables
        variables = mock_execute.call_args[1]['variables']
        question_input = variables['question']

        assert len(question_input['queries']) == 2
        assert question_input['queries'][0]['name'] == "Query1"
        assert question_input['queries'][1]['name'] == "Query2"

        # Check result
        assert len(result['queries']) == 2

    def test_create_question_validation_title_required(self):
        """Test validation that title is required"""
        with pytest.raises(ValueError, match="title is required"):
            self.client.create_question(title="", queries=[{"query": "FIND Host"}])

        with pytest.raises(ValueError, match="title is required"):
            self.client.create_question(title=None, queries=[{"query": "FIND Host"}])

    def test_create_question_validation_queries_required(self):
        """Test validation that queries are required"""
        with pytest.raises(ValueError, match="queries must be a non-empty list"):
            self.client.create_question(title="Test", queries=[])

        with pytest.raises(ValueError, match="queries must be a non-empty list"):
            self.client.create_question(title="Test", queries=None)

    def test_create_question_validation_query_format(self):
        """Test validation of query format"""
        with pytest.raises(ValueError, match="must be a dictionary"):
            self.client.create_question(title="Test", queries=["invalid"])

        with pytest.raises(ValueError, match="must be a dictionary"):
            self.client.create_question(title="Test", queries=[123])

    def test_create_question_validation_query_field_required(self):
        """Test validation that query field is required in each query"""
        with pytest.raises(ValueError, match="must have a 'query' field"):
            self.client.create_question(title="Test", queries=[{"name": "Test"}])

        with pytest.raises(ValueError, match="must have a 'query' field"):
            self.client.create_question(title="Test", queries=[{"version": "v1"}])

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_create_question_auto_naming(self, mock_execute):
        """Test automatic query naming when not provided"""
        # Mock response
        mock_execute.return_value = {
            "data": {
                "createQuestion": {
                    "id": "question-auto",
                    "title": "Auto Naming Test",
                    "queries": [
                        {"name": "Query0", "query": "FIND Host"},
                        {"name": "Query1", "query": "FIND User"}
                    ]
                }
            }
        }

        # Create question without query names
        self.client.create_question(
            title="Auto Naming Test",
            queries=[
                {"query": "FIND Host"},
                {"query": "FIND User"}
            ]
        )

        # Check variables
        variables = mock_execute.call_args[1]['variables']
        question_input = variables['question']

        assert question_input['queries'][0]['name'] == "Query0"
        assert question_input['queries'][1]['name'] == "Query1"

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_create_question_results_are_default(self, mock_execute):
        """Test that resultsAre defaults to INFORMATIVE when not provided"""
        # Mock response
        mock_execute.return_value = {
            "data": {
                "createQuestion": {
                    "id": "question-default",
                    "title": "Default Results Test",
                    "queries": [{"name": "Query0", "query": "FIND Host"}]
                }
            }
        }

        # Create question without resultsAre
        self.client.create_question(
            title="Default Results Test",
            queries=[{"query": "FIND Host"}]
        )

        # Check variables
        variables = mock_execute.call_args[1]['variables']
        question_input = variables['question']

        assert question_input['queries'][0]['resultsAre'] == "INFORMATIVE"

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_create_question_version_optional(self, mock_execute):
        """Test that version is only included when provided"""
        # Mock response
        mock_execute.return_value = {
            "data": {
                "createQuestion": {
                    "id": "question-version",
                    "title": "Version Test",
                    "queries": [{"name": "Query0", "query": "FIND Host"}]
                }
            }
        }

        # Create question without version
        self.client.create_question(
            title="Version Test",
            queries=[{"query": "FIND Host"}]
        )

        # Check variables
        variables = mock_execute.call_args[1]['variables']
        question_input = variables['question']

        # Version should not be in the query if not provided
        assert 'version' not in question_input['queries'][0]

        # Create question with version
        mock_execute.return_value = {
            "data": {
                "createQuestion": {
                    "id": "question-version2",
                    "title": "Version Test 2",
                    "queries": [{"name": "Query0", "query": "FIND Host", "version": "v1"}]
                }
            }
        }

        self.client.create_question(
            title="Version Test 2",
            queries=[{"query": "FIND Host", "version": "v1"}]
        )

        # Check variables
        variables = mock_execute.call_args[1]['variables']
        question_input = variables['question']

        # Version should be included when provided
        assert question_input['queries'][0]['version'] == "v1"

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_create_question_optional_fields_handling(self, mock_execute):
        """Test that optional fields are only included when provided and not None"""
        # Mock response
        mock_execute.return_value = {
            "data": {
                "createQuestion": {
                    "id": "question-optional",
                    "title": "Optional Fields Test"
                }
            }
        }

        # Create question with some None values
        self.client.create_question(
            title="Optional Fields Test",
            queries=[{"query": "FIND Host"}],
            description=None,  # Should not be included
            tags=None,  # Should not be included
            showTrend=False,  # Should be included
            pollingInterval="ONE_DAY"  # Should be included
        )

        # Check variables
        variables = mock_execute.call_args[1]['variables']
        question_input = variables['question']

        # None values should not be included
        assert 'description' not in question_input
        assert 'tags' not in question_input

        # Non-None values should be included
        assert question_input['showTrend'] == False
        assert question_input['pollingInterval'] == "ONE_DAY"

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_create_question_integration_definition_id(self, mock_execute):
        """Test question creation with integration definition ID"""
        # Mock response
        mock_execute.return_value = {
            "data": {
                "createQuestion": {
                    "id": "question-integration",
                    "title": "Integration Question",
                    "integrationDefinitionId": "integration-123"
                }
            }
        }

        # Create question with integration definition ID
        result = self.client.create_question(
            title="Integration Question",
            queries=[{"query": "FIND aws_instance"}],
            integrationDefinitionId="integration-123"
        )

        # Check variables
        variables = mock_execute.call_args[1]['variables']
        question_input = variables['question']

        assert question_input['integrationDefinitionId'] == "integration-123"

        # Check result
        assert result['integrationDefinitionId'] == "integration-123"
