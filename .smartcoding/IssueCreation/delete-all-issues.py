import subprocess
import json
import re

# === CONFIG ===
# Repository will be auto-detected from current directory
# For forked repositories, this will use the fork (not upstream)
DRY_RUN = False  # Set to True to preview without deleting

# Cached repo info
_cached_repo = None

def get_repo_from_git_remote():
    """Parse owner/repo from git remote URL (origin).
    
    This gets the actual repository from git config, not from gh CLI
    which may resolve to upstream for forks.
    """
    cmd = ["git", "remote", "get-url", "origin"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None, None
    
    url = result.stdout.strip()
    
    # Parse various URL formats:
    # https://github.com/owner/repo.git
    # git@github.com:owner/repo.git
    # https://github.com/owner/repo
    
    https_match = re.search(r'github\.com[/:]([^/]+)/([^/.]+)(?:\.git)?$', url)
    if https_match:
        return https_match.group(1), https_match.group(2)
    
    return None, None

def get_current_repo():
    """Get the current repository from git remote URL.
    
    Uses git remote URL to ensure we get the actual repository we're working in,
    not the upstream parent (which gh CLI may return for forks).
    """
    global _cached_repo
    
    if _cached_repo:
        return _cached_repo
    
    # Get from git remote URL (most reliable for forks)
    owner, name = get_repo_from_git_remote()
    
    if not owner or not name:
        print(f"Error: Could not detect repository from git remote.")
        return None
    
    _cached_repo = f"{owner}/{name}"
    
    # Check if this is a fork and log info
    cmd = ["gh", "api", f"repos/{owner}/{name}", "--jq", ".fork,.parent.full_name"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')
        if len(lines) >= 1 and lines[0] == 'true':
            parent_name = lines[1] if len(lines) > 1 else "unknown"
            print(f"  Note: This is a fork of {parent_name}")
            print(f"  Issues will be deleted from this fork: {_cached_repo}")
    
    return _cached_repo

def get_all_issues(repo):
    """Get all open and closed issues from the repository."""
    issues = []
    
    # Get open issues
    cmd = ["gh", "issue", "list", "--repo", repo, "--state", "all", "--json", "number,title,state", "--limit", "1000"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error fetching issues: {result.stderr}")
        return []
    
    issues = json.loads(result.stdout)
    return issues

def delete_issue(issue_number, repo):
    """Delete a single issue."""
    if DRY_RUN:
        print(f"  DRY RUN: Would delete issue #{issue_number}")
        return True
    
    cmd = ["gh", "issue", "delete", str(issue_number), "--repo", repo, "--yes"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"  Error deleting issue #{issue_number}: {result.stderr.strip()}")
        return False
    else:
        print(f"  ✓ Deleted issue #{issue_number}")
        return True

def main():
    # Detect current repository
    print("Detecting repository...")
    repo = get_current_repo()
    
    if not repo:
        print("Error: Could not detect repository.")
        return
    
    print()
    print("=" * 60)
    print("GitHub Issue Deleter")
    print(f"Repository: {repo}")
    print(f"Mode: {'DRY RUN' if DRY_RUN else '⚠️  LIVE - WILL DELETE ISSUES'}")
    print("=" * 60)
    print()
    
    # Get all issues
    print("Fetching all issues...")
    issues = get_all_issues(repo)
    
    if not issues:
        print("No issues found.")
        return
    
    print(f"Found {len(issues)} issues")
    print()
    
    # Show issues to be deleted
    print("Issues that will be deleted:")
    for issue in issues[:10]:  # Show first 10
        print(f"  #{issue['number']}: {issue['title']} ({issue['state']})")
    if len(issues) > 10:
        print(f"  ... and {len(issues) - 10} more")
    print()
    
    # Confirm before proceeding
    if not DRY_RUN:
        print("⚠️  WARNING: This action is IRREVERSIBLE!")
        print(f"⚠️  This will permanently delete ALL {len(issues)} issues from {repo}!")
        print()
        confirm = input("Type 'DELETE ALL ISSUES' to confirm: ").strip()
        if confirm != "DELETE ALL ISSUES":
            print("Aborted.")
            return
        print()
    
    # Delete each issue
    print("Deleting issues...")
    deleted = 0
    failed = 0
    
    for issue in issues:
        print(f"Issue #{issue['number']}: {issue['title'][:50]}...")
        if delete_issue(issue['number'], repo):
            deleted += 1
        else:
            failed += 1
    
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"{'Would delete' if DRY_RUN else 'Deleted'}: {deleted}")
    if failed:
        print(f"Failed: {failed}")
    
    if DRY_RUN:
        print()
        print("This was a DRY RUN. Set DRY_RUN = False to actually delete issues.")

if __name__ == "__main__":
    main()
