FILE = r"C:\Users\karim\Documents\GitHub\amin-alsir-test\primitives.py"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Fix DRV001
old1 = '''        uploaded = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()'''

new1 = '''        uploaded = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink",
            supportsAllDrives=True
        ).execute()'''

# Fix DRV004
old2 = '''        folder = service.files().create(
            body=folder_metadata, fields="id",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()'''

new2 = '''        folder = service.files().create(
            body=folder_metadata, fields="id",
            supportsAllDrives=True
        ).execute()'''

if old1 in content:
    content = content.replace(old1, new1)
    print("Fix 1 OK: DRV001")
else:
    print("Fix 1 FAILED")

if old2 in content:
    content = content.replace(old2, new2)
    print("Fix 2 OK: DRV004")
else:
    print("Fix 2 FAILED")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("Done.")
