#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Convert issues with "Division" label from a milestone into milestones in the same repo.

For each issue with the "Division" label in the source milestone:
1. Create a new milestone with the issue title as name
2. Set the milestone due date to 2025-12-31
3. Set the description from the issue body

Usage:
    uv run division_issues_to_milestones.py <milestone_url> [--dry-run]

Examples:
    uv run division_issues_to_milestones.py https://github.com/zama-ai/planning-blockchain/milestone/26 --dry-run
    uv run division_issues_to_milestones.py https://github.com/zama-ai/planning-blockchain/milestone/26
"""

import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed


def parse_milestone_url(url: str) -> tuple[str, str, int]:
    """Parse a GitHub milestone URL and return (owner, repo, milestone_number)."""
    pattern = r"https://github\.com/([^/]+)/([^/]+)/milestone/(\d+)"
    match = re.match(pattern, url)
    if not match:
        raise ValueError(f"Invalid GitHub milestone URL: {url}")
    return match.group(1), match.group(2), int(match.group(3))


def run_gh_command(args: list[str], check: bool = True) -> str:
    """Run a gh CLI command and return output."""
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"gh command failed: {result.stderr}")
    return result.stdout.strip()


def run_gh_json(args: list[str]) -> dict | list:
    """Run a gh CLI command and return parsed JSON output."""
    output = run_gh_command(args)
    return json.loads(output) if output else {}


def get_milestone_info(owner: str, repo: str, milestone_number: int) -> dict:
    """Get milestone info including title."""
    return run_gh_json([
        "api", f"repos/{owner}/{repo}/milestones/{milestone_number}"
    ])


def get_milestone_issues_with_label(owner: str, repo: str, milestone_title: str, label: str) -> list[dict]:
    """Get all issues in a milestone with a specific label."""
    issues = run_gh_json([
        "issue", "list",
        "--repo", f"{owner}/{repo}",
        "--milestone", milestone_title,
        "--label", label,
        "--state", "all",
        "--limit", "500",
        "--json", "number,title,body,url,labels"
    ])
    return issues


def get_existing_milestones(owner: str, repo: str) -> dict[str, dict]:
    """Get all existing milestones as a dict by title."""
    milestones = run_gh_json([
        "api", f"repos/{owner}/{repo}/milestones?state=all&per_page=100"
    ])
    return {m["title"]: m for m in milestones}


def create_milestone(owner: str, repo: str, title: str, description: str, due_date: str) -> dict | None:
    """Create a new milestone. Returns the milestone or None if it already exists."""
    data = {
        "title": title,
        "description": description or "",
        "due_on": f"{due_date}T23:59:59Z"
    }
    result = subprocess.run(
        ["gh", "api", f"repos/{owner}/{repo}/milestones", "-X", "POST",
         "-f", f"title={data['title']}",
         "-f", f"description={data['description']}",
         "-f", f"due_on={data['due_on']}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        if "already_exists" in result.stderr or "Validation Failed" in result.stderr:
            return None  # Already exists
        raise RuntimeError(f"Failed to create milestone: {result.stderr}")
    return json.loads(result.stdout)


def process_issue(issue: dict, owner: str, repo: str, existing_milestones: dict[str, dict], due_date: str, dry_run: bool) -> tuple[str, str]:
    """Process a single issue. Returns (status, message)."""
    issue_number = issue["number"]
    issue_title = issue["title"]
    issue_body = issue.get("body", "") or ""

    # Check if milestone already exists
    if issue_title in existing_milestones:
        return "exists", f"#{issue_number}: {issue_title[:50]}... (milestone already exists)"

    if dry_run:
        return "would_create", f"#{issue_number}: {issue_title[:50]}... (would create milestone)"

    # Create the milestone
    try:
        milestone = create_milestone(owner, repo, issue_title, issue_body, due_date)
        if milestone:
            return "created", f"#{issue_number}: {issue_title[:50]}... (created milestone #{milestone['number']})"
        else:
            return "exists", f"#{issue_number}: {issue_title[:50]}... (milestone already exists)"
    except Exception as e:
        return "failed", f"#{issue_number}: {issue_title[:50]}... (FAILED: {e})"


def main():
    parser = argparse.ArgumentParser(
        description="Convert Division-labeled issues from a milestone into milestones."
    )
    parser.add_argument("milestone_url", help="Source milestone URL")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--due-date",
        default="2025-12-31",
        help="Due date for new milestones (YYYY-MM-DD format, default: 2025-12-31)",
    )
    parser.add_argument(
        "--label",
        default="Division",
        help="Label to filter issues by (default: Division)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Number of parallel workers (default: 10)",
    )

    args = parser.parse_args()

    # Parse milestone URL
    owner, repo, milestone_number = parse_milestone_url(args.milestone_url)
    print(f"Repository: {owner}/{repo}")
    print(f"Milestone number: {milestone_number}")
    print(f"Label filter: {args.label}")
    print(f"Due date: {args.due_date}")

    if args.dry_run:
        print("\n[DRY RUN MODE - No changes will be made]\n")

    # Get milestone info
    milestone_info = get_milestone_info(owner, repo, milestone_number)
    milestone_title = milestone_info["title"]
    print(f"Milestone title: {milestone_title}")

    # Get existing milestones for checking duplicates
    print("Fetching existing milestones...")
    existing_milestones = get_existing_milestones(owner, repo)
    print(f"Found {len(existing_milestones)} existing milestones")

    # Get issues with Division label
    print(f"\nFetching issues with '{args.label}' label...")
    issues = get_milestone_issues_with_label(owner, repo, milestone_title, args.label)

    if not issues:
        print(f"No issues found with label '{args.label}' in milestone '{milestone_title}'")
        return 0

    print(f"Found {len(issues)} issues with '{args.label}' label\n")

    # Process issues in parallel
    stats = {"created": 0, "would_create": 0, "exists": 0, "failed": 0}

    print("Processing issues...")
    print("=" * 70)

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_issue = {
            executor.submit(
                process_issue, issue, owner, repo, existing_milestones, args.due_date, args.dry_run
            ): issue
            for issue in issues
        }

        results = []
        for future in as_completed(future_to_issue):
            issue = future_to_issue[future]
            try:
                status, message = future.result()
                results.append((issue["number"], status, message))
            except Exception as e:
                results.append((issue["number"], "failed", f"#{issue['number']}: ERROR - {e}"))

    # Sort by issue number and print
    results.sort(key=lambda x: -x[0])

    for _, status, message in results:
        stats[status] = stats.get(status, 0) + 1
        icon = {"created": "✓", "would_create": "→", "exists": "○", "failed": "✗"}.get(status, "?")
        print(f"  {icon} {message}")

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total issues processed: {len(issues)}")
    if args.dry_run:
        print(f"  - Would create:       {stats.get('would_create', 0)}")
    else:
        print(f"  - Created:            {stats.get('created', 0)}")
    print(f"  - Already exist:      {stats.get('exists', 0)}")
    print(f"  - Failed:             {stats.get('failed', 0)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
