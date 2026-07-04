"""
delete_orphan_files.py
Deletes ONLY the 4 confirmed orphaned Drive items (reviewed manually).
Requires typed confirmation before deleting anything.
Has a hardcoded PROTECTED_IDS list as a safety net -
the production Sheet and Drive folder can never be deleted by this script,
even if ALLOWED_TO_DELETE is edited by mistake.
"""

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive"]
CREDENTIALS_FILE = "credentials.json"

# Reviewed manually on 2026-06-17 - safe to delete
ALLOWED_TO_DELETE = [
    {"id": "1mJMu0dpyfqmr1TOlfyhrrH38dbeEcVN-", "name": "test-folder"},
    {"id": "1gbBM76bGA3NilmMKSHv4ya5GXW5_OB4p", "name": "Tp-004 (old orphaned copy)"},
    {"id": "1EHqTMhtRNPW-1d26lNqOn9xUy8MgmpcL", "name": "Tp-001 (old orphaned copy)"},
    {"id": "1rH7WPgBMN-XTpknHkjymuizTV8vIRBqmgCYdbWb5um8", "name": "amin_alsir_cases_new_V2 (duplicate sheet)"},
]

# Hard safety net - these can NEVER be deleted by this script
PROTECTED_IDS = {
    "1NvrC7PUQZreA9sATJCK4fgb06067NYmQPBaZVS0qSBk",  # Production Sheet
    "1_T8yAzq62a28jDcX93W-DHLEF5E_YUee",              # Production Drive folder
    "0AGGAp8sywzBkUk9PVA",                             # The Shared Drive itself
}


def main():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    service = build("drive", "v3", credentials=creds)

    print("=" * 60)
    print("ITEMS TO BE PERMANENTLY DELETED:")
    print("=" * 60)
    for item in ALLOWED_TO_DELETE:
        flag = " (PROTECTED - WILL SKIP)" if item["id"] in PROTECTED_IDS else ""
        print(f"  - {item['name']}  (ID: {item['id']}){flag}")
    print("=" * 60)

    confirm = input("\nType DELETE (all caps) to confirm permanent deletion: ").strip()
    if confirm != "DELETE":
        print("Cancelled. Nothing was deleted.")
        return

    print()
    for item in ALLOWED_TO_DELETE:
        file_id = item["id"]
        name = item["name"]

        if file_id in PROTECTED_IDS:
            print(f"SKIPPED (protected, will never delete): {name} ({file_id})")
            continue

        try:
            service.files().delete(fileId=file_id, supportsAllDrives=True).execute()
            print(f"DELETED: {name} ({file_id})")
        except Exception as e:
            print(f"ERROR deleting {name} ({file_id}): {e}")

    print("\nDone. Review the output above carefully.")


if __name__ == "__main__":
    main()
