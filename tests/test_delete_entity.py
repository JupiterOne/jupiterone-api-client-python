import json
import pytest
import responses

from jupiterone.client import JupiterOneClient


@responses.activate
def test_delete_entity_basic():
    """Test basic entity deletion with deleteEntityV2"""
    
    def request_callback(request):
        headers = {
            'Content-Type': 'application/json'
        }
        response = {
            'data': {
                'deleteEntityV2': {
                    'entity': {
                        '_id': '1'
                    },
                    '__typename': 'DeleteEntityResult'
                }
            }
        }

        return (200, headers, json.dumps(response))
    
    responses.add_callback(
        responses.POST, 'https://graphql.us.jupiterone.io',
        callback=request_callback,
        content_type='application/json',
    )

    j1 = JupiterOneClient(account='testAccount', token='testToken')
    response = j1.delete_entity('1')

    assert type(response) == dict
    assert type(response['entity']) == dict
    assert response['entity']['_id'] == '1'
    assert response['__typename'] == 'DeleteEntityResult'


@responses.activate
def test_delete_entity_with_timestamp():
    """Test entity deletion with timestamp parameter"""
    
    def request_callback(request):
        headers = {
            'Content-Type': 'application/json'
        }
        response = {
            'data': {
                'deleteEntityV2': {
                    'entity': {
                        '_id': '2'
                    },
                    '__typename': 'DeleteEntityResult'
                }
            }
        }

        return (200, headers, json.dumps(response))
    
    responses.add_callback(
        responses.POST, 'https://graphql.us.jupiterone.io',
        callback=request_callback,
        content_type='application/json',
    )

    j1 = JupiterOneClient(account='testAccount', token='testToken')
    response = j1.delete_entity('2', timestamp=1640995200000)

    assert type(response) == dict
    assert type(response['entity']) == dict
    assert response['entity']['_id'] == '2'


@responses.activate
def test_delete_entity_with_hard_delete():
    """Test entity deletion with hardDelete parameter"""
    
    def request_callback(request):
        headers = {
            'Content-Type': 'application/json'
        }
        response = {
            'data': {
                'deleteEntityV2': {
                    'entity': {
                        '_id': '3'
                    },
                    '__typename': 'DeleteEntityResult'
                }
            }
        }

        return (200, headers, json.dumps(response))
    
    responses.add_callback(
        responses.POST, 'https://graphql.us.jupiterone.io',
        callback=request_callback,
        content_type='application/json',
    )

    j1 = JupiterOneClient(account='testAccount', token='testToken')
    response = j1.delete_entity('3', hard_delete=False)

    assert type(response) == dict
    assert type(response['entity']) == dict
    assert response['entity']['_id'] == '3'


@responses.activate
def test_delete_entity_with_all_parameters():
    """Test entity deletion with all parameters"""
    
    def request_callback(request):
        headers = {
            'Content-Type': 'application/json'
        }
        response = {
            'data': {
                'deleteEntityV2': {
                    'entity': {
                        '_id': '4'
                    },
                    '__typename': 'DeleteEntityResult'
                }
            }
        }

        return (200, headers, json.dumps(response))
    
    responses.add_callback(
        responses.POST, 'https://graphql.us.jupiterone.io',
        callback=request_callback,
        content_type='application/json',
    )

    j1 = JupiterOneClient(account='testAccount', token='testToken')
    response = j1.delete_entity('4', timestamp=1640995200000, hard_delete=True)

    assert type(response) == dict
    assert type(response['entity']) == dict
    assert response['entity']['_id'] == '4'
