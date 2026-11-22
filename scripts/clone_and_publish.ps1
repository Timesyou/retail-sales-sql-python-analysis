[CmdletBinding()]
param(
    [string]$RepositoryPath = (Join-Path $HOME "source\retail-sales-sql-python-analysis")
)

$ErrorActionPreference = "Stop"
$Remote = "https://github.com/Timesyou/retail-sales-sql-python-analysis.git"
$Publisher = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "publish_to_github.ps1"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git was not found. Install Git for Windows and retry."
}

if (-not (Test-Path -LiteralPath $RepositoryPath)) {
    $Parent = Split-Path -Parent $RepositoryPath
    if ($Parent -and -not (Test-Path -LiteralPath $Parent)) {
        New-Item -ItemType Directory -Path $Parent -Force | Out-Null
    }
    Write-Host "Cloning $Remote into $RepositoryPath" -ForegroundColor Cyan
    & git clone $Remote $RepositoryPath
    if ($LASTEXITCODE -ne 0) {
        throw "Clone failed. Check network access and the target folder."
    }
}

& $Publisher -RepositoryPath $RepositoryPath
if ($LASTEXITCODE -ne 0) {
    throw "Publishing did not complete. Review the Git message above."
}
