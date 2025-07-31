"""Test _execute_syncapi_request method"""

import json
import pytest
from unittest.mock import Mock, patch

from jupiterone.client import JupiterOneClient
from jupiterone.errors import JupiterOneApiError, JupiterOneApiRetryError


class TestExecuteSyncApiRequest:
    """Test _execute_syncapi_request method"""

    def setup_method(self):
        """Set up test fixtures"""
        self.client = JupiterOneClient(account="test-account", token="test-token")

    @patch.object(JupiterOneClient, 'session')
    def test_execute_syncapi_request_success(self, mock_session):
        """Test successful sync API request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response._content = json.dumps({
            "data": {
                "result": "success",
                "items": [{"id": "1"}, {"id": "2"}]
            }
        }).encode('utf-8')
        mock_response.json.return_value = {
            "data": {
                "result": "success",
                "items": [{"id": "1"}, {"id": "2"}]
            }
        }

        mock_session.post.return_value = mock_response

        result = self.client._execute_syncapi_request(
            endpoint="/test/endpoint",
            payload={"key": "value"}
        )

        # Verify the request was made correctly
        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args
        assert call_args[0][0] == f"{self.client.sync_url}/test/endpoint"
        assert call_args[1]['headers'] == self.client.headers
        assert call_args[1]['json'] == {"key": "value"}
        assert call_args[1]['timeout'] == 60

        # Verify the result
        assert result == {
            "data": {
                "result": "success",
                "items": [{"id": "1"}, {"id": "2"}]
            }
        }

    @patch.object(JupiterOneClient, 'session')
    def test_execute_syncapi_request_without_payload(self, mock_session):
        """Test sync API request without payload"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response._content = json.dumps({"data": "success"}).encode('utf-8')
        mock_response.json.return_value = {"data": "success"}

        mock_session.post.return_value = mock_response

        result = self.client._execute_syncapi_request(endpoint="/test/endpoint")

        # Verify the request was made correctly
        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args
        assert call_args[0][0] == f"{self.client.sync_url}/test/endpoint"
        assert call_args[1]['json'] is None

        # Verify the result
        assert result == {"data": "success"}

    @patch.object(JupiterOneClient, 'session')
    def test_execute_syncapi_request_empty_response(self, mock_session):
        """Test sync API request with empty response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response._content = b''
        mock_response.json.return_value = {}

        mock_session.post.return_value = mock_response

        result = self.client._execute_syncapi_request(endpoint="/test/endpoint")

        # Verify the result
        assert result == {}

    @patch.object(JupiterOneClient, 'session')
    def test_execute_syncapi_request_401_error(self, mock_session):
        """Test sync API request with 401 unauthorized error"""
        mock_response = Mock()
        mock_response.status_code = 401

        mock_session.post.return_value = mock_response

        with pytest.raises(JupiterOneApiError, match="401: Unauthorized"):
            self.client._execute_syncapi_request(endpoint="/test/endpoint")

    @patch.object(JupiterOneClient, 'session')
    def test_execute_syncapi_request_429_error(self, mock_session):
        """Test sync API request with 429 rate limit error"""
        mock_response = Mock()
        mock_response.status_code = 429

        mock_session.post.return_value = mock_response

        with pytest.raises(JupiterOneApiRetryError, match="JupiterOne API rate limit exceeded"):
            self.client._execute_syncapi_request(endpoint="/test/endpoint")

    @patch.object(JupiterOneClient, 'session')
    def test_execute_syncapi_request_503_error(self, mock_session):
        """Test sync API request with 503 service unavailable error"""
        mock_response = Mock()
        mock_response.status_code = 503

        mock_session.post.return_value = mock_response

        with pytest.raises(JupiterOneApiRetryError, match="JupiterOne API rate limit exceeded"):
            self.client._execute_syncapi_request(endpoint="/test/endpoint")

    @patch.object(JupiterOneClient, 'session')
    def test_execute_syncapi_request_504_error(self, mock_session):
        """Test sync API request with 504 gateway timeout error"""
        mock_response = Mock()
        mock_response.status_code = 504

        mock_session.post.return_value = mock_response

        with pytest.raises(JupiterOneApiRetryError, match="Gateway Timeout"):
            self.client._execute_syncapi_request(endpoint="/test/endpoint")

    @patch.object(JupiterOneClient, 'session')
    def test_execute_syncapi_request_500_error(self, mock_session):
        """Test sync API request with 500 internal server error"""
        mock_response = Mock()
        mock_response.status_code = 500

        mock_session.post.return_value = mock_response

        with pytest.raises(JupiterOneApiError, match="JupiterOne API internal server error"):
            self.client._execute_syncapi_request(endpoint="/test/endpoint")

    @patch.object(JupiterOneClient, 'session')
    def test_execute_syncapi_request_200_with_errors(self, mock_session):
        """Test sync API request with 200 status but GraphQL errors"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response._content = json.dumps({
            "errors": [
                {"message": "GraphQL error occurred"},
                {"message": "Another error"}
            ]
        }).encode('utf-8')
        mock_response.json.return_value = {
            "errors": [
                {"message": "GraphQL error occurred"},
                {"message": "Another error"}
            ]
        }

        mock_session.post.return_value = mock_response

        with pytest.raises(JupiterOneApiError) as exc_info:
            self.client._execute_syncapi_request(endpoint="/test/endpoint")

        # Verify the error contains the GraphQL errors
        assert "GraphQL error occurred" in str(exc_info.value)
        assert "Another error" in str(exc_info.value)

    @patch.object(JupiterOneClient, 'session')
    def test_execute_syncapi_request_200_with_429_in_errors(self, mock_session):
        """Test sync API request with 200 status but 429 in GraphQL errors"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response._content = json.dumps({
            "errors": [
                {"message": "429: Rate limit exceeded"}
            ]
        }).encode('utf-8')
        mock_response.json.return_value = {
            "errors": [
                {"message": "429: Rate limit exceeded"}
            ]
        }

        mock_session.post.return_value = mock_response

        with pytest.raises(JupiterOneApiRetryError, match="JupiterOne API rate limit exceeded"):
            self.client._execute_syncapi_request(endpoint="/test/endpoint")

    @patch.object(JupiterOneClient, 'session')
    def test_execute_syncapi_request_unknown_status_code(self, mock_session):
        """Test sync API request with unknown status code"""
        mock_response = Mock()
        mock_response.status_code = 418  # I'm a teapot
        mock_response._content = b'{"error": "I\'m a teapot"}'
        mock_response.headers = {"Content-Type": "application/json"}

        mock_session.post.return_value = mock_response

        with pytest.raises(JupiterOneApiError, match="418:I'm a teapot"):
            self.client._execute_syncapi_request(endpoint="/test/endpoint")

    @patch.object(JupiterOneClient, 'session')
    def test_execute_syncapi_request_unknown_status_code_json_error(self, mock_session):
        """Test sync API request with unknown status code and JSON error"""
        mock_response = Mock()
        mock_response.status_code = 418
        mock_response._content = b'{"error": "I\'m a teapot"}'
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

        mock_session.post.return_value = mock_response

        with pytest.raises(JupiterOneApiError, match="418:{\"error\": \"I'm a teapot\"}"):
            self.client._execute_syncapi_request(endpoint="/test/endpoint")

    @patch.object(JupiterOneClient, 'session')
    def test_execute_syncapi_request_unknown_status_code_plain_text(self, mock_session):
        """Test sync API request with unknown status code and plain text response"""
        mock_response = Mock()
        mock_response.status_code = 418
        mock_response._content = b'I am a teapot'
        mock_response.headers = {"Content-Type": "text/plain"}

        mock_session.post.return_value = mock_response

        with pytest.raises(JupiterOneApiError, match="418:I am a teapot"):
            self.client._execute_syncapi_request(endpoint="/test/endpoint")

    @patch.object(JupiterOneClient, 'session')
    def test_execute_syncapi_request_complex_payload(self, mock_session):
        """Test sync API request with complex payload"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response._content = json.dumps({"data": "success"}).encode('utf-8')
        mock_response.json.return_value = {"data": "success"}

        mock_session.post.return_value = mock_response

        complex_payload = {
            "entities": [
                {"_id": "1", "_type": "aws_instance", "name": "instance-1"},
                {"_id": "2", "_type": "aws_instance", "name": "instance-2"}
            ],
            "relationships": [
                {"_id": "rel-1", "_type": "aws_instance_uses_aws_vpc"}
            ],
            "metadata": {
                "source": "test",
                "timestamp": 1234567890
            }
        }

        result = self.client._execute_syncapi_request(
            endpoint="/persister/synchronization/jobs/123/upload",
            payload=complex_payload
        )

        # Verify the request was made correctly
        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args
        assert call_args[1]['json'] == complex_payload

        # Verify the result
        assert result == {"data": "success"}

    @patch.object(JupiterOneClient, 'session')
    def test_execute_syncapi_request_with_headers(self, mock_session):
        """Test sync API request verifies correct headers are sent"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response._content = json.dumps({"data": "success"}).encode('utf-8')
        mock_response.json.return_value = {"data": "success"}

        mock_session.post.return_value = mock_response

        self.client._execute_syncapi_request(endpoint="/test/endpoint")

        # Verify the headers were sent correctly
        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args
        headers = call_args[1]['headers']
        
        assert headers["Authorization"] == "Bearer test-token"
        assert headers["JupiterOne-Account"] == "test-account"
        assert headers["Content-Type"] == "application/json"

    @patch.object(JupiterOneClient, 'session')
    def test_execute_syncapi_request_custom_sync_url(self, mock_session):
        """Test sync API request with custom sync URL"""
        # Create client with custom sync URL
        client = JupiterOneClient(
            account="test-account",
            token="test-token",
            sync_url="https://custom-api.example.com"
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response._content = json.dumps({"data": "success"}).encode('utf-8')
        mock_response.json.return_value = {"data": "success"}

        mock_session.post.return_value = mock_response

        client._execute_syncapi_request(endpoint="/test/endpoint")

        # Verify the custom sync URL was used
        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args
        assert call_args[0][0] == "https://custom-api.example.com/test/endpoint" 