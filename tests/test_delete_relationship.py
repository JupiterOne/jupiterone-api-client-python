import json
import pytest
import responses

from jupiterone.client import JupiterOneClient
from jupiterone.errors import JupiterOneClientError


MOCK_RESPONSE = {
    'data': {
        'deleteRelationship': {
            'relationship': {
                '_id': '1'
            },
            'edge': {
                'id': '1',
                'toVertexId': '1',
                'fromVertexId': '2',
                'relationship': {
                    '_id': '1'
                },
                'properties': {}
            }
        }
    }
}


def _make_callback(captured_requests):
    """Return a callback that records request bodies and returns a success response."""
    def request_callback(request):
        captured_requests.append(json.loads(request.body))
        return (200, {'Content-Type': 'application/json'}, json.dumps(MOCK_RESPONSE))
    return request_callback


@responses.activate
def test_delete_relationship_sends_required_variables():
    captured = []
    responses.add_callback(
        responses.POST, 'https://graphql.us.jupiterone.io',
        callback=_make_callback(captured),
        content_type='application/json',
    )

    j1 = JupiterOneClient(account='testAccount', token='testToken1234567890')
    response = j1.delete_relationship(
        relationship_id='1',
        from_entity_id='2222222222',
        to_entity_id='3333333333'
    )

    assert len(captured) == 1
    variables = captured[0]['variables']
    assert variables['relationshipId'] == '1'
    assert variables['fromEntityId'] == '2222222222'
    assert variables['toEntityId'] == '3333333333'

    assert response['relationship']['_id'] == '1'
    assert response['edge']['toVertexId'] == '1'
    assert response['edge']['fromVertexId'] == '2'


def test_delete_relationship_raises_without_from_entity_id():
    j1 = JupiterOneClient(account='testAccount', token='testToken1234567890')
    with pytest.raises(JupiterOneClientError, match="from_entity_id is required"):
        j1.delete_relationship(relationship_id='1', to_entity_id='3333333333')


def test_delete_relationship_raises_without_to_entity_id():
    j1 = JupiterOneClient(account='testAccount', token='testToken1234567890')
    with pytest.raises(JupiterOneClientError, match="to_entity_id is required"):
        j1.delete_relationship(relationship_id='1', from_entity_id='2222222222')
