# patch_pricing_fallback_v3.ps1
# Robust version: matches only on short ASCII anchors ("// fallback static"
# and the closing "});"), not the full Arabic-heavy text block.
# This avoids any encoding/whitespace mismatch issues.

$path = "index.html"

if (-not (Test-Path $path)) {
    Write-Host "ERROR: index.html not found in current folder. Run this from the project folder." -ForegroundColor Red
    exit 1
}

$content = [IO.File]::ReadAllText($path)

$pattern = '// fallback static[\s\S]*?\r?\n\s*\}\);'

$matches = [regex]::Matches($content, $pattern)

if ($matches.Count -eq 0) {
    Write-Host "ERROR: Anchor text '// fallback static' not found, or closing '});' not found after it." -ForegroundColor Red
    exit 1
}
if ($matches.Count -gt 1) {
    Write-Host "ERROR: Found $($matches.Count) matches - expected exactly 1. Stopping to avoid wrong edits." -ForegroundColor Red
    exit 1
}

$newInner = @"
var grid = document.getElementById('price-grid');
        grid.innerHTML = '<div style="color:#c4a04c;text-align:center;padding:3rem;">تواصل معنا للاطلاع على الأسعار</div>';
      });
"@

$evaluator = { param($m) $newInner }
$newContent = [regex]::Replace($content, $pattern, $evaluator)

[IO.File]::WriteAllText($path, $newContent)

Write-Host "DONE. Fallback pricing block replaced successfully." -ForegroundColor Green
