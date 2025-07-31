"""Test query_with_deferred_response method"""

import json
import pytest
import time
from unittest.mock import Mock, patch
from requests.exceptions import RequestException

from jupiterone.client import JupiterOneClient
from jupiterone.errors import JupiterOneApiError


class TestQueryWithDeferredResponse:
    """Test query_with_deferred_response method"""

    def setup_method(self):
        """Set up test fixtures"""
        self.client = JupiterOneClient(account="test-account", token="test-token")

    @patch.object(JupiterOneClient, 'session', create=True)
    def test_query_with_deferred_response_single_page(self, mock_session):
        """Test deferred response query with single page of results"""
        # Mock the initial request to get download URL
        mock_url_response = Mock()
        mock_url_response.status_code = 200
        mock_url_response.json.return_value = {
            'data': {
                'queryV1': {
                    'url': 'https://download.example.com/results.json'
                }
            }
        }

        # Mock the download response
        mock_download_response = Mock()
        mock_download_response.json.return_value = {
            'status': 'COMPLETED',
            'data': [
                {'id': '1', 'name': 'entity1'},
                {'id': '2', 'name': 'entity2'}
            ]
        }

        mock_session.post.return_value = mock_url_response
        mock_session.get.return_value = mock_download_response

        result = self.client.query_with_deferred_response("FIND * LIMIT 10")

        # Verify the initial request
        mock_session.post.assert_called_once()
        post_call = mock_session.post.call_args
        assert post_call[0][0] == self.client.graphql_url
        assert post_call[1]['headers'] == self.client.headers
        
        # Verify the download request
        mock_session.get.assert_called_once_with('https://download.example.com/results.json', timeout=60)

        # Verify the result
        assert result == [
            {'id': '1', 'name': 'entity1'},
            {'id': '2', 'name': 'entity2'}
        ]

    @patch.object(JupiterOneClient, 'session', create=True)
    def test_query_with_deferred_response_multiple_pages(self, mock_session):
        """Test deferred response query with multiple pages"""
        # Mock the initial request
        mock_url_response = Mock()
        mock_url_response.status_code = 200
        mock_url_response.json.return_value = {
            'data': {
                'queryV1': {
                    'url': 'https://download.example.com/results1.json'
                }
            }
        }

        # Mock the first download response with cursor
        mock_download_response1 = Mock()
        mock_download_response1.json.return_value = {
            'status': 'COMPLETED',
            'data': [
                {'id': '1', 'name': 'entity1'},
                {'id': '2', 'name': 'entity2'}
            ],
            'cursor': 'cursor123'
        }

        # Mock the second download response (final page)
        mock_download_response2 = Mock()
        mock_download_response2.json.return_value = {
            'status': 'COMPLETED',
            'data': [
                {'id': '3', 'name': 'entity3'},
                {'id': '4', 'name': 'entity4'}
            ]
        }

        mock_session.post.return_value = mock_url_response
        mock_session.get.side_effect = [mock_download_response1, mock_download_response2]

        result = self.client.query_with_deferred_response("FIND * LIMIT 10")

        # Verify the initial request
        mock_session.post.assert_called_once()
        
        # Verify both download requests
        assert mock_session.get.call_count == 2
        get_calls = mock_session.get.call_args_list
        assert get_calls[0][0][0] == 'https://download.example.com/results1.json'
        assert get_calls[1][0][0] == 'https://download.example.com/results1.json'  # Same URL for cursor-based pagination

        # Verify the combined result
        expected_result = [
            {'id': '1', 'name': 'entity1'},
            {'id': '2', 'name': 'entity2'},
            {'id': '3', 'name': 'entity3'},
            {'id': '4', 'name': 'entity4'}
        ]
        assert result == expected_result

    @patch.object(JupiterOneClient, 'session', create=True)
    def test_query_with_deferred_response_with_cursor(self, mock_session):
        """Test deferred response query with initial cursor"""
        # Mock the initial request
        mock_url_response = Mock()
        mock_url_response.status_code = 200
        mock_url_response.json.return_value = {
            'data': {
                'queryV1': {
                    'url': 'https://download.example.com/results.json'
                }
            }
        }

        # Mock the download response
        mock_download_response = Mock()
        mock_download_response.json.return_value = {
            'status': 'COMPLETED',
            'data': [
                {'id': '3', 'name': 'entity3'},
                {'id': '4', 'name': 'entity4'}
            ]
        }

        mock_session.post.return_value = mock_url_response
        mock_session.get.return_value = mock_download_response

        result = self.client.query_with_deferred_response("FIND * LIMIT 10", cursor="initial_cursor")

        # Verify the initial request includes cursor
        mock_session.post.assert_called_once()
        post_call = mock_session.post.call_args
        request_data = post_call[1]['json']
        assert request_data['variables']['cursor'] == 'initial_cursor'

        # Verify the result
        assert result == [
            {'id': '3', 'name': 'entity3'},
            {'id': '4', 'name': 'entity4'}
        ]

    @patch.object(JupiterOneClient, 'session', create=True)
    def test_query_with_deferred_response_polling(self, mock_session):
        """Test deferred response query with polling for completion"""
        # Mock the initial request
        mock_url_response = Mock()
        mock_url_response.status_code = 200
        mock_url_response.json.return_value = {
            'data': {
                'queryV1': {
                    'url': 'https://download.example.com/results.json'
                }
            }
        }

        # Mock the download responses - first IN_PROGRESS, then COMPLETED
        mock_download_response1 = Mock()
        mock_download_response1.json.return_value = {
            'status': 'IN_PROGRESS',
            'data': []
        }

        mock_download_response2 = Mock()
        mock_download_response2.json.return_value = {
            'status': 'COMPLETED',
            'data': [
                {'id': '1', 'name': 'entity1'}
            ]
        }

        mock_session.post.return_value = mock_url_response
        mock_session.get.side_effect = [mock_download_response1, mock_download_response2]

        result = self.client.query_with_deferred_response("FIND * LIMIT 10")

        # Verify the polling occurred
        assert mock_session.get.call_count == 2
        get_calls = mock_session.get.call_args_list
        assert get_calls[0][0][0] == 'https://download.example.com/results.json'
        assert get_calls[1][0][0] == 'https://download.example.com/results.json'

        # Verify the result
        assert result == [{'id': '1', 'name': 'entity1'}]

    @patch.object(JupiterOneClient, 'session', create=True)
    def test_query_with_deferred_response_rate_limit_retry(self, mock_session):
        """Test deferred response query with rate limit retry"""
        # Mock the initial request with rate limit
        mock_url_response_429 = Mock()
        mock_url_response_429.status_code = 429
        mock_url_response_429.headers = {'Retry-After': '2'}

        mock_url_response_success = Mock()
        mock_url_response_success.status_code = 200
        mock_url_response_success.json.return_value = {
            'data': {
                'queryV1': {
                    'url': 'https://download.example.com/results.json'
                }
            }
        }

        # Mock the download response
        mock_download_response = Mock()
        mock_download_response.json.return_value = {
            'status': 'COMPLETED',
            'data': [{'id': '1', 'name': 'entity1'}]
        }

        mock_session.post.side_effect = [mock_url_response_429, mock_url_response_success]
        mock_session.get.return_value = mock_download_response

        with patch('time.sleep') as mock_sleep:
            result = self.client.query_with_deferred_response("FIND * LIMIT 10")

        # Verify retry occurred
        assert mock_session.post.call_count == 2
        mock_sleep.assert_called_once_with(2)

        # Verify the result
        assert result == [{'id': '1', 'name': 'entity1'}]

    @patch.object(JupiterOneClient, 'session', create=True)
    def test_query_with_deferred_response_max_retries_exceeded(self, mock_session):
        """Test deferred response query when max retries are exceeded"""
        # Mock the initial request to always return 429
        mock_url_response = Mock()
        mock_url_response.status_code = 429
        mock_url_response.headers = {'Retry-After': '1'}

        mock_session.post.return_value = mock_url_response

        with patch('time.sleep') as mock_sleep:
            result = self.client.query_with_deferred_response("FIND * LIMIT 10")

        # Verify max retries were attempted
        assert mock_session.post.call_count == 5
        assert mock_sleep.call_count == 4  # 4 retries with sleep

        # Verify the result is empty (no successful download)
        assert result == []

    @patch.object(JupiterOneClient, 'session', create=True)
    def test_query_with_deferred_response_download_error(self, mock_session):
        """Test deferred response query with download error"""
        # Mock the initial request
        mock_url_response = Mock()
        mock_url_response.status_code = 200
        mock_url_response.json.return_value = {
            'data': {
                'queryV1': {
                    'url': 'https://download.example.com/results.json'
                }
            }
        }

        # Mock the download request to raise an exception
        mock_session.post.return_value = mock_url_response
        mock_session.get.side_effect = RequestException("Download failed")

        result = self.client.query_with_deferred_response("FIND * LIMIT 10")

        # Verify the result is the exception
        assert isinstance(result, RequestException)
        assert str(result) == "Download failed"

    @patch.object(JupiterOneClient, 'session', create=True)
    def test_query_with_deferred_response_initial_request_failure(self, mock_session):
        """Test deferred response query with initial request failure"""
        # Mock the initial request to fail
        mock_url_response = Mock()
        mock_url_response.status_code = 500
        mock_url_response.ok = False

        mock_session.post.return_value = mock_url_response

        result = self.client.query_with_deferred_response("FIND * LIMIT 10")

        # Verify the result is empty (no successful download)
        assert result == []

    @patch.object(JupiterOneClient, 'session', create=True)
    def test_query_with_deferred_response_empty_result(self, mock_session):
        """Test deferred response query with empty result"""
        # Mock the initial request
        mock_url_response = Mock()
        mock_url_response.status_code = 200
        mock_url_response.json.return_value = {
            'data': {
                'queryV1': {
                    'url': 'https://download.example.com/results.json'
                }
            }
        }

        # Mock the download response with empty data
        mock_download_response = Mock()
        mock_download_response.json.return_value = {
            'status': 'COMPLETED',
            'data': []
        }

        mock_session.post.return_value = mock_url_response
        mock_session.get.return_value = mock_download_response

        result = self.client.query_with_deferred_response("FIND * LIMIT 10")

        # Verify the result is empty
        assert result == []

    @patch.object(JupiterOneClient, 'session', create=True)
    def test_query_with_deferred_response_complex_query(self, mock_session):
        """Test deferred response query with complex J1QL query"""
        # Mock the initial request
        mock_url_response = Mock()
        mock_url_response.status_code = 200
        mock_url_response.json.return_value = {
            'data': {
                'queryV1': {
                    'url': 'https://download.example.com/results.json'
                }
            }
        }

        # Mock the download response
        mock_download_response = Mock()
        mock_download_response.json.return_value = {
            'status': 'COMPLETED',
            'data': [
                {'_id': '1', '_type': 'aws_instance', 'name': 'instance-1'},
                {'_id': '2', '_type': 'aws_instance', 'name': 'instance-2'}
            ]
        }

        mock_session.post.return_value = mock_url_response
        mock_session.get.return_value = mock_download_response

        complex_query = """
        FIND aws_instance 
        THAT RELATES TO aws_vpc 
        WITH tag.Environment = 'production'
        RETURN _id, _type, name, tag.Environment
        LIMIT 100
        """

        result = self.client.query_with_deferred_response(complex_query)

        # Verify the query was sent correctly
        mock_session.post.assert_called_once()
        post_call = mock_session.post.call_args
        request_data = post_call[1]['json']
        assert request_data['variables']['query'] == complex_query.strip()
        assert request_data['variables']['deferredResponse'] == 'FORCE'

        # Verify the result
        assert len(result) == 2
        assert result[0]['_type'] == 'aws_instance'
        assert result[1]['name'] == 'instance-2' 