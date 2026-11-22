[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$RepositoryPath,

    [string]$CommitMessage = "Add ShelfSense retail inventory analytics project"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$ExpectedRemotes = @(
    "https://github.com/Timesyou/retail-sales-sql-python-analysis.git",
    "https://github.com/Timesyou/retail-sales-sql-python-analysis",
    "git@github.com:Timesyou/retail-sales-sql-python-analysis.git",
    "git@github.com:Timesyou/retail-sales-sql-python-analysis"
)

if (-not (Test-Path -LiteralPath $RepositoryPath -PathType Container)) {
    throw "Repository folder does not exist: $RepositoryPath"
}

$RepositoryPath = (Resolve-Path -LiteralPath $RepositoryPath).Path
& git -C $RepositoryPath rev-parse --is-inside-work-tree *> $null
if ($LASTEXITCODE -ne 0) {
    throw "The target folder is not a Git repository. Clone the repository first."
}

$Remote = (& git -C $RepositoryPath remote get-url origin).Trim()
if ($LASTEXITCODE -ne 0 -or $Remote -notin $ExpectedRemotes) {
    throw "Safety check failed. origin must point to Timesyou/retail-sales-sql-python-analysis. Found: $Remote"
}

$Branch = (& git -C $RepositoryPath branch --show-current).Trim()
if ($LASTEXITCODE -ne 0 -or $Branch -ne "main") {
    throw "Expected the existing repository's main branch. Current branch: $Branch"
}

$Before = & git -C $RepositoryPath status --porcelain
if ($LASTEXITCODE -ne 0) {
    throw "Could not inspect Git working-tree status."
}
if ($Before) {
    throw "The target repository has uncommitted changes. Commit or stash them first; this script will not overwrite existing work."
}

Write-Host "Copying ShelfSense project files into $RepositoryPath" -ForegroundColor Cyan
$ExcludedDirectories = @(".git", ".venv", "venv", "__pycache__", "build", "dist", ".pytest_cache")
Get-ChildItem -LiteralPath $ProjectRoot -Force | Where-Object {
    $_.Name -notin $ExcludedDirectories -and -not $_.Name.EndsWith(".egg-info")
} | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $RepositoryPath -Recurse -Force
}

& git -C $RepositoryPath add --all
if ($LASTEXITCODE -ne 0) {
    throw "git add failed. No push was attempted."
}

$Staged = & git -C $RepositoryPath diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "No changes to publish; the repository already matches this project." -ForegroundColor Yellow
    exit 0
}
if ($LASTEXITCODE -ne 1) {
    throw "Could not inspect staged changes. No push was attempted."
}

& git -C $RepositoryPath commit -m $CommitMessage
if ($LASTEXITCODE -ne 0) {
    throw "git commit failed. Check your Git identity and retry. No push was attempted."
}

& git -C $RepositoryPath push origin main
if ($LASTEXITCODE -ne 0) {
    throw "Push failed. The local commit is preserved; review the Git error before retrying."
}

Write-Host "ShelfSense was pushed to https://github.com/Timesyou/retail-sales-sql-python-analysis" -ForegroundColor Green
