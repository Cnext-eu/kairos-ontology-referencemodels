# Repo Copilot Instructions

This repository follows the org-wide Copilot rules:
https://github.com/Cnext-eu/smartcoding-kairos-template/blob/5dfd7c0cd01b97933004ecdcbd993f4925b2311c/.github/base-instructions.md

Always apply those rules first.

---

## Domain Context (Repo-Specific)

// need to refer to domain specific md files of kairos product docs


---

## Technical Context


---

## Release Process

When creating a new version release:

1. **Update VERSION file** - Bump the version number (e.g., 1.2.0 → 1.3.0)
2. **Update CHANGELOG.md** - Add new version section with changes
3. **Commit changes** - Use semantic commit message (e.g., "chore: release v1.3.0 - description")
4. **Create GitHub Release**:
   - Go to GitHub repository → Releases → Create new release
   - Tag version: `v1.3.0` (matching VERSION file)
   - Release title: `v1.3.0`
   - **Mark as latest release** (check the box)
   - Copy changelog content to release notes
   - Publish release

---

End of repo instructions.
