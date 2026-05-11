# AI Instructions for DSD User Stories → GitHub Issues

## Context for AI Assistant

You are helping to transfer **validated user stories** from the DSD document (`03-user-stories.md`) into GitHub Issues for project management.

## ⚠️ CRITICAL WARNINGS ⚠️

### 1. Validation Required BEFORE Issue Creation

**DO NOT create GitHub issues until the user stories have been:**
- ✅ Reviewed by the product owner
- ✅ Validated for accuracy and completeness
- ✅ Approved for implementation
- ✅ Confirmed to match actual project requirements

**Why?** Once GitHub issues are created:
- They become part of the project's permanent history
- Team members may start working on them immediately
- Deleting issues is disruptive and leaves audit trails
- Incorrect stories create confusion and rework

### 2. This is NOT for the Template Example

The Kidslife IDP user stories in this template are **EXAMPLES ONLY**. 

**Before running this process:**
1. User must have replaced `starter-requirements.md` with their actual project
2. DSD must be regenerated with real requirements
3. User stories must reflect the actual project (not Kidslife IDP)

---

## Prerequisites

Before proceeding:

1. ✅ **Validated DSD exists** at `.docs/2-DSD/version {timestamp}/03-user-stories.md`
2. ✅ **Product owner has reviewed** all user stories
3. ✅ **User confirms** stories are production-ready
4. ✅ **GitHub CLI installed** (`gh --version`)
5. ✅ **Authenticated to GitHub** (`gh auth status`)
6. ✅ **Correct repository** (check with `gh repo view`)

---

## Process Overview

**Labels are pre-configured** during repository initialization in `.github/labeler.yml`. No need to create labels.

### Using GitHub Issue Templates

When creating issues manually from user stories, use the appropriate issue templates:
- **For Epics**: Use `.github/ISSUE_TEMPLATE/epic.yml`
- **For User Stories**: Use `.github/ISSUE_TEMPLATE/user-story.yml`

### Labeling Guidelines

Select **up to 4 labels** from the `.github/labeler.yml` file for each issue:
- **Area labels**: `area: core`, `area: model`, `area: training`, `area: inference`, `area: evaluation`, `area: data`, `area: api`, `area: performance`, `area: infra`, `area: docs`

### Automated Issue Creation Process

If using the automated script:
- Parse user stories from markdown file
- Create GitHub issues (Epics first, then User Stories)
- Apply up to 4 relevant labels to each issue
- Link user stories to their parent epics

---

## Tool Location

Python scripts are in: `.docs/tools/IssueCreation/`

**Available scripts:**
- `create-story-issue.py` - Creates GitHub issues from user stories
- `delete-all-issues.py` - ⚠️ Destructive: Deletes all issues (use for cleanup only)

**Note:** Labels are already configured in `.github/labeler.yml` during repository initialization.

---

## Step-by-Step Instructions

### Create Issues from User Stories

**Purpose:** Create GitHub issues for all epics and user stories.

**⚠️ FINAL CONFIRMATION REQUIRED**

Before running this command, ask the user:

> **Are you absolutely sure you want to create GitHub issues from the user stories?**
> 
> This will:
> - Create X epic issues
> - Create Y user story issues
> - Apply labels to all issues
> - Link stories to epics
> 
> **This action cannot be easily undone. Have you validated all user stories?**
> 
> Reply "CONFIRMED" to proceed.

**Command:**
```powershell
cd .docs/tools/IssueCreation
python create-story-issue.py --file "../../2-DSD/version {timestamp}/03-user-stories.md"
```

**What it does:**
1. Parses `03-user-stories.md` to extract epics and user stories
2. Creates epic issues using the `epic.yml` template structure
3. Creates user story issues using the `user-story.yml` template structure
4. Links each user story to its parent epic (sub-issue relationship)
5. Applies up to 4 relevant labels from `.github/labeler.yml` to each issue

**Expected output:**
```
Processing Epic: Document Ingestion & Storage
  Epic ID: E1
  Creating epic issue using epic.yml template...
  Created: https://github.com/Cnext-eu/repo/issues/1
  Labels added: area: core, area: data (up to 4 labels)

Processing UserStory: [STORY-001] Email Polling for Document Ingestion
  Story ID: STORY-001
  Epic: E1 (issue #1)
  Creating user story issue using user-story.yml template...
  Created: https://github.com/Cnext-eu/repo/issues/2
  Labels added: area: core, area: data, area: api (up to 4 labels)
  ✓ Linked as sub-issue of Epic #1

...

Summary:
  Epics created: 6
  User stories created: 45
  Total issues: 51
```

**Issue format:**
- **Epic title:** `[E1] Document Ingestion & Storage`
- **Story title:** `[STORY-001] Email Polling for Document Ingestion`
- **Story body:** Includes "As a...", acceptance criteria, technical notes, story points

---

## Configuration Options

### Dry Run Mode

To preview what would be created without actually creating issues:

**Edit the script:**
```python
# In create-story-issue.py
DRY_RUN = True  # Change to True
```

**Then run the script.** It will print commands without executing them:
```
DRY RUN CMD: gh issue create --title "[STORY-001] Email Polling..." --label "area: core" --label "area: data"
```

**Remember to set back to `False` before actual run!**

---

## Validation Checklist

Before running Step 2 (create issues), verify:

### User Story Quality
- [ ] All stories have clear "As a... I want... So that..." format
- [ ] Acceptance criteria are testable and specific
- [ ] Story points are assigned
- [ ] Priorities are set (HIGH/MEDIUM/LOW)
- [ ] All stories belong to an epic

### Technical Correctness
- [ ] Technologies mentioned are correct for your project
- [ ] API endpoints match your architecture
- [ ] Database schemas align with your data model
- [ ] Sprint assignments are realistic

### Business Alignment
- [ ] Stories match actual business requirements
- [ ] Stakeholders are correctly identified
- [ ] Success metrics are measurable
- [ ] Dependencies are accurate

### Format Compliance
- [ ] Epic IDs are unique (E1, E2, E3...)
- [ ] Story IDs are unique (STORY-001, STORY-002...)
- [ ] Each issue will use up to 4 labels from `.github/labeler.yml`
- [ ] Issues will use the templates from `.github/ISSUE_TEMPLATE/` (epic.yml, user-story.yml)
- [ ] No TODOs or placeholders remain

---

## Post-Creation Steps

After issues are created:

### 1. Verify in GitHub
- Go to your repository's Issues tab
- Check that epics and stories are created
- Verify labels are applied correctly
- Confirm sub-issue relationships (stories linked to epics)

### 2. Add to GitHub Project (Optional)
```powershell
# Add all issues to a project
gh issue list --limit 100 | ForEach-Object {
    gh issue edit $_.number --add-project "Project Name"
}
```

### 3. Assign to Team Members
- Manually assign issues via GitHub UI
- Or use GitHub CLI:
```powershell
gh issue edit 2 --assignee "username"
```

### 4. Set Milestones
```powershell
# Create milestones for sprints
gh api repos/:owner/:repo/milestones -f title="Sprint 1" -f due_on="2025-01-15T00:00:00Z"

# Assign issues to milestone
gh issue edit 2 --milestone "Sprint 1"
```

---

## Cleanup (If Needed)

### Delete All Issues (⚠️ DESTRUCTIVE)

**Only use if you need to start over:**

```powershell
cd .docs/tools/IssueCreation
python delete-all-issues.py
```

**Confirmation required:** Script will ask "Are you sure? (yes/no)"

**Note:** Labels are configured in `.github/labeler.yml` and should not be deleted. They are part of the repository configuration.

---

## Troubleshooting

### Issue: "Label does not exist"
**Solution:** Labels are pre-configured in `.github/labeler.yml`. Check that you're using the correct label names from that file (up to 4 labels per issue).

### Issue: "Epic not found for story"
**Cause:** Epic ID in story's `EpicID:` field doesn't match any epic
**Solution:** Check that epic IDs are correct in `03-user-stories.md`

### Issue: Duplicate issues created
**Cause:** Script was run multiple times
**Solution:** Delete duplicate issues manually or use `delete-all-issues.py` and start over

### Issue: Sub-issue linking fails
**Cause:** GitHub API may not support sub-issues in your repository type
**Solution:** Issues will still be created; you can manually link them or use GitHub Projects

---

## Customization

### Modify Labels

Labels are configured in `.github/labeler.yml`. To add or modify labels:
1. Edit `.github/labeler.yml`
2. Update label definitions and rules
3. Commit changes to repository

### Change Issue Title Format

Edit `.docs/tools/IssueCreation/create-story-issue.py`:

Search for the title formatting section and modify:
```python
# Default: [STORY-001] Title
# Custom example: US-001: Title
title = f"US-{story_id}: {story_title}"
```

---

## Example Workflow

**Complete example from start to finish:**

```powershell
# 1. Navigate to project root
cd G:\Git\smartcoding-kairos-template

# 2. Verify user stories exist
Get-Content .docs\2-DSD\version 20251221T213935\03-user-stories.md

# 3. Review and validate user stories (manual step)
# ... Product owner reviews ...

# 4. Check GitHub authentication
gh auth status

# 5. Verify labels are configured
Get-Content .github\labeler.yml

# 6. Wait for confirmation from user
# "Are you sure? Reply CONFIRMED."

# 7. Create issues
cd .docs\tools\IssueCreation
python create-story-issue.py --file "../../2-DSD/version 20251221T213935/03-user-stories.md"

# 8. Verify in GitHub
gh issue list --limit 10

# 9. Open GitHub in browser to review
gh repo view --web
```

---

## Summary

**DO:**
✅ Validate user stories thoroughly before creating issues  
✅ Use issue templates from `.github/ISSUE_TEMPLATE/` (epic.yml, user-story.yml)  
✅ Apply up to 4 labels from `.github/labeler.yml` per issue  
✅ Use dry-run mode to preview changes  
✅ Verify in GitHub after creation  

**DON'T:**
❌ Create issues from unvalidated user stories  
❌ Run scripts on the template example (Kidslife IDP)  
❌ Skip the confirmation step  
❌ Run multiple times (creates duplicates)  
❌ Modify or delete labels from `.github/labeler.yml` without understanding impact  

---

## Example Prompt for AI

**User to AI:**
```
I've validated the user stories in my DSD. Please help me create GitHub issues:

1. Review the user stories in: .docs/2-DSD/version 20251221T213935/03-user-stories.md
2. Create GitHub issues using the templates from .github/ISSUE_TEMPLATE/
3. Apply up to 4 labels from .github/labeler.yml to each issue
4. Ask me to confirm before creating issues

Use the instructions in .docs/tools/smartcoding/AI_INSTRUCTIONS-4-DSD-IssueCreation.md
```

**AI should respond:**
```
I'll help you create GitHub issues from your validated user stories.

⚠️ **Important:** Have you completed these validation steps?
- [ ] Product owner reviewed all user stories
- [ ] Stories match your actual project (not template examples)
- [ ] All acceptance criteria are complete
- [ ] Story points and priorities assigned
- [ ] Technical details verified

If yes, I'll proceed with:

**Create Issues from User Stories**
- Using issue templates: epic.yml and user-story.yml
- Applying up to 4 labels from labeler.yml per issue
- Linking user stories to their parent epics

Before creating issues, I'll ask for explicit confirmation.

Ready to proceed? Reply "YES" to start.
```

---

**Remember:** GitHub issues are permanent project artifacts. Always validate before creating!
