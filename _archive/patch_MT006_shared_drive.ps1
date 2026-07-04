# =======================================
# patch_MT006_shared_drive.ps1
# Fix MT006: create the spreadsheet directly inside the Shared Drive
# via Drive API, instead of via Sheets API (which fails because the
# Service Account has no storage quota of its own).
# =======================================

$filePath = ".\primitives.py"

if (-not (Test-Path $filePath)) {
    Write-Host "ERROR: primitives.py not found in current directory." -ForegroundColor Red
    Write-Host "Make sure you run this script from inside the project folder." -ForegroundColor Yellow
    exit
}

# -----------------------------------------------
# Step 1: Backup
# -----------------------------------------------
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupPath = ".\primitives_backup_$timestamp.py"
Copy-Item -Path $filePath -Destination $backupPath
Write-Host "Backup created: $backupPath" -ForegroundColor Cyan

$content = [IO.File]::ReadAllText($filePath)
$content = $content -replace "`r`n", "`n"

# -----------------------------------------------
# Step 2: Old block (the exact current MT006 body, the failing part)
# We only replace from "spreadsheet = sheets_service..." through
# "spreadsheet_id = spreadsheet[...]" — the part that fails — and
# keep everything below it (headers_data, sharing, return) untouched
# by NOT including it in oldBlock/newBlock.
# -----------------------------------------------
$oldBlock = @'
        sheet_name = f"amin_alsir_{tenant_code}"

        spreadsheet = sheets_service.spreadsheets().create(body={
            "properties": {"title": sheet_name},
            "sheets": [
                {"properties": {"title": "Clients"}},
                {"properties": {"title": "Topics"}},
                {"properties": {"title": "Events"}},
                {"properties": {"title": "Documents"}},
                {"properties": {"title": "Shipments"}},
                {"properties": {"title": "Custody"}},
                {"properties": {"title": "Assistants"}},
                {"properties": {"title": "Notifications"}},
                {"properties": {"title": "Services"}},
            ]
        }).execute()

        spreadsheet_id = spreadsheet["spreadsheetId"]
'@

$newBlock = @'
        sheet_name = f"amin_alsir_{tenant_code}"

        # FIXED: create the file via Drive API directly inside the Shared Drive.
        # The old approach (sheets_service.spreadsheets().create()) fails with
        # HttpError 403 because the Service Account has no storage quota of
        # its own to own newly created Sheets files.
        file_metadata = {
            "name": sheet_name,
            "mimeType": "application/vnd.google-apps.spreadsheet",
            "parents": [SHARED_DRIVE_ID],
        }
        new_file = drive_service.files().create(
            body=file_metadata,
            fields="id",
            supportsAllDrives=True,
        ).execute()
        spreadsheet_id = new_file.get("id")
        print(f"DONE: MT006 - spreadsheet file created in Shared Drive ({spreadsheet_id})")

        # Add all required tabs via Sheets API batchUpdate
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": [
                {"addSheet": {"properties": {"title": "Clients"}}},
                {"addSheet": {"properties": {"title": "Topics"}}},
                {"addSheet": {"properties": {"title": "Events"}}},
                {"addSheet": {"properties": {"title": "Documents"}}},
                {"addSheet": {"properties": {"title": "Shipments"}}},
                {"addSheet": {"properties": {"title": "Custody"}}},
                {"addSheet": {"properties": {"title": "Assistants"}}},
                {"addSheet": {"properties": {"title": "Notifications"}}},
                {"addSheet": {"properties": {"title": "Services"}}},
            ]}
        ).execute()

        # Remove the default "Sheet1" tab that Drive auto-creates with every new spreadsheet
        spreadsheet_info = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        default_sheet_id = spreadsheet_info["sheets"][0]["properties"]["sheetId"]
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": [{"deleteSheet": {"sheetId": default_sheet_id}}]}
        ).execute()
'@

# -----------------------------------------------
# Step 3: Safety check — exact match must occur exactly once
# -----------------------------------------------
$occurrences = ([regex]::Matches($content, [regex]::Escape($oldBlock))).Count

if ($occurrences -eq 0) {
    Write-Host "ERROR: Could not find the exact old code block in primitives.py." -ForegroundColor Red
    Write-Host "No changes were made. The file is untouched." -ForegroundColor Yellow
    exit
}
elseif ($occurrences -gt 1) {
    Write-Host "ERROR: The old code block was found $occurrences times (expected exactly 1)." -ForegroundColor Red
    Write-Host "Aborting to avoid an incorrect replacement. No changes were made." -ForegroundColor Yellow
    exit
}

# -----------------------------------------------
# Step 4: Apply replacement
# -----------------------------------------------
$content = $content.Replace($oldBlock, $newBlock)
$content = $content -replace "`n", "`r`n"
[IO.File]::WriteAllText($filePath, $content)

Write-Host "DONE: primitives.py updated successfully." -ForegroundColor Green
Write-Host "MT006 will now create the spreadsheet file directly inside the Shared Drive." -ForegroundColor Green
Write-Host "If anything looks wrong, restore the backup: $backupPath" -ForegroundColor Cyan
