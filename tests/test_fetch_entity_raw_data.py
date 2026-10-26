"""Tests for fetch_entity_raw_data_v2 and the deprecated fetch_entity_raw_data"""

import warnings
from unittest.mock import patch

import pytest

from jupiterone.client import JupiterOneClient
from jupiterone.constants import GET_ENTITY_RAW_DATA, GET_ENTITY_RAW_DATA_V2
from jupiterone.errors import JupiterOneApiError, JupiterOneClientError

ENTITY_ID = "7c697b79-f527-5b0a-a1f6-9fec1a3a6ad7"
ADDRESS = {
    "source": "integration-managed",
    "integrationInstanceId": "adc8f9dc-3ff0-4d33-bb88-1836b99ce8c7",
    "entityKey": "some-entity-key",
    "entityType": "crowdstrike_vulnerability",
}
AVAILABLE_RESULT = {
    "entityId": ENTITY_ID,
    "status": "AVAILABLE",
    "message": None,
    "collectedAt": "2026-10-20T12:00:00.000Z",
    "payload": [
        {"name": "api", "contentType": "application/json", "data": {"id": 1}},
        {"name": "note", "contentType": "text/plain", "data": "some text"},
    ],
}
EXPIRED_RESULT = {
    "entityId": ENTITY_ID,
    "status": "NOT_AVAILABLE_OR_EXPIRED",
    "message": "Raw data is not available or has expired",
    "collectedAt": None,
    "payload": [],
}


def _kwargs():
    return dict(
        source=ADDRESS["source"],
        integration_instance_id=ADDRESS["integrationInstanceId"],
        entity_key=ADDRESS["entityKey"],
        entity_type=ADDRESS["entityType"],
    )


class TestFetchEntityRawDataV2:
    def setup_method(self):
        self.client = JupiterOneClient(account="test-account", token="test-token")

    @patch("jupiterone.client.JupiterOneClient.query_v1")
    @patch("jupiterone.client.JupiterOneClient._execute_query")
    def test_explicit_address_returns_unwrapped_result(self, mock_execute, mock_query):
        mock_execute.return_value = {"data": {"entityRawDataV2": AVAILABLE_RESULT}}

        result = self.client.fetch_entity_raw_data_v2(ENTITY_ID, **_kwargs())

        assert result == AVAILABLE_RESULT
        mock_query.assert_not_called()  # no address lookup needed
        mock_execute.assert_called_once_with(
            query=GET_ENTITY_RAW_DATA_V2,
            variables={"entityId": ENTITY_ID, "address": ADDRESS},
        )

    @patch("jupiterone.client.JupiterOneClient._execute_query")
    def test_query_does_not_use_legacy(self, mock_execute):
        mock_execute.return_value = {"data": {"entityRawDataV2": AVAILABLE_RESULT}}
        self.client.fetch_entity_raw_data_v2(ENTITY_ID, **_kwargs())

        sent = mock_execute.call_args.kwargs["query"]
        assert "entityRawDataV2(" in sent
        assert "entityRawDataLegacy(" not in sent
        assert "status" in sent and "message" in sent and "collectedAt" in sent

    @patch("jupiterone.client.JupiterOneClient._execute_query")
    def test_not_available_or_expired_does_not_raise(self, mock_execute):
        mock_execute.return_value = {"data": {"entityRawDataV2": EXPIRED_RESULT}}

        result = self.client.fetch_entity_raw_data_v2(ENTITY_ID, **_kwargs())

        assert result["status"] == "NOT_AVAILABLE_OR_EXPIRED"
        assert result["payload"] == []
        assert result["message"]

    @patch("jupiterone.client.JupiterOneClient.query_v1")
    @patch("jupiterone.client.JupiterOneClient._execute_query")
    def test_address_resolved_via_j1ql_when_only_entity_id(self, mock_execute, mock_query):
        mock_query.return_value = {"data": [dict(ADDRESS)]}
        mock_execute.return_value = {"data": {"entityRawDataV2": AVAILABLE_RESULT}}

        result = self.client.fetch_entity_raw_data_v2(ENTITY_ID)

        assert result == AVAILABLE_RESULT
        j1ql = mock_query.call_args.args[0]
        assert f"_id = '{ENTITY_ID}'" in j1ql
        assert "LIMIT 1" in j1ql
        assert mock_execute.call_args.kwargs["variables"] == {
            "entityId": ENTITY_ID,
            "address": ADDRESS,
        }

    @patch("jupiterone.client.JupiterOneClient.query_v1")
    @patch("jupiterone.client.JupiterOneClient._execute_query")
    def test_partial_address_only_fills_missing_fields(self, mock_execute, mock_query):
        mock_query.return_value = {"data": [dict(ADDRESS)]}
        mock_execute.return_value = {"data": {"entityRawDataV2": AVAILABLE_RESULT}}

        self.client.fetch_entity_raw_data_v2(
            ENTITY_ID, entity_key="caller-supplied-key"
        )

        address = mock_execute.call_args.kwargs["variables"]["address"]
        assert address["entityKey"] == "caller-supplied-key"
        assert address["source"] == ADDRESS["source"]

    @patch("jupiterone.client.JupiterOneClient.query_v1")
    @patch("jupiterone.client.JupiterOneClient._execute_query")
    def test_entity_id_is_escaped_in_j1ql(self, mock_execute, mock_query):
        mock_query.return_value = {"data": []}

        self.client.fetch_entity_raw_data_v2("bad'id\\")

        j1ql = mock_query.call_args.args[0]
        assert "_id = 'bad\\'id\\\\'" in j1ql

    @patch("jupiterone.client.JupiterOneClient.query_v1")
    @patch("jupiterone.client.JupiterOneClient._execute_query")
    def test_unknown_entity_returns_not_available_without_api_call(
        self, mock_execute, mock_query
    ):
        mock_query.return_value = {"data": []}

        result = self.client.fetch_entity_raw_data_v2(ENTITY_ID)

        assert result["status"] == "NOT_AVAILABLE_OR_EXPIRED"
        assert result["entityId"] == ENTITY_ID
        assert result["payload"] == []
        mock_execute.assert_not_called()

    @patch("jupiterone.client.JupiterOneClient.query_v1")
    @patch("jupiterone.client.JupiterOneClient._execute_query")
    def test_non_integration_entity_returns_not_available_without_api_call(
        self, mock_execute, mock_query
    ):
        # e.g. unified entities have no _integrationInstanceId
        mock_query.return_value = {
            "data": [{"source": "system-unification", "entityKey": "k|is|unified_entity",
                      "entityType": "unified_entity"}]
        }

        result = self.client.fetch_entity_raw_data_v2(ENTITY_ID)

        assert result["status"] == "NOT_AVAILABLE_OR_EXPIRED"
        assert "integrationInstanceId" in result["message"]
        mock_execute.assert_not_called()

    @pytest.mark.parametrize("bad_id", [None, "", "   ", 123])
    def test_invalid_entity_id_raises(self, bad_id):
        with pytest.raises(JupiterOneClientError):
            self.client.fetch_entity_raw_data_v2(bad_id, **_kwargs())

    @patch("jupiterone.client.JupiterOneClient._execute_query")
    def test_api_errors_still_raise(self, mock_execute):
        mock_execute.side_effect = JupiterOneApiError("boom")

        with pytest.raises(JupiterOneApiError):
            self.client.fetch_entity_raw_data_v2(ENTITY_ID, **_kwargs())


class TestFetchEntityRawDataDeprecated:
    """fetch_entity_raw_data(entity_id) must keep its original return shape."""

    def setup_method(self):
        self.client = JupiterOneClient(account="test-account", token="test-token")

    @patch("jupiterone.client.JupiterOneClient.query_v1")
    @patch("jupiterone.client.JupiterOneClient._execute_query")
    def test_keeps_legacy_envelope_and_adds_fields(self, mock_execute, mock_query):
        mock_query.return_value = {"data": [dict(ADDRESS)]}
        response = {"data": {"entityRawDataLegacy": AVAILABLE_RESULT}}
        mock_execute.return_value = response

        with pytest.warns(DeprecationWarning):
            result = self.client.fetch_entity_raw_data(entity_id=ENTITY_ID)

        assert result == response
        legacy = result["data"]["entityRawDataLegacy"]
        assert legacy["entityId"] == ENTITY_ID
        for item in legacy["payload"]:
            # keys that existing callers read
            assert {"contentType", "name", "data"} <= item.keys()

    @patch("jupiterone.client.JupiterOneClient.query_v1")
    @patch("jupiterone.client.JupiterOneClient._execute_query")
    def test_no_longer_calls_entity_raw_data_legacy(self, mock_execute, mock_query):
        mock_query.return_value = {"data": [dict(ADDRESS)]}
        mock_execute.return_value = {"data": {"entityRawDataLegacy": AVAILABLE_RESULT}}

        with pytest.warns(DeprecationWarning):
            self.client.fetch_entity_raw_data(entity_id=ENTITY_ID)

        sent = mock_execute.call_args.kwargs["query"]
        assert sent == GET_ENTITY_RAW_DATA
        assert "entityRawDataLegacy(" not in sent
        assert "entityRawDataLegacy: entityRawDataV2(" in sent
        assert mock_execute.call_args.kwargs["variables"] == {
            "entityId": ENTITY_ID,
            "address": ADDRESS,
        }

    @patch("jupiterone.client.JupiterOneClient.query_v1")
    @patch("jupiterone.client.JupiterOneClient._execute_query")
    def test_positional_call_still_works(self, mock_execute, mock_query):
        mock_query.return_value = {"data": [dict(ADDRESS)]}
        mock_execute.return_value = {"data": {"entityRawDataLegacy": AVAILABLE_RESULT}}

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            result = self.client.fetch_entity_raw_data(ENTITY_ID)

        assert result["data"]["entityRawDataLegacy"]["status"] == "AVAILABLE"

    @patch("jupiterone.client.JupiterOneClient.query_v1")
    @patch("jupiterone.client.JupiterOneClient._execute_query")
    def test_unavailable_entity_keeps_envelope_without_raising(
        self, mock_execute, mock_query
    ):
        mock_query.return_value = {"data": []}

        with pytest.warns(DeprecationWarning):
            result = self.client.fetch_entity_raw_data(entity_id=ENTITY_ID)

        legacy = result["data"]["entityRawDataLegacy"]
        assert legacy["status"] == "NOT_AVAILABLE_OR_EXPIRED"
        assert legacy["payload"] == []
        mock_execute.assert_not_called()

    def test_warning_points_at_caller(self):
        with patch(
            "jupiterone.client.JupiterOneClient.query_v1", return_value={"data": []}
        ):
            with pytest.warns(DeprecationWarning) as record:
                self.client.fetch_entity_raw_data(entity_id=ENTITY_ID)

        assert record[0].filename == __file__
