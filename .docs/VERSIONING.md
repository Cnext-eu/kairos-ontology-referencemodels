# Version Management Guide

This document outlines the versioning and changelog practices for the SmartCoding HLSD Template.

## Versioning Strategy

This project follows [Semantic Versioning 2.0.0](https://semver.org/):

### Version Format: `MAJOR.MINOR.PATCH`

- **MAJOR** version: Incompatible changes, breaking API changes
  - Example: Restructuring the template folder hierarchy
  - Example: Removing or renaming required documents
  
- **MINOR** version: New features, backward-compatible additions
  - Example: Adding new optional documents
  - Example: New AI assistant capabilities
  - Example: Enhanced PDF generation features
  
- **PATCH** version: Bug fixes, backward-compatible fixes
  - Example: Fixing typos in templates
  - Example: Correcting PlantUML syntax
  - Example: Fixing PDF generation issues

### Pre-release Versions

For development and testing:
- `1.1.0-alpha.1` - Early testing
- `1.1.0-beta.1` - Feature complete, testing
- `1.1.0-rc.1` - Release candidate

## Changelog Management

### File Location
- **CHANGELOG.md** at project root
- Updated with every release

### Format
Follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format with these categories:

- **Added** - New features and capabilities
- **Changed** - Changes in existing functionality
- **Deprecated** - Features to be removed in future
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security vulnerability fixes
- **Documentation** - Documentation updates

### Unreleased Section
Keep an `[Unreleased]` section at the top for work in progress:

```markdown
## [Unreleased]

### Added
- New feature X

### Fixed
- Bug in component Y
```

## Commit Message Convention

Use [Conventional Commits](https://www.conventionalcommits.org/) for automated changelog generation:

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat:` - New feature (triggers MINOR version bump)
- `fix:` - Bug fix (triggers PATCH version bump)
- `docs:` - Documentation only changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `test:` - Adding or updating tests
- `build:` - Build system changes
- `ci:` - CI/CD changes
- `chore:` - Other changes (dependencies, etc.)
- `revert:` - Reverting previous commit

### Breaking Changes
Add `BREAKING CHANGE:` in footer or `!` after type (triggers MAJOR version bump):

```
feat!: restructure template folder hierarchy

BREAKING CHANGE: Template folders have been reorganized.
Users must migrate existing projects to new structure.
```

### Examples
```bash
# Feature (MINOR bump)
git commit -m "feat(templates): add deployment plan template"

# Bug fix (PATCH bump)
git commit -m "fix(pdf): correct PlantUML rendering issue"

# Breaking change (MAJOR bump)
git commit -m "feat(structure)!: change HLSD folder organization

BREAKING CHANGE: HLSD documents moved from flat structure to categorized folders"

# Documentation
git commit -m "docs(readme): update quick start guide"
```

## Release Process

### Manual Release

1. **Update VERSION file**
   ```
   1.2.0
   ```

2. **Update CHANGELOG.md**
   - Move items from `[Unreleased]` to new version section
   - Add release date
   - Update comparison links

3. **Commit and Tag**
   ```bash
   git add VERSION CHANGELOG.md
   git commit -m "chore(release): 1.2.0"
   git tag -a v1.2.0 -m "Release version 1.2.0"
   git push origin main --tags
   ```

### Automated Release (Optional)

For Node.js projects, use `standard-version`:

```bash
# Install
npm install --save-dev standard-version

# Add to package.json scripts
"scripts": {
  "release": "standard-version",
  "release:minor": "standard-version --release-as minor",
  "release:major": "standard-version --release-as major",
  "release:patch": "standard-version --release-as patch"
}

# Run release
npm run release
```

The `.versionrc.json` file configures the automated release behavior.

## Version File

The `VERSION` file at the root contains the current version number:
- Plain text format
- Single line with semantic version
- Updated during release process
- Used by automation tools

## Best Practices

### DO
✅ Update changelog with every significant change  
✅ Use conventional commit messages  
✅ Tag releases in Git with `v` prefix (e.g., `v1.2.0`)  
✅ Keep unreleased changes in changelog  
✅ Write clear, user-focused changelog entries  
✅ Increment version appropriately based on changes  
✅ Create GitHub releases with changelog excerpts  

### DON'T
❌ Skip versioning for "small" changes  
❌ Reuse version numbers  
❌ Make breaking changes in MINOR/PATCH versions  
❌ Use vague changelog entries ("various fixes")  
❌ Forget to update VERSION file  
❌ Create tags without annotated messages  
❌ Mix multiple change types in one commit  

## Hotfix Process

For urgent production fixes:

1. Create hotfix branch from latest tag:
   ```bash
   git checkout -b hotfix/1.2.1 v1.2.0
   ```

2. Make fix and commit:
   ```bash
   git commit -m "fix(critical): resolve security vulnerability"
   ```

3. Update VERSION and CHANGELOG:
   - Bump PATCH version
   - Document the fix

4. Merge and tag:
   ```bash
   git checkout main
   git merge hotfix/1.2.1
   git tag -a v1.2.1 -m "Hotfix: Security vulnerability"
   git push origin main --tags
   ```

## FAQ

**Q: When should I bump the MAJOR version?**  
A: When you make changes that break existing workflows or require users to modify their usage.

**Q: Should I version the generated HLSD documents?**  
A: The template itself is versioned. Individual HLSD instances use timestamped folders for their own versioning.

**Q: How do I handle multiple changes in one release?**  
A: Group them by type in the changelog. Version bump should reflect the highest-impact change.

**Q: What if I forgot to update the changelog?**  
A: Update it in the next commit with retroactive entries for the missed changes.

## References

- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [standard-version](https://github.com/conventional-changelog/standard-version)
