"""Test Custom File Transfer (CFT) methods"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, mock_open
from jupiterone.client import JupiterOneClient
from jupiterone.errors import JupiterOneApiError
from jupiterone.constants import INVOKE_INTEGRATION_INSTANCE


class TestCFTMethods:
    """Test Custom File Transfer (CFT) methods"""

    def setup_method(self):
        """Set up test fixtures"""
        self.client = JupiterOneClient(account="test-account", token="test-token")
        self.integration_instance_id = "test-integration-instance-123"
        self.dataset_id = "test-dataset-456"
        self.filename = "test_data.csv"

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_get_cft_upload_url_success(self, mock_execute_query):
        """Test successful CFT upload URL retrieval"""
        mock_response = {
            "data": {
                "integrationFileTransferUploadUrl": {
                    "uploadUrl": "https://s3.amazonaws.com/test-bucket/test-file.csv",
                    "expiresAt": "2024-01-01T12:00:00Z"
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.get_cft_upload_url(
            integration_instance_id=self.integration_instance_id,
            filename=self.filename,
            dataset_id=self.dataset_id
        )

        assert result == mock_response["data"]["integrationFileTransferUploadUrl"]
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_get_cft_upload_url_error(self, mock_execute_query):
        """Test CFT upload URL retrieval with error"""
        mock_execute_query.side_effect = JupiterOneApiError("API Error")

        with pytest.raises(JupiterOneApiError):
            self.client.get_cft_upload_url(
                integration_instance_id=self.integration_instance_id,
                filename=self.filename,
                dataset_id=self.dataset_id
            )

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_get_cft_upload_url_missing_data(self, mock_execute_query):
        """Test CFT upload URL retrieval with missing data in response"""
        mock_response = {
            "data": {
                "integrationFileTransferUploadUrl": None
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.get_cft_upload_url(
            integration_instance_id=self.integration_instance_id,
            filename=self.filename,
            dataset_id=self.dataset_id
        )

        assert result is None

    @patch('builtins.open', new_callable=mock_open, read_data="test,csv,data")
    @patch('requests.Session.put')
    def test_upload_cft_file_csv_success(self, mock_put, mock_file):
        """Test successful CSV file upload"""
        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/csv'}
        mock_response.text = '{"status": "success"}'
        mock_response.json.return_value = {"status": "success"}
        mock_put.return_value = mock_response

        # Create a temporary file path
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
            temp_file.write(b"test,csv,data")
            temp_file_path = temp_file.name

        try:
            result = self.client.upload_cft_file(
                upload_url="https://s3.amazonaws.com/test-bucket/test-file.csv",
                file_path=temp_file_path
            )

            # Verify the result structure
            assert result['status_code'] == 200
            assert result['success'] is True
            assert result['response_data'] == {'text': '{"status": "success"}'}
            assert 'Content-Type' in result['headers']
            assert result['headers']['Content-Type'] == 'text/csv'

            # Verify the PUT request was made correctly
            mock_put.assert_called_once()
            call_args = mock_put.call_args
            assert call_args[0][0] == "https://s3.amazonaws.com/test-bucket/test-file.csv"
            assert call_args[1]['headers']['Content-Type'] == 'text/csv'
            assert call_args[1]['timeout'] == 300

        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)

    @patch('builtins.open', new_callable=mock_open, read_data="test,csv,data")
    @patch('requests.Session.put')
    def test_upload_cft_file_csv_error_response(self, mock_put, mock_file):
        """Test CSV file upload with error response"""
        # Mock error HTTP response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.text = '{"error": "Bad Request"}'
        mock_response.json.return_value = {"error": "Bad Request"}
        mock_put.return_value = mock_response

        # Create a temporary file path
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
            temp_file.write(b"test,csv,data")
            temp_file_path = temp_file.name

        try:
            result = self.client.upload_cft_file(
                upload_url="https://s3.amazonaws.com/test-bucket/test-file.csv",
                file_path=temp_file_path
            )

            # Verify the result structure for error case
            assert result['status_code'] == 400
            assert result['success'] is False
            assert result['response_data'] == {'text': '{"error": "Bad Request"}'}

        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)

    def test_upload_cft_file_nonexistent_file(self):
        """Test CSV file upload with nonexistent file"""
        with pytest.raises(FileNotFoundError):
            self.client.upload_cft_file(
                upload_url="https://s3.amazonaws.com/test-bucket/test-file.csv",
                file_path="/nonexistent/file.csv"
            )

    def test_upload_cft_file_non_csv_extension(self):
        """Test file upload with non-CSV extension"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_file.write(b"test data")
            temp_file_path = temp_file.name

        try:
            with pytest.raises(ValueError, match="File must be a CSV file"):
                self.client.upload_cft_file(
                    upload_url="https://s3.amazonaws.com/test-bucket/test-file.csv",
                    file_path=temp_file_path
                )
        finally:
            os.unlink(temp_file_path)

    def test_upload_cft_file_csv_extension_case_insensitive(self):
        """Test file upload with CSV extension in different cases"""
        # Test uppercase .CSV
        with tempfile.NamedTemporaryFile(suffix='.CSV', delete=False) as temp_file:
            temp_file.write(b"test,csv,data")
            temp_file_path = temp_file.name

        try:
            with patch('requests.Session.put') as mock_put:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.headers = {'Content-Type': 'text/csv'}
                mock_response.text = '{"status": "success"}'
                mock_response.json.return_value = {"status": "success"}
                mock_put.return_value = mock_response

                result = self.client.upload_cft_file(
                    upload_url="https://s3.amazonaws.com/test-bucket/test-file.csv",
                    file_path=temp_file_path
                )

                assert result['success'] is True

        finally:
            os.unlink(temp_file_path)

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_invoke_cft_integration_success(self, mock_execute_query):
        """Test successful CFT integration invocation"""
        mock_response = {
            "data": {
                "invokeIntegrationInstance": {
                    "success": True,
                    "integrationJobId": "job-123"
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.invoke_cft_integration(self.integration_instance_id)

        assert result is True
        mock_execute_query.assert_called_once_with(
            INVOKE_INTEGRATION_INSTANCE,
            {"id": self.integration_instance_id}
        )

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_invoke_cft_integration_already_executing(self, mock_execute_query):
        """Test CFT integration invocation when already executing"""
        mock_response = {
            "data": {
                "invokeIntegrationInstance": {
                    "success": False,
                    "integrationJobId": None
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.invoke_cft_integration(self.integration_instance_id)

        assert result is False
        mock_execute_query.assert_called_once()

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_invoke_cft_integration_api_error(self, mock_execute_query):
        """Test CFT integration invocation with API error"""
        mock_execute_query.side_effect = JupiterOneApiError("API Error")

        with pytest.raises(JupiterOneApiError):
            self.client.invoke_cft_integration(self.integration_instance_id)

    @patch('jupiterone.client.JupiterOneClient._execute_query')
    def test_invoke_cft_integration_unexpected_response(self, mock_execute_query):
        """Test CFT integration invocation with unexpected response structure"""
        mock_response = {
            "data": {
                "invokeIntegrationInstance": {
                    "success": True,
                    "integrationJobId": None  # Unexpected: success but no job ID
                }
            }
        }
        mock_execute_query.return_value = mock_response

        result = self.client.invoke_cft_integration(self.integration_instance_id)

        # Should return True when success is True (regardless of job ID)
        assert result is True

    def test_invoke_cft_integration_empty_instance_id(self):
        """Test CFT integration invocation with empty instance ID"""
        with pytest.raises(ValueError, match="integration_instance_id is required"):
            self.client.invoke_cft_integration("")

    def test_invoke_cft_integration_none_instance_id(self):
        """Test CFT integration invocation with None instance ID"""
        with pytest.raises(ValueError, match="integration_instance_id is required"):
            self.client.invoke_cft_integration(None)
