#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""1Password deduplication script - removes duplicate entries by username."""

import json
import subprocess
import sys
from collections import defaultdict


def run_op(args: list[str]) -> tuple[bool, str]:
    """Execute op CLI command, return (success, output)."""
    try:
        result = subprocess.run(
            ["op", *args], capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            return False, result.stderr.strip() or "Unknown error"
        return True, result.stdout
    except FileNotFoundError:
        return False, "op CLI not installed"
    except subprocess.TimeoutExpired:
        return False, "Timed out - run `op signin` to authenticate"


def get_all_items() -> list[dict]:
    """Get all login items from 1Password."""
    success, output = run_op(
        ["item", "list", "--categories", "Login", "--format", "json"]
    )
    if not success:
        print(f"Error listing items: {output}", file=sys.stderr)
        return []
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        print("Failed to parse 1Password response", file=sys.stderr)
        return []


def get_item_details(item_id: str) -> dict | None:
    """Get full item details by ID."""
    success, output = run_op(["item", "get", item_id, "--format", "json"])
    if not success:
        return None
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return None


def extract_username(item: dict) -> str | None:
    """Extract username from item details."""
    for field in item.get("fields", []):
        fid = field.get("id", "")
        purpose = field.get("purpose", "")
        if purpose == "USERNAME" or fid == "username":
            return field.get("value")
    return None


def delete_item(item_id: str) -> bool:
    """Delete an item from 1Password."""
    success, output = run_op(["item", "delete", item_id])
    if not success:
        print(f"  Failed to delete: {output}", file=sys.stderr)
        return False
    return True


def main():
    print("1Password Deduplication Tool")
    print("=" * 40)
    print()

    # Get all items
    print("Fetching all login items...")
    items = get_all_items()
    if not items:
        print("No items found or error occurred.")
        return

    print(f"Found {len(items)} login items. Analyzing...")
    print()

    # Group items by username
    by_username: dict[str, list[dict]] = defaultdict(list)

    for item in items:
        details = get_item_details(item["id"])
        if not details:
            continue
        username = extract_username(details)
        if username:
            by_username[username].append(
                {
                    "id": item["id"],
                    "title": item.get("title", "Untitled"),
                    "vault": item.get("vault", {}).get("name", "Unknown"),
                    "updated_at": item.get("updated_at", ""),
                }
            )

    # Find duplicates
    duplicates = {u: items for u, items in by_username.items() if len(items) > 1}

    if not duplicates:
        print("No duplicates found!")
        return

    print(f"Found {len(duplicates)} usernames with duplicates:")
    print()

    total_to_delete = 0
    deletion_plan: list[tuple[str, list[dict]]] = []

    for username, items in sorted(duplicates.items()):
        # Sort by updated_at descending, keep the most recent
        items_sorted = sorted(items, key=lambda x: x["updated_at"], reverse=True)
        keep = items_sorted[0]
        to_delete = items_sorted[1:]

        print(f"Username: {username}")
        print(f"  KEEP: {keep['title']} (vault: {keep['vault']})")
        for item in to_delete:
            print(f"  DELETE: {item['title']} (vault: {item['vault']})")
        print()

        deletion_plan.append((username, to_delete))
        total_to_delete += len(to_delete)

    print(f"Total items to delete: {total_to_delete}")
    print()

    # Confirm before deletion
    confirm = input("Proceed with deletion? (type 'yes' to confirm): ")
    if confirm.lower() != "yes":
        print("Aborted.")
        return

    print()
    print("Deleting duplicates...")

    deleted = 0
    failed = 0
    for _username, items in deletion_plan:
        for item in items:
            print(f"  Deleting: {item['title']}...", end=" ")
            if delete_item(item["id"]):
                print("OK")
                deleted += 1
            else:
                print("FAILED")
                failed += 1

    print()
    print(f"Done! Deleted {deleted} items, {failed} failures.")


if __name__ == "__main__":
    main()
