param([Parameter(Mandatory=$true)][string]$Destination)
$ErrorActionPreference = 'Stop'
$sourceRoot = Split-Path $PSScriptRoot -Parent
$targetRoot = [IO.Path]::GetFullPath($Destination)
if (Test-Path -LiteralPath $targetRoot) {
    throw 'Choose a new, nonexistent destination. Existing folders are never overwritten.'
}
# An explicit allowlist excludes Git history, instructor work, cached outputs,
# local credentials, and future files that have not been reviewed for release.
$releaseFiles = @(
    '.gitignore', '.python-version', 'AGENTS.md', 'CLAUDE.md', 'README.md',
    'assignment.md', 'pyproject.toml', 'uv.lock', 'notebooks/README.md',
    'submission/README.md', 'starter_data/README.md',
    'starter_data/Automation Build Challenge - NA.xlsx',
    'starter_data/Automation Build Challenge - SA.xlsx',
    'starter_data/Automation Build Challenge - Managers.xlsx'
)
foreach ($relative in $releaseFiles) {
    $sourceFile = Join-Path $sourceRoot $relative
    if (-not (Test-Path -LiteralPath $sourceFile -PathType Leaf)) {
        throw "Required release file missing: $relative"
    }
}
New-Item -ItemType Directory -Path $targetRoot | Out-Null
foreach ($relative in $releaseFiles) {
    $targetFile = Join-Path $targetRoot $relative
    New-Item -ItemType Directory -Path (Split-Path $targetFile -Parent) -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $sourceRoot $relative) -Destination $targetFile
    if ((Get-FileHash -LiteralPath $targetFile).Hash -ne
        (Get-FileHash -LiteralPath (Join-Path $sourceRoot $relative)).Hash) {
        throw "Copy verification failed: $relative"
    }
}
Write-Output "Prepared $($releaseFiles.Count) reviewed files at $targetRoot"
Write-Output 'No Git history copied. No repository created, committed, or published.'
