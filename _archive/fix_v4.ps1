# ===================================================================
# Fix v4 - repairs ONLY the broken innerHTML line from the previous
# patch (lines ~274-279). Uses a simple single-quoted JS string with
# no nested quotes at all, so there is nothing left to go wrong.
# ===================================================================

$path = "amin_alsir_client_dashboard.html"

if (-not (Test-Path $path)) {
    Write-Host "File not found: $path" -ForegroundColor Red
    exit
}

Copy-Item -Path $path -Destination "$path.backup2" -Force
Write-Host "Backup created: $path.backup2" -ForegroundColor Green

$content = [IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)

# Match everything from the broken innerHTML assignment up to the
# next "return;" (across multiple physical lines if needed), and
# replace it with two clean, guaranteed-valid lines.
$options = [System.Text.RegularExpressions.RegexOptions]::Singleline
$pattern = "document\.getElementById\('loading'\)\.innerHTML[\s\S]*?return;"
$regex = New-Object System.Text.RegularExpressions.Regex($pattern, $options)

$replacement = "document.getElementById('loading').innerHTML = 'Please open this dashboard from the link your office sent you on Telegram.';`n    return;"

if ($regex.IsMatch($content)) {
    $content = $regex.Replace($content, $replacement, 1)
    [IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
    Write-Host "Fixed successfully." -ForegroundColor Cyan
} else {
    Write-Host "Pattern not found - the broken line may look different than expected." -ForegroundColor Red
}
