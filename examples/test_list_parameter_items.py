#!/usr/bin/env python3
"""
Test script: Create an account parameter of the list type with N items.

Takes an integer argument for how many list items to include, allowing
easy testing of list size limits.

Prerequisites (environment variables):
- JUPITERONE_ACCOUNT_ID
- JUPITERONE_API_TOKEN
- (optional) JUPITERONE_URL
- (optional) JUPITERONE_SYNC_URL

Usage:
  python test_list_parameter_21_items.py <number_of_items>
  python test_list_parameter_21_items.py 21
  python test_list_parameter_21_items.py 50
"""

import os
import sys
from jupiterone import JupiterOneClient

PARAM_NAME = "TEST_LIST_PARAM_N_ITEMS"


def build_list(n: int) -> list:
    return [f"item_{str(i).zfill(3)}_test_entity_type" for i in range(1, n + 1)]


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <number_of_items>")
        sys.exit(1)

    try:
        count = int(sys.argv[1])
    except ValueError:
        print(f"ERROR: '{sys.argv[1]}' is not a valid integer")
        sys.exit(1)

    if count < 1:
        print("ERROR: number of items must be at least 1")
        sys.exit(1)

    param_value = build_list(count)

    print(f"Test: Create list-type account parameter with {count} items")
    print("=" * 70)

    account_id = os.getenv("JUPITERONE_ACCOUNT_ID")
    api_token = os.getenv("JUPITERONE_API_TOKEN")

    if not account_id or not api_token:
        print("ERROR: JUPITERONE_ACCOUNT_ID and JUPITERONE_API_TOKEN must be set")
        sys.exit(1)

    j1 = JupiterOneClient(
        account=account_id,
        token=api_token,
        url=os.getenv("JUPITERONE_URL", "https://graphql.us.jupiterone.io"),
        sync_url=os.getenv("JUPITERONE_SYNC_URL", "https://api.us.jupiterone.io"),
    )

    print(f"Parameter name : {PARAM_NAME}")
    print(f"List length    : {len(param_value)}")
    print(f"Items          : {param_value[:3]} ... {param_value[-1]}")
    print()

    # Step 1: Create the parameter
    print("[1/3] Creating parameter...")
    try:
        result = j1.create_update_parameter(
            name=PARAM_NAME,
            value=param_value,
            secret=False,
        )
        success = result and result.get("data", {}).get("setParameter", {}).get("success") is True
        print(f"  Response: {result}")
        if success:
            print("  Result: SUCCESS")
        else:
            print("  Result: UNEXPECTED RESPONSE (see above)")
    except Exception as exc:
        print(f"  Result: FAILED — {exc}")
        sys.exit(1)

    # Step 2: Read back and verify
    print(f"\n[2/3] Reading parameter back...")
    try:
        details = j1.get_parameter_details(name=PARAM_NAME)
        print(f"  Response: {details}")

        stored_value = (
            details.get("data", {})
            .get("parameter", {})
            .get("value")
        )
        if isinstance(stored_value, list):
            print(f"  Stored list length: {len(stored_value)}")
            if len(stored_value) == count:
                print(f"  Verification: ALL {count} ITEMS PERSISTED")
            else:
                print(f"  Verification: MISMATCH — expected {count}, got {len(stored_value)}")
        else:
            print(f"  Verification: VALUE IS NOT A LIST — type={type(stored_value)}")
    except Exception as exc:
        print(f"  Result: FAILED to read back — {exc}")

    # Step 3: Cleanup
    print("\n[3/3] Cleaning up (overwriting with empty list)...")
    try:
        cleanup = j1.create_update_parameter(
            name=PARAM_NAME,
            value=[],
            secret=False,
        )
        print(f"  Cleanup response: {cleanup}")
        print("  Cleanup: DONE")
    except Exception as exc:
        print(f"  Cleanup: FAILED — {exc}")

    print("\n" + "=" * 70)
    print("Test complete.")


if __name__ == "__main__":
    main()
