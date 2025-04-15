import os
import time
import json
import requests
from requests.adapters import HTTPAdapter, Retry


def const():

    # JupiterOne GraphQL API:
    url = "https://graphql.us.jupiterone.io"

    # JupiterOne API creds
    acct = os.environ.get("JUPITERONE_ACCOUNT")
    token = os.environ.get("JUPITERONE_TOKEN")

    # J1QL query to be executed
    query = "FIND *"

    return [acct, token, url, query]


def get_data(url, query, variables):

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + const()[1],
        'Jupiterone-Account': const()[0]
    }

    payload = {
        "query": query,
        "variables": variables
    }

    try:
        s = requests.Session()
        retries = Retry(total=10, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))
        response = s.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            raise Exception("Failed to fetch data. HTTP status code: " + str(response.status_code))
    except Exception as e:
        raise Exception("POST request to JupiterOne GraphQL API failed. Exception: " + str(e))


def fetch_first_result(url, query, variables):

    deferred_response = get_data(url, query, variables)
    results_url = deferred_response['data']['queryV1'].get('url')
    results_data = requests.get(results_url).json()
    return results_data


def build_payload(q):
    query = '''
        query J1QL($query: String!, $variables: JSON, $cursor: String, $deferredResponse: DeferredResponseOption 
        $flags: QueryV1Flags) {
          queryV1(query: $query, variables: $variables, cursor: $cursor, deferredResponse: $deferredResponse, 
          flags: $flags) {
            type
            url
            cursor
          }
          }
        '''

    variables = {
        "query": q,
        "deferredResponse": "FORCE",
        "cursor": ""
    }

    return query, variables


# def poll_deferred_response_url(url):
#
#     r = requests.get(url, verify=True).json()
#     max_retry = 10
#     retry_count = 0
#     retry_delay = 2
#
#     while r['status'] == "IN_PROGRESS" and retry_count < max_retry:
#         r = requests.get(url, verify=True).json()
#         retry_count += 1
#         time.sleep(retry_delay)
#         retry_delay *= 2
#
#     if r['status'] == "COMPLETED":
#         response_url = r['url']
#         return response_url
#
#     else:
#         formatted_json = json.dumps(r, indent=4)
#         # print(formatted_json)
#
#
# def fetch_cursor_results(results):
#
#     full_results = []
#     full_results.extend(results["data"])
#
#     try:
#
#         while results["cursor"]:
#
#             variables = build_payload(const()[3])[1]
#
#             variables["cursor"] = results["cursor"]
#             print(results["cursor"])
#
#             url = fetch_results_url(const()[2],
#                                     build_payload(const()[3])[0],
#                                     variables)
#
#             print(url)
#
#             # results_download_url = poll_deferred_response_url(url)
#
#             r = requests.get(results_download_url, verify=True).json()
#             print(r)
#             #
#             # full_results.extend(r["data"])
#             #
#             # return full_results
#
#     except Exception as e:
#         err = e
#
#         return err


def fetch_all_results(api_endpoint, query, variables=None, headers=None):
    """
    Fetch all URLs from a paginated GraphQL API endpoint.

    Args:
        api_endpoint (str): The GraphQL API URL to request data from.
        query (str): The GraphQL query string.
        variables (dict, optional): Variables for the GraphQL query.
        headers (dict, optional): Headers for the request.

    Returns:
        list: A list of URLs retrieved from the API.
    """

    all_results_data = []
    cursor = None  # Initial cursor
    first_request = True

    while True:

        # Update variables with the current cursor if available
        if variables is None:
            variables = {}
        if cursor:
            variables['cursor'] = cursor

        payload = {
            "query": query,
            "variables": variables
        }

        try:
            s = requests.Session()
            retries = Retry(total=10, backoff_factor=1, status_forcelist=[502, 503, 504])
            s.mount('https://', HTTPAdapter(max_retries=retries))
            response = s.post(api_endpoint, headers=headers, json=payload)

            if response.status_code == 200:
                data = response.json()
                # return data
                # print(data)

                # Extract URLs from the response (modify according to API response structure)
                url = data.get('data', {}).get('queryV1', []).get('url', "")

                # print(url)
                # print(first_request)

                if first_request and url:
                    # Execute a GET request to the first URL and return the contents
                    first_url_response = requests.get(url)
                    first_url_response_data = first_url_response.json()['data']
                    first_url_response_url = first_url_response.json()['url']
                    first_url_response_cursor = first_url_response.json()['cursor']
                    # print(first_url_response_data)
                    # print(first_url_response_cursor)
                    # print(first_url_response_url)

                    all_results_data.append(first_url_response_data)

                    while first_url_response_cursor:
                        url_response = requests.get(first_url_response_url).json()
                        print(url_response)
                        cursor = url_response.get('cursor')

                        all_results_data.append(url_response)

                        if not cursor:
                            break


                    return all_results_data

                first_request = False  # Mark first request as done

                # Check for next cursor
                cursor = data.get('data', {}).get('cursor')
                if not cursor:
                    break  # Stop if there is no next cursor

            else:
                raise Exception("Failed to fetch data. HTTP status code: " + str(response.status_code))
        except Exception as e:
            raise Exception("POST request to JupiterOne GraphQL API failed. Exception: " + str(e))

    return all_results_data


if __name__ == "__main__":

    deferred_response_first_result = fetch_first_result(const()[2],
                                          build_payload(const()[3])[0],
                                          build_payload(const()[3])[1])
    # print(deferred_response_first_result)

    all_results_data = []

    response_status = deferred_response_first_result['status']
    response_url = deferred_response_first_result['url']
    response_data = deferred_response_first_result['data']
    response_cursor = deferred_response_first_result['cursor']

    all_results_data.extend(response_data)

    cursor = response_cursor

    while cursor:
        variables = build_payload(const()[3])[1]['cursor'] = cursor
        # print(variables)
        r = get_data(url=response_url, query=build_payload(const()[3])[0], variables=const()[3])
        print(r)
        r_data = r['data']
        r_cursor = r['cursor']

        all_results_data.extend(r_data)

        cursor = r_cursor

        if not cursor:
            break



    # endpoint = const()[2]
    # query = build_payload("find *")[0]
    # variables = build_payload(const()[3])[1]
    # # print(variables)
    # headers = {
    #     'Content-Type': 'application/json',
    #     'Authorization': 'Bearer ' + const()[1],
    #     'Jupiterone-Account': const()[0]
    # }
    #
    # r = fetch_all_urls(endpoint, query, variables, headers)

    # print(fetch_all_urls(endpoint, query, variables, headers))



    # deferredResponseURL = fetch_results_url(const()[2],
    #                                       build_payload(const()[3])[0],
    #                                       build_payload(const()[3])[1])
    # # print(deferredResponseURL)
    #
    # results_download_url = poll_deferred_response_url(deferredResponseURL)
    #
    # r = requests.get(results_download_url, verify=True).json()
    # print(len(r["data"]))
    #
    # out = fetch_cursor_results(r)
    # print(len(out))





    #
    # # # write full results data to local .json file
    # # with open("J1VulnExtr.json", "w", encoding="utf-8") as outfile:
    # #     json.dump(full_results, outfile)
