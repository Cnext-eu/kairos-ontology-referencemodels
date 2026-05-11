<div align="center">

# Project Name

**Brief description of your project**

</div>

---

## 🚀 Getting Started

Follow the **Cnext SmartCoding** workflow with your AI assistant:
see  [.docs\README.md](.docs\README.md) for more instructions

---

## 🔄 Updating SmartCoding AI Instructions

This project uses AI instruction files from the `.smartcoding/` folder. These files are maintained in the template repository and can be updated using Git subtree.

**Current SmartCoding Version**: See [.smartcoding/VERSION](.smartcoding/VERSION)

### First-Time Setup

**Option 1: Run Setup Script (Easiest)**

```bash
# PowerShell (Windows)
.\.smartcoding\setup-subtree.ps1

# Bash (Linux/Mac)
chmod +x .smartcoding/setup-subtree.sh
./.smartcoding/setup-subtree.sh
```

**Option 2: GitHub Action**
- Go to **Actions** → **Setup SmartCoding Subtree** → **Run workflow**

**Option 3: Manual**
```bash
git remote add smartcoding-template https://github.com/Cnext-eu/smartcoding-kairos-template.git
```

### Pull Updates (Bi-Weekly Recommended)

```bash
# Pull latest AI instructions (from smartcoding-only branch)
git subtree pull --prefix=.smartcoding smartcoding-template smartcoding-only --squash

# Or pull a specific version (safer)
git subtree pull --prefix=.smartcoding smartcoding-template smartcoding-v1.1.0 --squash

# Commit and push
git commit -m "chore: update smartcoding AI instructions"
git push
```

**Full instructions**: See [.smartcoding/README.md](.smartcoding/README.md)

**Version history**: See [.smartcoding/CHANGELOG.md](.smartcoding/CHANGELOG.md)
