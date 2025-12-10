#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Move all sub-issues from one parent issue to another and optionally add labels.

Usage:
    uv run move_subissues.py <source_issue_url> <target_issue_url> [--label LABEL]...

Examples:
    uv run move_subissues.py https://github.com/org/repo/issues/123 https://github.com/org/other-repo/issues/456
    uv run move_subissues.py https://github.com/org/repo/issues/123 https://github.com/org/other-repo/issues/456 --label scalability
    uv run move_subissues.py https://github.com/org/repo/issues/123 https://github.com/org/other-repo/issues/456 --label scalability --label priority
"""

import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed


def parse_issue_url(url: str) -> tuple[str, str, int]:
    """Parse a GitHub issue URL and return (owner, repo, issue_number)."""
    pattern = r"https://github\.com/([^/]+)/([^/]+)/issues/(\d+)"
    match = re.match(pattern, url)
    if not match:
        raise ValueError(f"Invalid GitHub issue URL: {url}")
    return match.group(1), match.group(2), int(match.group(3))


def run_gh_command(args: list[str]) -> dict:
    """Run a gh CLI command and return parsed JSON output."""
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh command failed: {result.stderr}")
    return json.loads(result.stdout) if result.stdout.strip() else {}


def run_graphql(query: str) -> dict:
    """Run a GraphQL query using gh api."""
    result = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"GraphQL query failed: {result.stderr}")
    return json.loads(result.stdout)


def get_issue_node_id(owner: str, repo: str, number: int) -> str:
    """Get the node ID of an issue."""
    query = f"""
    {{
      repository(owner: "{owner}", name: "{repo}") {{
        issue(number: {number}) {{
          id
          title
        }}
      }}
    }}
    """
    result = run_graphql(query)
    issue = result["data"]["repository"]["issue"]
    print(f"  Found: {issue['title']}")
    return issue["id"]


def get_subissues(owner: str, repo: str, number: int) -> list[dict]:
    """Get all sub-issues of a parent issue."""
    query = f"""
    {{
      repository(owner: "{owner}", name: "{repo}") {{
        issue(number: {number}) {{
          subIssues(first: 100) {{
            nodes {{
              id
              number
              title
              repository {{
                nameWithOwner
              }}
            }}
          }}
        }}
      }}
    }}
    """
    result = run_graphql(query)
    return result["data"]["repository"]["issue"]["subIssues"]["nodes"]


def move_subissue(source_id: str, target_id: str, subissue: dict) -> tuple[bool, str]:
    """Move a single sub-issue from source to target parent."""
    subissue_id = subissue["id"]
    repo = subissue["repository"]["nameWithOwner"]
    number = subissue["number"]
    title = subissue["title"]

    try:
        # Remove from source
        remove_query = f"""
        mutation {{
          removeSubIssue(input: {{
            issueId: "{source_id}",
            subIssueId: "{subissue_id}"
          }}) {{
            issue {{ id }}
          }}
        }}
        """
        run_graphql(remove_query)

        # Add to target
        add_query = f"""
        mutation {{
          addSubIssue(input: {{
            issueId: "{target_id}",
            subIssueId: "{subissue_id}"
          }}) {{
            issue {{ id }}
          }}
        }}
        """
        run_graphql(add_query)
        return True, f"Moved {repo}#{number}: {title}"
    except Exception as e:
        return False, f"Failed to move {repo}#{number}: {e}"


def add_label_to_issue(repo: str, number: int, label: str) -> tuple[bool, str]:
    """Add a label to an issue, creating the label if it doesn't exist."""
    try:
        result = subprocess.run(
            ["gh", "issue", "edit", str(number), "--repo", repo, "--add-label", label],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            if "not found" in result.stderr:
                # Create the label
                subprocess.run(
                    [
                        "gh",
                        "label",
                        "create",
                        label,
                        "--repo",
                        repo,
                        "--description",
                        f"{label.capitalize()}-related issues",
                        "--color",
                        "0E8A16",
                    ],
                    capture_output=True,
                    text=True,
                )
                # Retry adding the label
                subprocess.run(
                    [
                        "gh",
                        "issue",
                        "edit",
                        str(number),
                        "--repo",
                        repo,
                        "--add-label",
                        label,
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
        return True, f"Added label '{label}' to {repo}#{number}"
    except Exception as e:
        return False, f"Failed to add label to {repo}#{number}: {e}"


def main():
    parser = argparse.ArgumentParser(
        description="Move sub-issues from one parent issue to another and optionally add labels."
    )
    parser.add_argument("source_url", help="Source parent issue URL")
    parser.add_argument("target_url", help="Target parent issue URL")
    parser.add_argument(
        "--label",
        "-l",
        action="append",
        dest="labels",
        default=[],
        help="Label(s) to add to all sub-issues (can be specified multiple times)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args()

    # Parse URLs
    source_owner, source_repo, source_number = parse_issue_url(args.source_url)
    target_owner, target_repo, target_number = parse_issue_url(args.target_url)

    print(f"Source: {source_owner}/{source_repo}#{source_number}")
    source_id = get_issue_node_id(source_owner, source_repo, source_number)

    print(f"Target: {target_owner}/{target_repo}#{target_number}")
    target_id = get_issue_node_id(target_owner, target_repo, target_number)

    # Get sub-issues
    print(f"\nFetching sub-issues from {source_owner}/{source_repo}#{source_number}...")
    subissues = get_subissues(source_owner, source_repo, source_number)

    if not subissues:
        print("No sub-issues found.")
        return 0

    print(f"Found {len(subissues)} sub-issues:")
    for si in subissues:
        print(f"  - {si['repository']['nameWithOwner']}#{si['number']}: {si['title']}")

    if args.dry_run:
        print("\n[DRY RUN] Would move the above sub-issues and add labels:", args.labels)
        return 0

    # Move sub-issues in parallel
    print(f"\nMoving {len(subissues)} sub-issues...")
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(move_subissue, source_id, target_id, si): si
            for si in subissues
        }
        for future in as_completed(futures):
            success, message = future.result()
            print(f"  {'✓' if success else '✗'} {message}")

    # Add labels if specified
    if args.labels:
        print(f"\nAdding labels {args.labels} to sub-issues...")
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for si in subissues:
                repo = si["repository"]["nameWithOwner"]
                number = si["number"]
                for label in args.labels:
                    futures.append(
                        executor.submit(add_label_to_issue, repo, number, label)
                    )

            for future in as_completed(futures):
                success, message = future.result()
                print(f"  {'✓' if success else '✗'} {message}")

    print("\nDone!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
