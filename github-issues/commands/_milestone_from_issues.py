#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Convert issues from a milestone into milestones, migrating their sub-issues.

For each issue in the source milestone:
1. Create a new milestone with the issue title as name
2. Set the milestone due date and description
3. Move all sub-issues of the original issue to use the new milestone

For issues WITHOUT sub-issues, use --target-repo to specify where the milestone should be created.
Use --route to specify prefix-based routing: issues starting with a prefix go to a specific repo.

Usage:
    uv run _milestone_from_issues.py <milestone_url> [--due-date YYYY-MM-DD] [--dry-run] [--limit N]
    uv run _milestone_from_issues.py <milestone_url> --target-repo owner/repo [--dry-run]
    uv run _milestone_from_issues.py <milestone_url> --route "[MPC]=org/mpc-repo" --route "[Gateway]=org/gateway-repo"

Examples:
    uv run _milestone_from_issues.py https://github.com/org/repo/milestone/26
    uv run _milestone_from_issues.py https://github.com/org/repo/milestone/26 --due-date 2025-12-31
    uv run _milestone_from_issues.py https://github.com/org/repo/milestone/26 --limit 1 --dry-run
    uv run _milestone_from_issues.py https://github.com/org/repo/milestone/26 --target-repo org/other-repo
    uv run _milestone_from_issues.py https://github.com/org/repo/milestone/26 \\
        --route "[MPC]=zama-ai/kms-internal" \\
        --route "[Copro]=zama-ai/fhevm-internal" \\
        --route "[Gateway]=zama-ai/fhevm-internal"
"""

import argparse
import json
import re
import subprocess
import sys


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


def get_milestone_issues(owner: str, repo: str, milestone_number: int) -> list[dict]:
    """Get all issues in a milestone."""
    # First get the milestone title
    milestone_info = run_gh_json([
        "api", f"repos/{owner}/{repo}/milestones/{milestone_number}"
    ])
    milestone_title = milestone_info["title"]
    print(f"Milestone: {milestone_title}")

    # Get all issues in the milestone (use --limit to avoid default 30 limit)
    issues = run_gh_json([
        "issue", "list",
        "--repo", f"{owner}/{repo}",
        "--milestone", milestone_title,
        "--state", "all",
        "--limit", "500",
        "--json", "number,title,body,url"
    ])
    return issues


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
              url
              repository {{
                owner {{
                  login
                }}
                name
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


def create_milestone(owner: str, repo: str, title: str, description: str, due_date: str) -> dict:
    """Create a new milestone."""
    # Use gh api to create milestone
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
        # Check if milestone already exists
        if "already_exists" in result.stderr or "Validation Failed" in result.stderr:
            print(f"  Milestone '{title}' already exists, fetching it...")
            milestones = run_gh_json([
                "api", f"repos/{owner}/{repo}/milestones",
                "--jq", f'[.[] | select(.title == "{title}")]'
            ])
            if milestones:
                return milestones[0]
        raise RuntimeError(f"Failed to create milestone: {result.stderr}")
    return json.loads(result.stdout)


def set_issue_milestone(owner: str, repo: str, issue_number: int, milestone_title: str) -> bool:
    """Set the milestone on an issue by milestone title."""
    result = subprocess.run(
        ["gh", "issue", "edit", str(issue_number),
         "--repo", f"{owner}/{repo}",
         "--milestone", milestone_title],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def find_route_target(title: str, routes: dict[str, str]) -> str | None:
    """Find the target repo for an issue based on its title prefix."""
    for prefix, target in routes.items():
        if title.startswith(prefix):
            return target
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Convert milestone issues into milestones with their sub-issues."
    )
    parser.add_argument("milestone_url", help="Source milestone URL")
    parser.add_argument(
        "--due-date",
        default="2025-12-31",
        help="Due date for new milestones (YYYY-MM-DD format, default: 2025-12-31)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit number of issues to process (0 = all)",
    )
    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Skip first N issues (for testing specific issues)",
    )
    parser.add_argument(
        "--target-repo",
        type=str,
        action="append",
        dest="target_repos",
        help="Target repo(s) for issues without sub-issues (format: owner/repo). Can be specified multiple times.",
    )
    parser.add_argument(
        "--route",
        type=str,
        action="append",
        dest="routes",
        help="Route issues by prefix to specific repos. Format: 'prefix=owner/repo'. Example: '[MPC]=zama-ai/kms-internal'",
    )

    args = parser.parse_args()

    # Parse routes into a dict
    routes: dict[str, str] = {}
    if args.routes:
        for route in args.routes:
            if "=" not in route:
                print(f"ERROR: Invalid route format '{route}'. Expected 'prefix=owner/repo'")
                return 1
            prefix, target = route.split("=", 1)
            routes[prefix] = target
        print(f"Routes configured: {routes}")

    # Parse milestone URL
    owner, repo, milestone_number = parse_milestone_url(args.milestone_url)
    print(f"Source milestone: {owner}/{repo}/milestone/{milestone_number}")

    # Get issues in milestone
    issues = get_milestone_issues(owner, repo, milestone_number)

    if not issues:
        print("No issues found in milestone.")
        return 0

    print(f"\nFound {len(issues)} issues in milestone:")
    for issue in issues:
        print(f"  - #{issue['number']}: {issue['title']}")

    if args.offset > 0:
        issues = issues[args.offset:]
        print(f"\nSkipped first {args.offset} issue(s)")

    if args.limit > 0:
        issues = issues[:args.limit]
        print(f"Limited to {args.limit} issue(s)")

    # Process each issue
    for issue in issues:
        print(f"\n{'='*60}")
        print(f"Processing issue #{issue['number']}: {issue['title']}")
        print(f"{'='*60}")

        issue_number = issue["number"]
        issue_title = issue["title"]
        issue_body = issue.get("body", "") or ""

        # Get sub-issues
        subissues = get_subissues(owner, repo, issue_number)
        print(f"  Found {len(subissues)} sub-issues")

        if subissues:
            for si in subissues:
                print(f"    - {si['repository']['nameWithOwner']}#{si['number']}: {si['title']}")

        # Group sub-issues by repository
        subissues_by_repo: dict[str, list[dict]] = {}
        for si in subissues:
            repo_key = si["repository"]["nameWithOwner"]
            if repo_key not in subissues_by_repo:
                subissues_by_repo[repo_key] = []
            subissues_by_repo[repo_key].append(si)

        # Determine target repos for milestone creation
        # If issue has sub-issues, use repos where sub-issues exist
        # If issue has no sub-issues, use --target-repo(s) if provided
        target_repos_for_milestone: list[str] = list(subissues_by_repo.keys())

        if not target_repos_for_milestone:
            # Try to find a route based on issue title prefix
            route_target = find_route_target(issue_title, routes)
            if route_target:
                target_repos_for_milestone = [route_target]
                print(f"  No sub-issues found, routing to: {route_target} (matched prefix)")
            elif args.target_repos:
                target_repos_for_milestone = args.target_repos
                print(f"  No sub-issues found, will create milestone in target repo(s): {', '.join(target_repos_for_milestone)}")
            else:
                print("  WARNING: No sub-issues, no matching route, and no --target-repo specified. Skipping milestone creation.")
                print("  Use --route 'prefix=owner/repo' or --target-repo owner/repo to specify where to create the milestone.")
                continue

        if args.dry_run:
            print(f"\n  [DRY RUN] Would create milestones named '{issue_title}' in repos:")
            for repo_key in target_repos_for_milestone:
                subissue_count = len(subissues_by_repo.get(repo_key, []))
                if subissue_count:
                    print(f"    - {repo_key} ({subissue_count} sub-issues)")
                else:
                    print(f"    - {repo_key} (no sub-issues)")
            print(f"  [DRY RUN] Would set due date: {args.due_date}")
            print(f"  [DRY RUN] Would set description from issue body ({len(issue_body)} chars)")
            continue

        # Create milestone in each target repo and update sub-issues if any
        milestones_created = []
        subissues_updated = 0

        for repo_key in target_repos_for_milestone:
            si_owner, si_repo = repo_key.split("/")
            repo_subissues = subissues_by_repo.get(repo_key, [])

            # Create milestone in this repo
            print(f"\n  Creating milestone in {repo_key}: '{issue_title}'")
            try:
                milestone = create_milestone(si_owner, si_repo, issue_title, issue_body, args.due_date)
                milestone_num = milestone["number"]
                print(f"    Created milestone #{milestone_num}: {milestone['html_url']}")
                milestones_created.append(f"{repo_key}#{milestone_num}")
            except Exception as e:
                print(f"    ERROR creating milestone: {e}")
                continue

            # Update sub-issues in this repo to use new milestone (if any)
            if repo_subissues:
                milestone_title = milestone["title"]
                print(f"    Updating {len(repo_subissues)} sub-issues...")
                for si in repo_subissues:
                    si_number = si["number"]
                    success = set_issue_milestone(si_owner, si_repo, si_number, milestone_title)
                    status = "✓" if success else "✗"
                    print(f"      {status} #{si_number}: {si['title']}")
                    if success:
                        subissues_updated += 1

        print(f"\n  Summary for '{issue_title}':")
        print(f"    - Milestones created: {len(milestones_created)}")
        for m in milestones_created:
            print(f"      - {m}")
        print(f"    - Due date: {args.due_date}")
        if subissues:
            print(f"    - Sub-issues updated: {subissues_updated}/{len(subissues)}")

    print(f"\n{'='*60}")
    print("Done!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
