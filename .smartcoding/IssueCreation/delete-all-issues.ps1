# PowerShell script to delete all GitHub issues
# This script activates the virtual environment and runs delete-all-issues.py

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "GitHub Issues Deletion Tool" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Find the venv directory (could be in parent tools folder or current folder)
$venvPath = $null
$possibleVenvPaths = @(
    "..\venv",
    "..\..\venv",
    "venv"
)

foreach ($path in $possibleVenvPaths) {
    $testPath = Join-Path $PSScriptRoot $path
    if (Test-Path $testPath) {
        $venvPath = $testPath
        break
    }
}

if (-not $venvPath) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create a virtual environment first:" -ForegroundColor Yellow
    Write-Host "  python -m venv ..\venv" -ForegroundColor Yellow
    Write-Host "  ..\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Using virtual environment: $venvPath" -ForegroundColor Green
Write-Host ""

# Activate virtual environment
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
if (-not (Test-Path $activateScript)) {
    Write-Host "ERROR: Virtual environment activation script not found at:" -ForegroundColor Red
    Write-Host "  $activateScript" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& $activateScript

# Check if GitHub CLI is installed
try {
    $ghVersion = gh --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "GitHub CLI not found"
    }
    Write-Host "GitHub CLI: $($ghVersion[0])" -ForegroundColor Green
} catch {
    Write-Host "ERROR: GitHub CLI (gh) is not installed!" -ForegroundColor Red
    Write-Host "Please install it from: https://cli.github.com/" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check GitHub authentication
Write-Host "Checking GitHub authentication..." -ForegroundColor Yellow
$null = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Not authenticated with GitHub!" -ForegroundColor Red
    Write-Host "Please run: gh auth login" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ Authenticated with GitHub" -ForegroundColor Green
Write-Host ""

# Run the Python script
$pythonScript = Join-Path $PSScriptRoot "delete-all-issues.py"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Starting deletion script..." -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

try {
    python $pythonScript
    $exitCode = $LASTEXITCODE
    
    Write-Host ""
    if ($exitCode -eq 0) {
        Write-Host "Script completed successfully." -ForegroundColor Green
    } else {
        Write-Host "Script exited with code: $exitCode" -ForegroundColor Yellow
    }
} catch {
    Write-Host ""
    Write-Host "ERROR: Script execution failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green
