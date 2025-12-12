#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Recursively set milestone on all sub-issues of issues in a given milestone.

For each issue in the source milestone, traverses all sub-issues recursively
and ensures they have the correct milestone set (matching the root issue's milestone).

Usage:
    uv run set_milestone_recursive.py <milestone_url> [--dry-run]

Examples:
    uv run set_milestone_recursive.py https://github.com/org/repo/milestone/26 --dry-run
    uv run set_milestone_recursive.py https://github.com/org/repo/milestone/26
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


def get_milestone_info(owner: str, repo: str, milestone_number: int) -> dict:
    """Get milestone info including title."""
    return run_gh_json([
        "api", f"repos/{owner}/{repo}/milestones/{milestone_number}"
    ])


def get_milestone_issues(owner: str, repo: str, milestone_title: str) -> list[dict]:
    """Get all issues in a milestone."""
    issues = run_gh_json([
        "issue", "list",
        "--repo", f"{owner}/{repo}",
        "--milestone", milestone_title,
        "--state", "all",
        "--limit", "500",
        "--json", "number,title,url"
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
              milestone {{
                title
                number
              }}
            }}
          }}
        }}
      }}
    }}
    """
    result = run_graphql(query)
    return result["data"]["repository"]["issue"]["subIssues"]["nodes"]


def get_milestone_by_title(owner: str, repo: str, title: str) -> dict | None:
    """Get a milestone by title in a specific repo."""
    milestones = run_gh_json([
        "api", f"repos/{owner}/{repo}/milestones?state=all&per_page=100"
    ])
    for m in milestones:
        if m["title"] == title:
            return m
    return None


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


def process_subissues_recursive(
    owner: str,
    repo: str,
    issue_number: int,
    target_milestone_title: str,
    dry_run: bool,
    depth: int = 0,
    stats: dict = None
) -> dict:
    """Recursively process all sub-issues and set their milestone."""
    if stats is None:
        stats = {"checked": 0, "updated": 0, "skipped": 0, "failed": 0, "missing_milestone": 0}

    indent = "  " * depth
    subissues = get_subissues(owner, repo, issue_number)

    for si in subissues:
        si_owner = si["repository"]["owner"]["login"]
        si_repo = si["repository"]["name"]
        si_number = si["number"]
        si_title = si["title"]
        si_repo_full = si["repository"]["nameWithOwner"]
        current_milestone = si.get("milestone")
        current_milestone_title = current_milestone["title"] if current_milestone else None

        stats["checked"] += 1

        # Check if milestone needs to be set/updated
        if current_milestone_title == target_milestone_title:
            print(f"{indent}✓ {si_repo_full}#{si_number}: {si_title[:50]}... (milestone already set)")
            stats["skipped"] += 1
        else:
            # Check if target milestone exists in the sub-issue's repo
            target_milestone = get_milestone_by_title(si_owner, si_repo, target_milestone_title)

            if not target_milestone:
                print(f"{indent}⚠ {si_repo_full}#{si_number}: {si_title[:50]}... (milestone '{target_milestone_title}' not found in repo)")
                stats["missing_milestone"] += 1
            elif dry_run:
                current_str = f"'{current_milestone_title}'" if current_milestone_title else "none"
                print(f"{indent}→ {si_repo_full}#{si_number}: {si_title[:50]}... (would change {current_str} → '{target_milestone_title}')")
                stats["updated"] += 1
            else:
                success = set_issue_milestone(si_owner, si_repo, si_number, target_milestone_title)
                if success:
                    current_str = f"'{current_milestone_title}'" if current_milestone_title else "none"
                    print(f"{indent}✓ {si_repo_full}#{si_number}: {si_title[:50]}... (changed {current_str} → '{target_milestone_title}')")
                    stats["updated"] += 1
                else:
                    print(f"{indent}✗ {si_repo_full}#{si_number}: {si_title[:50]}... (FAILED to update)")
                    stats["failed"] += 1

        # Recursively process sub-issues of this sub-issue
        process_subissues_recursive(
            si_owner, si_repo, si_number,
            target_milestone_title, dry_run,
            depth + 1, stats
        )

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Recursively set milestone on all sub-issues of issues in a milestone."
    )
    parser.add_argument("milestone_url", help="Source milestone URL")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit number of root issues to process (0 = all)",
    )

    args = parser.parse_args()

    # Parse milestone URL
    owner, repo, milestone_number = parse_milestone_url(args.milestone_url)
    print(f"Source milestone: {owner}/{repo}/milestone/{milestone_number}")

    # Get milestone info
    milestone_info = get_milestone_info(owner, repo, milestone_number)
    milestone_title = milestone_info["title"]
    print(f"Milestone title: {milestone_title}")

    if args.dry_run:
        print("\n[DRY RUN MODE - No changes will be made]\n")

    # Get all issues in the milestone
    issues = get_milestone_issues(owner, repo, milestone_title)

    if not issues:
        print("No issues found in milestone.")
        return 0

    print(f"Found {len(issues)} root issues in milestone\n")

    if args.limit > 0:
        issues = issues[:args.limit]
        print(f"Limited to {args.limit} issue(s)\n")

    total_stats = {"checked": 0, "updated": 0, "skipped": 0, "failed": 0, "missing_milestone": 0}

    for issue in issues:
        print(f"{'='*70}")
        print(f"Processing #{issue['number']}: {issue['title']}")
        print(f"{'='*70}")

        stats = process_subissues_recursive(
            owner, repo, issue["number"],
            milestone_title, args.dry_run
        )

        # Aggregate stats
        for key in total_stats:
            total_stats[key] += stats[key]

        if stats["checked"] == 0:
            print("  (no sub-issues)")
        print()

    # Print summary
    print(f"{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Total sub-issues checked: {total_stats['checked']}")
    print(f"  - Already correct:      {total_stats['skipped']}")
    print(f"  - {'Would update' if args.dry_run else 'Updated'}:          {total_stats['updated']}")
    print(f"  - Missing milestone:    {total_stats['missing_milestone']}")
    if not args.dry_run:
        print(f"  - Failed:               {total_stats['failed']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
