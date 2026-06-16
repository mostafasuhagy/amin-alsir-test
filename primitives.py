import os
import re
import json
import gspread
import hashlib
import time
from datetime import datetime
from google.oauth2.service_account import Credentials

SHEET_NAME = "amin_alsir_cases_new_V2"
CALENDAR_ID = "mostafa.suhagy@gmail.com"
DRIVE_FOLDER_ID = "1_T8yAzq62a28jDcX93W-DHLEF5E_YUee"
SHARED_DRIVE_ID = "0AGGAp8sywzBkUk9PVA"
TENANTS_SHEET = "amin_alsir_cases_new_V2"

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/calendar",
]

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# ط§ظ„ظ…ظ†ط§ط·ظ‚ ط§ظ„ط²ظ…ظ†ظٹط© ظ„ظ„ط¯ظˆظ„ ط§ظ„ط¹ط±ط¨ظٹط©
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
ARAB_TIMEZONES = {
    "ظ…طµط±":       "Africa/Cairo",
    "ط§ظ„ط³ط¹ظˆط¯ظٹط©":  "Asia/Riyadh",
    "ط§ظ„ط¥ظ…ط§ط±ط§طھ":  "Asia/Dubai",
    "ط§ظ„ظƒظˆظٹطھ":    "Asia/Kuwait",
    "ظ‚ط·ط±":       "Asia/Qatar",
    "ط§ظ„ط¨ط­ط±ظٹظ†":   "Asia/Bahrain",
    "ط§ظ„ط£ط±ط¯ظ†":    "Asia/Amman",
    "ظ„ط¨ظ†ط§ظ†":     "Asia/Beirut",
    "ط§ظ„ظ…ط؛ط±ط¨":    "Africa/Casablanca",
    "طھظˆظ†ط³":      "Africa/Tunis",
    "ط§ظ„ط¬ط²ط§ط¦ط±":   "Africa/Algiers",
    "ظ„ظٹط¨ظٹط§":     "Africa/Tripoli",
    "ط§ظ„ط¹ط±ط§ظ‚":    "Asia/Baghdad",
    "ط³ظˆط±ظٹط§":     "Asia/Damascus",
    "ط§ظ„ظٹظ…ظ†":     "Asia/Aden",
    "ط¹ظ…ط§ظ†":      "Asia/Muscat",
    "ط§ظ„ط³ظˆط¯ط§ظ†":   "Africa/Khartoum",
    "ظپظ„ط³ط·ظٹظ†":   "Asia/Gaza",
}

def GET_TIMEZONE(country):
    return ARAB_TIMEZONES.get(country, "Africa/Cairo")

def NOW_LOCAL(country="ظ…طµط±"):
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(GET_TIMEZONE(country))
        return datetime.now(tz).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return datetime.now().strftime("%Y-%m-%d %H:%M")

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Multi-Tenant â€” ط¥ط¯ط§ط±ط© ط§ظ„ظ…ط´طھط±ظƒظٹظ†
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def MT001(chat_id):
    try:
        records = P005("Tenants", TENANTS_SHEET)
        for r in records:
            if str(r.get("chat_id", "")) == str(chat_id):
                return r
        return None
    except Exception as e:
        print(f"â‌Œ MT001: {e}")
        return None

def MT002(chat_id, office_name, country, boss_chat_id, sheet_name, drive_folder_id=""):
    try:
        code = G001("Of", "Tenants", TENANTS_SHEET)
        ok = P003("Tenants", [
            code,
            str(chat_id),
            office_name,
            country,
            GET_TIMEZONE(country),
            str(boss_chat_id),
            sheet_name,
            drive_folder_id,
            "active",
            NOW_LOCAL(country),
        ], TENANTS_SHEET)
        print(f"âœ… MT002: طھظ… طھط³ط¬ظٹظ„ ظ…ظƒطھط¨ â€” {office_name} ({country})")
        return code if ok else None
    except Exception as e:
        print(f"â‌Œ MT002: {e}")
        return None

def MT003(chat_id):
    try:
        tenant = MT001(chat_id)
        if not tenant:
            return False
        return tenant.get("status", "") == "active"
    except Exception as e:
        print(f"â‌Œ MT003: {e}")
        return False

def MT004(chat_id):
    try:
        tenant = MT001(chat_id)
        if not tenant:
            return SHEET_NAME
        return tenant.get("sheet_name", SHEET_NAME)
    except Exception as e:
        print(f"â‌Œ MT004: {e}")
        return SHEET_NAME

def MT005(chat_id):
    try:
        tenant = MT001(chat_id)
        if not tenant:
            return "Africa/Cairo"
        return tenant.get("timezone", "Africa/Cairo")
    except Exception as e:
        print(f"â‌Œ MT005: {e}")
        return "Africa/Cairo"

def MT006(office_name, tenant_code):
    try:
        from googleapiclient.discovery import build

        creds_json = os.environ.get("GOOGLE_CREDENTIALS")
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        sheets_service = build("sheets", "v4", credentials=creds)
        drive_service  = build("drive",  "v3", credentials=creds)

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
        print(f"âœ… MT006: طھظ… ط¥ظ†ط´ط§ط، ط§ظ„ط´ظٹطھ â€” {sheet_name} ({spreadsheet_id})")

        headers_data = [
            {"range": "Clients!A1",       "values": [["client_code", "client_name", "national_id", "mobile", "address", "date_added", "notes", "telegram_chat_id"]]},
            {"range": "Topics!A1",        "values": [["topic_code", "client_code", "client_name", "service_code", "service_name", "assistant_code", "assistant_name", "date_opened", "status", "notes"]]},
            {"range": "Events!A1",        "values": [["work_order_no", "event_date", "topic_code", "client_name", "event_type", "event_time", "location_court", "result", "next_appointment", "notes", "attachments"]]},
            {"range": "Documents!A1",     "values": [["doc_code", "topic_code", "doc_type", "doc_name", "file_extension", "drive_link", "uploaded_by", "upload_date", "status", "approval_date", "notes"]]},
            {"range": "Shipments!A1",     "values": [["shipment_code", "topic_code", "sender", "receiver", "send_date", "file_name", "file_type", "pickup_location", "receive_status", "receive_date", "notes"]]},
            {"range": "Custody!A1",       "values": [["custody_code", "responsible_code", "amount", "payment_due", "payment_status", "actual_payment_date", "notes"]]},
            {"range": "Assistants!A1",    "values": [["assistant_code", "assistant_name", "bar_number", "mobile", "date_added", "notes", "attachments_code", "telegram_chat_id"]]},
            {"range": "Notifications!A1", "values": [["notification_code", "type", "ref_code", "name", "message", "date"]]},
            {"range": "Services!A1",      "values": [["service_code", "service_name", "date_added", "notes"]]},
        ]

        sheets_service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"valueInputOption": "RAW", "data": headers_data}
        ).execute()
        print(f"âœ… MT006: طھظ… ط¥ط¶ط§ظپط© ط§ظ„ظ‡ظٹط¯ط±ط² ظ„ظƒظ„ ط§ظ„ظ€ tabs")

        drive_service.permissions().create(
            fileId=spreadsheet_id,
            body={
                "type": "user",
                "role": "writer",
                "emailAddress": "amin-alsir-bot@amin-alsir.iam.gserviceaccount.com"
            }
        ).execute()
        print(f"âœ… MT006: طھظ… ظ…ط´ط§ط±ظƒط© ط§ظ„ط´ظٹطھ ظ…ط¹ Service Account")

        return sheet_name, spreadsheet_id

    except Exception as e:
        print(f"â‌Œ MT006: {e}")
        return None, None

def MT007(tenant_code):
    try:
        service = P001D()
        if not service:
            return None

        folder_name = f"amin_alsir_{tenant_code}"
        folder_metadata = {
            "name":     folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents":  [DRIVE_FOLDER_ID],
        }
        folder = service.files().create(
            body=folder_metadata,
            fields="id",
            supportsAllDrives=True
        ).execute()
        folder_id = folder.get("id")
        print(f"âœ… MT007: طھظ… ط¥ظ†ط´ط§ط، ظ…ط¬ظ„ط¯ Drive â€” {folder_name} ({folder_id})")
        return folder_id

    except Exception as e:
        print(f"â‌Œ MT007: {e}")
        return None

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# P001 â€” ط§ظ„ط§طھطµط§ظ„ ط¨ظ€ Google Sheets
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def P001(sheet_name=SHEET_NAME):
    try:
        creds_json = os.environ.get("GOOGLE_CREDENTIALS")
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        return client.open(sheet_name)
    except Exception as e:
        print(f"â‌Œ P001: {e}")
        return None

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# P001C â€” ط§ظ„ط§طھطµط§ظ„ ط¨ظ€ Google Calendar
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def P001C():
    try:
        from googleapiclient.discovery import build
        creds_json = os.environ.get("GOOGLE_CREDENTIALS")
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        service = build("calendar", "v3", credentials=creds)
        return service
    except Exception as e:
        print(f"â‌Œ P001C: {e}")
        return None

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# P001D â€” ط§ظ„ط§طھطµط§ظ„ ط¨ظ€ Google Drive (Shared Drive)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def P001D():
    try:
        from googleapiclient.discovery import build
        creds_json = os.environ.get("GOOGLE_CREDENTIALS")
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        service = build("drive", "v3", credentials=creds)
        return service
    except Exception as e:
        print(f"â‌Œ P001D: {e}")
        return None

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Google Sheets Functions
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def P002(tab, ref_code, sheet_name=SHEET_NAME):
    try:
        ws = P001(sheet_name).worksheet(tab)
        for r in ws.get_all_records():
            if str(list(r.values())[0]).strip().lower() == str(ref_code).strip().lower():
                return r
        return None
    except Exception as e:
        print(f"â‌Œ P002: {e}")
        return None

def P003(tab, data, sheet_name=SHEET_NAME):
    try:
        P001(sheet_name).worksheet(tab).append_row(data, value_input_option="USER_ENTERED")
        return True
    except Exception as e:
        print(f"â‌Œ P003: {e}")
        return False

def P004(tab, row, col, value, sheet_name=SHEET_NAME):
    try:
        P001(sheet_name).worksheet(tab).update_cell(row, col, value)
        return True
    except Exception as e:
        print(f"â‌Œ P004: {e}")
        return False

def P005(tab, sheet_name=SHEET_NAME):
    try:
        return P001(sheet_name).worksheet(tab).get_all_records()
    except Exception as e:
        print(f"â‌Œ P005: {e}")
        return []

def P006(tab, col_name, value, sheet_name=SHEET_NAME):
    try:
        return [r for r in P005(tab, sheet_name) if str(r.get(col_name, "")).strip().lower() == str(value).strip().lower()]
    except Exception as e:
        print(f"â‌Œ P006: {e}")
        return []

def G001(prefix, tab, sheet_name=SHEET_NAME):
    try:
        count = len(P005(tab, sheet_name)) + 1
        return f"{prefix}-{count:03d}"
    except Exception as e:
        print(f"â‌Œ G001: {e}")
        return f"{prefix}-001"

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Notification Logger
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def LOG_NOTIFICATION(notif_type, ref_code, name, message):
    try:
        code = G001("Nt", "Notifications")
        P003("Notifications", [
            code,
            notif_type,
            ref_code,
            name,
            message,
            datetime.now().strftime("%Y-%m-%d %H:%M"),
        ])
        print(f"âœ… LOG_NOTIFICATION: {code} â€” {notif_type} â€” {name}")
    except Exception as e:
        print(f"â‌Œ LOG_NOTIFICATION: {e}")

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Validators
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def V001(text):
    return bool(text) and isinstance(text, str) and len(text.strip()) >= 3

def V002(nid):
    return bool(re.match(r'^\d{14}$', str(nid).strip())) if nid else False

def V003(mobile):
    return bool(re.match(r'^01[0-9]{9}$', str(mobile).strip())) if mobile else False

def V004(date_str):
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            datetime.strptime(str(date_str).strip(), fmt)
            return True
        except: continue
    return False

def V005(amount):
    try:
        return float(str(amount).replace(",", "")) > 0
    except: return False

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Google Calendar Functions
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def CAL001(title, date_str, time_str="", location="", description="", calendar_id=CALENDAR_ID):
    try:
        service = P001C()
        if not service:
            return None
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                date_obj = datetime.strptime(date_str.strip(), fmt)
                break
            except: continue
        else:
            print(f"â‌Œ CAL001: طھظ†ط³ظٹظ‚ ط§ظ„طھط§ط±ظٹط® ط؛ظٹط± طµط­ظٹط­: {date_str}")
            return None
        if time_str:
            try:
                hour, minute = time_str.strip().split(":")[:2]
                minute = minute[:2]
                start_dt = date_obj.replace(hour=int(hour), minute=int(minute))
                end_dt   = start_dt.replace(hour=int(hour)+1)
                event = {
                    "summary": title, "location": location, "description": description,
                    "start": {"dateTime": start_dt.strftime("%Y-%m-%dT%H:%M:00"), "timeZone": "Africa/Cairo"},
                    "end":   {"dateTime": end_dt.strftime("%Y-%m-%dT%H:%M:00"),   "timeZone": "Africa/Cairo"},
                }
            except:
                event = {
                    "summary": title, "location": location, "description": description,
                    "start": {"date": date_obj.strftime("%Y-%m-%d")},
                    "end":   {"date": date_obj.strftime("%Y-%m-%d")},
                }
        else:
            event = {
                "summary": title, "location": location, "description": description,
                "start": {"date": date_obj.strftime("%Y-%m-%d")},
                "end":   {"date": date_obj.strftime("%Y-%m-%d")},
            }
        result = service.events().insert(calendarId=calendar_id, body=event).execute()
        event_id = result.get("id")
        print(f"âœ… CAL001: طھظ… ط¥ط¶ط§ظپط© ط§ظ„ط­ط¯ط« â€” {event_id}")
        return event_id
    except Exception as e:
        print(f"â‌Œ CAL001: {e}")
        return None

def CAL002(calendar_id=CALENDAR_ID, days_ahead=30):
    try:
        service = P001C()
        if not service:
            return []
        now = datetime.utcnow().isoformat() + "Z"
        result = service.events().list(
            calendarId=calendar_id, timeMin=now,
            maxResults=20, singleEvents=True, orderBy="startTime"
        ).execute()
        events = result.get("items", [])
        formatted = []
        for e in events:
            start = e["start"].get("dateTime", e["start"].get("date", ""))
            formatted.append({
                "id": e.get("id", ""), "title": e.get("summary", "â€”"),
                "start": start, "location": e.get("location", ""),
                "description": e.get("description", ""),
            })
        return formatted
    except Exception as e:
        print(f"â‌Œ CAL002: {e}")
        return []

def CAL003(event_id, calendar_id=CALENDAR_ID):
    try:
        service = P001C()
        if not service:
            return False
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        print(f"âœ… CAL003: طھظ… ط­ط°ظپ ط§ظ„ط­ط¯ط« â€” {event_id}")
        return True
    except Exception as e:
        print(f"â‌Œ CAL003: {e}")
        return False

def CAL004(event_id, updates, calendar_id=CALENDAR_ID):
    try:
        service = P001C()
        if not service:
            return False
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        event.update(updates)
        service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
        print(f"âœ… CAL004: طھظ… طھط¹ط¯ظٹظ„ ط§ظ„ط­ط¯ط« â€” {event_id}")
        return True
    except Exception as e:
        print(f"â‌Œ CAL004: {e}")
        return False

def CAL005(event_id, result_text, calendar_id=CALENDAR_ID):
    try:
        return CAL004(event_id, {"description": f"ط§ظ„ظ†طھظٹط¬ط©: {result_text}"}, calendar_id)
    except Exception as e:
        print(f"â‌Œ CAL005: {e}")
        return False

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Google Drive Functions
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def DRV001(file_path, file_name, topic_code, folder_id=DRIVE_FOLDER_ID):
    try:
        from googleapiclient.http import MediaFileUpload
        import mimetypes

        service = P001D()
        if not service:
            return None

        sub_folder_id = DRV004(topic_code, folder_id)
        if not sub_folder_id:
            return None

        mime_type, _ = mimetypes.guess_type(file_name)
        if not mime_type:
            mime_type = "application/octet-stream"

        file_metadata = {
            "name":    file_name,
            "parents": [sub_folder_id],
        }
        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=False)
        uploaded = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink",
            supportsAllDrives=True
        ).execute()

        file_id    = uploaded.get("id")
        drive_link = uploaded.get("webViewLink", f"https://drive.google.com/file/d/{file_id}/view")

        service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"},
            supportsAllDrives=True
        ).execute()

        print(f"âœ… DRV001: طھظ… ط±ظپط¹ ط§ظ„ظ…ظ„ظپ â€” {file_name} â†’ {drive_link}")
        return drive_link

    except Exception as e:
        print(f"â‌Œ DRV001: {e}")
        return None


def DRV002(topic_code, folder_id=DRIVE_FOLDER_ID):
    try:
        service = P001D()
        if not service:
            return []

        query = (
            f"name='{topic_code}' and "
            f"'{folder_id}' in parents and "
            f"mimeType='application/vnd.google-apps.folder' and "
            f"trashed=false"
        )
        res = service.files().list(
            q=query, fields="files(id, name)",
            supportsAllDrives=True
        ).execute()
        folders = res.get("files", [])
        if not folders:
            return []

        sub_folder_id = folders[0]["id"]
        query2 = f"'{sub_folder_id}' in parents and trashed=false"
        res2 = service.files().list(
            q=query2,
            fields="files(id, name, webViewLink, createdTime)",
            orderBy="createdTime desc",
            supportsAllDrives=True
        ).execute()

        files = []
        for f in res2.get("files", []):
            files.append({
                "name":         f.get("name", "â€”"),
                "link":         f.get("webViewLink", f"https://drive.google.com/file/d/{f['id']}/view"),
                "created_time": f.get("createdTime", "")[:10],
            })

        print(f"âœ… DRV002: طھظ… ط¬ظ„ط¨ {len(files)} ظ…ظ„ظپ ظ„ظ„ظ…ظˆط¶ظˆط¹ {topic_code}")
        return files

    except Exception as e:
        print(f"â‌Œ DRV002: {e}")
        return []


def DRV003(file_id):
    try:
        service = P001D()
        if not service:
            return False
        service.files().delete(fileId=file_id, supportsAllDrives=True).execute()
        print(f"âœ… DRV003: طھظ… ط­ط°ظپ ط§ظ„ظ…ظ„ظپ â€” {file_id}")
        return True
    except Exception as e:
        print(f"â‌Œ DRV003: {e}")
        return False


def DRV004(folder_name, parent_id=DRIVE_FOLDER_ID):
    try:
        service = P001D()
        if not service:
            return None

        query = (
            f"name='{folder_name}' and "
            f"'{parent_id}' in parents and "
            f"mimeType='application/vnd.google-apps.folder' and "
            f"trashed=false"
        )
        res = service.files().list(
            q=query, fields="files(id, name)",
            supportsAllDrives=True
        ).execute()
        existing = res.get("files", [])
        if existing:
            print(f"âœ… DRV004: ظ…ط¬ظ„ط¯ ظ…ظˆط¬ظˆط¯ â€” {folder_name} ({existing[0]['id']})")
            return existing[0]["id"]

        folder_metadata = {
            "name":     folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents":  [parent_id],
        }
        folder = service.files().create(
            body=folder_metadata,
            fields="id",
            supportsAllDrives=True
        ).execute()
        folder_id = folder.get("id")
        print(f"âœ… DRV004: طھظ… ط¥ظ†ط´ط§ط، ظ…ط¬ظ„ط¯ â€” {folder_name} ({folder_id})")
        return folder_id

    except Exception as e:
        print(f"â‌Œ DRV004: {e}")
        return None


def DRV005(file_path, file_name, folder_id=DRIVE_FOLDER_ID):
    try:
        from googleapiclient.http import MediaFileUpload
        import mimetypes

        service = P001D()
        if not service:
            return None

        mime_type, _ = mimetypes.guess_type(file_name)
        if not mime_type:
            mime_type = "application/octet-stream"

        file_metadata = {
            "name":    file_name,
            "parents": [folder_id],
        }
        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=False)
        uploaded = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink",
            supportsAllDrives=True
        ).execute()

        file_id    = uploaded.get("id")
        drive_link = uploaded.get("webViewLink", f"https://drive.google.com/file/d/{file_id}/view")

        service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"},
            supportsAllDrives=True
        ).execute()

        print(f"âœ… DRV005: طھظ… ط±ظپط¹ ط§ظ„ظ…ظ„ظپ â€” {file_name} â†’ {drive_link}")
        return drive_link

    except Exception as e:
        print(f"â‌Œ DRV005: {e}")
        return None

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Telegram Message Functions
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
async def T001(context, chat_id, text):
    try:
        return await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
    except Exception as e:
        print(f"â‌Œ T001: {e}")
        return None

async def T002(context, chat_id, text, buttons):
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        kb = [[InlineKeyboardButton(b["text"], callback_data=b["callback_data"]) for b in row] for row in buttons]
        return await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    except Exception as e:
        print(f"â‌Œ T002: {e}")
        return None

async def T003(context, chat_id, message_id, new_text, buttons=None):
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        markup = None
        if buttons:
            kb = [[InlineKeyboardButton(b["text"], callback_data=b["callback_data"]) for b in row] for row in buttons]
            markup = InlineKeyboardMarkup(kb)
        await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_text, parse_mode="Markdown", reply_markup=markup)
        return True
    except Exception as e:
        print(f"â‌Œ T003: {e}")
        return False

async def T004(update, context):
    try:
        msg = update.message
        if msg.document:
            f = msg.document
            return {"type": "document", "file_id": f.file_id, "file_name": f.file_name}
        elif msg.photo:
            f = msg.photo[-1]
            return {"type": "photo", "file_id": f.file_id}
        return None
    except Exception as e:
        print(f"â‌Œ T004: {e}")
        return None

async def T005(context, chat_id, text, options):
    try:
        return await T002(context, chat_id, text, [[opt] for opt in options])
    except Exception as e:
        print(f"â‌Œ T005: {e}")
        return None

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Notification Functions
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
async def N001(context, boss_chat_id, text):
    try:
        await context.bot.send_message(
            chat_id=boss_chat_id,
            text=f"ًں”” *ط¥ط´ط¹ط§ط± â€” ط£ظ…ظٹظ† ط§ظ„ط³ط±*\n\n{text}",
            parse_mode="Markdown"
        )
        LOG_NOTIFICATION("ط±ط¦ظٹط³", str(boss_chat_id), "ط§ظ„ظ…ط¯ظٹط±", text)
        return True
    except Exception as e:
        print(f"â‌Œ N001: {e}")
        return False

async def N002(context, client_chat_id, text):
    try:
        await context.bot.send_message(
            chat_id=client_chat_id,
            text=f"ًں“© *ط±ط³ط§ظ„ط© ظ…ظ† ظ…ظƒطھط¨ ط§ظ„ظ…ط­ط§ظ…ط§ط©*\n\n{text}",
            parse_mode="Markdown"
        )
        LOG_NOTIFICATION("ط¹ظ…ظٹظ„", str(client_chat_id), "ط¹ظ…ظٹظ„", text)
        return True
    except Exception as e:
        print(f"â‌Œ N002: {e}")
        return False

async def N003(context, assistant_chat_id, text):
    try:
        await context.bot.send_message(
            chat_id=assistant_chat_id,
            text=f"ًں“‹ *ظ…ظ‡ظ…ط© ط¬ط¯ظٹط¯ط© â€” ط£ظ…ظٹظ† ط§ظ„ط³ط±*\n\n{text}",
            parse_mode="Markdown"
        )
        LOG_NOTIFICATION("ظ…ط³ط§ط¹ط¯", str(assistant_chat_id), "ظ…ط³ط§ط¹ط¯", text)
        return True
    except Exception as e:
        print(f"â‌Œ N003: {e}")
        return False

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Events Helper Functions
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def C001(title, date, location=""):
    try:
        if not V001(title) or not V004(date): return None
        success = P003("Events", [title, date, location, datetime.now().strftime("%Y-%m-%d %H:%M")])
        return {"title": title, "date": date, "location": location} if success else None
    except Exception as e:
        print(f"â‌Œ C001: {e}")
        return None

def C002(event_ref, updated_data):
    try:
        records = P005("Events")
        for i, record in enumerate(records, start=2):
            if str(list(record.values())[0]) == str(event_ref):
                for col, val in updated_data.items():
                    col_i = list(record.keys()).index(col) + 1
                    P004("Events", i, col_i, val)
                return True
        return False
    except Exception as e:
        print(f"â‌Œ C002: {e}")
        return False

def C003():
    try:
        records = P005("Events")
        today = datetime.now().date()
        upcoming = []
        for r in records:
            date_val = r.get("event_date", "") or r.get("date", "")
            for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
                try:
                    d = datetime.strptime(str(date_val).strip(), fmt).date()
                    if d >= today:
                        upcoming.append(r)
                    break
                except: continue
        return sorted(upcoming, key=lambda x: x.get("event_date", x.get("date", "")))
    except Exception as e:
        print(f"â‌Œ C003: {e}")
        return []

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Link Functions
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def L001(user_type, ref_code):
    try:
        token = hashlib.sha256(f"{user_type}:{ref_code}:{int(time.time())}".encode()).hexdigest()[:16]
        return f"https://t.me/amin_alsir_bot?start={user_type}_{ref_code}_{token}"
    except Exception as e:
        print(f"â‌Œ L001: {e}")
        return None

async def L002(context, recipient_chat_id, link):
    try:
        await context.bot.send_message(chat_id=recipient_chat_id, text=f"ًں”— *ط±ط§ط¨ط· ظ„ظˆط­ط© ط§ظ„ظ‚ظٹط§ط¯ط©*\n\n{link}", parse_mode="Markdown")
        return True
    except Exception as e:
        print(f"â‌Œ L002: {e}")
        return False

def L003(link):
    try:
        if not link or "start=" not in link: return None
        parts = link.split("start=")[-1].split("_")
        if len(parts) < 3: return None
        return {"user_type": parts[0], "ref_code": parts[1], "token": parts[2]}
    except Exception as e:
        print(f"â‌Œ L003: {e}")
        return None
