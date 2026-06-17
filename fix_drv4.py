import sys

FILE = r"C:\Users\karim\Documents\GitHub\amin-alsir-test\primitives.py"

with open(FILE, "rb") as f:
    raw = f.read()

# decode
content = raw.decode("utf-8-sig")

# الجزء القديم بالضبط
old = (
    "        res = service.files().list(\r\n"
    "            q=query, fields=\"files(id, name)\",\r\n"
    "            supportsAllDrives=True\r\n"
    "        ).execute()\r\n"
    "        existing = res.get(\"files\", [])\r\n"
    "        if existing:"
)

# الجزء الجديد
new = (
    "        res = service.files().list(\r\n"
    "            q=query, fields=\"files(id, name)\",\r\n"
    "            supportsAllDrives=True,\r\n"
    "            includeItemsFromAllDrives=True,\r\n"
    "            corpora=\"drive\",\r\n"
    "            driveId=SHARED_DRIVE_ID\r\n"
    "        ).execute()\r\n"
    "        existing = res.get(\"files\", [])\r\n"
    "        if existing:"
)

count = content.count(old)
print(f"Found: {count} match(es)")

if count == 1:
    content = content.replace(old, new)
    with open(FILE, "wb") as f:
        f.write(content.encode("utf-8"))
    print("OK - DRV004 fixed")
elif count == 0:
    print("NOT FOUND - checking line endings...")
    # try LF only
    old_lf = old.replace("\r\n", "\n")
    count_lf = content.count(old_lf)
    print(f"LF version found: {count_lf}")
    if count_lf == 1:
        new_lf = new.replace("\r\n", "\n")
        content = content.replace(old_lf, new_lf)
        with open(FILE, "wb") as f:
            f.write(content.encode("utf-8"))
        print("OK - fixed with LF")
else:
    print("Multiple matches - manual fix needed")
