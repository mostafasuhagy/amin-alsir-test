# ===================================================================
# Cleanup script - moves everything that is NOT a known core file into
# an _archive folder. Nothing is deleted. Safe by construction: only
# files explicitly listed in $keepFiles stay in the project root.
#
# USAGE:
#   1) First run in DRY RUN mode (default) to see what would move:
#        powershell -ExecutionPolicy Bypass -File .\cleanup_project.ps1
#   2) If the list looks right, run for real:
#        powershell -ExecutionPolicy Bypass -File .\cleanup_project.ps1 -Execute
# ===================================================================

param(
    [switch]$Execute
)

# Files that MUST stay in the project root - add to this list if you
# know of any other file the running system actually needs.
$keepFiles = @(
    "main.py",
    "primitives.py",
    "routines.py",
    "amin_alsir_dashboard.html",
    "amin_alsir_client_dashboard.html",
    "amin_alsir_assistant_dashboard.html",
    "manifest_client.json",
    "manifest.json",
    "icon-192.png",
    "icon-512.png",
    "favicon.ico",
    "Procfile",
    "nixpacks.toml",
    "requirements.txt",
    "CNAME",
    ".gitignore",
    ".gitattributes",
    "credentials.json",
    "manifest_assistant.json",
    "icon_client.png",
    "icon_assistant.png",
    "cleanup_project.ps1"
)

$archiveDir = "_archive"

if (-not (Test-Path $archiveDir)) {
    if ($Execute) {
        New-Item -ItemType Directory -Path $archiveDir | Out-Null
    }
}

$allFiles = Get-ChildItem -Path . -File | Where-Object { $_.Name -ne "cleanup_project.ps1" }
$toMove = $allFiles | Where-Object { $keepFiles -notcontains $_.Name }

Write-Host ""
if ($Execute) {
    Write-Host "EXECUTE MODE - files will actually be moved." -ForegroundColor Red
} else {
    Write-Host "DRY RUN MODE - nothing will be moved yet." -ForegroundColor Yellow
}
Write-Host ""

Write-Host ("Files that will stay in place (" + ($allFiles.Count - $toMove.Count) + "):") -ForegroundColor Green
foreach ($f in $allFiles) {
    if ($keepFiles -contains $f.Name) {
        Write-Host ("  KEEP  " + $f.Name)
    }
}

Write-Host ""
Write-Host ("Files that will move to " + $archiveDir + " (" + $toMove.Count + "):") -ForegroundColor Cyan
foreach ($f in $toMove) {
    Write-Host ("  MOVE  " + $f.Name)
    if ($Execute) {
        Move-Item -Path $f.FullName -Destination (Join-Path $archiveDir $f.Name) -Force
    }
}

Write-Host ""
if ($Execute) {
    Write-Host "Done. Files moved into _archive." -ForegroundColor Green
} else {
    Write-Host "This was a dry run. Nothing was moved." -ForegroundColor Yellow
    Write-Host "If the lists above look correct, run again with -Execute:" -ForegroundColor Yellow
    Write-Host "  powershell -ExecutionPolicy Bypass -File .\cleanup_project.ps1 -Execute" -ForegroundColor Yellow
}
