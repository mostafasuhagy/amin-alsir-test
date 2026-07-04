# ===================================================================
# Fix v5 - swap lookup priority inside resolveClient(): the explicit
# client_code from the URL (?c=) now takes priority over chat_id,
# since chat_id can be shared across multiple test clients using the
# same personal Telegram account.
# ===================================================================

$path = "amin_alsir_client_dashboard.html"

if (-not (Test-Path $path)) {
    Write-Host "File not found: $path" -ForegroundColor Red
    exit
}

Copy-Item -Path $path -Destination "$path.backup3" -Force
Write-Host "Backup created: $path.backup3" -ForegroundColor Green

$content = [IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)

$options = [System.Text.RegularExpressions.RegexOptions]::Singleline
$pattern = "(let found = null;)[\s\S]*?(if \(found\) \{)"
$regex = New-Object System.Text.RegularExpressions.Regex($pattern, $options)

$newLines = @(
    '$1',
    '  if (urlCode) {',
    "    found = clients.find(c => c.client_code === urlCode);",
    '  }',
    '  if (!found && CLIENT_CHAT_ID) {',
    "    found = clients.find(c => String(c.telegram_chat_id || '').trim() === String(CLIENT_CHAT_ID).trim());",
    '  }',
    '  $2'
)
$replacement = ($newLines -join "`n")

if ($regex.IsMatch($content)) {
    $content = $regex.Replace($content, $replacement, 1)
    [IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
    Write-Host "Fixed successfully - urlCode now takes priority over chat_id." -ForegroundColor Cyan
} else {
    Write-Host "Pattern not found - resolveClient() may have a different shape than expected." -ForegroundColor Red
}
