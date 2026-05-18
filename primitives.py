import os
import re
import json
import gspread
import hashlib
import time
from datetime import datetime
from google.oauth2.service_account import Credentials

SHEET_NAME = "amin_alsir_cases_new_V2"
CALENDAR_ID = "mostafa.suhagy@gmail.com"  # Google Calendar ID
DRIVE_FOLDER_ID = "1_T8yAzq62a28jDcX93W-DHLEF5E_YUee"  # ✅ مجلد amin_alsir_docs

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/calendar",  # ✅ Google Calendar
]

# ─────────────────────────────────────────────
# P001 — الاتصال بـ Google Sheets
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# P001C — الاتصال بـ Google Calendar
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# P001D — الاتصال بـ Google Drive
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# Google Sheets Functions
# ─────────────────────────────────────────────
def P002(tab, ref_code, sheet_name=SHEET_NAME):
    try:
        ws = P001(sheet_name).worksheet(tab)
        for r in ws.get_all_records():
            if str(list(r.values())[0]) == str(ref_code):
                return r
        return None
    except Exception as e:
        print(f"❌ P002: {e}")
        return None

def P003(tab, data, sheet_name=SHEET_NAME):
    try:
        P001(sheet_name).worksheet(tab).append_row(data, value_input_option="USER_ENTERED")
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
        return [r for r in P005(tab, sheet_name) if str(r.get(col_name, "")) == str(value)]
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

# ─────────────────────────────────────────────
# Validators
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# Google Calendar Functions
# ─────────────────────────────────────────────

def CAL001(title, date_str, time_str="", location="", description="", calendar_id=CALENDAR_ID):
    """
    إضافة حدث جديد في Google Calendar
    date_str: DD/MM/YYYY أو YYYY-MM-DD
    time_str: HH:MM (اختياري)
    """
    try:
        service = P001C()
        if not service:
            return None

        # تحويل التاريخ
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                date_obj = datetime.strptime(date_str.strip(), fmt)
                break
            except: continue
        else:
            print(f"❌ CAL001: تنسيق التاريخ غير صحيح: {date_str}")
            return None

        # بناء الحدث
        if time_str:
            try:
                hour, minute = time_str.strip().split(":")[:2]
                minute = minute[:2]
                start_dt = date_obj.replace(hour=int(hour), minute=int(minute))
                end_dt   = start_dt.replace(hour=int(hour)+1)
                event = {
                    "summary":     title,
                    "location":    location,
                    "description": description,
                    "start": {"dateTime": start_dt.strftime("%Y-%m-%dT%H:%M:00"), "timeZone": "Africa/Cairo"},
                    "end":   {"dateTime": end_dt.strftime("%Y-%m-%dT%H:%M:00"),   "timeZone": "Africa/Cairo"},
                }
            except:
                event = {
                    "summary":     title,
                    "location":    location,
                    "description": description,
                    "start": {"date": date_obj.strftime("%Y-%m-%d")},
                    "end":   {"date": date_obj.strftime("%Y-%m-%d")},
                }
        else:
            event = {
                "summary":     title,
                "location":    location,
                "description": description,
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
    """
    عرض الأحداث القادمة من Google Calendar
    """
    try:
        service = P001C()
        if not service:
            return []

        now = datetime.utcnow().isoformat() + "Z"
        result = service.events().list(
            calendarId=calendar_id,
            timeMin=now,
            maxResults=20,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = result.get("items", [])
        formatted = []
        for e in events:
            start = e["start"].get("dateTime", e["start"].get("date", ""))
            formatted.append({
                "id":          e.get("id", ""),
                "title":       e.get("summary", "—"),
                "start":       start,
                "location":    e.get("location", ""),
                "description": e.get("description", ""),
            })
        return formatted

    except Exception as e:
        print(f"❌ CAL002: {e}")
        return []


def CAL003(event_id, calendar_id=CALENDAR_ID):
    """
    حذف حدث من Google Calendar
    """
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
    """
    تعديل حدث في Google Calendar
    updates: dict مثل {"summary": "عنوان جديد", "location": "مكان جديد"}
    """
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
    """
    تسجيل نتيجة حدث في Google Calendar (تحديث الوصف)
    """
    try:
        return CAL004(event_id, {"description": f"النتيجة: {result_text}"}, calendar_id)
    except Exception as e:
        print(f"❌ CAL005: {e}")
        return False

# ─────────────────────────────────────────────
# Google Drive Functions
# ─────────────────────────────────────────────

def DRV001(file_path, file_name, topic_code, folder_id=DRIVE_FOLDER_ID):
    """
    رفع ملف إلى Google Drive داخل مجلد الموضوع
    file_path  : المسار المحلي للملف (مؤقت)
    file_name  : اسم الملف كما سيُحفظ في Drive
    topic_code : كود الموضوع (يُستخدم لإنشاء مجلد فرعي)
    يُرجع: drive_link أو None
    """
    try:
        from googleapiclient.http import MediaFileUpload
        import mimetypes

        service = P001D()
        if not service:
            return None

        # إنشاء أو الحصول على مجلد الموضوع داخل amin_alsir_docs
        sub_folder_id = DRV004(topic_code, folder_id)
        if not sub_folder_id:
            return None

        # تحديد نوع الملف
        mime_type, _ = mimetypes.guess_type(file_name)
        if not mime_type:
            mime_type = "application/octet-stream"

        # رفع الملف
        file_metadata = {
            "name":    file_name,
            "parents": [sub_folder_id],
        }
        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
        uploaded = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink"
        ).execute()

        file_id   = uploaded.get("id")
        drive_link = uploaded.get("webViewLink", f"https://drive.google.com/file/d/{file_id}/view")

        # منح صلاحية عرض للجميع (anyone with link)
        service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"}
        ).execute()

        print(f"✅ DRV001: تم رفع الملف — {file_name} → {drive_link}")
        return drive_link

    except Exception as e:
        print(f"❌ DRV001: {e}")
        return None


def DRV002(topic_code, folder_id=DRIVE_FOLDER_ID):
    """
    عرض ملفات موضوع معين من Google Drive
    يُرجع: قائمة بالملفات [{name, link, created_time}]
    """
    try:
        service = P001D()
        if not service:
            return []

        # البحث عن مجلد الموضوع
        query = (
            f"name='{topic_code}' and "
            f"'{folder_id}' in parents and "
            f"mimeType='application/vnd.google-apps.folder' and "
            f"trashed=false"
        )
        res = service.files().list(q=query, fields="files(id, name)").execute()
        folders = res.get("files", [])
        if not folders:
            return []

        sub_folder_id = folders[0]["id"]

        # جلب الملفات داخل المجلد
        query2 = f"'{sub_folder_id}' in parents and trashed=false"
        res2 = service.files().list(
            q=query2,
            fields="files(id, name, webViewLink, createdTime)",
            orderBy="createdTime desc"
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
    """
    حذف ملف من Google Drive
    يُرجع: True / False
    """
    try:
        service = P001D()
        if not service:
            return False
        service.files().delete(fileId=file_id).execute()
        print(f"✅ DRV003: تم حذف الملف — {file_id}")
        return True
    except Exception as e:
        print(f"❌ DRV003: {e}")
        return False


def DRV004(folder_name, parent_id=DRIVE_FOLDER_ID):
    """
    إنشاء مجلد فرعي في Drive إذا لم يكن موجوداً، أو إرجاع ID المجلد الموجود
    يُرجع: folder_id أو None
    """
    try:
        service = P001D()
        if not service:
            return None

        # البحث عن مجلد بنفس الاسم
        query = (
            f"name='{folder_name}' and "
            f"'{parent_id}' in parents and "
            f"mimeType='application/vnd.google-apps.folder' and "
            f"trashed=false"
        )
        res = service.files().list(q=query, fields="files(id, name)").execute()
        existing = res.get("files", [])
        if existing:
            print(f"✅ DRV004: مجلد موجود — {folder_name} ({existing[0]['id']})")
            return existing[0]["id"]

        # إنشاء مجلد جديد
        folder_metadata = {
            "name":     folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents":  [parent_id],
        }
        folder = service.files().create(body=folder_metadata, fields="id").execute()
        folder_id = folder.get("id")
        print(f"✅ DRV004: تم إنشاء مجلد — {folder_name} ({folder_id})")
        return folder_id

    except Exception as e:
        print(f"❌ DRV004: {e}")
        return None


def DRV005(file_path, file_name, folder_id=DRIVE_FOLDER_ID):
    """
    رفع ملف مباشرة إلى المجلد الرئيسي (بدون مجلد موضوع)
    مفيد للمرفقات العامة أو الشحنات
    يُرجع: drive_link أو None
    """
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
        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
        uploaded = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink"
        ).execute()

        file_id    = uploaded.get("id")
        drive_link = uploaded.get("webViewLink", f"https://drive.google.com/file/d/{file_id}/view")

        # منح صلاحية عرض للجميع
        service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"}
        ).execute()

        print(f"✅ DRV005: تم رفع الملف — {file_name} → {drive_link}")
        return drive_link

    except Exception as e:
        print(f"❌ DRV005: {e}")
        return None

# ─────────────────────────────────────────────
# Telegram Message Functions
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# Notification Functions
# ─────────────────────────────────────────────
async def N001(context, boss_chat_id, text):
    try:
        await context.bot.send_message(chat_id=boss_chat_id, text=f"🔔 *إشعار — أمين السر*\n\n{text}", parse_mode="Markdown")
        return True
    except Exception as e:
        print(f"❌ N001: {e}")
        return False

async def N002(context, client_chat_id, text):
    try:
        await context.bot.send_message(chat_id=client_chat_id, text=f"📩 *رسالة من مكتب المحاماة*\n\n{text}", parse_mode="Markdown")
        return True
    except Exception as e:
        print(f"❌ N002: {e}")
        return False

async def N003(context, assistant_chat_id, text):
    try:
        await context.bot.send_message(chat_id=assistant_chat_id, text=f"📋 *مهمة جديدة — أمين السر*\n\n{text}", parse_mode="Markdown")
        return True
    except Exception as e:
        print(f"❌ N003: {e}")
        return False

# ─────────────────────────────────────────────
# Events Helper Functions
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# Link Functions
# ─────────────────────────────────────────────
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
