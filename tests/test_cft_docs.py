"""Docs-drift guard for the Custom File Transfer (CFT) upload helpers (TD-9692).

The docs and examples must only read keys of ``upload_info`` that the
``integrationFileTransferUploadUrl`` mutation actually selects, and the
``dataset_id`` docstring must say it is the instance's Dataset Name.
"""
import glob
import os
import re
from unittest.mock import patch

from jupiterone.client import JupiterOneClient

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _selected_fields():
    client = JupiterOneClient(account="test-account", token="test-token")
    with patch("jupiterone.client.JupiterOneClient._execute_query") as mock_exec:
        mock_exec.return_value = {
            "data": {"integrationFileTransferUploadUrl": {}}
        }
        client.get_cft_upload_url("instance", "data.csv", "EuropaUsers")
    query = mock_exec.call_args[0][0]
    match = re.search(
        r"integrationFileTransferUploadUrl\s*\(\s*integrationInstanceId:[^)]*\)\s*\{([^}]*)\}", query
    )
    assert match, "could not find the selection set in the mutation"
    return set(match.group(1).split())


def _upload_info_reads():
    paths = [os.path.join(ROOT, "README.md")]
    paths += sorted(glob.glob(os.path.join(ROOT, "examples", "*.py")))
    paths += sorted(glob.glob(os.path.join(ROOT, "jupiterone", "*.py")))
    pattern = re.compile(r"upload_info\[['\"](\w+)['\"]\]")
    reads = []
    for path in paths:
        with open(path, encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                for key in pattern.findall(line):
                    reads.append((os.path.relpath(path, ROOT), lineno, key))
    return reads


def test_selected_fields_found():
    assert {"uploadUrl", "expiresIn"} <= _selected_fields()


def test_docs_only_read_selected_upload_info_keys():
    selected = _selected_fields()
    reads = _upload_info_reads()
    assert reads, "no upload_info[...] reads found; the scan is not looking anywhere"
    bad = [f"{p}:{n} reads '{k}'" for p, n, k in reads if k not in selected]
    assert not bad, f"keys not selected by the mutation {sorted(selected)}: {bad}"


def test_get_cft_upload_url_docstring_says_dataset_name():
    doc = JupiterOneClient.get_cft_upload_url.__doc__
    assert "Dataset Name" in doc


def test_get_cft_upload_url_docstring_names_lookup():
    doc = JupiterOneClient.get_cft_upload_url.__doc__
    assert "get_integration_instance_details" in doc
