# SmartCoding AI Instructions - Changelog

All notable changes to the SmartCoding AI instruction files will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Action to automatically update `smartcoding-only` branch when `.smartcoding/` changes
- Manual script `update-smartcoding-branch.ps1` for updating smartcoding-only branch

### Fixed
- Subtree pull now correctly pulls only `.smartcoding/` folder contents, not entire template repo
- Created dedicated `smartcoding-only` branch for clean subtree operations
- Added write permissions to GitHub Action workflow for branch push operations

## [1.0.0] - 2026-02-01

### Added
- **AI_INSTRUCTIONS-0-starter-requirements.md**: New project requirements capture workflow
- **AI_INSTRUCTIONS-1-HLSD.md**: High-Level Solution Design generation workflow
- **AI_INSTRUCTIONS-2-HLSD-PDF.md**: PDF generation workflow for HLSD documents
- **AI_INSTRUCTIONS-3-DSD.md**: Detailed Solution Design generation workflow
- **AI_INSTRUCTIONS-4-DSD-IssueCreation.md**: GitHub issue creation workflow from user stories
- **AI_INSTRUCTIONS-8-ChangeRequest.md**: Change request capture workflow for existing projects
- **AI_INSTRUCTIONS-9-BugReport.md**: Bug report capture workflow for existing projects
- Kairos platform reference documentation (v0.4)
- Example starter-requirements.md template
- Reference materials for AI-assisted development

### Features
- Scenario-based workflow detection (new project vs bug vs change request)
- Todo list tracking for all workflows
- Comprehensive templates for all document types
- Senior Business Analyst persona for requirements
- Senior QA Analyst persona for bug reports
- Semantic versioning and changelog tracking
- Bi-weekly release cycle

### Documentation
- VERSION file for tracking releases
- CHANGELOG.md for version history
- README.md with update instructions for child repositories

---

## Version History Guidelines

### Version Format
**MAJOR.MINOR.PATCH** (following Semantic Versioning)

- **MAJOR**: Breaking changes to AI instructions, workflow restructuring, incompatible changes
- **MINOR**: New AI instruction files, new features, workflow enhancements, backward-compatible additions
- **PATCH**: Bug fixes, typos, clarifications, documentation improvements

### Release Tags
Format: `smartcoding-v1.0.0`

### Release Cycle
Bi-weekly releases every other Friday
