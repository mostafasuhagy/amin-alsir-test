# ===================================================================
# Client dashboard patch (v3 - ASCII-only script, no Arabic characters
# inside the .ps1 file itself, to avoid PowerShell 5.1 encoding bugs)
# ===================================================================

$path = "amin_alsir_client_dashboard.html"

if (-not (Test-Path $path)) {
    Write-Host "File not found: $path" -ForegroundColor Red
    exit
}

Copy-Item -Path $path -Destination "$path.backup" -Force
Write-Host "Backup created: $path.backup" -ForegroundColor Green

# Read the file explicitly as UTF-8 so existing Arabic content
# inside the HTML is preserved correctly regardless of system codepage.
$content = [IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)
$madeChanges = $false

# --- Replacement 1: CLIENT_CODE line (pure ASCII, safe) ---
$old1 = "const CLIENT_CODE='Cl-001';"
$new1 = "let CLIENT_CODE = null;"

if ($content.Contains($old1)) {
    $content = $content.Replace($old1, $new1)
    Write-Host "Step 1 done: CLIENT_CODE line replaced" -ForegroundColor Green
    $madeChanges = $true
} else {
    Write-Host "Step 1 SKIPPED: CLIENT_CODE line not found as expected" -ForegroundColor Yellow
}

# --- Replacement 2: CLIENT_NAME line, matched via regex on ASCII
#     anchors only (does not need to literally contain Arabic text
#     inside this script, so it cannot get corrupted by encoding). ---
$pattern2 = "const CLIENT_NAME='([^']*)';"
if ($content -match $pattern2) {
    $existingLine = $Matches[0]
    # Extract whatever Arabic name was already inside the matched
    # line so we do not need to type Arabic ourselves (avoids any
    # encoding risk from typing Arabic directly in this script).
    $innerValue = $Matches[1]

    $new2lines = @(
        "let CLIENT_NAME = '$innerValue';",
        "",
        "async function resolveClient(){",
        "  const params = new URLSearchParams(window.location.search);",
        "  const urlCode = params.get('c');",
        "  const clients = await fetchSheet('Clients');",
        "  let found = null;",
        "  if (CLIENT_CHAT_ID) {",
        "    found = clients.find(c => String(c.telegram_chat_id || '').trim() === String(CLIENT_CHAT_ID).trim());",
        "  }",
        "  if (!found && urlCode) {",
        "    found = clients.find(c => c.client_code === urlCode);",
        "  }",
        "  if (found) {",
        "    CLIENT_CODE = found.client_code;",
        "    CLIENT_NAME = found.client_name || '$innerValue';",
        "    return true;",
        "  }",
        "  return false;",
        "}"
    )
    $new2 = ($new2lines -join "`n")
    $content = $content.Replace($existingLine, $new2)
    Write-Host "Step 2 done: CLIENT_NAME line replaced, resolveClient() added" -ForegroundColor Green
    $madeChanges = $true
} else {
    Write-Host "Step 2 SKIPPED: CLIENT_NAME line not found as expected" -ForegroundColor Yellow
}

# --- Replacement 3: window.onload line (pure ASCII, safe) ---
$old3 = "window.onload=async()=>{updateClientInfo();await loadAllData();document.getElementById('loading').style.opacity='0';setTimeout(()=>document.getElementById('loading').style.display='none',500);};"
$new3lines = @(
    "window.onload=async()=>{",
    "  const ok = await resolveClient();",
    "  if (!ok) {",
    "    document.getElementById('loading').innerHTML = '<div style=" + [char]34 + "text-align:center;padding:30px;max-width:320px" + [char]34 + ">Please open this dashboard from the link your office sent you on Telegram.</div>';",
    "    return;",
    "  }",
    "  updateClientInfo();",
    "  await loadAllData();",
    "  document.getElementById('loading').style.opacity='0';",
    "  setTimeout(()=>document.getElementById('loading').style.display='none',500);",
    "};"
)
$new3 = ($new3lines -join "`n")

if ($content.Contains($old3)) {
    $content = $content.Replace($old3, $new3)
    Write-Host "Step 3 done: window.onload line replaced" -ForegroundColor Green
    $madeChanges = $true
} else {
    Write-Host "Step 3 SKIPPED: window.onload line not found as expected" -ForegroundColor Yellow
}

if ($madeChanges) {
    [IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
    Write-Host ""
    Write-Host "File saved successfully (UTF-8, no BOM)." -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "No changes made - none of the expected lines matched your file." -ForegroundColor Red
}
