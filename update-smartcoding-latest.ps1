# update-smartcoding-latest.ps1
# Fetches the .smartcoding folder and related files from the smartcoding-kairos-template repository

param(
    [string]$RepoUrl = "https://github.com/Cnext-eu/smartcoding-kairos-template.git",
    [string]$RepoOwner = "Cnext-eu",
    [string]$RepoName = "smartcoding-kairos-template",
    [string]$Branch,  # If not specified, will use latest release tag
    [switch]$SkipSelfUpdateCheck  # Prevents infinite loop on re-run
)

# Files and folders to sync from template
$itemsToSync = @(
    ".smartcoding",
    ".github/base-instructions.md",
    ".github/copilot-instructions.md",
    ".github/workflows/sync-odoo-userstory.yml",
    ".github/workflows/sync-odoo-initialize-project.yml",
    "update-smartcoding-latest.ps1"
)

# Sparse checkout patterns (need leading / for no-cone mode)
$sparseCheckoutPatterns = @(
    "/.smartcoding/",
    "/.github/",
    "/update-smartcoding-latest.ps1"
)

# Track if script itself was updated
$scriptUpdated = $false
# Update script at its actual location (not just cwd)
$currentScriptPath = Join-Path $PSScriptRoot "update-smartcoding-latest.ps1"
$currentScriptHash = $null

# Get hash of current script (if exists)
if (Test-Path $currentScriptPath) {
    $currentScriptHash = (Get-FileHash $currentScriptPath -Algorithm MD5).Hash
}

# Temporary directory (fallback to ~/tmp if TEMP env var is not set, e.g. on Linux)
$tempBase = if ($env:TEMP) { $env:TEMP }
            elseif ($env:TMPDIR) { $env:TMPDIR }
            elseif ($env:TMP) { $env:TMP }
            elseif (Test-Path "/tmp") { "/tmp" }
            else { Join-Path $HOME "tmp" }

if (-not (Test-Path $tempBase)) {
    New-Item -ItemType Directory -Path $tempBase -Force | Out-Null
}

$tempDir = Join-Path $tempBase "smartcoding-temp-$(Get-Date -Format 'yyyyMMddHHmmss')"

try {
    # Check for latest release if no branch specified
    if (-not $Branch) {
        Write-Host "Checking for latest release..." -ForegroundColor Cyan
        
        try {
            $releaseInfo = gh api "repos/$RepoOwner/$RepoName/releases/latest" | ConvertFrom-Json
            $Branch = $releaseInfo.tag_name
            $releaseVersion = $releaseInfo.name
            $releaseDate = $releaseInfo.published_at
            
            Write-Host "  Latest release: $releaseVersion ($Branch)" -ForegroundColor Yellow
            Write-Host "  Published: $releaseDate" -ForegroundColor Gray
        }
        catch {
            Write-Host "  No releases found, falling back to main branch" -ForegroundColor Yellow
            $Branch = "main"
        }
    }
    
    Write-Host "Cloning repository (sparse) from $Branch..." -ForegroundColor Cyan
    
    # Clone with no checkout
    git clone --filter=blob:none --no-checkout --depth 1 --branch $Branch $RepoUrl $tempDir
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to clone repository. Check your Git credentials for private repos."
    }
    
    # Configure sparse checkout (use no-cone for individual file support)
    Push-Location $tempDir
    git sparse-checkout init --no-cone
    # Pass patterns via stdin for reliable array expansion (patterns need leading /)
    $sparseCheckoutPatterns | ForEach-Object { $_ } | git sparse-checkout set --stdin
    git checkout $Branch
    Pop-Location
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to checkout files"
    }
    
    # Get version info
    $versionFile = Join-Path $tempDir ".smartcoding\VERSION"
    if (Test-Path $versionFile) {
        $version = (Get-Content $versionFile -Raw).Trim()
        Write-Host "Template version: $version" -ForegroundColor Yellow
    }
    
    # Self-update FIRST: copy this script to root if it exists in template
    $scriptSource = Join-Path $tempDir "update-smartcoding-latest.ps1"
    if (Test-Path $scriptSource) {
        Write-Host "Checking update-smartcoding-latest.ps1..." -ForegroundColor Cyan
        Copy-Item -Path $scriptSource -Destination $currentScriptPath -Force
        
        # Check if script was actually updated
        $newScriptHash = (Get-FileHash $currentScriptPath -Algorithm MD5).Hash
        if ($currentScriptHash -and ($currentScriptHash -ne $newScriptHash)) {
            $scriptUpdated = $true
            Write-Host "  Script updated!" -ForegroundColor Yellow
        } else {
            Write-Host "  Script unchanged" -ForegroundColor Gray
        }
    }
    
    # Copy each item
    foreach ($item in $itemsToSync) {
        $sourcePath = Join-Path $tempDir $item
        
        if (Test-Path $sourcePath) {
            $targetPath = $item
            
            # Check if source is a directory or file
            if (Test-Path $sourcePath -PathType Container) {
                # For directories: remove existing and copy fresh to avoid nesting
                Write-Host "Copying $item..." -ForegroundColor Cyan
                if (Test-Path $targetPath) {
                    Remove-Item $targetPath -Recurse -Force
                }
                Copy-Item -Path $sourcePath -Destination $targetPath -Recurse -Force
                Write-Host "  Updated $item" -ForegroundColor Green
            } else {
                # For files: ensure parent directory exists
                $parentDir = Split-Path $targetPath -Parent
                if ($parentDir -and -not (Test-Path $parentDir)) {
                    New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
                }
                
                Write-Host "Copying $item..." -ForegroundColor Cyan
                Copy-Item -Path $sourcePath -Destination $targetPath -Force
                Write-Host "  Updated $item" -ForegroundColor Green
            }
        } else {
            Write-Host "  Warning: $item not found in template" -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
    Write-Host "Successfully synced SmartCoding files!" -ForegroundColor Green
    
    # If script was updated and we haven't already done a re-run check, prompt user
    if ($scriptUpdated -and -not $SkipSelfUpdateCheck) {
        Write-Host ""
        Write-Host "========================================================" -ForegroundColor Yellow
        Write-Host "  The update script itself was updated!" -ForegroundColor Yellow
        Write-Host "  Please run the script ONE MORE TIME to apply latest." -ForegroundColor Yellow
        Write-Host "  Command: .\update-smartcoding-latest.ps1" -ForegroundColor Cyan
        Write-Host "========================================================" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
finally {
    # Cleanup
    if (Test-Path $tempDir) {
        Write-Host "Cleaning up..." -ForegroundColor Gray
        Remove-Item $tempDir -Recurse -Force
    }
}

Write-Host "Done!" -ForegroundColor Green
