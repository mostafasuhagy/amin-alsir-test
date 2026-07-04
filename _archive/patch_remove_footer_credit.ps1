# patch_remove_footer_credit.ps1
# Removes the "Powered by 247 For Online Trade" line from the footer.
# Anchored on the ASCII brand name (unique in the file) to avoid any
# Arabic text matching issues.

$path = "index.html"

if (-not (Test-Path $path)) {
    Write-Host "ERROR: index.html not found in current folder. Run this from the project folder." -ForegroundColor Red
    exit 1
}

$content = [IO.File]::ReadAllText($path)

$pattern = '\r?\n\s*<p[^>]*>[^<]*<span>247 For Online Trade</span></p>'

$matches = [regex]::Matches($content, $pattern)

if ($matches.Count -eq 0) {
    Write-Host "ERROR: Could not find the '247 For Online Trade' footer line." -ForegroundColor Red
    exit 1
}
if ($matches.Count -gt 1) {
    Write-Host "ERROR: Found $($matches.Count) matches - expected exactly 1. Stopping to avoid wrong edits." -ForegroundColor Red
    exit 1
}

$newContent = [regex]::Replace($content, $pattern, '')

[IO.File]::WriteAllText($path, $newContent)

Write-Host "DONE. Footer credit line removed successfully." -ForegroundColor Green
