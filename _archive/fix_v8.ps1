# ===================================================================
# Fix v8 - focused only on removing the exposed BOT_TOKEN / BOSS_CHAT_ID
# lines, with extra diagnostics to confirm success this time.
# ===================================================================

$path = "amin_alsir_client_dashboard.html"

if (-not (Test-Path $path)) {
    Write-Host "File not found: $path" -ForegroundColor Red
    exit
}

Copy-Item -Path $path -Destination "$path.backup6" -Force
Write-Host "Backup created: $path.backup6" -ForegroundColor Green

$content = [IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)

$oldTokenLine = "const BOT_TOKEN='8716122412:AAHREvaHnoYsydnaPevVa5JDrT0wnxzz3Mk';"
$oldBossLine  = "const BOSS_CHAT_ID='8653723225';"

Write-Host ""
Write-Host "Diagnostic before replacement:" -ForegroundColor Cyan
Write-Host ("  BOT_TOKEN line found? " + $content.Contains($oldTokenLine))
Write-Host ("  BOSS_CHAT_ID line found? " + $content.Contains($oldBossLine))

$before = $content.Length
$content = $content.Replace($oldTokenLine, "")
$content = $content.Replace($oldBossLine, "")
$after = $content.Length

Write-Host ""
Write-Host ("Characters removed: " + ($before - $after)) -ForegroundColor Cyan

if ($before -ne $after) {
    [IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
    Write-Host ""
    Write-Host "File saved successfully - token lines removed." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "NOTHING WAS REMOVED. Paste the exact line 247-248 text here so I can fix the match." -ForegroundColor Red
}

Write-Host ""
Write-Host "Diagnostic after replacement (re-reading saved file):" -ForegroundColor Cyan
$recheck = [IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)
Write-Host ("  Still contains 'AAHR'? " + $recheck.Contains("AAHR"))
Write-Host ("  Still contains 'BOSS_CHAT_ID'? " + $recheck.Contains("BOSS_CHAT_ID"))
Write-Host ("  Contains new Railway endpoint? " + $recheck.Contains("amin-alsir-test-production.up.railway.app"))
