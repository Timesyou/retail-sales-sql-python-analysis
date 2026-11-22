[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$Python = Get-Command python -ErrorAction SilentlyContinue
if (-not $Python) {
    throw "Python was not found. Install Python 3.10 or later and make sure python.exe is on PATH."
}

$VersionText = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if ($LASTEXITCODE -ne 0) {
    throw "Could not read the Python version."
}
$Parts = $VersionText.Split('.')
$Major = [int]$Parts[0]
$Minor = [int]$Parts[1]
if ($Major -lt 3 -or (($Major -eq 3) -and ($Minor -lt 10))) {
    throw "ShelfSense requires Python 3.10 or later. Found $VersionText."
}

Push-Location $ProjectRoot
try {
    & python -m pip install --editable .
    if ($LASTEXITCODE -ne 0) { throw "Package installation failed." }

    & python -m shelfsense --sales data/sales.csv --inventory data/inventory.csv --output demo-output
    if ($LASTEXITCODE -ne 0) { throw "The demonstration run failed." }

    Start-Process (Join-Path $ProjectRoot "demo-output\dashboard.html")
    Write-Host "ShelfSense demo completed. Reports are in demo-output." -ForegroundColor Green
}
finally {
    Pop-Location
}
