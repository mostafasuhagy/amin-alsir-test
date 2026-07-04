# ===================================================================
# Fix v7 - ASCII-only script.
# 1) Removes the exposed BOT_TOKEN and BOSS_CHAT_ID constants from the
#    client dashboard entirely.
# 2) Points sendNotify() to the new secure /api/notify-boss endpoint
#    on the server instead of calling Telegram directly from the
#    browser. The regex anchors used here are pure ASCII, so no
#    Arabic text needs to be typed inside this script (avoiding the
#    PowerShell 5.1 encoding issue we hit before).
# ===================================================================

$path = "amin_alsir_client_dashboard.html"
$railwayUrl = "https://amin-alsir-test-production.up.railway.app/api/notify-boss"

if (-not (Test-Path $path)) {
    Write-Host "File not found: $path" -ForegroundColor Red
    exit
}

Copy-Item -Path $path -Destination "$path.backup5" -Force
Write-Host "Backup created: $path.backup5" -ForegroundColor Green

$content = [IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)
$madeChanges = $false

# --- Step 1: remove BOT_TOKEN and BOSS_CHAT_ID lines (pure ASCII) ---
# Handled as two independent single-line replacements so this does not
# depend on matching exact newline characters (LF vs CRLF).
$oldTokenLine = "const BOT_TOKEN='8716122412:AAHREvaHnoYsydnaPevVa5JDrT0wnxzz3Mk';"
$oldBossLine  = "const BOSS_CHAT_ID='8653723225';"
$step1Done = $false

if ($content.Contains($oldTokenLine)) {
    $content = $content.Replace($oldTokenLine, "")
    $step1Done = $true
}
if ($content.Contains($oldBossLine)) {
    $content = $content.Replace($oldBossLine, "")
    $step1Done = $true
}

if ($step1Done) {
    Write-Host "Step 1 done: BOT_TOKEN and/or BOSS_CHAT_ID removed" -ForegroundColor Green
    $madeChanges = $true
} else {
    Write-Host "Step 1 SKIPPED: token lines not found as expected (may already be removed)" -ForegroundColor Yellow
}

# --- Step 2: replace the Telegram fetch call with the secure endpoint ---
$options = [System.Text.RegularExpressions.RegexOptions]::Singleline
$pattern = ";const text=[\s\S]*?if\(data\.ok\)\{"
$regex = New-Object System.Text.RegularExpressions.Regex($pattern, $options)

$replacement = ";try{const res=await fetch('$railwayUrl',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sheet_id:SHEET_ID,client_code:CLIENT_CODE,client_name:CLIENT_NAME,subject:subject,message:msg})});const data=await res.json();if(data.ok){"

if ($regex.IsMatch($content)) {
    $content = $regex.Replace($content, $replacement, 1)
    Write-Host "Step 2 done: sendNotify now uses the secure endpoint" -ForegroundColor Green
    $madeChanges = $true
} else {
    Write-Host "Step 2 SKIPPED: sendNotify pattern not found as expected" -ForegroundColor Yellow
}

if ($madeChanges) {
    [IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
    Write-Host ""
    Write-Host "File saved successfully." -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "No changes made." -ForegroundColor Red
}
