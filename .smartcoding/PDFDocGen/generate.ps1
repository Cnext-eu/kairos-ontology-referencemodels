# PowerShell script to generate PDFs from markdown files
# HLSD Documentation - SmartCoding PDFDocGen Tool
# Location: .smartcoding/PDFDocGen/

# Prompt for project name with default suggestion
Write-Host "HLSD Documentation - PDF Generator" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

$projectName = Read-Host "Enter project short name (default: kidslife)"
if ([string]::IsNullOrWhiteSpace($projectName)) {
    $projectName = "kidslife"
}

Write-Host ""
Write-Host "Generating PDFs for project: $projectName" -ForegroundColor Green
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.8 or later." -ForegroundColor Red
    Write-Host "  Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check if virtual environment exists
$venvPath = Join-Path $PSScriptRoot "venv"
if (-not (Test-Path $venvPath)) {
    Write-Host ""
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $venvPath
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
& $activateScript

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
$requirementsFile = Join-Path $PSScriptRoot "requirements.txt"
pip install -q -r $requirementsFile

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Run the PDF generator
Write-Host ""
Write-Host "Generating PDFs..." -ForegroundColor Yellow
Write-Host ""

$scriptPath = Join-Path $PSScriptRoot "generate_pdfs.py"

# Check command line arguments and add project name
if ($args.Count -gt 0) {
    python $scriptPath --project $projectName @args
} else {
    # Default: generate all
    python $scriptPath --project $projectName
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=============================" -ForegroundColor Cyan
    Write-Host "✓ PDF generation complete!" -ForegroundColor Green
    Write-Host ""
    
    # Find latest version folder and open its pdf-output directory
    $hlsdDir = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) "1-HLSD"
    $versionFolders = Get-ChildItem -Path $hlsdDir -Directory -Filter "version*" | Sort-Object Name
    if ($versionFolders) {
        $latestVersion = $versionFolders[-1]
        $outputDir = Join-Path $latestVersion.FullName "pdf-output"
        if (Test-Path $outputDir) {
            Write-Host "Opening output directory: .docs/1-HLSD/$($latestVersion.Name)/pdf-output" -ForegroundColor Cyan
            Invoke-Item $outputDir
        }
    }
} else {
    Write-Host ""
    Write-Host "✗ PDF generation failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
