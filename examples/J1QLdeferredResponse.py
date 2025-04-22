import os
import time
import json
import requests
from requests.adapters import HTTPAdapter, Retry

# JupiterOne API creds
acct = os.environ.get("JUPITERONE_ACCOUNT")
token = os.environ.get("JUPITERONE_TOKEN")

# JupiterOne GraphQL API:
j1_graphql_url = "https://graphql.dev.jupiterone.io"

# JupiterOne GraphQL API headers
j1_graphql_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token,
        'Jupiterone-Account': acct
}

gql_query = """
query J1QL(
  $query: String!
  $variables: JSON
  $cursor: String
  $deferredResponse: DeferredResponseOption
) {
  queryV1(
    query: $query
    variables: $variables
    deferredResponse: $deferredResponse
    cursor: $cursor
  ) {
    type
    url
  }
}
"""

gql_variables = {
  "query": "FIND Finding",
  "deferredResponse": "FORCE",
  "cursor": "",
  "flags": {
    "variableResultSize": True
  },
}

payload = {
    "query": gql_query,
    "variables": gql_variables
}

all_query_results = []
cursor = None

while True:

    payload['variables']['cursor'] = cursor

    s = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504, 429])
    s.mount('https://', HTTPAdapter(max_retries=retries))
    url_response = s.post(j1_graphql_url, headers=j1_graphql_headers, json=payload)
    download_url = url_response.json()['data']['queryV1']['url']
    print(download_url)

    download_response = s.get(download_url).json()

    status = download_response['status']

    while status == 'IN_PROGRESS':
        time.sleep(0.2) # Sleep 200 milliseconds between checking status

        download_response = s.get(download_url).json() # fetch results data from download URL

        status = download_response['status'] # update 'status' for next iteration

    all_query_results.extend(download_response['data']) # add results to all results list
    print(len(download_response['data']))

    # Update cursor from response
    if 'cursor' in download_response:
        cursor = download_response['cursor']
        print(cursor)

    else:
        break

# print(all_query_results)
print(len(all_query_results))
