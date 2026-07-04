# list_orphan_files.py
# الهدف: عرض كل الملفات/الفولدرات الموجودة في My Drive الخاص بالـ Service Account
# (وليس داخل الـ Shared Drive) — للتأكد من الفولدرات اليتيمة قبل حذفها.
# هذا السكريبت للعرض فقط (Read-Only) ولا يحذف أي شيء.

from google.oauth2 import service_account
from googleapiclient.discovery import build

# === إعدادات ===
SERVICE_ACCOUNT_FILE = "credentials.json"  # يجب أن يكون في نفس مجلد المشروع
SCOPES = ["https://www.googleapis.com/auth/drive"]

SHARED_DRIVE_ID = "0AGGAp8sywzBkUk9PVA"  # نفس القيمة المستخدمة في primitives.py


def main():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("drive", "v3", credentials=creds)

    print("=" * 70)
    print("All files/folders visible to the Service Account")
    print("(includes its own My Drive + anything shared with it)")
    print("=" * 70)

    page_token = None
    all_files = []

    while True:
        response = (
            service.files()
            .list(
                q="trashed = false",
                spaces="drive",
                fields="nextPageToken, files(id, name, mimeType, parents, owners, driveId, size, createdTime)",
                pageToken=page_token,
                pageSize=100,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                corpora="allDrives",
            )
            .execute()
        )

        files = response.get("files", [])
        all_files.extend(files)

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    if not all_files:
        print("No files visible to this account.")
        return

    print(f"\nTotal files/folders found: {len(all_files)}\n")

    # Classify: is the file inside the known Shared Drive, or elsewhere (likely orphan)?
    orphans = []
    inside_shared_drive = []

    for f in all_files:
        drive_id = f.get("driveId")
        if drive_id == SHARED_DRIVE_ID:
            inside_shared_drive.append(f)
        else:
            orphans.append(f)

    print("-" * 70)
    print(f"OK - Files inside the correct Shared Drive ({SHARED_DRIVE_ID}): {len(inside_shared_drive)} item(s)")
    print("-" * 70)

    print("\n" + "=" * 70)
    print(f"WARNING - Possibly orphaned files/folders (outside the Shared Drive): {len(orphans)} item(s)")
    print("=" * 70)

    for f in orphans:
        size = f.get("size", "-")
        is_folder = f.get("mimeType") == "application/vnd.google-apps.folder"
        kind = "[FOLDER]" if is_folder else "[FILE]"
        owners = ", ".join([o.get("emailAddress", "?") for o in f.get("owners", [])])
        created = f.get("createdTime", "?")
        print(f"\n{kind} Name: {f.get('name')}")
        print(f"   ID: {f.get('id')}")
        print(f"   Size: {size} bytes")
        print(f"   Owner: {owners}")
        print(f"   Created: {created}")
        print(f"   driveId: {f.get('driveId', 'Personal My Drive (no driveId)')}")

    print("\n" + "=" * 70)
    print("This script deleted NOTHING. Please review the list above carefully first.")
    print("=" * 70)


if __name__ == "__main__":
    main()
