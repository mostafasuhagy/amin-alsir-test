# =======================================
# patch_tenant_resources.ps1
# Add automatic creation of dedicated Sheet + Drive folder
# for each new office (tenant) during registration in main.py
# =======================================

$filePath = ".\main.py"

if (-not (Test-Path $filePath)) {
    Write-Host "ERROR: main.py not found in current directory." -ForegroundColor Red
    Write-Host "Make sure you run this script from inside the project folder." -ForegroundColor Yellow
    exit
}

# -----------------------------------------------
# Step 1: Create a timestamped backup before touching anything
# -----------------------------------------------
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupPath = ".\main_backup_$timestamp.py"
Copy-Item -Path $filePath -Destination $backupPath
Write-Host "Backup created: $backupPath" -ForegroundColor Cyan

$content = [IO.File]::ReadAllText($filePath)
$content = $content -replace "`r`n", "`n"

# -----------------------------------------------
# Step 2: Define old and new code blocks exactly
# -----------------------------------------------
$oldBlock = @'
    if data.startswith("COUNTRY-"):
        country = data.replace("COUNTRY-", "")
        office_name = context.user_data.get("data", {}).get("office_name", "")
        sheet_name = "amin_alsir_cases_new_V2"

        code = MT002(chat_id, office_name, country, chat_id, sheet_name)
'@

$newBlock = @'
    if data.startswith("COUNTRY-"):
        country = data.replace("COUNTRY-", "")
        office_name = context.user_data.get("data", {}).get("office_name", "")

        # NEW: create a dedicated Sheet + Drive folder for this new tenant
        sheet_name, sheet_id = MT006(office_name, str(chat_id))
        folder_id = MT007(str(chat_id))

        if not sheet_name or not folder_id:
            print(f"FAIL: tenant resources not created for chat_id={chat_id} (sheet_name={sheet_name}, folder_id={folder_id})")
            await query.edit_message_text(
                "حدث خطأ في إنشاء الموارد الخاصة بمكتبك. حاول مرة أخرى لاحقاً."
            )
            return

        code = MT002(chat_id, office_name, country, chat_id, sheet_name, folder_id)
'@

# -----------------------------------------------
# Step 3: Verify the old block exists EXACTLY once before touching the file
# -----------------------------------------------
$occurrences = ([regex]::Matches($content, [regex]::Escape($oldBlock))).Count

if ($occurrences -eq 0) {
    Write-Host "ERROR: Could not find the exact old code block in main.py." -ForegroundColor Red
    Write-Host "No changes were made. The file is untouched." -ForegroundColor Yellow
    Write-Host "This usually means main.py has a different version than expected." -ForegroundColor Yellow
    exit
}
elseif ($occurrences -gt 1) {
    Write-Host "ERROR: The old code block was found $occurrences times (expected exactly 1)." -ForegroundColor Red
    Write-Host "Aborting to avoid an incorrect replacement. No changes were made." -ForegroundColor Yellow
    exit
}

# -----------------------------------------------
# Step 4: Apply the replacement (exactly once, confirmed safe)
# -----------------------------------------------
$content = $content.Replace($oldBlock, $newBlock)
$content = $content -replace "`n", "`r`n"
[IO.File]::WriteAllText($filePath, $content)

Write-Host "DONE: main.py updated successfully." -ForegroundColor Green
Write-Host "Each new tenant will now get its own Sheet (MT006) and Drive folder (MT007)." -ForegroundColor Green
Write-Host "If anything looks wrong, restore the backup: $backupPath" -ForegroundColor Cyan
