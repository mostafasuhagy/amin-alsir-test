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
TRIAL_DAYS = 7

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/calendar",
]

# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
# ╪د┘┘à┘╪د╪╖┘é ╪د┘╪▓┘à┘┘è╪ر ┘┘╪»┘ê┘ ╪د┘╪╣╪▒╪ذ┘è╪ر
# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
ARAB_TIMEZONES = {
    "┘à╪╡╪▒":       "Africa/Cairo",
    "╪د┘╪│╪╣┘ê╪»┘è╪ر":  "Asia/Riyadh",
    "╪د┘╪ح┘à╪د╪▒╪د╪ز":  "Asia/Dubai",
    "╪د┘┘â┘ê┘è╪ز":    "Asia/Kuwait",
    "┘é╪╖╪▒":       "Asia/Qatar",
    "╪د┘╪ذ╪ص╪▒┘è┘":   "Asia/Bahrain",
    "╪د┘╪ث╪▒╪»┘":    "Asia/Amman",
    "┘╪ذ┘╪د┘":     "Asia/Beirut",
    "╪د┘┘à╪║╪▒╪ذ":    "Africa/Casablanca",
    "╪ز┘ê┘╪│":      "Africa/Tunis",
    "╪د┘╪ش╪▓╪د╪خ╪▒":   "Africa/Algiers",
    "┘┘è╪ذ┘è╪د":     "Africa/Tripoli",
    "╪د┘╪╣╪▒╪د┘é":    "Asia/Baghdad",
    "╪│┘ê╪▒┘è╪د":     "Asia/Damascus",
    "╪د┘┘è┘à┘":     "Asia/Aden",
    "╪╣┘à╪د┘":      "Asia/Muscat",
    "╪د┘╪│┘ê╪»╪د┘":   "Africa/Khartoum",
    "┘┘╪│╪╖┘è┘":   "Asia/Gaza",
}

def GET_TIMEZONE(country):
    return ARAB_TIMEZONES.get(country, "Africa/Cairo")

def NOW_LOCAL(country="┘à╪╡╪▒"):
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(GET_TIMEZONE(country))
        return datetime.now(tz).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return datetime.now().strftime("%Y-%m-%d %H:%M")

# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
# Multi-Tenant ظ¤ ╪ح╪»╪د╪▒╪ر ╪د┘┘à╪┤╪ز╪▒┘â┘è┘
# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
def MT001(chat_id):
    try:
        records = P005("Tenants", TENANTS_SHEET)
        for r in records:
            if str(r.get("chat_id", "")) == str(chat_id):
                return r
        return None
    except Exception as e:
        print(f"ظإî MT001: {e}")
        return None

def MT002(chat_id, office_name, country, boss_chat_id, sheet_name, drive_folder_id="",
           status="trial", billing_cycle="", sheet_id=""):
    try:
        code = G001("Of", "Tenants", TENANTS_SHEET)
        today_str = NOW_LOCAL(country)[:10]  # YYYY-MM-DD ┘┘é╪╖ ┘╪ث╪╣┘à╪»╪ر ╪د┘╪ز╪د╪▒┘è╪«
        ok = P003("Tenants", [
            code,                  # A  tenant_code
            str(chat_id),          # B  chat_id
            office_name,           # C  office_name
            country,                # D  country
            GET_TIMEZONE(country), # E  timezone
            str(boss_chat_id),     # F  boss_chat_id
            sheet_name,             # G  sheet_name
            drive_folder_id,        # H  drive_folder_id
            status,                 # I  status (trial / pending_payment / active)
            NOW_LOCAL(country),    # J  date_added
            today_str,               # K  trial_start_date
            billing_cycle,           # L  billing_cycle
            "",                       # M  subscription_end_date (╪ز╪ز╪ص╪»╪» ╪ذ╪╣╪» ╪د┘╪»┘╪╣/╪د┘╪ز┘ç╪د╪ة ╪د┘╪ز╪ش╪▒╪ذ╪ر)
            sheet_id,                  # N  sheet_id
        ], TENANTS_SHEET)
        print(f"ظ£à MT002: ╪ز┘à ╪ز╪│╪ش┘è┘ ┘à┘â╪ز╪ذ ظ¤ {office_name} ({country}) ظ¤ status={status}")
        return code if ok else None
    except Exception as e:
        print(f"ظإî MT002: {e}")
        return None

def MT003(chat_id):
    try:
        tenant = MT001(chat_id)
        if not tenant:
            return False
        return tenant.get("status", "") == "active"
    except Exception as e:
        print(f"ظإî MT003: {e}")
        return False

def MT004(chat_id):
    try:
        tenant = MT001(chat_id)
        if not tenant:
            return SHEET_NAME
        return tenant.get("sheet_name", SHEET_NAME)
    except Exception as e:
        print(f"ظإî MT004: {e}")
        return SHEET_NAME

def MT005(chat_id):
    try:
        tenant = MT001(chat_id)
        if not tenant:
            return "Africa/Cairo"
        return tenant.get("timezone", "Africa/Cairo")
    except Exception as e:
        print(f"ظإî MT005: {e}")
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

        # ظ¤ظ¤ ╪ح┘╪┤╪د╪ة ┘à┘┘ ╪د┘╪┤┘è╪ز ┘à╪ذ╪د╪┤╪▒╪ر ╪»╪د╪«┘ ╪د┘┘ Shared Drive ظ¤ظ¤
        # ┘╪د ┘╪│╪ز╪«╪»┘à sheets_service.spreadsheets().create() ┘╪ث┘┘ç╪د ╪ز┘╪┤╪خ
        # ╪د┘┘à┘┘ ┘┘è "My Drive" ╪د┘╪«╪د╪╡ ╪ذ╪ص╪│╪د╪ذ ╪د┘┘ Service Account╪î ┘ê┘ç┘è ┘à╪│╪د╪ص╪ر
        # ╪ز╪«╪▓┘è┘ ╪┤╪«╪╡┘è╪ر ┘à╪ص╪»┘ê╪»╪ر ╪ش╪»┘ï╪د (╪┤╪ذ┘ç ╪╡┘╪▒┘è╪ر) ┘ê╪ز┘à╪ز┘╪خ ╪ذ╪│╪▒╪╣╪ر ┘à╪╣ ╪ز┘â╪▒╪د╪▒
        # ╪د┘╪ح┘╪┤╪د╪ة╪î ┘╪ز╪▒╪ش╪╣ 403 "the caller does not have permission" (╪▒╪│╪د┘╪ر
        # ╪«╪╖╪ث ┘à╪╢┘┘ّ┘╪ر ┘à┘ ╪ش┘ê╪ش┘ ┘┘à╪┤┘â┘╪ر Storage quota ┘╪د ╪╣┘╪د┘é╪ر ┘┘ç╪د ╪ذ╪د┘╪╡┘╪د╪ص┘è╪د╪ز).
        # ╪د┘╪ص┘: ┘╪│╪ز╪«╪»┘à drive_service.files().create() ┘à╪╣ ╪ز╪ص╪»┘è╪» parents
        # ╪╣┘┘ë ╪د┘┘ Shared Drive (┘à╪│╪د╪ص╪ز┘ç ┘à┘┘╪╡┘╪ر ┘ê┘à╪ز╪ش╪»╪»╪ر)╪î ┘┘è┘╪┤╪ث ╪د┘┘à┘┘ ┘ç┘╪د┘â
        # ┘à┘ ╪د┘┘╪ص╪╕╪ر ╪د┘╪ث┘ê┘┘ë ┘ê┘╪د ┘è╪│╪ز┘ç┘┘â ╪ث┘è ╪┤┘è╪ة ┘à┘ ┘à╪│╪د╪ص╪ر ╪د┘┘ Service Account.
        file_metadata = {
            "name": sheet_name,
            "mimeType": "application/vnd.google-apps.spreadsheet",
            "parents": [SHARED_DRIVE_ID],
        }
        created_file = drive_service.files().create(
            body=file_metadata,
            fields="id",
            supportsAllDrives=True
        ).execute()
        spreadsheet_id = created_file["id"]
        print(f"ظ£à MT006: ╪ز┘à ╪ح┘╪┤╪د╪ة ╪د┘╪┤┘è╪ز ╪»╪د╪«┘ Shared Drive ظ¤ {sheet_name} ({spreadsheet_id})")

        # ╪د┘┘à┘┘ ╪د┘╪ش╪»┘è╪» ╪ذ┘è╪ز┘ê┘╪» ╪ذ╪ز╪د╪ذ ╪د┘╪ز╪▒╪د╪╢┘è ┘ê╪د╪ص╪» ╪د╪│┘à┘ç "Sheet1" ظ¤ ┘╪╢┘è┘
        # ╪د┘╪ز╪د╪ذ╪د╪ز ╪د┘┘à╪╖┘┘ê╪ذ╪ر╪î ╪س┘à ┘╪ص╪░┘ "Sheet1" ╪د┘╪د┘╪ز╪▒╪د╪╢┘è ┘┘è ┘┘╪│ ╪د┘╪╖┘╪ذ.
        add_sheets_body = {
            "requests": [
                {"addSheet": {"properties": {"title": "Clients"}}},
                {"addSheet": {"properties": {"title": "Topics"}}},
                {"addSheet": {"properties": {"title": "Events"}}},
                {"addSheet": {"properties": {"title": "Documents"}}},
                {"addSheet": {"properties": {"title": "Shipments"}}},
                {"addSheet": {"properties": {"title": "Custody"}}},
                {"addSheet": {"properties": {"title": "Assistants"}}},
                {"addSheet": {"properties": {"title": "Notifications"}}},
                {"addSheet": {"properties": {"title": "Services"}}},
            ]
        }
        batch_response = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=add_sheets_body
        ).execute()
        print(f"ظ£à MT006: ╪ز┘à ╪ح╪╢╪د┘╪ر ╪د┘┘ tabs ╪د┘╪ز╪│╪╣╪ر")

        # ╪ص╪░┘ "Sheet1" ╪د┘╪د┘╪ز╪▒╪د╪╢┘è (sheetId ┘è┘â┘ê┘ ╪»╪د┘è┘à┘ï╪د 0 ┘┘è ┘à┘┘ ╪ش╪»┘è╪»)
        try:
            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": [{"deleteSheet": {"sheetId": 0}}]}
            ).execute()
            print(f"ظ£à MT006: ╪ز┘à ╪ص╪░┘ Sheet1 ╪د┘╪د┘╪ز╪▒╪د╪╢┘è")
        except Exception as e:
            print(f"ظأبي╕ MT006: ┘╪┤┘ ╪ص╪░┘ Sheet1 ╪د┘╪د┘╪ز╪▒╪د╪╢┘è ظ¤ {e}")

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
        print(f"ظ£à MT006: ╪ز┘à ╪ح╪╢╪د┘╪ر ╪د┘┘ç┘è╪»╪▒╪▓ ┘┘â┘ ╪د┘┘ tabs")

        # ظ¤ظ¤ ┘à╪┤╪د╪▒┘â╪ر ╪د┘╪┤┘è╪ز ┘à╪╣ ╪ص╪│╪د╪ذ Apps Script (┘┘┘â╪ز╪د╪ذ╪ر ┘à┘ ┘┘ê╪ص╪د╪ز ╪د┘┘é┘è╪د╪»╪ر) ظ¤ظ¤
        # Code.gs ┘à┘╪┤┘ê╪▒ ┘ê┘è╪╣┘à┘ ╪ز╪ص╪ز ╪ص╪│╪د╪ذ mostafa.suhagy@gmail.com╪î ┘┘╪د╪▓┘à
        # ┘è┘â┘ê┘ ╪╣┘╪»┘ç ╪╡┘╪د╪ص┘è╪ر "┘à╪ص╪▒╪▒" ╪╣┘┘ë ┘â┘ ╪┤┘è╪ز ┘à┘â╪ز╪ذ ╪ش╪»┘è╪»╪î ┘ê╪ح┘╪د postToSheet
        # ┘ç╪ز┘╪┤┘ ╪ذ╪╡┘à╪ز ╪ذ╪▒╪│╪د┘╪ر "You do not have permission to access the
        # requested document." ╪ص╪ز┘ë ┘┘ê ╪د┘┘â╪ز╪د╪ذ╪ر ┘┘╪│┘ç╪د (P003) ╪╣╪ذ╪▒ ╪د┘╪ذ┘ê╪ز ╪┤╪║╪د┘╪ر.
        try:
            drive_service.permissions().create(
                fileId=spreadsheet_id,
                body={
                    "type": "user",
                    "role": "writer",
                    "emailAddress": "mostafa.suhagy@gmail.com"
                },
                supportsAllDrives=True
            ).execute()
            print(f"ظ£à MT006: ╪ز┘à ┘à╪┤╪د╪▒┘â╪ر ╪د┘╪┤┘è╪ز ┘à╪╣ ╪ص╪│╪د╪ذ Apps Script (mostafa.suhagy@gmail.com)")
        except Exception as e:
            print(f"ظأبي╕ MT006: ┘╪┤┘╪ز ┘à╪┤╪د╪▒┘â╪ر ╪د┘╪┤┘è╪ز ┘à╪╣ ╪ص╪│╪د╪ذ Apps Script ظ¤ {e}")

        # ظ¤ظ¤ ┘à╪┤╪د╪▒┘â╪ر ╪د┘╪┤┘è╪ز ┘┘┘é╪▒╪د╪ة╪ر ╪د┘╪╣╪د┘à╪ر (anyone with the link) ظ¤ظ¤
        # ┘┘ê╪ص╪د╪ز ╪د┘┘é┘è╪د╪»╪ر (HTML dashboards) ╪ذ╪ز┘é╪▒╪د ╪ذ┘è╪د┘╪د╪ز ╪د┘╪┤┘è╪ز ┘à╪ذ╪د╪┤╪▒╪ر ╪╣╪ذ╪▒
        # ╪▒╪د╪ذ╪╖ gviz/tq (CSV export) ┘à┘ ┘à╪ز╪╡┘╪ص ╪د┘┘à╪│╪ز╪«╪»┘à ╪ذ╪»┘ê┘ ╪ز╪│╪ش┘è┘ ╪»╪«┘ê┘╪î
        # ┘┘╪د╪▓┘à ╪د┘╪┤┘è╪ز ┘è┘â┘ê┘ "Anyone with the link - Viewer" ┘ê╪ح┘╪د fetchSheet()
        # ┘ç╪ز╪▒╪ش╪╣ CORS error / redirect ┘╪╡┘╪ص╪ر ╪ز╪│╪ش┘è┘ ╪»╪«┘ê┘ Google.
        try:
            drive_service.permissions().create(
                fileId=spreadsheet_id,
                body={
                    "type": "anyone",
                    "role": "reader"
                },
                supportsAllDrives=True
            ).execute()
            print(f"ظ£à MT006: ╪ز┘à ╪ز┘╪╣┘è┘ ╪د┘┘é╪▒╪د╪ة╪ر ╪د┘╪╣╪د┘à╪ر ┘┘╪┤┘è╪ز (Anyone with the link - Viewer)")
        except Exception as e:
            print(f"ظأبي╕ MT006: ┘╪┤┘ ╪ز┘╪╣┘è┘ ╪د┘┘é╪▒╪د╪ة╪ر ╪د┘╪╣╪د┘à╪ر ┘┘╪┤┘è╪ز ظ¤ {e}")

        return sheet_name, spreadsheet_id

    except Exception as e:
        print(f"ظإî MT006: {e}")
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
            "parents":  [SHARED_DRIVE_ID],
        }
        folder = service.files().create(
            body=folder_metadata,
            fields="id",
            supportsAllDrives=True
        ).execute()
        folder_id = folder.get("id")
        print(f"ظ£à MT007: ╪ز┘à ╪ح┘╪┤╪د╪ة ┘à╪ش┘╪» Drive ظ¤ {folder_name} ({folder_id})")
        return folder_id

    except Exception as e:
        print(f"ظإî MT007: {e}")
        return None

# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
# P001 ظ¤ ╪د┘╪د╪ز╪╡╪د┘ ╪ذ┘ Google Sheets
# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
def P001(sheet_name=SHEET_NAME):
    try:
        creds_json = os.environ.get("GOOGLE_CREDENTIALS")
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        return client.open(sheet_name)
    except Exception as e:
        print(f"ظإî P001: {e}")
        return None

# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
# P001C ظ¤ ╪د┘╪د╪ز╪╡╪د┘ ╪ذ┘ Google Calendar
# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
def P001C():
    try:
        from googleapiclient.discovery import build
        creds_json = os.environ.get("GOOGLE_CREDENTIALS")
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        service = build("calendar", "v3", credentials=creds)
        return service
    except Exception as e:
        print(f"ظإî P001C: {e}")
        return None

# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
# P001D ظ¤ ╪د┘╪د╪ز╪╡╪د┘ ╪ذ┘ Google Drive (Shared Drive)
# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
def P001D():
    try:
        from googleapiclient.discovery import build
        creds_json = os.environ.get("GOOGLE_CREDENTIALS")
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        service = build("drive", "v3", credentials=creds)
        return service
    except Exception as e:
        print(f"ظإî P001D: {e}")
        return None

# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
# Google Sheets Functions
# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
def P002(tab, ref_code, sheet_name=SHEET_NAME):
    try:
        ws = P001(sheet_name).worksheet(tab)
        for r in ws.get_all_records():
            if str(list(r.values())[0]).strip().lower() == str(ref_code).strip().lower():
                return r
        return None
    except Exception as e:
        print(f"ظإî P002: {e}")
        return None

def P003(tab, data, sheet_name=SHEET_NAME):
    try:
        P001(sheet_name).worksheet(tab).append_row(data, value_input_option="USER_ENTERED")
        return True
    except Exception as e:
        print(f"ظإî P003: {e}")
        return False

def P004(tab, row, col, value, sheet_name=SHEET_NAME):
    try:
        P001(sheet_name).worksheet(tab).update_cell(row, col, value)
        return True
    except Exception as e:
        print(f"ظإî P004: {e}")
        return False

def P005(tab, sheet_name=SHEET_NAME):
    try:
        return P001(sheet_name).worksheet(tab).get_all_records()
    except Exception as e:
        print(f"ظإî P005: {e}")
        return []

def P006(tab, col_name, value, sheet_name=SHEET_NAME):
    try:
        return [r for r in P005(tab, sheet_name) if str(r.get(col_name, "")).strip().lower() == str(value).strip().lower()]
    except Exception as e:
        print(f"ظإî P006: {e}")
        return []

def G001(prefix, tab, sheet_name=SHEET_NAME):
    try:
        count = len(P005(tab, sheet_name)) + 1
        return f"{prefix}-{count:03d}"
    except Exception as e:
        print(f"ظإî G001: {e}")
        return f"{prefix}-001"

# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
# Notification Logger
# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
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
        print(f"ظ£à LOG_NOTIFICATION: {code} ظ¤ {notif_type} ظ¤ {name}")
    except Exception as e:
        print(f"ظإî LOG_NOTIFICATION: {e}")

# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
# Validators
# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
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

# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
# Google Calendar Functions
# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
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
            print(f"ظإî CAL001: ╪ز┘╪│┘è┘é ╪د┘╪ز╪د╪▒┘è╪« ╪║┘è╪▒ ╪╡╪ص┘è╪ص: {date_str}")
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
        print(f"ظ£à CAL001: ╪ز┘à ╪ح╪╢╪د┘╪ر ╪د┘╪ص╪»╪س ظ¤ {event_id}")
        return event_id
    except Exception as e:
        print(f"ظإî CAL001: {e}")
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
                "id": e.get("id", ""), "title": e.get("summary", "ظ¤"),
                "start": start, "location": e.get("location", ""),
                "description": e.get("description", ""),
            })
        return formatted
    except Exception as e:
        print(f"ظإî CAL002: {e}")
        return []

def CAL003(event_id, calendar_id=CALENDAR_ID):
    try:
        service = P001C()
        if not service:
            return False
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        print(f"ظ£à CAL003: ╪ز┘à ╪ص╪░┘ ╪د┘╪ص╪»╪س ظ¤ {event_id}")
        return True
    except Exception as e:
        print(f"ظإî CAL003: {e}")
        return False

def CAL004(event_id, updates, calendar_id=CALENDAR_ID):
    try:
        service = P001C()
        if not service:
            return False
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        event.update(updates)
        service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
        print(f"ظ£à CAL004: ╪ز┘à ╪ز╪╣╪»┘è┘ ╪د┘╪ص╪»╪س ظ¤ {event_id}")
        return True
    except Exception as e:
        print(f"ظإî CAL004: {e}")
        return False

def CAL005(event_id, result_text, calendar_id=CALENDAR_ID):
    try:
        return CAL004(event_id, {"description": f"╪د┘┘╪ز┘è╪ش╪ر: {result_text}"}, calendar_id)
    except Exception as e:
        print(f"ظإî CAL005: {e}")
        return False

# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
# Google Drive Functions
# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
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

        print(f"ظ£à DRV001: ╪ز┘à ╪▒┘╪╣ ╪د┘┘à┘┘ ظ¤ {file_name} ظْ {drive_link}")
        return drive_link

    except Exception as e:
        print(f"ظإî DRV001: {e}")
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
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            corpora="drive",
            driveId=SHARED_DRIVE_ID
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
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            corpora="drive",
            driveId=SHARED_DRIVE_ID
        ).execute()

        files = []
        for f in res2.get("files", []):
            files.append({
                "name":         f.get("name", "ظ¤"),
                "link":         f.get("webViewLink", f"https://drive.google.com/file/d/{f['id']}/view"),
                "created_time": f.get("createdTime", "")[:10],
            })

        print(f"ظ£à DRV002: ╪ز┘à ╪ش┘╪ذ {len(files)} ┘à┘┘ ┘┘┘à┘ê╪╢┘ê╪╣ {topic_code}")
        return files

    except Exception as e:
        print(f"ظإî DRV002: {e}")
        return []


def DRV003(file_id):
    try:
        service = P001D()
        if not service:
            return False
        service.files().delete(fileId=file_id, supportsAllDrives=True).execute()
        print(f"ظ£à DRV003: ╪ز┘à ╪ص╪░┘ ╪د┘┘à┘┘ ظ¤ {file_id}")
        return True
    except Exception as e:
        print(f"ظإî DRV003: {e}")
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
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            corpora="drive",
            driveId=SHARED_DRIVE_ID
        ).execute()
        existing = res.get("files", [])
        if existing:
            print(f"ظ£à DRV004: ┘à╪ش┘╪» ┘à┘ê╪ش┘ê╪» ظ¤ {folder_name} ({existing[0]['id']})")
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
        print(f"ظ£à DRV004: ╪ز┘à ╪ح┘╪┤╪د╪ة ┘à╪ش┘╪» ظ¤ {folder_name} ({folder_id})")
        return folder_id

    except Exception as e:
        print(f"ظإî DRV004: {e}")
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

        print(f"ظ£à DRV005: ╪ز┘à ╪▒┘╪╣ ╪د┘┘à┘┘ ظ¤ {file_name} ظْ {drive_link}")
        return drive_link

    except Exception as e:
        print(f"ظإî DRV005: {e}")
        return None

# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
# Telegram Message Functions
# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
async def T001(context, chat_id, text):
    try:
        return await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
    except Exception as e:
        print(f"ظإî T001: {e}")
        return None

async def T002(context, chat_id, text, buttons):
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        kb = [[InlineKeyboardButton(b["text"], callback_data=b["callback_data"]) for b in row] for row in buttons]
        return await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    except Exception as e:
        print(f"ظإî T002: {e}")
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
        print(f"ظإî T003: {e}")
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
        print(f"ظإî T004: {e}")
        return None

async def T005(context, chat_id, text, options):
    try:
        return await T002(context, chat_id, text, [[opt] for opt in options])
    except Exception as e:
        print(f"ظإî T005: {e}")
        return None

# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
# Notification Functions
# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
async def N001(context, boss_chat_id, text):
    try:
        await context.bot.send_message(
            chat_id=boss_chat_id,
            text=f"≡ا¤¤ *╪ح╪┤╪╣╪د╪▒ ظ¤ ╪ث┘à┘è┘ ╪د┘╪│╪▒*\n\n{text}",
            parse_mode="Markdown"
        )
        LOG_NOTIFICATION("╪▒╪خ┘è╪│", str(boss_chat_id), "╪د┘┘à╪»┘è╪▒", text)
        return True
    except Exception as e:
        print(f"ظإî N001: {e}")
        return False

async def N002(context, client_chat_id, text):
    try:
        await context.bot.send_message(
            chat_id=client_chat_id,
            text=f"≡اôر *╪▒╪│╪د┘╪ر ┘à┘ ┘à┘â╪ز╪ذ ╪د┘┘à╪ص╪د┘à╪د╪ر*\n\n{text}",
            parse_mode="Markdown"
        )
        LOG_NOTIFICATION("╪╣┘à┘è┘", str(client_chat_id), "╪╣┘à┘è┘", text)
        return True
    except Exception as e:
        print(f"ظإî N002: {e}")
        return False

async def N003(context, assistant_chat_id, text):
    try:
        await context.bot.send_message(
            chat_id=assistant_chat_id,
            text=f"≡اôï *┘à┘ç┘à╪ر ╪ش╪»┘è╪»╪ر ظ¤ ╪ث┘à┘è┘ ╪د┘╪│╪▒*\n\n{text}",
            parse_mode="Markdown"
        )
        LOG_NOTIFICATION("┘à╪│╪د╪╣╪»", str(assistant_chat_id), "┘à╪│╪د╪╣╪»", text)
        return True
    except Exception as e:
        print(f"ظإî N003: {e}")
        return False

# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
# Events Helper Functions
# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
def C001(title, date, location=""):
    try:
        if not V001(title) or not V004(date): return None
        success = P003("Events", [title, date, location, datetime.now().strftime("%Y-%m-%d %H:%M")])
        return {"title": title, "date": date, "location": location} if success else None
    except Exception as e:
        print(f"ظإî C001: {e}")
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
        print(f"ظإî C002: {e}")
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
        print(f"ظإî C003: {e}")
        return []

# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
# Link Functions
# ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤ظ¤
def L001(user_type, ref_code):
    try:
        token = hashlib.sha256(f"{user_type}:{ref_code}:{int(time.time())}".encode()).hexdigest()[:16]
        return f"https://t.me/amin_alsir_bot?start={user_type}_{ref_code}_{token}"
    except Exception as e:
        print(f"ظإî L001: {e}")
        return None

async def L002(context, recipient_chat_id, link):
    try:
        await context.bot.send_message(chat_id=recipient_chat_id, text=f"≡ا¤ù *╪▒╪د╪ذ╪╖ ┘┘ê╪ص╪ر ╪د┘┘é┘è╪د╪»╪ر*\n\n{link}", parse_mode="Markdown")
        return True
    except Exception as e:
        print(f"ظإî L002: {e}")
        return False

def L003(link):
    try:
        if not link or "start=" not in link: return None
        parts = link.split("start=")[-1].split("_")
        if len(parts) < 3: return None
        return {"user_type": parts[0], "ref_code": parts[1], "token": parts[2]}
    except Exception as e:
        print(f"ظإî L003: {e}")
        return None
