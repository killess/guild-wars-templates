# Copies the live Guild Wars templates (synced by OneDrive) into this repo's
# Templates folder, making it an exact copy, then opens GitHub Desktop so the
# changes can be committed and pushed.
# Run it by double-clicking "Sync Templates.cmd".

$source = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Guild Wars\Templates'
$dest   = Join-Path $PSScriptRoot 'Templates'

if (-not (Test-Path $source)) {
    Write-Host "Templates folder not found: $source" -ForegroundColor Red
    Read-Host 'Press Enter to close'
    exit 1
}

Write-Host "Copying $source"
Write-Host "     to $dest"
# /MIR makes $dest an exact copy (deletions included); git history keeps
# anything removed, so nothing is lost for good.
robocopy $source $dest /MIR /NFL /NDL /NJH /NJS /NP /R:2 /W:2 | Out-Null
if ($LASTEXITCODE -ge 8) {
    Write-Host "Copy failed (robocopy code $LASTEXITCODE)" -ForegroundColor Red
    Read-Host 'Press Enter to close'
    exit 1
}

Write-Host ''
git -C $PSScriptRoot status --short --untracked-files=all -- Templates | Measure-Object |
    ForEach-Object { Write-Host "$($_.Count) template change(s) to commit (a moved file counts twice)." -ForegroundColor Green }

$gh = Join-Path $env:LOCALAPPDATA 'GitHubDesktop\GitHubDesktop.exe'
if (Test-Path $gh) {
    Write-Host 'Opening GitHub Desktop - commit, then Push origin.'
    Start-Process $gh -ArgumentList "`"$PSScriptRoot`""
} else {
    Write-Host 'Open GitHub Desktop to commit and push.'
}
Start-Sleep -Seconds 3
