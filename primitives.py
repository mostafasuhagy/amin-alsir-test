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

# ─────────────────────────────────────
# المناطق الزمنية للدول العربية
# ─────────────────────────────────────
ARAB_TIMEZONES = {
    "مصر":       "Africa/Cairo",
    "السعودية":  "Asia/Riyadh",
    "الإمارات":  "Asia/Dubai",
    "الكويت":    "Asia/Kuwait",
    "قطر":       "Asia/Qatar",
    "البحرين":   "Asia/Bahrain",
    "الأردن":    "Asia/Amman",
    "لبنان":     "Asia/Beirut",
    "المغرب":    "Africa/Casablanca",
    "تونس":      "Africa/Tunis",
    "الجزائر":   "Africa/Algiers",
    "ليبيا":     "Africa/Tripoli",
    "العراق":    "Asia/Baghdad",
    "سوريا":     "Asia/Damascus",
    "اليمن":     "Asia/Aden",
    "عمان":      "Asia/Muscat",
    "السودان":   "Africa/Khartoum",
    "فلسطين":   "Asia/Gaza",
}

def GET_TIMEZONE(country):
    return ARAB_TIMEZONES.get(country, "Africa/Cairo")

def NOW_LOCAL(country="مصر"):
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(GET_TIMEZONE(country))
        return datetime.now(tz).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return datetime.now().strftime("%Y-%m-%d %H:%M")

# ─────────────────────────────────────
# Multi-Tenant — إدارة المشتركين
# ─────────────────────────────────────
def MT001(chat_id):
    try:
        records = P005("Tenants", TENANTS_SHEET)
        for r in records:
            if str(r.get("chat_id", "")) == str(chat_id):
                return r
        return None
    except Exception as e:
        print(f"❌ MT001: {e}")
        return None

def MT002(chat_id, office_name, country, boss_chat_id, sheet_name, drive_folder_id="",
           status="trial", billing_cycle="", sheet_id=""):
    try:
        code = G001("Of", "Tenants", TENANTS_SHEET)
        today_str = NOW_LOCAL(country)[:10]  # YYYY-MM-DD فقط لأعمدة التاريخ
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
            "",                       # M  subscription_end_date (تتحدد بعد الدفع/انتهاء التجربة)
            sheet_id,                  # N  sheet_id
        ], TENANTS_SHEET)
        print(f"✅ MT002: تم تسجيل مكتب — {office_name} ({country}) — status={status}")
        return code if ok else None
    except Exception as e:
        print(f"❌ MT002: {e}")
        return None

def MT003(chat_id):
    try:
        tenant = MT001(chat_id)
        if not tenant:
            return False
        return tenant.get("status", "") == "active"
    except Exception as e:
        print(f"❌ MT003: {e}")
        return False

def MT004(chat_id):
    try:
        tenant = MT001(chat_id)
        if not tenant:
            return SHEET_NAME
        return tenant.get("sheet_name", SHEET_NAME)
    except Exception as e:
        print(f"❌ MT004: {e}")
        return SHEET_NAME

def MT005(chat_id):
    try:
        tenant = MT001(chat_id)
        if not tenant:
            return "Africa/Cairo"
        return tenant.get("timezone", "Africa/Cairo")
    except Exception as e:
        print(f"❌ MT005: {e}")
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

        # ── إنشاء ملف الشيت مباشرة داخل الـ Shared Drive ──
        # لا نستخدم sheets_service.spreadsheets().create() لأنها تنشئ
        # الملف في "My Drive" الخاص بحساب الـ Service Account، وهي مساحة
        # تخزين شخصية محدودة جدًا (شبه صفرية) وتمتلئ بسرعة مع تكرار
        # الإنشاء، فترجع 403 "the caller does not have permission" (رسالة
        # خطأ مضلّلة من جوجل لمشكلة Storage quota لا علاقة لها بالصلاحيات).
        # الحل: نستخدم drive_service.files().create() مع تحديد parents
        # على الـ Shared Drive (مساحته منفصلة ومتجددة)، فينشأ الملف هناك
        # من اللحظة الأولى ولا يستهلك أي شيء من مساحة الـ Service Account.
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
        print(f"✅ MT006: تم إنشاء الشيت داخل Shared Drive — {sheet_name} ({spreadsheet_id})")

        # الملف الجديد بيتولد بتاب افتراضي واحد اسمه "Sheet1" — نضيف
        # التابات المطلوبة، ثم نحذف "Sheet1" الافتراضي في نفس الطلب.
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
        print(f"✅ MT006: تم إضافة الـ tabs التسعة")

        # حذف "Sheet1" الافتراضي (sheetId يكون دايمًا 0 في ملف جديد)
        try:
            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": [{"deleteSheet": {"sheetId": 0}}]}
            ).execute()
            print(f"✅ MT006: تم حذف Sheet1 الافتراضي")
        except Exception as e:
            print(f"⚠️ MT006: فشل حذف Sheet1 الافتراضي — {e}")

        # ── تنسيق كل أعمدة كل تاب كـ "نص عادي" (PLAIN_TEXT) ──
        # بدون هذا، Google Sheets يخمّن نوع كل عمود تلقائيًا من البيانات
        # المُدخلة، وأكواد مثل "Cl-001" أو تواريخ مثل "2026-06-28" ممكن
        # تتفسّر غلط كأرقام أو تواريخ، فتظهر بصيغة مختلفة تمامًا (مثل
        # تحويل وقت الإدخال نفسه لتاريخ في عمود الكود). هذا يثبّت كل
        # خلية كنص خام صراحة، بصرف النظر عن شكل القيمة المُدخلة.
        try:
            new_sheet_ids = [
                reply["addSheet"]["properties"]["sheetId"]
                for reply in batch_response.get("replies", [])
                if "addSheet" in reply
            ]
            format_requests = [
                {
                    "repeatCell": {
                        "range": {"sheetId": sid},
                        "cell": {"userEnteredFormat": {"numberFormat": {"type": "TEXT"}}},
                        "fields": "userEnteredFormat.numberFormat",
                    }
                }
                for sid in new_sheet_ids
            ]
            if format_requests:
                sheets_service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body={"requests": format_requests}
                ).execute()
                print(f"✅ MT006: تم تثبيت تنسيق النص العادي لكل الـ tabs")
        except Exception as e:
            print(f"⚠️ MT006: فشل تثبيت تنسيق النص العادي — {e}")

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
        print(f"✅ MT006: تم إضافة الهيدرز لكل الـ tabs")

        # ── مشاركة الشيت مع حساب Apps Script (للكتابة من لوحات القيادة) ──
        # Code.gs منشور ويعمل تحت حساب mostafa.suhagy@gmail.com، فلازم
        # يكون عنده صلاحية "محرر" على كل شيت مكتب جديد، وإلا postToSheet
        # هتفشل بصمت برسالة "You do not have permission to access the
        # requested document." حتى لو الكتابة نفسها (P003) عبر البوت شغالة.
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
            print(f"✅ MT006: تم مشاركة الشيت مع حساب Apps Script (mostafa.suhagy@gmail.com)")
        except Exception as e:
            print(f"⚠️ MT006: فشلت مشاركة الشيت مع حساب Apps Script — {e}")

        # ── مشاركة الشيت للقراءة العامة (anyone with the link) ──
        # لوحات القيادة (HTML dashboards) بتقرا بيانات الشيت مباشرة عبر
        # رابط gviz/tq (CSV export) من متصفح المستخدم بدون تسجيل دخول،
        # فلازم الشيت يكون "Anyone with the link - Viewer" وإلا fetchSheet()
        # هترجع CORS error / redirect لصفحة تسجيل دخول Google.
        try:
            drive_service.permissions().create(
                fileId=spreadsheet_id,
                body={
                    "type": "anyone",
                    "role": "reader"
                },
                supportsAllDrives=True
            ).execute()
            print(f"✅ MT006: تم تفعيل القراءة العامة للشيت (Anyone with the link - Viewer)")
        except Exception as e:
            print(f"⚠️ MT006: فشل تفعيل القراءة العامة للشيت — {e}")

        return sheet_name, spreadsheet_id

    except Exception as e:
        print(f"❌ MT006: {e}")
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
        print(f"✅ MT007: تم إنشاء مجلد Drive — {folder_name} ({folder_id})")
        return folder_id

    except Exception as e:
        print(f"❌ MT007: {e}")
        return None

# ─────────────────────────────────────
# P001 — الاتصال بـ Google Sheets
# ─────────────────────────────────────
def P001(sheet_name=SHEET_NAME):
    try:
        creds_json = os.environ.get("GOOGLE_CREDENTIALS")
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        return client.open(sheet_name)
    except Exception as e:
        print(f"❌ P001: {e}")
        return None

# ─────────────────────────────────────
# P001C — الاتصال بـ Google Calendar
# ─────────────────────────────────────
def P001C():
    try:
        from googleapiclient.discovery import build
        creds_json = os.environ.get("GOOGLE_CREDENTIALS")
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        service = build("calendar", "v3", credentials=creds)
        return service
    except Exception as e:
        print(f"❌ P001C: {e}")
        return None

# ─────────────────────────────────────
# P001D — الاتصال بـ Google Drive (Shared Drive)
# ─────────────────────────────────────
def P001D():
    try:
        from googleapiclient.discovery import build
        creds_json = os.environ.get("GOOGLE_CREDENTIALS")
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        service = build("drive", "v3", credentials=creds)
        return service
    except Exception as e:
        print(f"❌ P001D: {e}")
        return None

# ─────────────────────────────────────
# Google Sheets Functions
# ─────────────────────────────────────
def P002(tab, ref_code, sheet_name=SHEET_NAME):
    try:
        ws = P001(sheet_name).worksheet(tab)
        for r in ws.get_all_records():
            if str(list(r.values())[0]).strip().lower() == str(ref_code).strip().lower():
                return r
        return None
    except Exception as e:
        print(f"❌ P002: {e}")
        return None

def P003(tab, data, sheet_name=SHEET_NAME):
    try:
        # نحوّل كل قيمة في الصف إلى نص صراحة قبل الكتابة. هذا يضمن أن
        # Google Sheets لن يفسّر أي قيمة (كود، رقم قومي، تاريخ مكتوب
        # كنص) كتاريخ أو رقم تلقائيًا، بصرف النظر عن تنسيق العمود أو
        # محتواه — الحل النهائي القاطع لمشكلة تحوّل الأكواد لتواريخ.
        safe_data = [str(v) if v is not None else "" for v in data]
        # العمود الأول هو دائمًا كود مرجعي (client_code, topic_code...).
        # نضيف له علامة اقتباس مبتدئة (') — وهي الطريقة القياسية في
        # Google Sheets لإجبار أي خلية على المعاملة كنص خام صراحة،
        # بصرف النظر عن أي تخمين تلقائي لنوع البيانات.
        if safe_data and not safe_data[0].startswith("'"):
            safe_data[0] = "'" + safe_data[0]
        P001(sheet_name).worksheet(tab).append_row(safe_data, value_input_option="RAW")
        return True
    except Exception as e:
        print(f"❌ P003: {e}")
        return False

def P004(tab, row, col, value, sheet_name=SHEET_NAME):
    try:
        P001(sheet_name).worksheet(tab).update_cell(row, col, value)
        return True
    except Exception as e:
        print(f"❌ P004: {e}")
        return False

def P005(tab, sheet_name=SHEET_NAME):
    try:
        return P001(sheet_name).worksheet(tab).get_all_records()
    except Exception as e:
        print(f"❌ P005: {e}")
        return []

def P006(tab, col_name, value, sheet_name=SHEET_NAME):
    try:
        return [r for r in P005(tab, sheet_name) if str(r.get(col_name, "")).strip().lower() == str(value).strip().lower()]
    except Exception as e:
        print(f"❌ P006: {e}")
        return []

def G001(prefix, tab, sheet_name=SHEET_NAME):
    try:
        count = len(P005(tab, sheet_name)) + 1
        return f"{prefix}-{count:03d}"
    except Exception as e:
        print(f"❌ G001: {e}")
        return f"{prefix}-001"

# ─────────────────────────────────────
# Notification Logger
# ─────────────────────────────────────
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
        print(f"✅ LOG_NOTIFICATION: {code} — {notif_type} — {name}")
    except Exception as e:
        print(f"❌ LOG_NOTIFICATION: {e}")

# ─────────────────────────────────────
# Validators
# ─────────────────────────────────────
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

# ─────────────────────────────────────
# Google Calendar Functions
# ─────────────────────────────────────
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
            print(f"❌ CAL001: تنسيق التاريخ غير صحيح: {date_str}")
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
        print(f"✅ CAL001: تم إضافة الحدث — {event_id}")
        return event_id
    except Exception as e:
        print(f"❌ CAL001: {e}")
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
                "id": e.get("id", ""), "title": e.get("summary", "—"),
                "start": start, "location": e.get("location", ""),
                "description": e.get("description", ""),
            })
        return formatted
    except Exception as e:
        print(f"❌ CAL002: {e}")
        return []

def CAL003(event_id, calendar_id=CALENDAR_ID):
    try:
        service = P001C()
        if not service:
            return False
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        print(f"✅ CAL003: تم حذف الحدث — {event_id}")
        return True
    except Exception as e:
        print(f"❌ CAL003: {e}")
        return False

def CAL004(event_id, updates, calendar_id=CALENDAR_ID):
    try:
        service = P001C()
        if not service:
            return False
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        event.update(updates)
        service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
        print(f"✅ CAL004: تم تعديل الحدث — {event_id}")
        return True
    except Exception as e:
        print(f"❌ CAL004: {e}")
        return False

def CAL005(event_id, result_text, calendar_id=CALENDAR_ID):
    try:
        return CAL004(event_id, {"description": f"النتيجة: {result_text}"}, calendar_id)
    except Exception as e:
        print(f"❌ CAL005: {e}")
        return False

# ─────────────────────────────────────
# Google Drive Functions
# ─────────────────────────────────────
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

        print(f"✅ DRV001: تم رفع الملف — {file_name} → {drive_link}")
        return drive_link

    except Exception as e:
        print(f"❌ DRV001: {e}")
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
                "name":         f.get("name", "—"),
                "link":         f.get("webViewLink", f"https://drive.google.com/file/d/{f['id']}/view"),
                "created_time": f.get("createdTime", "")[:10],
            })

        print(f"✅ DRV002: تم جلب {len(files)} ملف للموضوع {topic_code}")
        return files

    except Exception as e:
        print(f"❌ DRV002: {e}")
        return []


def DRV003(file_id):
    try:
        service = P001D()
        if not service:
            return False
        service.files().delete(fileId=file_id, supportsAllDrives=True).execute()
        print(f"✅ DRV003: تم حذف الملف — {file_id}")
        return True
    except Exception as e:
        print(f"❌ DRV003: {e}")
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
            print(f"✅ DRV004: مجلد موجود — {folder_name} ({existing[0]['id']})")
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
        print(f"✅ DRV004: تم إنشاء مجلد — {folder_name} ({folder_id})")
        return folder_id

    except Exception as e:
        print(f"❌ DRV004: {e}")
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

        print(f"✅ DRV005: تم رفع الملف — {file_name} → {drive_link}")
        return drive_link

    except Exception as e:
        print(f"❌ DRV005: {e}")
        return None

# ─────────────────────────────────────
# Telegram Message Functions
# ─────────────────────────────────────
async def T001(context, chat_id, text):
    try:
        return await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
    except Exception as e:
        print(f"❌ T001: {e}")
        return None

async def T002(context, chat_id, text, buttons):
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        kb = [[InlineKeyboardButton(b["text"], callback_data=b["callback_data"]) for b in row] for row in buttons]
        return await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    except Exception as e:
        print(f"❌ T002: {e}")
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
        print(f"❌ T003: {e}")
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
        print(f"❌ T004: {e}")
        return None

async def T005(context, chat_id, text, options):
    try:
        return await T002(context, chat_id, text, [[opt] for opt in options])
    except Exception as e:
        print(f"❌ T005: {e}")
        return None

# ─────────────────────────────────────
# Notification Functions
# ─────────────────────────────────────
async def N001(context, boss_chat_id, text):
    try:
        await context.bot.send_message(
            chat_id=boss_chat_id,
            text=f"🔔 *إشعار — أمين السر*\n\n{text}",
            parse_mode="Markdown"
        )
        LOG_NOTIFICATION("رئيس", str(boss_chat_id), "المدير", text)
        return True
    except Exception as e:
        print(f"❌ N001: {e}")
        return False

async def N002(context, client_chat_id, text):
    try:
        await context.bot.send_message(
            chat_id=client_chat_id,
            text=f"📩 *رسالة من مكتب المحاماة*\n\n{text}",
            parse_mode="Markdown"
        )
        LOG_NOTIFICATION("عميل", str(client_chat_id), "عميل", text)
        return True
    except Exception as e:
        print(f"❌ N002: {e}")
        return False

async def N003(context, assistant_chat_id, text):
    try:
        await context.bot.send_message(
            chat_id=assistant_chat_id,
            text=f"📋 *مهمة جديدة — أمين السر*\n\n{text}",
            parse_mode="Markdown"
        )
        LOG_NOTIFICATION("مساعد", str(assistant_chat_id), "مساعد", text)
        return True
    except Exception as e:
        print(f"❌ N003: {e}")
        return False

# ─────────────────────────────────────
# Events Helper Functions
# ─────────────────────────────────────
def C001(title, date, location=""):
    try:
        if not V001(title) or not V004(date): return None
        success = P003("Events", [title, date, location, datetime.now().strftime("%Y-%m-%d %H:%M")])
        return {"title": title, "date": date, "location": location} if success else None
    except Exception as e:
        print(f"❌ C001: {e}")
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
        print(f"❌ C002: {e}")
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
        print(f"❌ C003: {e}")
        return []

# ─────────────────────────────────────
# Link Functions
# ─────────────────────────────────────
def L001(user_type, ref_code):
    try:
        token = hashlib.sha256(f"{user_type}:{ref_code}:{int(time.time())}".encode()).hexdigest()[:16]
        return f"https://t.me/amin_alsir_bot?start={user_type}_{ref_code}_{token}"
    except Exception as e:
        print(f"❌ L001: {e}")
        return None

async def L002(context, recipient_chat_id, link):
    try:
        await context.bot.send_message(chat_id=recipient_chat_id, text=f"🔗 *رابط لوحة القيادة*\n\n{link}", parse_mode="Markdown")
        return True
    except Exception as e:
        print(f"❌ L002: {e}")
        return False

def L003(link):
    try:
        if not link or "start=" not in link: return None
        parts = link.split("start=")[-1].split("_")
        if len(parts) < 3: return None
        return {"user_type": parts[0], "ref_code": parts[1], "token": parts[2]}
    except Exception as e:
        print(f"❌ L003: {e}")
        return None
