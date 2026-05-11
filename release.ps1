# release.ps1
# Automates the release process: version bump, changelog update, commit, and GitHub release

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("major", "minor", "patch")]
    [string]$ReleaseType,
    
    [Parameter(Mandatory=$false)]
    [string]$Description
)

# Color functions
function Write-Success { param($msg) Write-Host $msg -ForegroundColor Green }
function Write-Info { param($msg) Write-Host $msg -ForegroundColor Cyan }
function Write-Warning { param($msg) Write-Host $msg -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host $msg -ForegroundColor Red }

# Check if we're in a git repository
if (-not (Test-Path ".git")) {
    Write-Error "Error: Not in a git repository"
    exit 1
}

# Check if VERSION file exists
if (-not (Test-Path "VERSION")) {
    Write-Error "Error: VERSION file not found"
    exit 1
}

# Check if CHANGELOG.md exists
if (-not (Test-Path "CHANGELOG.md")) {
    Write-Error "Error: CHANGELOG.md not found"
    exit 1
}

# Check for uncommitted changes
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Error "Error: You have uncommitted changes. Please commit or stash them first."
    git status --short
    exit 1
}

# Read current version
$currentVersion = (Get-Content "VERSION" -Raw).Trim()
Write-Info "Current version: $currentVersion"

# Parse version
if ($currentVersion -notmatch '^(\d+)\.(\d+)\.(\d+)$') {
    Write-Error "Error: Invalid version format in VERSION file. Expected: major.minor.patch"
    exit 1
}

$major = [int]$matches[1]
$minor = [int]$matches[2]
$patch = [int]$matches[3]

# Ask for release type if not provided
if (-not $ReleaseType) {
    Write-Host ""
    Write-Host "Select release type:" -ForegroundColor Yellow
    Write-Host "  1. Major (breaking changes) - $major.$minor.$patch → $($major+1).0.0"
    Write-Host "  2. Minor (new features) - $major.$minor.$patch → $major.$($minor+1).0"
    Write-Host "  3. Patch (bug fixes) - $major.$minor.$patch → $major.$minor.$($patch+1)"
    Write-Host ""
    
    $choice = Read-Host "Enter choice (1/2/3)"
    
    switch ($choice) {
        "1" { $ReleaseType = "major" }
        "2" { $ReleaseType = "minor" }
        "3" { $ReleaseType = "patch" }
        default {
            Write-Error "Invalid choice"
            exit 1
        }
    }
}

# Calculate new version
switch ($ReleaseType) {
    "major" {
        $newVersion = "$($major+1).0.0"
        $changeType = "Breaking Changes"
    }
    "minor" {
        $newVersion = "$major.$($minor+1).0"
        $changeType = "New Features"
    }
    "patch" {
        $newVersion = "$major.$minor.$($patch+1)"
        $changeType = "Bug Fixes"
    }
}

Write-Info "New version: $newVersion"

# Ask for description if not provided
if (-not $Description) {
    Write-Host ""
    $Description = Read-Host "Enter release description (brief summary of changes)"
    if (-not $Description) {
        Write-Error "Error: Description is required"
        exit 1
    }
}

# Confirm before proceeding
Write-Host ""
Write-Warning "This will:"
Write-Host "  - Update VERSION to $newVersion"
Write-Host "  - Update CHANGELOG.md"
Write-Host "  - Commit changes with: 'chore: release v$newVersion - $Description'"
Write-Host "  - Create GitHub release v$newVersion (marked as latest)"
Write-Host ""

$confirm = Read-Host "Proceed? (yes/no)"
if ($confirm -notmatch '^(yes|y)$') {
    Write-Info "Release cancelled"
    exit 0
}

Write-Host ""
Write-Info "Starting release process..."

# Update VERSION files (root and .smartcoding)
Write-Info "Updating VERSION files..."
Set-Content -Path "VERSION" -Value $newVersion -NoNewline

# Also update .smartcoding/VERSION if it exists
if (Test-Path ".smartcoding\VERSION") {
    Set-Content -Path ".smartcoding\VERSION" -Value $newVersion -NoNewline
    Write-Success "✓ VERSION files updated to $newVersion"
} else {
    Write-Success "✓ VERSION updated to $newVersion"
}

# Update CHANGELOG.md
Write-Info "Updating CHANGELOG.md..."
$changelog = Get-Content "CHANGELOG.md" -Raw
$today = Get-Date -Format "yyyy-MM-dd"

$newEntry = @"
## [Unreleased]

## [$newVersion] - $today

### $changeType
- $Description

"@

$changelog = $changelog -replace '## \[Unreleased\]', $newEntry
Set-Content -Path "CHANGELOG.md" -Value $changelog -NoNewline
Write-Success "✓ CHANGELOG.md updated"

# Commit changes
Write-Info "Committing changes..."
git add VERSION CHANGELOG.md .smartcoding\VERSION
git commit -m "chore: release v$newVersion - $Description"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Error: Failed to commit changes"
    exit 1
}
Write-Success "✓ Changes committed"

# Push to remote
Write-Info "Pushing to remote..."
git push
if ($LASTEXITCODE -ne 0) {
    Write-Error "Error: Failed to push to remote"
    exit 1
}
Write-Success "✓ Pushed to remote"

# Read changelog entry for release notes
$changelogContent = Get-Content "CHANGELOG.md" -Raw
if ($changelogContent -match "(?s)## \[$newVersion\].*?(?=## \[|$)") {
    $releaseNotes = $matches[0].Trim()
} else {
    $releaseNotes = "Release v$newVersion`n`n$Description"
}

# Create GitHub release
Write-Info "Creating GitHub release..."
$tempFile = New-TemporaryFile
Set-Content -Path $tempFile -Value $releaseNotes

gh release create "v$newVersion" `
    --title "v$newVersion" `
    --notes-file $tempFile `
    --latest

Remove-Item $tempFile

if ($LASTEXITCODE -ne 0) {
    Write-Error "Error: Failed to create GitHub release"
    Write-Warning "Version has been committed and pushed. You may need to create the release manually."
    exit 1
}

Write-Success "✓ GitHub release created"

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Release v$newVersion completed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Info "Summary:"
Write-Host "  Version: $currentVersion → $newVersion"
Write-Host "  Type: $ReleaseType ($changeType)"
Write-Host "  Description: $Description"
Write-Host ""
Write-Success "All done! 🎉"
