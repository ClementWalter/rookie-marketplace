#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Recursively set milestone on all sub-issues for ALL milestones in a repository.

For each milestone in the repo, and for each issue in that milestone,
traverses all sub-issues recursively and ensures they have the correct
milestone set (matching the root issue's milestone).

Uses parallel processing for speed.

Usage:
    uv run set_milestone_recursive_all.py <repo> [--dry-run] [--state STATE] [--workers N]

Examples:
    uv run set_milestone_recursive_all.py zama-ai/planning-blockchain --dry-run
    uv run set_milestone_recursive_all.py zama-ai/planning-blockchain --state open
    uv run set_milestone_recursive_all.py zama-ai/planning-blockchain --workers 20
"""

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class Stats:
    checked: int = 0
    updated: int = 0
    skipped: int = 0
    failed: int = 0
    missing_milestone: int = 0
    lock: Lock = field(default_factory=Lock)

    def add(self, other: "Stats"):
        with self.lock:
            self.checked += other.checked
            self.updated += other.updated
            self.skipped += other.skipped
            self.failed += other.failed
            self.missing_milestone += other.missing_milestone


# Cache for milestone lookups (repo -> title -> milestone)
_milestone_cache: dict[str, dict[str, dict | None]] = {}
_milestone_cache_lock = Lock()

# Print lock for clean output
_print_lock = Lock()


def safe_print(*args, **kwargs):
    with _print_lock:
        print(*args, **kwargs)


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


def get_all_milestones(owner: str, repo: str, state: str = "all") -> list[dict]:
    """Get all milestones from a repository."""
    milestones = run_gh_json([
        "api", f"repos/{owner}/{repo}/milestones?state={state}&per_page=100"
    ])
    return milestones


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


def get_milestone_by_title_cached(owner: str, repo: str, title: str) -> dict | None:
    """Get a milestone by title in a specific repo (with caching)."""
    repo_key = f"{owner}/{repo}"

    with _milestone_cache_lock:
        if repo_key in _milestone_cache and title in _milestone_cache[repo_key]:
            return _milestone_cache[repo_key][title]

    # Fetch all milestones for this repo
    milestones = run_gh_json([
        "api", f"repos/{owner}/{repo}/milestones?state=all&per_page=100"
    ])

    with _milestone_cache_lock:
        if repo_key not in _milestone_cache:
            _milestone_cache[repo_key] = {}
        for m in milestones:
            _milestone_cache[repo_key][m["title"]] = m

        return _milestone_cache[repo_key].get(title)


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


@dataclass
class SubIssueTask:
    """A task to process a sub-issue."""
    owner: str
    repo: str
    issue_number: int
    issue_title: str
    repo_full: str
    current_milestone_title: str | None
    target_milestone_title: str
    depth: int


def collect_subissues_recursive(
    owner: str,
    repo: str,
    issue_number: int,
    target_milestone_title: str,
    depth: int = 0
) -> list[SubIssueTask]:
    """Collect all sub-issues recursively into a flat list of tasks."""
    tasks = []
    subissues = get_subissues(owner, repo, issue_number)

    for si in subissues:
        si_owner = si["repository"]["owner"]["login"]
        si_repo = si["repository"]["name"]
        si_number = si["number"]
        si_title = si["title"]
        si_repo_full = si["repository"]["nameWithOwner"]
        current_milestone = si.get("milestone")
        current_milestone_title = current_milestone["title"] if current_milestone else None

        tasks.append(SubIssueTask(
            owner=si_owner,
            repo=si_repo,
            issue_number=si_number,
            issue_title=si_title,
            repo_full=si_repo_full,
            current_milestone_title=current_milestone_title,
            target_milestone_title=target_milestone_title,
            depth=depth
        ))

        # Recursively collect sub-issues
        tasks.extend(collect_subissues_recursive(
            si_owner, si_repo, si_number,
            target_milestone_title, depth + 1
        ))

    return tasks


def process_subissue_task(task: SubIssueTask, dry_run: bool) -> tuple[str, Stats]:
    """Process a single sub-issue task. Returns (message, stats)."""
    stats = Stats()
    stats.checked = 1
    indent = "    " + "  " * task.depth

    # Check if milestone needs to be set/updated
    if task.current_milestone_title == task.target_milestone_title:
        msg = f"{indent}✓ {task.repo_full}#{task.issue_number}: {task.issue_title[:40]}... (ok)"
        stats.skipped = 1
        return msg, stats

    # Check if target milestone exists in the sub-issue's repo
    target_milestone = get_milestone_by_title_cached(task.owner, task.repo, task.target_milestone_title)

    if not target_milestone:
        msg = f"{indent}⚠ {task.repo_full}#{task.issue_number}: {task.issue_title[:40]}... (milestone not in repo)"
        stats.missing_milestone = 1
        return msg, stats

    current_str = f"'{task.current_milestone_title}'" if task.current_milestone_title else "none"

    if dry_run:
        msg = f"{indent}→ {task.repo_full}#{task.issue_number}: {task.issue_title[:40]}... ({current_str} → '{task.target_milestone_title}')"
        stats.updated = 1
        return msg, stats

    success = set_issue_milestone(task.owner, task.repo, task.issue_number, task.target_milestone_title)
    if success:
        msg = f"{indent}✓ {task.repo_full}#{task.issue_number}: {task.issue_title[:40]}... ({current_str} → '{task.target_milestone_title}')"
        stats.updated = 1
    else:
        msg = f"{indent}✗ {task.repo_full}#{task.issue_number}: {task.issue_title[:40]}... (FAILED)"
        stats.failed = 1

    return msg, stats


def process_milestone(owner: str, repo: str, milestone: dict, dry_run: bool, max_workers: int) -> Stats:
    """Process all issues in a milestone and their sub-issues."""
    milestone_title = milestone["title"]
    milestone_number = milestone["number"]

    safe_print(f"\n{'='*70}")
    safe_print(f"MILESTONE: {milestone_title} (#{milestone_number})")
    safe_print(f"{'='*70}")

    issues = get_milestone_issues(owner, repo, milestone_title)

    if not issues:
        safe_print("  No issues in this milestone")
        return Stats()

    safe_print(f"  {len(issues)} root issues, collecting sub-issues...")

    # Collect all sub-issue tasks first (this part uses GraphQL calls)
    all_tasks: list[tuple[dict, list[SubIssueTask]]] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_issue = {
            executor.submit(
                collect_subissues_recursive,
                owner, repo, issue["number"], milestone_title
            ): issue
            for issue in issues
        }

        for future in as_completed(future_to_issue):
            issue = future_to_issue[future]
            try:
                tasks = future.result()
                all_tasks.append((issue, tasks))
            except Exception as e:
                safe_print(f"  ERROR collecting sub-issues for #{issue['number']}: {e}")

    # Sort by issue number for consistent output
    all_tasks.sort(key=lambda x: x[0]["number"], reverse=True)

    total_subissues = sum(len(tasks) for _, tasks in all_tasks)
    safe_print(f"  Found {total_subissues} sub-issues total, processing...\n")

    milestone_stats = Stats()

    # Process each root issue's sub-issues
    for issue, tasks in all_tasks:
        safe_print(f"  #{issue['number']}: {issue['title'][:55]}...")

        if not tasks:
            continue

        # Process sub-issues in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_task = {
                executor.submit(process_subissue_task, task, dry_run): task
                for task in tasks
            }

            # Collect results and print in order
            results = []
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    msg, stats = future.result()
                    results.append((task.depth, task.issue_number, msg, stats))
                except Exception as e:
                    safe_print(f"    ERROR processing {task.repo_full}#{task.issue_number}: {e}")

            # Sort by depth then issue number for cleaner output
            results.sort(key=lambda x: (x[0], -x[1]))

            for _, _, msg, stats in results:
                safe_print(msg)
                milestone_stats.add(stats)

    return milestone_stats


def main():
    parser = argparse.ArgumentParser(
        description="Recursively set milestone on all sub-issues for ALL milestones in a repo."
    )
    parser.add_argument("repo", help="Repository (format: owner/repo)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--state",
        choices=["open", "closed", "all"],
        default="all",
        help="Filter milestones by state (default: all)",
    )
    parser.add_argument(
        "--milestone",
        type=str,
        help="Process only a specific milestone by title (optional)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Number of parallel workers (default: 10)",
    )

    args = parser.parse_args()

    # Parse repo
    if "/" not in args.repo:
        print(f"ERROR: Invalid repo format '{args.repo}'. Expected 'owner/repo'")
        return 1

    owner, repo = args.repo.split("/", 1)
    print(f"Repository: {owner}/{repo}")
    print(f"Workers: {args.workers}")

    if args.dry_run:
        print("\n[DRY RUN MODE - No changes will be made]")

    # Get all milestones
    milestones = get_all_milestones(owner, repo, args.state)

    if not milestones:
        print(f"No milestones found (state={args.state})")
        return 0

    # Filter by specific milestone if requested
    if args.milestone:
        milestones = [m for m in milestones if m["title"] == args.milestone]
        if not milestones:
            print(f"Milestone '{args.milestone}' not found")
            return 1

    print(f"Found {len(milestones)} milestone(s) to process")

    total_stats = Stats()

    for milestone in milestones:
        stats = process_milestone(owner, repo, milestone, args.dry_run, args.workers)
        total_stats.add(stats)

    # Print summary
    print(f"\n{'='*70}")
    print("FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"Milestones processed:     {len(milestones)}")
    print(f"Total sub-issues checked: {total_stats.checked}")
    print(f"  - Already correct:      {total_stats.skipped}")
    print(f"  - {'Would update' if args.dry_run else 'Updated'}:          {total_stats.updated}")
    print(f"  - Missing milestone:    {total_stats.missing_milestone}")
    if not args.dry_run:
        print(f"  - Failed:               {total_stats.failed}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
