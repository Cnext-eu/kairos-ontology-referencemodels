import re
import subprocess
import json
import sys
import tempfile
import os
from pathlib import Path

# === CONFIG ===
DRY_RUN = False  # True = print commands, don't execute

# Repository configuration
# Set REPO_OWNER and REPO_NAME to explicitly target a specific repository
# If None, will auto-detect from current git repository
# For forked repositories: Issues will be created in the fork (not the parent)
REPO_OWNER = None  # e.g., "YourUsername" or "Cnext-eu"
REPO_NAME = None    # e.g., "kairos-app-juri-mail2flow"

# GitHub Project configuration (will be selected by user)
PROJECT_NUMBER = None  # Selected by user
PROJECT_ID = None  # Cached after first lookup
PROJECT_TITLE = None  # Cached project title
TYPE_FIELD_ID = None  # Cached after first lookup
TYPE_FIELD_OPTIONS = {}  # Cached mapping of type names to option IDs
SELECTED_PROJECT = None  # User's selected project info

# Store mapping of Epic IDs to GitHub issue numbers
epic_issue_map = {}

# Note: Labels are pre-configured in .github/labeler.yml and should not be created by this script

# Cached repo info for consistent use across all operations
_cached_repo_owner = None
_cached_repo_name = None

def normalize_label(text: str) -> str:
    return text.strip()

def get_repo_from_git_remote():
    """Parse owner/repo from git remote URL (origin).
    
    This gets the actual repository from git config, not from gh CLI
    which may resolve to upstream for forks.
    """
    import re
    
    cmd = ["git", "remote", "get-url", "origin"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None, None
    
    url = result.stdout.strip()
    
    # Parse various URL formats:
    # https://github.com/owner/repo.git
    # git@github.com:owner/repo.git
    # https://github.com/owner/repo
    
    # HTTPS format
    https_match = re.search(r'github\.com[/:]([^/]+)/([^/.]+)(?:\.git)?$', url)
    if https_match:
        return https_match.group(1), https_match.group(2)
    
    return None, None

def get_repo_flag():
    """Get the --repo flag for gh CLI commands.
    
    Always returns explicit --repo flag to ensure issues are created
    in the current repository (fork), not the upstream.
    """
    global _cached_repo_owner, _cached_repo_name
    
    # If explicitly configured, use that
    if REPO_OWNER and REPO_NAME:
        return ["--repo", f"{REPO_OWNER}/{REPO_NAME}"]
    
    # Use cached values if available
    if _cached_repo_owner and _cached_repo_name:
        return ["--repo", f"{_cached_repo_owner}/{_cached_repo_name}"]
    
    # Get from git remote URL (most reliable for forks)
    owner, name = get_repo_from_git_remote()
    if owner and name:
        _cached_repo_owner = owner
        _cached_repo_name = name
        return ["--repo", f"{owner}/{name}"]
    
    return []

def get_authenticated_user():
    """Get the currently authenticated GitHub user."""
    cmd = ["gh", "api", "user", "--jq", ".login"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return result.stdout.strip()

def build_labels(item, is_epic=False):
    """Build labels list from parsed epic or story data.
    
    Labels are pre-configured in .github/labeler.yml.
    Use up to 4 labels per issue from the available area labels:
    - area: core, area: model, area: training, area: inference
    - area: evaluation, area: data, area: api, area: performance
    - area: infra, area: docs
    """
    labels = set()
    
    # Get labels from the item (already a list for new format)
    if 'labels' in item:
        if isinstance(item['labels'], list):
            labels.update(item['labels'])
        else:
            # Fallback for string format
            for l in str(item['labels']).split(','):
                clean = normalize_label(l)
                if clean:
                    labels.add(clean)
    
    # Limit to 4 labels as per guidelines
    return sorted(list(labels))[:4]

# Cache for existing labels to avoid repeated API calls
_existing_labels = None

def get_existing_labels():
    """Get list of existing labels in the repository."""
    global _existing_labels
    if _existing_labels is not None:
        return _existing_labels
    
    cmd = ["gh", "label", "list"] + get_repo_flag() + ["--json", "name", "--limit", "100"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        data = json.loads(result.stdout)
        _existing_labels = {label["name"].lower(): label["name"] for label in data}
    else:
        _existing_labels = {}
    return _existing_labels

def ensure_labels_exist(labels):
    """Create labels that don't exist in the repository."""
    existing = get_existing_labels()
    
    # Default colors for auto-created labels
    label_colors = {
        "epic": "7057ff",
        "user-story": "0e8a16",
        "infrastructure": "d4c5f9",
        "setup": "c2e0c6",
        "feature": "a2eeef",
        "bug": "d73a4a",
        "enhancement": "84b6eb",
    }
    default_color = "ededed"
    
    for label in labels:
        if label.lower() not in existing:
            color = label_colors.get(label.lower(), default_color)
            cmd = ["gh", "label", "create"] + get_repo_flag() + [label, "--color", color, "--force"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✓ Created label: {label}")
                existing[label.lower()] = label
            else:
                print(f"  Warning: Could not create label '{label}': {result.stderr.strip()}")

def create_issue(title, body, labels, issue_type=None):
    """Create a GitHub issue and return its number and URL."""
    cmd = ["gh", "issue", "create"] + get_repo_flag() + ["--title", title, "--body", body]
    
    if DRY_RUN:
        for label in labels:
            cmd.extend(["--label", label])
        print(f"DRY RUN CMD: {' '.join(cmd[:6])}... [body truncated]")
        return None, None
    else:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  Error creating issue: {result.stderr.strip()}")
            return None, None
        
        issue_url = result.stdout.strip()
        # Extract issue number from URL
        issue_number = issue_url.split('/')[-1] if issue_url else None
        print(f"  Created: {issue_url}")
        
        # Add labels (create if they don't exist)
        if labels and issue_url:
            ensure_labels_exist(labels)
            label_cmd = ["gh", "issue", "edit"] + get_repo_flag() + [issue_url, "--add-label", ",".join(labels)]
            label_result = subprocess.run(label_cmd, capture_output=True, text=True)
            if label_result.returncode != 0:
                print(f"  Warning: Could not add labels: {label_result.stderr.strip()}")
            else:
                print(f"  Labels added: {', '.join(labels)}")
        
        # Add to project and set Type field
        if issue_number and issue_type:
            issue_id = get_issue_node_id(issue_number)
            if issue_id:
                add_issue_to_project(issue_id, issue_type)
        
        return issue_number, issue_url

def get_issue_node_id(issue_number):
    """Get the GraphQL node ID for an issue number using current repo."""
    cmd = ["gh", "issue", "view"] + get_repo_flag() + [str(issue_number), "--json", "id"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    data = json.loads(result.stdout)
    return data.get("id")

def get_repo_info():
    """Get current repository owner and name from git remote URL.
    
    Uses git remote URL to ensure we get the actual repository we're working in,
    not the upstream parent (which gh CLI may return for forks).
    """
    global _cached_repo_owner, _cached_repo_name
    
    # If explicitly configured, use that
    if REPO_OWNER and REPO_NAME:
        return REPO_OWNER, REPO_NAME
    
    # Use cached values if available
    if _cached_repo_owner and _cached_repo_name:
        return _cached_repo_owner, _cached_repo_name
    
    # Get from git remote URL (most reliable for forks)
    owner, name = get_repo_from_git_remote()
    if owner and name:
        _cached_repo_owner = owner
        _cached_repo_name = name
        
        # Check if this is a fork and log info
        cmd = ["gh", "api", f"repos/{owner}/{name}", "--jq", ".fork,.parent.full_name"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 1 and lines[0] == 'true':
                parent_name = lines[1] if len(lines) > 1 else "unknown"
                print(f"  Note: This is a fork of {parent_name}")
                print(f"  Issues will be created in this fork: {owner}/{name}")
        
        return owner, name
    
    return None, None

def list_available_projects():
    """List all available GitHub Projects (repo + organization). Only returns active (non-closed) projects."""
    owner, repo = get_repo_info()
    if not owner or not repo:
        return []
    
    projects = []
    
    # Query for repository projects (including closed status)
    repo_query = f'''query {{
      repository(owner: "{owner}", name: "{repo}") {{
        projectsV2(first: 10) {{
          nodes {{
            id
            title
            number
            closed
            fields(first: 20) {{
              nodes {{
                ... on ProjectV2SingleSelectField {{
                  id
                  name
                  options {{
                    id
                    name
                  }}
                }}
              }}
            }}
          }}
        }}
      }}
    }}'''
    
    cmd = ["gh", "api", "graphql", "-f", f"query={repo_query}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        data = json.loads(result.stdout)
        repo_projects = data.get("data", {}).get("repository", {}).get("projectsV2", {}).get("nodes", [])
        for p in repo_projects:
            # Skip closed/archived projects
            if p.get("closed", False):
                continue
            projects.append({
                "id": p.get("id"),
                "title": p.get("title"),
                "number": p.get("number"),
                "source": f"repo:{owner}/{repo}",
                "is_repo_project": True,
                "fields": p.get("fields", {}).get("nodes", [])
            })
    else:
        if "read:project" in result.stderr:
            print("  Warning: GitHub token missing 'read:project' scope")
            print("  Update token at: https://github.com/settings/tokens")
    
    # Query for organization projects (if owner is an org)
    org_query = f'''query {{
      organization(login: "{owner}") {{
        projectsV2(first: 10) {{
          nodes {{
            id
            title
            number
            closed
            fields(first: 20) {{
              nodes {{
                ... on ProjectV2SingleSelectField {{
                  id
                  name
                  options {{
                    id
                    name
                  }}
                }}
              }}
            }}
          }}
        }}
      }}
    }}'''
    
    cmd = ["gh", "api", "graphql", "-f", f"query={org_query}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        data = json.loads(result.stdout)
        org_projects = data.get("data", {}).get("organization", {}).get("projectsV2", {}).get("nodes", [])
        for p in org_projects:
            # Skip closed/archived projects
            if p.get("closed", False):
                continue
            # Avoid duplicates (repo projects linked from org)
            if not any(ep["id"] == p.get("id") for ep in projects):
                projects.append({
                    "id": p.get("id"),
                    "title": p.get("title"),
                    "number": p.get("number"),
                    "source": f"org:{owner}",
                    "is_repo_project": False,
                    "fields": p.get("fields", {}).get("nodes", [])
                })
    
    # Sort: repo-linked projects first
    projects.sort(key=lambda x: (0 if x.get("is_repo_project") else 1, x.get("number", 0)))
    
    return projects

def prompt_project_selection():
    """Prompt user to select a GitHub Project from available options."""
    global SELECTED_PROJECT, PROJECT_ID, PROJECT_TITLE, TYPE_FIELD_ID, TYPE_FIELD_OPTIONS
    
    print("\nChecking for available GitHub Projects...")
    projects = list_available_projects()
    
    if not projects:
        print("  No active GitHub Projects found.")
        response = input("Continue without project assignment? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("\nOperation cancelled by user.")
            sys.exit(0)
        return None
    
    # Find recommended project (first repo-linked project)
    recommended_idx = None
    for i, p in enumerate(projects):
        if p.get("is_repo_project"):
            recommended_idx = i
            break
    
    print(f"\nAvailable GitHub Projects ({len(projects)} active):")
    print("-" * 60)
    for i, p in enumerate(projects, 1):
        marker = " (recommended)" if i - 1 == recommended_idx else ""
        print(f"  [{i}] {p['title']} (#{p['number']}) - {p['source']}{marker}")
    print(f"  [0] Skip - Don't assign to any project")
    print("-" * 60)
    
    # Default to recommended project
    default_choice = recommended_idx + 1 if recommended_idx is not None else None
    prompt_text = f"Select a project [default: {default_choice}]: " if default_choice else "Select a project: "
    
    while True:
        try:
            choice = input(prompt_text).strip()
            
            # Handle empty input (use default)
            if choice == "" and default_choice:
                choice_num = default_choice
            else:
                choice_num = int(choice)
            
            if choice_num == 0:
                print("  Skipping project assignment.")
                return None
            
            if 1 <= choice_num <= len(projects):
                selected = projects[choice_num - 1]
                SELECTED_PROJECT = selected
                PROJECT_ID = selected["id"]
                PROJECT_TITLE = selected["title"]
                
                # Extract Type field info
                for field in selected.get("fields", []):
                    if field.get("name", "").lower() in ["type", "issue type", "type:"]:
                        TYPE_FIELD_ID = field.get("id")
                        options = field.get("options", [])
                        TYPE_FIELD_OPTIONS = {opt.get("name"): opt.get("id") for opt in options}
                        break
                
                print(f"\n  ✓ Selected: {selected['title']} (#{selected['number']})")
                if TYPE_FIELD_OPTIONS:
                    print(f"  ✓ Type field options: {', '.join(TYPE_FIELD_OPTIONS.keys())}")
                return selected
            else:
                print(f"  Invalid choice. Enter 0-{len(projects)}.")
        except ValueError:
            print("  Invalid input. Enter a number.")

def get_project_info():
    """Get the selected project and its Type field (uses user selection from prompt_project_selection)."""
    global PROJECT_ID, TYPE_FIELD_ID, TYPE_FIELD_OPTIONS
    
    # Return cached values if available (set by prompt_project_selection)
    if PROJECT_ID:
        return PROJECT_ID, TYPE_FIELD_ID, TYPE_FIELD_OPTIONS
    
    # No project selected
    return None, None, {}

def add_issue_to_project(issue_id, issue_type=None):
    """Add an issue to the project and optionally set its Type field."""
    project_id, type_field_id, type_options = get_project_info()
    
    if not project_id:
        return False
    
    # Add issue to project
    mutation = f'''mutation {{
      addProjectV2ItemById(input: {{
        projectId: "{project_id}"
        contentId: "{issue_id}"
      }}) {{
        item {{
          id
        }}
      }}
    }}'''
    
    cmd = ["gh", "api", "graphql", "-f", f"query={mutation}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        if "read:project" in result.stderr:
            # Already warned about scope in get_project_info, no need to repeat
            pass
        else:
            print(f"  Warning: Could not add to project: {result.stderr.strip()}")
        return False
    
    data = json.loads(result.stdout)
    item_id = data.get("data", {}).get("addProjectV2ItemById", {}).get("item", {}).get("id")
    
    if not item_id:
        print("  Warning: Could not get project item ID")
        return False
    
    print(f"  ✓ Added to project")
    
    # Set Type field if provided and field exists
    if issue_type and type_field_id and item_id:
        # Find matching type option (case-insensitive)
        type_option_id = None
        for opt_name, opt_id in type_options.items():
            if opt_name.lower() == issue_type.lower():
                type_option_id = opt_id
                break
        
        if type_option_id:
            update_mutation = f'''mutation {{
              updateProjectV2ItemFieldValue(input: {{
                projectId: "{project_id}"
                itemId: "{item_id}"
                fieldId: "{type_field_id}"
                value: {{
                  singleSelectOptionId: "{type_option_id}"
                }}
              }}) {{
                projectV2Item {{
                  id
                }}
              }}
            }}'''
            
            cmd = ["gh", "api", "graphql", "-f", f"query={update_mutation}"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✓ Set Type: {issue_type}")
            else:
                print(f"  Warning: Could not set Type field: {result.stderr.strip()}")
    
    return True

def add_sub_issue(parent_issue_number, child_issue_number):
    """Link a child issue to a parent epic using GitHub's sub-issue feature via GraphQL."""
    if DRY_RUN:
        print(f"  DRY RUN: Would link issue #{child_issue_number} as sub-issue of #{parent_issue_number}")
        return True
    
    # Get GraphQL node IDs for both issues
    parent_id = get_issue_node_id(parent_issue_number)
    child_id = get_issue_node_id(child_issue_number)
    
    if not parent_id or not child_id:
        print(f"  Warning: Could not get issue IDs for linking (parent: {parent_id}, child: {child_id})")
        return False
    
    # Use GraphQL mutation to add sub-issue
    mutation = f'''mutation {{
      addSubIssue(input: {{
        issueId: "{parent_id}"
        subIssueId: "{child_id}"
      }}) {{
        issue {{
          id
          number
        }}
        subIssue {{
          id
          number
        }}
      }}
    }}'''
    
    cmd = ["gh", "api", "graphql", "-f", f"query={mutation}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"  Warning: Could not link sub-issue: {result.stderr.strip()}")
        return False
    else:
        print(f"  ✓ Linked as sub-issue of Epic #{parent_issue_number}")
        return True

def parse_epics(content):
    """Parse all epics from DSD format: ## Epic: Title"""
    epics = []
    
    # Match epic pattern: ## Epic: Title
    epic_pattern = r'^## Epic: (.+?)$'
    
    for match in re.finditer(epic_pattern, content, re.MULTILINE):
        epic_title = match.group(1).strip()
        
        # Find the epic block (from this match to next ## Epic: or ## UserStory: or end)
        epic_start = match.start()
        next_section = re.search(r'\n## (Epic|UserStory):', content[epic_start+10:])
        epic_end = epic_start + 10 + next_section.start() if next_section else len(content)
        epic_block = content[epic_start:epic_end]
        
        # Extract ID field
        id_match = re.search(r'^ID: (.+?)$', epic_block, re.MULTILINE)
        epic_id = id_match.group(1).strip() if id_match else f"EPIC-{len(epics)+1}"
        
        # Extract epic number from ID (e.g., EPIC-UI-001 -> UI-001)
        epic_number = epic_id.replace('EPIC-', '')
        
        # Extract Labels field
        labels_match = re.search(r'^Labels: (.+?)$', epic_block, re.MULTILINE)
        if labels_match:
            labels_str = labels_match.group(1).strip()
            labels = [l.strip() for l in labels_str.split(',') if l.strip()]
        else:
            labels = ["area: core"]
        
        # Extract Team field
        team_match = re.search(r'^Team: (.+?)$', epic_block, re.MULTILINE)
        team = team_match.group(1).strip() if team_match else ""
        
        # Extract Description (multi-line after "Description:")
        desc_match = re.search(r'Description:\n((?:- .+\n?)+)', epic_block)
        description = desc_match.group(1).strip() if desc_match else ""
        
        # Use description as both description and business_value for template compatibility
        business_value = epic_title
        acceptance_criteria = "All user stories in this epic are completed and accepted"
        
        epic = {
            "title": epic_title,
            "id": epic_id,
            "number": epic_number,
            "description": description,
            "business_value": business_value,
            "acceptance_criteria": acceptance_criteria,
            "team": team,
            "labels": labels[:4],  # Limit to 4 labels
            "meta": {
                "ID": epic_id,
                "Labels": ", ".join(labels[:4])
            }
        }
        epics.append(epic)
    
    return epics

def parse_stories(content):
    """Parse all stories from DSD format: ## UserStory: Title"""
    stories = []
    
    # Match story pattern: ## UserStory: Title
    story_pattern = r'^## UserStory: (.+?)$'
    
    for match in re.finditer(story_pattern, content, re.MULTILINE):
        story_title = match.group(1).strip()
        
        # Find the story block (from this match to next ## UserStory: or ## Epic: or end)
        story_start = match.start()
        next_section = re.search(r'\n## (UserStory|Epic|Technical Story):', content[story_start+10:])
        story_end = story_start + 10 + next_section.start() if next_section else len(content)
        story_block = content[story_start:story_end]
        
        # Extract ID field
        id_match = re.search(r'^ID: (.+?)$', story_block, re.MULTILINE)
        story_id = id_match.group(1).strip() if id_match else f"US-{len(stories)+1}"
        
        # Extract EpicID field
        epic_id_match = re.search(r'^EpicID: (.+?)$', story_block, re.MULTILINE)
        epic_id = epic_id_match.group(1).strip() if epic_id_match else ""
        
        # Extract Priority field
        priority_match = re.search(r'^Priority: (.+?)$', story_block, re.MULTILINE)
        priority = priority_match.group(1).strip() if priority_match else "Medium"
        
        # Extract Team field
        team_match = re.search(r'^Team: (.+?)$', story_block, re.MULTILINE)
        team = team_match.group(1).strip() if team_match else ""
        
        # Extract Labels field
        labels_match = re.search(r'^Labels: (.+?)$', story_block, re.MULTILINE)
        if labels_match:
            labels_str = labels_match.group(1).strip()
            labels = [l.strip() for l in labels_str.split(',') if l.strip()]
        else:
            labels = ["area: core"]
        
        # Extract user story statement (As a... I want... So that...)
        # Look for the pattern after metadata fields
        us_pattern = r'As a (.+?),\nI want (.+?),\nso that (.+?)\.'
        us_match = re.search(us_pattern, story_block, re.DOTALL)
        if us_match:
            role = us_match.group(1).strip()
            capability = us_match.group(2).strip()
            benefit = us_match.group(3).strip()
            user_story = f"As a **{role}**,\nI want **{capability}**\nso that **{benefit}**."
        else:
            user_story = ""
        
        # Extract acceptance criteria (list items after "Acceptance criteria:")
        ac_pattern = r'Acceptance criteria:\n((?:- .+\n?)+)'
        ac_match = re.search(ac_pattern, story_block)
        if ac_match:
            # Convert to checkbox format for GitHub issues
            criteria_lines = ac_match.group(1).strip().split('\n')
            acceptance_criteria = '\n'.join([f"- [ ] {line.lstrip('- ')}" for line in criteria_lines])
        else:
            acceptance_criteria = ""
        
        # Extract notes/technical notes (list items after "Notes:")
        notes_pattern = r'Notes:\n((?:- .+\n?)+)'
        notes_match = re.search(notes_pattern, story_block)
        technical_notes = notes_match.group(1).strip() if notes_match else ""
        
        # Set default values for optional fields
        estimate = "3"  # Default story points
        dependencies = "None"
        sprint = ""
        
        # Map priority to size estimate for the template
        size_map = {
            "Critical": "l", "High": "m", 
            "Medium": "s", "Low": "xs"
        }
        size = size_map.get(priority, "s")
        
        story = {
            "title": story_title,
            "id": story_id,
            "epic_id": epic_id,
            "user_story": user_story,
            "acceptance_criteria": acceptance_criteria,
            "technical_notes": technical_notes,
            "priority": priority,
            "estimate": estimate,
            "size": size,
            "dependencies": dependencies,
            "sprint": sprint,
            "team": team,
            "labels": labels[:4],  # Limit to 4 labels
            "meta": {
                "ID": story_id,
                "EpicID": epic_id,
                "Priority": priority,
                "Labels": ", ".join(labels[:4])
            }
        }
        stories.append(story)
    
    return stories

def build_epic_body(epic):
    """Build the issue body for an Epic matching the epic.yml template format."""
    body_parts = []
    
    # Add Epic ID for reference and traceability
    body_parts.append(f"**Epic ID:** `{epic['id']}`")
    body_parts.append("")
    
    # Background section (maps to Epic Description in markdown)
    body_parts.append("## Background")
    body_parts.append("")
    body_parts.append(epic.get('description', 'Context and motivation for this epic'))
    body_parts.append("")
    
    # Objectives section (maps to Business Value)
    body_parts.append("## Objectives")
    body_parts.append("")
    body_parts.append(epic.get('business_value', 'High-level goals of this epic'))
    body_parts.append("")
    
    # Success Criteria section (from Acceptance Criteria in markdown)
    body_parts.append("## Success Criteria")
    body_parts.append("")
    if epic.get('acceptance_criteria'):
        body_parts.append(epic['acceptance_criteria'])
    else:
        body_parts.append("All user stories completed and accepted")
    body_parts.append("")
    
    # Stakeholders section
    body_parts.append("## Stakeholders")
    body_parts.append("")
    body_parts.append("Product Owner, Development Team, QA")
    body_parts.append("")
    
    # Dependencies / Blockers section
    body_parts.append("## Dependencies / Blockers")
    body_parts.append("")
    body_parts.append("_See linked user stories below_")
    body_parts.append("")
    
    # Child Issues section
    body_parts.append("## Child Issues")
    body_parts.append("")
    body_parts.append("User stories for this epic will be linked as sub-issues.")
    body_parts.append("")
    
    # Additional Notes
    body_parts.append("## Additional Notes")
    body_parts.append("")
    body_parts.append("_Add any relevant risks, open questions, or rollout considerations_")
    
    return "\n".join(body_parts)

def build_story_body(story, epic_issue_number=None):
    """Build the issue body for a User Story matching the user-story.yml template format."""
    body_parts = []
    
    # Add metadata for traceability
    body_parts.append(f"**Story ID:** `{story['id']}`")
    body_parts.append(f"**Epic ID:** `{story['epic_id']}`")
    if epic_issue_number:
        body_parts.append(f"**Parent Epic:** #{epic_issue_number}")
    body_parts.append(f"**Priority:** `{story['priority']}`")
    body_parts.append(f"**Estimated Size:** `{story['size']}`")
    body_parts.append(f"**Story Points:** `{story['estimate']}`")
    if story.get('sprint'):
        body_parts.append(f"**Sprint:** `{story['sprint']}`")
    body_parts.append("")
    
    # User Story section (matching template field id: story)
    body_parts.append("## User Story")
    body_parts.append("")
    if story.get('user_story'):
        body_parts.append(story['user_story'])
    else:
        body_parts.append("_User story not specified._")
    body_parts.append("")
    
    # Acceptance Criteria section (matching template field id: acceptance)
    body_parts.append("## Acceptance Criteria")
    body_parts.append("")
    if story.get('acceptance_criteria'):
        body_parts.append(story['acceptance_criteria'])
    else:
        body_parts.append("_No acceptance criteria specified._")
    body_parts.append("")
    
    # Additional Context section (matching template field id: context)
    body_parts.append("## Additional Context")
    body_parts.append("")
    
    # Add technical notes if present
    if story.get('technical_notes'):
        body_parts.append("**Technical Notes:**")
        body_parts.append("")
        body_parts.append(story['technical_notes'])
        body_parts.append("")
    
    # Add dependencies if present
    if story.get('dependencies') and story['dependencies'] != "None":
        body_parts.append("**Dependencies:**")
        body_parts.append("")
        body_parts.append(f"- {story['dependencies']}")
        body_parts.append("")
    
    if not story.get('technical_notes') and (not story.get('dependencies') or story['dependencies'] == "None"):
        body_parts.append("_No additional context._")
    
    return "\n".join(body_parts)

# === MAIN EXECUTION ===

print("=" * 60)
print("GitHub Issue Creator - Epics & User Stories")
print("=" * 60)

# Check command line arguments
if len(sys.argv) < 2:
    print("\nUsage: python create-story-issue.py <path-to-user-stories-md-file>")
    print("\nExample:")
    print("  python create-story-issue.py ../4.planning-audit-Configuration/03-user-stories-template.md")
    sys.exit(1)

# Get backlog file from command line argument
backlog_file_arg = sys.argv[1]
BACKLOG_FILE = Path(backlog_file_arg)

# Validate file exists
if not BACKLOG_FILE.exists():
    print(f"\nError: File not found: {BACKLOG_FILE}")
    print(f"Please provide a valid path to the user stories markdown file.")
    sys.exit(1)

print(f"\nUsing user stories file: {BACKLOG_FILE}")
print("")

# Read backlog
content = BACKLOG_FILE.read_text(encoding="utf-8")

# Parse epics and stories
epics = parse_epics(content)
stories = parse_stories(content)

print(f"\nFound {len(epics)} Epics and {len(stories)} User Stories")
print("")

# === PHASE 1: Create all Epics ===
print("=" * 60)
print("PHASE 1: Creating Epics")
print("=" * 60)

print("\nNote: Using pre-configured labels from .github/labeler.yml\n")

# Display repository information
owner, repo = get_repo_info()
if owner and repo:
    print(f"Target Repository: {owner}/{repo}")
    if REPO_OWNER and REPO_NAME:
        print("  (Explicitly configured)")
    else:
        print("  (Auto-detected from git repository)")
    
    # Prompt user to select a GitHub Project
    prompt_project_selection()
    
    print("")
    
    # Ask for confirmation
    print(f"\nThis will create {len(epics)} Epics and {len(stories)} User Stories in {owner}/{repo}")
    if PROJECT_ID and PROJECT_TITLE:
        print(f"Issues will be added to project: {PROJECT_TITLE}")
    confirmation = input("Do you want to proceed? (yes/no): ").strip().lower()
    if confirmation not in ['yes', 'y']:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    print("")
else:
    print("Error: Could not detect repository information.")
    sys.exit(1)

for epic in epics:
    print(f"\n=== Creating Epic: {epic['title']} ===")
    print(f"Epic ID: {epic['id']}")
    
    # Build epic body
    body = build_epic_body(epic)
    
    # Build labels (up to 4 from .github/labeler.yml)
    labels = build_labels(epic, is_epic=True)
    print(f"Labels: {labels}")
    
    # Create the epic issue with [Epic] prefix
    title = f"[Epic] {epic['title']}"
    
    issue_number, issue_url = create_issue(title, body, labels, issue_type="Feature")
    
    if issue_number:
        epic_issue_map[epic['id']] = issue_number
        print(f"  ✓ Mapped {epic['id']} -> Issue #{issue_number}")
    elif DRY_RUN:
        # For dry run, use placeholder
        epic_issue_map[epic['id']] = f"DRY-{epic['id']}"

print(f"\nEpic Issue Map: {epic_issue_map}")

# === PHASE 2: Create all User Stories and link to Epics ===
print("\n" + "=" * 60)
print("PHASE 2: Creating User Stories & Linking to Epics")
print("=" * 60)

for story in stories:
    print(f"\n=== Creating Story: {story['title']} ===")
    print(f"Story ID: {story['id']}")
    print(f"Epic ID: {story['epic_id']}")
    
    # Get parent epic issue number
    parent_epic_number = epic_issue_map.get(story['epic_id'])
    
    # Build story body
    body = build_story_body(story, parent_epic_number)
    
    # Build labels (up to 4 from .github/labeler.yml)
    labels = build_labels(story, is_epic=False)
    print(f"Labels: {labels}")
    
    # Create the story issue with [User Story] prefix
    title = f"[User Story] {story['title']}"
    
    issue_number, issue_url = create_issue(title, body, labels, issue_type="Feature")
    
    # Link story to epic as sub-issue
    if issue_number and parent_epic_number and not DRY_RUN:
        add_sub_issue(parent_epic_number, issue_number)
    elif DRY_RUN and parent_epic_number:
        print(f"  DRY RUN: Would link to Epic #{parent_epic_number}")

# === SUMMARY ===
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Epics created: {len(epics)}")
print(f"User Stories created: {len(stories)}")
if PROJECT_TITLE:
    print(f"Project: {PROJECT_TITLE}")
print(f"\nEpic ID -> Issue Number Mapping:")
for epic_id, issue_num in epic_issue_map.items():
    print(f"  {epic_id} -> #{issue_num}")
