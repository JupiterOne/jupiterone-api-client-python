"""Test client initialization and error handling"""

import pytest
from unittest.mock import Mock, patch
from jupiterone.client import JupiterOneClient
from jupiterone.errors import JupiterOneClientError, JupiterOneApiError, JupiterOneApiRetryError


class TestClientInit:
    """Test client initialization"""

    def test_client_init_success(self):
        """Test successful client initialization"""
        client = JupiterOneClient(account="test-account", token="test-token")
        
        assert client.account == "test-account"
        assert client.token == "test-token"
        assert client.graphql_url == "https://graphql.us.jupiterone.io"
        assert client.sync_url == "https://api.us.jupiterone.io"
        assert "Authorization" in client.headers
        assert "JupiterOne-Account" in client.headers
        assert "Content-Type" in client.headers

    def test_client_init_with_custom_urls(self):
        """Test client initialization with custom URLs"""
        client = JupiterOneClient(
            account="test-account",
            token="test-token",
            url="https://custom-graphql.example.com",
            sync_url="https://custom-api.example.com"
        )
        
        assert client.graphql_url == "https://custom-graphql.example.com"
        assert client.sync_url == "https://custom-api.example.com"

    def test_client_init_missing_account(self):
        """Test client initialization with missing account"""
        with pytest.raises(JupiterOneClientError, match="account is required"):
            JupiterOneClient(token="test-token")

    def test_client_init_missing_token(self):
        """Test client initialization with missing token"""
        with pytest.raises(JupiterOneClientError, match="token is required"):
            JupiterOneClient(account="test-account")

    def test_client_init_empty_account(self):
        """Test client initialization with empty account"""
        with pytest.raises(JupiterOneClientError, match="account is required"):
            JupiterOneClient(account="", token="test-token")

    def test_client_init_empty_token(self):
        """Test client initialization with empty token"""
        with pytest.raises(JupiterOneClientError, match="token is required"):
            JupiterOneClient(account="test-account", token="")

    def test_client_init_none_account(self):
        """Test client initialization with None account"""
        with pytest.raises(JupiterOneClientError, match="account is required"):
            JupiterOneClient(account=None, token="test-token")

    def test_client_init_none_token(self):
        """Test client initialization with None token"""
        with pytest.raises(JupiterOneClientError, match="token is required"):
            JupiterOneClient(account="test-account", token=None)

    def test_account_property_setter(self):
        """Test account property setter"""
        client = JupiterOneClient(account="test-account", token="test-token")
        
        # Test setting valid account
        client.account = "new-account"
        assert client.account == "new-account"
        
        # Test setting invalid account
        with pytest.raises(JupiterOneClientError, match="account is required"):
            client.account = ""
        
        with pytest.raises(JupiterOneClientError, match="account is required"):
            client.account = None

    def test_token_property_setter(self):
        """Test token property setter"""
        client = JupiterOneClient(account="test-account", token="test-token")
        
        # Test setting valid token
        client.token = "new-token"
        assert client.token == "new-token"
        
        # Test setting invalid token
        with pytest.raises(JupiterOneClientError, match="token is required"):
            client.token = ""
        
        with pytest.raises(JupiterOneClientError, match="token is required"):
            client.token = None

    def test_headers_updated_after_token_change(self):
        """Test that headers are updated when token changes"""
        client = JupiterOneClient(account="test-account", token="test-token")
        
        # Note: The current implementation doesn't update headers when token/account changes
        # This test documents the current behavior
        original_auth = client.headers["Authorization"]
        client.token = "new-token"
        
        # Headers are not automatically updated in the current implementation
        assert client.headers["Authorization"] == original_auth
        assert client.headers["Authorization"] == "Bearer test-token"

    def test_headers_updated_after_account_change(self):
        """Test that headers are updated when account changes"""
        client = JupiterOneClient(account="test-account", token="test-token")
        
        # Note: The current implementation doesn't update headers when token/account changes
        # This test documents the current behavior
        original_account = client.headers["JupiterOne-Account"]
        client.account = "new-account"
        
        # Headers are not automatically updated in the current implementation
        assert client.headers["JupiterOne-Account"] == original_account
        assert client.headers["JupiterOne-Account"] == "test-account"


class TestErrorHandling:
    """Test error handling in the client"""

    def setup_method(self):
        """Set up test fixtures"""
        self.client = JupiterOneClient(account="test-account", token="test-token")

    @patch.object(JupiterOneClient, 'session')
    def test_execute_query_401_error(self, mock_session):
        """Test _execute_query method with 401 error"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_session.post.return_value = mock_response

        with pytest.raises(JupiterOneApiError, match="401: Unauthorized"):
            self.client._execute_query("test query")

    @patch.object(JupiterOneClient, 'session')
    def test_execute_query_429_error(self, mock_session):
        """Test _execute_query method with 429 error"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_session.post.return_value = mock_response

        with pytest.raises(JupiterOneApiRetryError, match="rate limit exceeded"):
            self.client._execute_query("test query")

    @patch.object(JupiterOneClient, 'session')
    def test_execute_query_503_error(self, mock_session):
        """Test _execute_query method with 503 error"""
        mock_response = Mock()
        mock_response.status_code = 503
        mock_session.post.return_value = mock_response

        with pytest.raises(JupiterOneApiRetryError, match="rate limit exceeded"):
            self.client._execute_query("test query")

    @patch.object(JupiterOneClient, 'session')
    def test_execute_query_504_error(self, mock_session):
        """Test _execute_query method with 504 error"""
        mock_response = Mock()
        mock_response.status_code = 504
        mock_session.post.return_value = mock_response

        with pytest.raises(JupiterOneApiRetryError, match="Gateway Timeout"):
            self.client._execute_query("test query")

    @patch.object(JupiterOneClient, 'session')
    def test_execute_query_500_error(self, mock_session):
        """Test _execute_query method with 500 error"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_session.post.return_value = mock_response

        with pytest.raises(JupiterOneApiError, match="internal server error"):
            self.client._execute_query("test query")

    @patch.object(JupiterOneClient, 'session')
    def test_execute_query_200_with_errors(self, mock_session):
        """Test _execute_query method with 200 status but GraphQL errors"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "errors": [{"message": "GraphQL error"}]
        }
        mock_session.post.return_value = mock_response

        with pytest.raises(JupiterOneApiError):
            self.client._execute_query("test query")

    @patch.object(JupiterOneClient, 'session')
    def test_execute_query_200_with_429_in_errors(self, mock_session):
        """Test _execute_query method with 200 status but 429 in GraphQL errors"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "errors": [{"message": "429 rate limit exceeded"}]
        }
        mock_session.post.return_value = mock_response

        with pytest.raises(JupiterOneApiRetryError, match="rate limit exceeded"):
            self.client._execute_query("test query")

    @patch.object(JupiterOneClient, 'session')
    def test_execute_query_200_success(self, mock_session):
        """Test _execute_query method with successful 200 response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {"result": "success"}
        }
        mock_session.post.return_value = mock_response

        result = self.client._execute_query("test query")
        
        assert result == {"data": {"result": "success"}}

    @patch.object(JupiterOneClient, 'session')
    def test_execute_query_with_variables(self, mock_session):
        """Test _execute_query method with variables"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {"result": "success"}
        }
        mock_session.post.return_value = mock_response

        variables = {"key": "value"}
        self.client._execute_query("test query", variables=variables)
        
        # Verify that variables were included in the request
        call_args = mock_session.post.call_args
        assert "variables" in call_args[1]["json"]
        assert call_args[1]["json"]["variables"] == variables

    @patch.object(JupiterOneClient, 'session')
    def test_execute_query_with_flags(self, mock_session):
        """Test _execute_query method includes flags"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {"result": "success"}
        }
        mock_session.post.return_value = mock_response

        self.client._execute_query("test query")
        
        # Verify that flags were included in the request
        call_args = mock_session.post.call_args
        assert "flags" in call_args[1]["json"]
        assert call_args[1]["json"]["flags"] == {"variableResultSize": True} 