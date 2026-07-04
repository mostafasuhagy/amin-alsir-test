# ===================================================================
# Fix v6b - ASCII-only script. Extracts the existing array elements
# from the current sendShipment() line via regex (no Arabic text is
# ever typed inside this script itself), then reassembles them in
# the correct column order matching the real Shipments sheet headers.
# ===================================================================

$path = "amin_alsir_client_dashboard.html"

if (-not (Test-Path $path)) {
    Write-Host "File not found: $path" -ForegroundColor Red
    exit
}

Copy-Item -Path $path -Destination "$path.backup4b" -Force
Write-Host "Backup created: $path.backup4b" -ForegroundColor Green

$content = [IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)

$pattern = "await postToSheet\('Shipments',\[([^\]]*)\]\);"
$m = [System.Text.RegularExpressions.Regex]::Match($content, $pattern)

if ($m.Success) {
    $inner = $m.Groups[1].Value
    $parts = $inner.Split(',')

    if ($parts.Length -eq 10) {
        # Original order (0-indexed):
        # 0='' 1=selectedTopic.code 2=CLIENT_CODE 3=CLIENT_NAME 4=desc
        # 5=notes||'em-dash' 6=(old status word) 7=(old pending word)
        # 8=now 9=''
        #
        # New order matching real headers: shipment_code | topic_code |
        # sender | receiver | send_date | file_name | file_type |
        # pickup_location | receive_status | receive_date | notes
        $newParts = @(
            $parts[0],   # shipment_code (blank)
            $parts[1],   # topic_code
            $parts[3],   # sender = CLIENT_NAME
            $parts[0],   # receiver (blank)
            $parts[8],   # send_date = now
            $parts[4],   # file_name = desc
            $parts[0],   # file_type (blank)
            $parts[0],   # pickup_location (blank)
            $parts[7],   # receive_status = old "pending" word (reused as-is)
            $parts[0],   # receive_date (blank)
            $parts[5]    # notes
        )
        $newInner = ($newParts -join ",")
        $newLine = "await postToSheet('Shipments',[" + $newInner + "]);"
        $content = $content.Replace($m.Value, $newLine)
        [IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
        Write-Host "Fixed successfully." -ForegroundColor Cyan
    } else {
        Write-Host ("Found the line but element count was " + $parts.Length + " instead of 10 - not touching the file. Send this script owner the raw line.") -ForegroundColor Red
    }
} else {
    Write-Host "Pattern not found - the sendShipment line may look different than expected." -ForegroundColor Red
}
