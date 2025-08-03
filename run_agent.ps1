<#!
.SYNOPSIS
    Start the ORALLM agent API using the local virtual environment.
#>
param(
    [int]$Port = 8000
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
$venv = Join-Path $root ".venv"
& "$venv\\Scripts\\uvicorn.exe" main:app --host 0.0.0.0 --port $Port
