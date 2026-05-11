# SmartCoding AI Instructions

**Current Version**: 1.2.0  
**Last Updated**: 2026-02-04  
**Release Cycle**: Bi-weekly (every 2 weeks)

## Overview

This folder contains AI instruction files for the SmartCoding methodology - a structured approach to creating solution designs and implementation documentation using AI-assisted development.

### What's Included

- **AI Instruction Files**: Step-by-step workflows for AI assistants (GitHub Copilot, etc.)
- **Templates**: Standardized formats for requirements, designs, bugs, and changes
- **Reference Materials**: Platform documentation and examples

---

## 📂 Documentation Paths by Project Type

**The AI will ask you about project type first.** Documentation goes to different folders based on your answer:

| Project Type | Description | Documentation Path |
|--------------|-------------|-------------------|
| **Kairos Core** | Core platform (Flow, Mail2Flow, etc.) | `.docs/core/` |
| **Kairos Implementation** | Client solution on Kairos Platform | `.docs/<client-name>/` |
| **Other Implementation** | Non-Kairos projects (data, integration) | `.docs/<client-name>/` |

**⚠️ Forked Repos:** If you forked a Kairos Core repo, don't modify `.docs/core/`. Create your client docs in `.docs/<client-name>/` instead.

---

## AI Instruction Files

| File | Purpose | Output |
|------|---------|--------|
| **AI_INSTRUCTIONS-0-starter-requirements.md** | New project requirements capture | `{docs_path}/starter-requirements.md` |
| **AI_INSTRUCTIONS-1-HLSD.md** | High-Level Solution Design generation | `{docs_path}/1-HLSD/version*/` |
| **AI_INSTRUCTIONS-2-HLSD-PDF.md** | HLSD PDF generation | `{docs_path}/1-HLSD/version*/pdf-output/` |
| **AI_INSTRUCTIONS-3-DSD.md** | Detailed Solution Design generation | `{docs_path}/2-DSD/version*/` |
| **AI_INSTRUCTIONS-4-DSD-IssueCreation.md** | GitHub issues from user stories | GitHub Issues |
| **AI_INSTRUCTIONS-8-ChangeRequest.md** | Change request capture | `{docs_path}/8-changes/change-*.md` |
| **AI_INSTRUCTIONS-9-BugReport.md** | Bug report capture | `{docs_path}/9-bugs/bug-*.md` |

> `{docs_path}` = `.docs/core/` or `.docs/<client-name>/` based on project type

## Workflow Decision Tree

```
New requirement or issue?
│
├─ FIRST: Determine project type
│         → Kairos Core? → docs_path = .docs/core/
│         → Client project? → docs_path = .docs/<client-name>/
│
├─ Check if {docs_path}/1-HLSD exists?
│
├─ NO  → NEW PROJECT
│        1. Use: AI_INSTRUCTIONS-0-starter-requirements.md
│           Output: {docs_path}/starter-requirements.md
│        2. Add reference materials to: {docs_path}/0-reference-material/
│           (diagrams, existing docs, specs, etc.)
│        3. Use: AI_INSTRUCTIONS-1-HLSD.md
│           (AI will check reference materials for context)
│
└─ YES → EXISTING PROJECT
         Ask: Bug or Change?
         │
         ├─ BUG → Use: AI_INSTRUCTIONS-9-BugReport.md
         │        Output: {docs_path}/9-bugs/bug-{timestamp}.md
         │
         └─ CHANGE → Use: AI_INSTRUCTIONS-8-ChangeRequest.md
                      Output: .docs/8-changes/change-{timestamp}.md
```

## 📁 Reference Materials

When creating a new HLSD, you can provide supporting documentation in `{docs_path}/0-reference-material/`:

**Supported Materials:**
- Requirements diagrams (PlantUML, draw.io, images)
- Existing architectural diagrams or documentation
- API specifications (OpenAPI, Swagger, Postman collections)
- Data models or database schemas
- Integration contracts or interface definitions
- Compliance documentation
- Any other relevant reference materials

**How AI Uses This:**
- The AI will check this folder before generating the HLSD
- Reference materials provide context for design decisions
- Helps maintain consistency with existing systems
- Reduces back-and-forth clarification questions

---

## �️ Prerequisites

**Required VS Code Extension:**

The SmartCoding AI instructions generate Mermaid diagrams for architecture visualization (C4 models, sequence diagrams, etc.). To preview these diagrams in VS Code:

**Install:** [Markdown Preview Mermaid Support](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid)

```bash
# Via VS Code command palette (Ctrl+Shift+P / Cmd+Shift+P)
ext install bierner.markdown-mermaid

# Or search in Extensions view
```

**Why it's needed:**
- HLSD and DSD documentation include Mermaid diagrams embedded in Markdown
- Without this extension, you'll see raw Mermaid code instead of rendered diagrams
- Essential for reviewing architecture diagrams during design validation

---

## �🔄 Updating SmartCoding AI Instructions

The `.smartcoding/` folder is maintained in the template repository and can be updated using Git subtree.

### First-Time Setup (Choose One Method)

**Method 1: Automated Setup Script (Recommended)**

Run the included setup script to automatically configure the remote:

```bash
# PowerShell (Windows)
.\.smartcoding\setup-subtree.ps1

# Bash (Linux/Mac)
chmod +x .smartcoding/setup-subtree.sh
./.smartcoding/setup-subtree.sh
```

**Method 2: GitHub Action**

Trigger the workflow manually from the Actions tab:
1. Go to **Actions** → **Setup SmartCoding Subtree**
2. Click **Run workflow**
3. Click **Run workflow** (use defaults)

**Method 3: Manual Setup**

```bash
# Add the template repo as a remote
git remote add smartcoding-template https://github.com/Cnext-eu/smartcoding-kairos-template.git

# Verify the remote was added
git remote -v
```

### Pull Latest Updates

**Option 1: Pull Latest Version (from smartcoding-only branch)**

```bash
# Pull the latest AI instructions from smartcoding-only branch
git subtree pull --prefix=.smartcoding smartcoding-template smartcoding-only --squash

# Review changes
git diff HEAD~1 .smartcoding/

# Commit if satisfied
git commit -m "chore: update smartcoding AI instructions to latest"
git push origin main
```

**Option 2: Pull Specific Version (Recommended for Stability)**

```bash
# Check available versions at:
# https://github.com/Cnext-eu/smartcoding-kairos-template/tags

# Pull a specific tagged version
git subtree pull --prefix=.smartcoding smartcoding-template smartcoding-v1.1.0 --squash

# Review changes
git diff HEAD~1 .smartcoding/

# Commit
git commit -m "chore: update smartcoding AI instructions to v1.1.0"
git push origin main
```

### Check Current Version

```bash
# View the current version
cat .smartcoding/VERSION

# View recent changes
cat .smartcoding/CHANGELOG.md
```

### Update Schedule

**Recommended**: Check for updates bi-weekly (every 2 weeks)

New versions are released approximately every 2 weeks with:
- New AI instruction files
- Enhanced workflows
- Bug fixes and improvements
- Documentation updates

### Before Updating

1. **Check the CHANGELOG**: Review what's new in `.smartcoding/CHANGELOG.md` or on GitHub releases
2. **Test in a branch**: Consider pulling updates to a feature branch first
3. **Review changes**: Use `git diff` to see what's changed before committing

```bash
# Update in a branch (safer approach)
git checkout -b update-smartcoding
git subtree pull --prefix=.smartcoding smartcoding-template smartcoding-v1.1.0 --squash
# Test, review
git checkout main
git merge update-smartcoding
```

### Troubleshooting

**Error: "fatal: refusing to merge unrelated histories"**
```bash
# Add --allow-unrelated-histories flag
git subtree pull --prefix=.smartcoding smartcoding-template main --squash --allow-unrelated-histories
```

**Want to see what changed without pulling?**
```bash
# Fetch changes first
git fetch smartcoding-template

# View differences between current and latest
git diff HEAD:.smartcoding smartcoding-template/main:.smartcoding
```

**Conflicts during subtree pull?**
```bash
# Resolve conflicts manually in .smartcoding/ folder
# Then complete the merge
git add .smartcoding/
git commit -m "chore: update smartcoding AI instructions (resolved conflicts)"
```

---

## 🤝 Contributing Improvements

If you've made improvements to the AI instructions that could benefit all projects:

### 1. Create a Contribution Branch

```bash
# Make your improvements to files in .smartcoding/
# Then push to a contribution branch in the template repo
git subtree push --prefix=.smartcoding smartcoding-template contribution-from-{your-project-name}
```

### 2. Create Pull Request

- Go to https://github.com/Cnext-eu/smartcoding-kairos-template
- Create a pull request from your contribution branch
- Describe the improvements and why they're beneficial
- Wait for review and approval

### 3. After Merge

Once merged and a new version is released, you can pull the official update:

```bash
git subtree pull --prefix=.smartcoding smartcoding-template main --squash
```

---

## 📋 Version History

See [CHANGELOG.md](./CHANGELOG.md) for detailed version history.

### Current Version: 1.0.0

Initial release with complete AI instruction workflows for:
- New project requirements capture
- HLSD and DSD generation
- PDF generation
- GitHub issue creation
- Bug reporting
- Change request management

---

## 🔗 Resources

- **Template Repository**: https://github.com/Cnext-eu/smartcoding-kairos-template
- **Issues & Feedback**: https://github.com/Cnext-eu/smartcoding-kairos-template/issues
- **Releases**: https://github.com/Cnext-eu/smartcoding-kairos-template/releases

---

## 📝 Notes

- **Do NOT edit** files in `.smartcoding/` directly in child repos unless contributing back
- **Local modifications** will be overwritten when pulling updates
- **Custom workflows**: If you need project-specific AI instructions, create them in `.docs/` instead
- **Version pinning**: Use specific version tags for production stability

## Support

For questions or issues with SmartCoding AI instructions:
1. Check the [CHANGELOG.md](./CHANGELOG.md)
2. Review [GitHub Issues](https://github.com/Cnext-eu/smartcoding-kairos-template/issues)
3. Contact the SmartCoding maintainers
