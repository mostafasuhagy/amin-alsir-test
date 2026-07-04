FILE = r"C:\Users\karim\Documents\GitHub\amin-alsir-test\primitives.py"
SHARED_DRIVE_ID = "0AGGAp8sywzBkUk9PVA"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Fix DRV001 — remove driveId from body, add driveId param to create()
old1 = '''        file_metadata = {
            "name":    file_name,
            "parents": [sub_folder_id],
            "driveId": "0AGGAp8sywzBkUk9PVA",
        }
        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=False)
        uploaded = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink",
            supportsAllDrives=True
        ).execute()'''

new1 = '''        file_metadata = {
            "name":    file_name,
            "parents": [sub_folder_id],
        }
        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=False)
        uploaded = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()'''

# Fix DRV004 — remove driveId from body
old2 = '''        folder_metadata = {
            "name":     folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents":  [parent_id],
            "driveId":  "0AGGAp8sywzBkUk9PVA",
        }
        folder = service.files().create(
            body=folder_metadata, fields="id",
            supportsAllDrives=True
        ).execute()'''

new2 = '''        folder_metadata = {
            "name":     folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents":  [parent_id],
        }
        folder = service.files().create(
            body=folder_metadata, fields="id",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()'''

if old1 in content:
    content = content.replace(old1, new1)
    print("Fix 1 OK: DRV001")
else:
    print("Fix 1 FAILED: text not found in DRV001")

if old2 in content:
    content = content.replace(old2, new2)
    print("Fix 2 OK: DRV004")
else:
    print("Fix 2 FAILED: text not found in DRV004")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("Done.")
