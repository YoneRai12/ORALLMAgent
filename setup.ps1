<#!
.SYNOPSIS
    Set up a disposable Windows environment for the ORALLM agent.
.DESCRIPTION
    - Installs Python (using winget) if missing
    - Clones the ORALLMAgent repository
    - Creates a virtual environment and installs dependencies
    - Generates a blank .env file for later secrets
    The script assumes a Windows 10/11 VM with ~4 CPU cores, 30GB disk and
    10GB RAM.
#>
param(
    [string]$RepoUrl = "https://github.com/ORALLMAgent/ORALLMAgent.git",
    [string]$InstallDir = "$env:USERPROFILE\\orallm_agent"
)
$ErrorActionPreference = "Stop"

# Install Python if not available
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python not found. Installing via winget..."
    winget install -e --id Python.Python.3.11 --source winget -h
}

# Clone or update repository
if (-not (Test-Path $InstallDir)) {
    git clone $RepoUrl $InstallDir
} else {
    Write-Host "Repository already exists. Pulling latest changes..."
    git -C $InstallDir pull
}

# Create virtual environment
$venv = Join-Path $InstallDir ".venv"
if (-not (Test-Path $venv)) {
    python -m venv $venv
}

# Install dependencies
& "$venv\\Scripts\\pip.exe" install --upgrade pip
& "$venv\\Scripts\\pip.exe" install -r (Join-Path $InstallDir "requirements.txt")

# Prepare .env file
$envFile = Join-Path $InstallDir ".env"
if (-not (Test-Path $envFile)) {
    Copy-Item (Join-Path $InstallDir ".env.example") $envFile
    Write-Host "Created template .env at $envFile"
}

Write-Host "Setup complete. Activate the environment with:"
Write-Host "`t$venv\\Scripts\\activate"
Write-Host "Then run: uvicorn main:app --host 0.0.0.0 --port 8000"
