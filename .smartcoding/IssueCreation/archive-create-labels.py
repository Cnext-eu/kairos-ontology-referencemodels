import subprocess
import re
import sys
from pathlib import Path

# === CONFIG ===
# Accept file path from command line argument
if len(sys.argv) > 2 and sys.argv[1] == "--file":
    BACKLOG_FILE = Path(sys.argv[2])
else:
    print("Error: Please provide a file path using --file argument")
    print("Usage: python create-labels.py --file <path-to-user-stories.md>")
    sys.exit(1)
DRY_RUN = False  # True = print commands, don't execute

# Label colors by category
LABEL_COLORS = {
    # Priority labels
    "priority:critical": "B60205",  # Red
    "priority:high": "D93F0B",      # Orange
    "priority:medium": "FBCA04",    # Yellow
    "priority:low": "0E8A16",       # Green
    
    # Team labels
    "team:core": "1D76DB",          # Blue
    "team:web": "5319E7",           # Purple
    "team:platform": "006B75",      # Teal
    
    # Type labels
    "user-story": "C5DEF5",         # Light blue
    "epic": "3E4B9E",               # Dark blue (base epic label)
    
    # Default color for other labels
    "default": "EDEDED"             # Light gray
}

def get_label_color(label: str) -> str:
    """Get color for a label based on its name."""
    if label in LABEL_COLORS:
        return LABEL_COLORS[label]
    if label.startswith("priority:"):
        return LABEL_COLORS.get(label, "FBCA04")
    if label.startswith("team:"):
        return LABEL_COLORS.get(label, "1D76DB")
    return LABEL_COLORS["default"]

def extract_all_labels(content: str) -> set:
    """Extract all unique labels from the backlog file."""
    labels = set()
    
    # Find all Labels: lines (support both "Labels:" and "**Labels:**" formats)
    label_pattern = r'^\*\*Labels:\*\*\s*(.+)$|^Labels:\s*(.+)$'
    for match in re.finditer(label_pattern, content, re.MULTILINE):
        raw_labels = match.group(1) or match.group(2)
        if raw_labels:
            # Remove backticks and split by comma
            raw_labels = raw_labels.replace('`', '')
            for label in raw_labels.split(","):
                clean = label.strip()
                if clean:
                    labels.add(clean)
    
    # Find all Priority: lines (support both formats)
    priority_pattern = r'^\*\*Priority:\*\*\s*(\w+)|^Priority:\s*(\w+)'
    for match in re.finditer(priority_pattern, content, re.MULTILINE):
        priority = (match.group(1) or match.group(2)).lower()
        labels.add(f"priority:{priority}")
    
    # Find all Team: lines (support both formats)
    team_pattern = r'^\*\*Team:\*\*\s*(\w+)|^Team:\s*(\w+)'
    for match in re.finditer(team_pattern, content, re.MULTILINE):
        team = (match.group(1) or match.group(2)).lower()
        labels.add(f"team:{team}")
    
    # Extract epic names from markdown headers (## Epic: Name or # EPIC X: Name)
    epic_pattern = r'^##?\s+EPIC\s+\d+:\s+(.+?)(?:\s+\(|$)|^##\s+Epic:\s+(.+?)$'
    for match in re.finditer(epic_pattern, content, re.MULTILINE | re.IGNORECASE):
        epic_name = (match.group(1) or match.group(2)).strip()
        # Convert to label format: "Document Ingestion & Storage" -> "epic:ingestion"
        epic_label = "epic:" + epic_name.lower().split()[0]
        labels.add(epic_label)
    
    # Always include base 'epic' label for epic issues
    labels.add("epic")
    
    return labels

# Read backlog file
content = BACKLOG_FILE.read_text(encoding="utf-8")
all_labels = extract_all_labels(content)

print(f"Found {len(all_labels)} unique labels to create:")
for label in sorted(all_labels):
    print(f"  - {label}")

print("\n" + "="*50 + "\n")

# Create each label
for label in sorted(all_labels):
    color = get_label_color(label)
    
    # Build gh label create command
    cmd = ["gh", "label", "create", label, "--color", color, "--force"]
    
    print(f"Creating label: {label} (color: #{color})")
    
    if DRY_RUN:
        print(f"  DRY RUN: {' '.join(cmd)}")
    else:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ Created")
        else:
            print(f"  ✗ Error: {result.stderr.strip()}")

print("\n" + "="*50)
print("Done! Labels have been created in the repository.")
print("You can now re-run create-story-issue.py to apply labels to existing issues.")
