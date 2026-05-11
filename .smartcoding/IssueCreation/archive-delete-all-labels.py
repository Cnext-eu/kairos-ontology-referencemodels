import subprocess
import json

# === CONFIG ===
# Auto-detect current repository or specify manually
REPO = "Cnext-eu/smartcoding-kairos-template"  # Current template repository
DRY_RUN = False  # Set to True to preview without deleting

def get_current_repo():
    """Get the current repository from git config."""
    cmd = ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    return REPO

def get_all_labels(repo):
    """Get all labels from the repository."""
    cmd = ["gh", "label", "list", "--repo", repo, "--json", "name", "--limit", "1000"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error fetching labels: {result.stderr}")
        return []
    
    labels = json.loads(result.stdout)
    return [label["name"] for label in labels]

def delete_label(label_name, repo):
    """Delete a single label."""
    if DRY_RUN:
        print(f"  DRY RUN: Would delete label '{label_name}'")
        return True
    
    cmd = ["gh", "label", "delete", label_name, "--repo", repo, "--yes"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"  Error deleting label '{label_name}': {result.stderr.strip()}")
        return False
    else:
        print(f"  ✓ Deleted label '{label_name}'")
        return True

def main():
    # Detect current repository
    repo = get_current_repo()
    
    print("=" * 60)
    print("GitHub Label Deleter")
    print(f"Repository: {repo}")
    print(f"Mode: {'DRY RUN' if DRY_RUN else '⚠️  LIVE - WILL DELETE LABELS'}")
    print("=" * 60)
    print()
    
    # Get all labels
    print("Fetching all labels...")
    labels = get_all_labels(repo)
    
    if not labels:
        print("No labels found.")
        return
    
    print(f"Found {len(labels)} labels")
    print()
    
    # Show labels to be deleted
    print("Labels that will be deleted:")
    for label in labels[:20]:  # Show first 20
        print(f"  - {label}")
    if len(labels) > 20:
        print(f"  ... and {len(labels) - 20} more")
    print()
    
    # Confirm before proceeding
    if not DRY_RUN:
        print("⚠️  WARNING: This action is IRREVERSIBLE!")
        print(f"⚠️  This will permanently delete ALL {len(labels)} labels from {repo}!")
        print("⚠️  This includes default labels like 'bug', 'enhancement', etc.")
        print()
        confirm = input("Type 'DELETE ALL LABELS' to confirm: ").strip()
        if confirm != "DELETE ALL LABELS":
            print("Aborted.")
            return
        print()
    
    # Delete each label
    print("Deleting labels...")
    deleted = 0
    failed = 0
    
    for label in labels:
        if delete_label(label, repo):
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
        print("This was a DRY RUN. Set DRY_RUN = False to actually delete labels.")

if __name__ == "__main__":
    main()
