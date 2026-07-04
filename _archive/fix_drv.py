import re

FILE = r"C:\Users\karim\Documents\GitHub\amin-alsir-test\primitives.py"
SHARED_DRIVE_ID = "0AGGAp8sywzBkUk9PVA"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# ── Fix 1: DRV001 — إضافة driveId لـ file_metadata ──
old1 = '''        file_metadata = {
            "name":    file_name,
            "parents": [sub_folder_id],
        }
        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=False)
        uploaded = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink",
            supportsAllDrives=True
        ).execute()'''

new1 = f'''        file_metadata = {{
            "name":    file_name,
            "parents": [sub_folder_id],
            "driveId": "{SHARED_DRIVE_ID}",
        }}
        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=False)
        uploaded = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink",
            supportsAllDrives=True
        ).execute()'''

# ── Fix 2: DRV004 — إضافة driveId لـ folder_metadata ──
old2 = '''        folder_metadata = {
            "name":     folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents":  [parent_id],
        }
        folder = service.files().create(
            body=folder_metadata, fields="id",
            supportsAllDrives=True
        ).execute()'''

new2 = f'''        folder_metadata = {{
            "name":     folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents":  [parent_id],
            "driveId":  "{SHARED_DRIVE_ID}",
        }}
        folder = service.files().create(
            body=folder_metadata, fields="id",
            supportsAllDrives=True
        ).execute()'''

# ── تطبيق التعديلات ──
if old1 in content:
    content = content.replace(old1, new1)
    print("✅ Fix 1: DRV001 — تم إضافة driveId")
else:
    print("❌ Fix 1: لم يتم إيجاد النص المطلوب في DRV001")

if old2 in content:
    content = content.replace(old2, new2)
    print("✅ Fix 2: DRV004 — تم إضافة driveId")
else:
    print("❌ Fix 2: لم يتم إيجاد النص المطلوب في DRV004")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("\n✅ تم الحفظ — primitives.py جاهز للـ commit")
