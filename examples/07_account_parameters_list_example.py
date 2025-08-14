#!/usr/bin/env python3
"""
JupiterOne Python SDK - Account Parameter (List Value) Example

This example demonstrates how to create or update an Account Parameter where the
value is a list of strings.

Prerequisites (environment variables):
- JUPITERONE_ACCOUNT_ID
- JUPITERONE_API_TOKEN
- (optional) JUPITERONE_URL
- (optional) JUPITERONE_SYNC_URL

Usage:
  python 07_account_parameters_list_example.py
"""

import os
from jupiterone import JupiterOneClient


def setup_client() -> JupiterOneClient:
    """Instantiate the JupiterOne client using environment variables."""
    return JupiterOneClient(
        account=os.getenv("JUPITERONE_ACCOUNT_ID"),
        token=os.getenv("JUPITERONE_API_TOKEN"),
        url=os.getenv("JUPITERONE_URL", "https://graphql.us.jupiterone.io"),
        sync_url=os.getenv("JUPITERONE_SYNC_URL", "https://api.us.jupiterone.io"),
    )


def main() -> None:
    print("JupiterOne - Create/Update Account Parameter (List Value)")
    print("=" * 70)

    # Configure the parameter name and value
    # Name can be anything meaningful to your workflows
    parameter_name = os.getenv("J1_LIST_PARAM_NAME", "ENTITY_TYPES_TO_INCLUDE")

    # Example list value requested: ["aws_account", "aws_security_group"]
    parameter_value = ["aws_account", "aws_security_group"]

    try:
        j1 = setup_client()

        print(f"Creating/Updating parameter '{parameter_name}' with value: {parameter_value}")
        result = j1.create_update_parameter(
            name=parameter_name,
            value=parameter_value,
            secret=False,
        )

        # The mutation returns a success flag; fetch the parameter to verify
        if result and result.get("setParameter", {}).get("success") is True:
            print("✓ Parameter upsert reported success")
        else:
            print("! Parameter upsert did not report success (check details below)")
        print(result)

        # Verify by reading it back (non-secret parameters will return the value)
        details = j1.get_parameter_details(name=parameter_name)
        print("\nFetched parameter details:")
        print(details)

        print("\n✓ Completed creating/updating list-valued account parameter")

    except Exception as exc:
        print(f"✗ Error: {exc}")
        print("\nMake sure you have set the following environment variables:")
        print("- JUPITERONE_ACCOUNT_ID")
        print("- JUPITERONE_API_TOKEN")
        print("- JUPITERONE_URL (optional)")
        print("- JUPITERONE_SYNC_URL (optional)")


if __name__ == "__main__":
    main()


