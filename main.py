from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
from routines import *
from primitives import *
from datetime import datetime

TOKEN = "8716122412:AAHREvaHnoYsydnaPevVa5JDrT0wnxzz3Mk"

BOSS_CHAT_ID = 0  # يتغير لكل مكتب

ROUTE_MAP = {
    # إدارة العملاء
    "F-001": F001,
    "F-002": F002,
    "F-003": F003,
    # إدارة المساعدين
    "A-001": RA001,
    "A-002": RA002,
    # إدارة الموضوعات
    "T-001": RT001,
    "T-002": RT002,
    "T-003": RT003,
    "T-004": RT004,
    # إدارة الأحداث
    "E-001": RE001,
    "E-002": RE002,
    "E-003": RE003,
    # إدارة المستندات
    "D-001": RD001,
    "D-002": RD002,
    "D-003": RD003,
    "D-004": RD004,
    "D-005": RD005,
    "D-006": RD006,
    # إدارة الشحنات
    "S-001": RS001,
    "S-002": RS002,
    "S-003": RS003,
    # المالية
    "M-001": RM001,
    "M-002": RM002,
    # الإشعارات
    "N-001": RN001,
    "N-002": RN002,
    "N-003": RN003,
}

# ─────────────────────────────────────────────
# لوحات المفاتيح
# ─────────────────────────────────────────────
def main_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👤 العملاء",      callback_data="MENU-CLIENTS"),
            InlineKeyboardButton("📋 الموضوعات",    callback_data="MENU-TOPICS"),
        ],
        [
            InlineKeyboardButton("📅 الأحداث",      callback_data="MENU-EVENTS"),
            InlineKeyboardButton("📁 المستندات",    callback_data="MENU-DOCS"),
        ],
        [
            InlineKeyboardButton("📦 الشحنات",      callback_data="MENU-SHIPMENTS"),
            InlineKeyboardButton("💰 المالية",       callback_data="MENU-FINANCE"),
        ],
        [
            InlineKeyboardButton("👥 المساعدون",    callback_data="MENU-ASSISTANTS"),
            InlineKeyboardButton("🔔 الإشعارات",    callback_data="MENU-NOTIFY"),
        ],
    ])

def clients_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ إضافة عميل جديد",  callback_data="F-001")],
        [InlineKeyboardButton("🔍 عرض بيانات عميل",  callback_data="F-002")],
        [InlineKeyboardButton("✏️ تعديل بيانات عميل", callback_data="F-003")],
        [InlineKeyboardButton("🔙 رجوع",              callback_data="MENU-MAIN")],
    ])

def topics_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ إضافة موضوع جديد",   callback_data="T-001")],
        [InlineKeyboardButton("📋 عرض موضوعات عميل",   callback_data="T-002")],
        [InlineKeyboardButton("🔄 تغيير حالة موضوع",   callback_data="T-003")],
        [InlineKeyboardButton("🗄️ أرشفة موضوع",        callback_data="T-004")],
        [InlineKeyboardButton("🔙 رجوع",               callback_data="MENU-MAIN")],
    ])

def events_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 عرض الأحداث القادمة",  callback_data="E-003")],
        [InlineKeyboardButton("➕ إضافة حدث جديد",       callback_data="E-001")],
        [InlineKeyboardButton("📢 تسجيل نتيجة حدث",     callback_data="E-002")],
        [InlineKeyboardButton("🔙 رجوع",                 callback_data="MENU-MAIN")],
    ])

def docs_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 رفع مستند وارد",         callback_data="D-001")],
        [InlineKeyboardButton("📤 طلب مستندات من جهة",    callback_data="D-002")],
        [InlineKeyboardButton("✅ موافقة على مستند",       callback_data="D-003")],
        [InlineKeyboardButton("❌ رفض مستند",              callback_data="D-004")],
        [InlineKeyboardButton("📂 عرض مستندات موضوع",     callback_data="D-005")],
        [InlineKeyboardButton("🗄️ أرشفة مستندات",         callback_data="D-006")],
        [InlineKeyboardButton("🔙 رجوع",                  callback_data="MENU-MAIN")],
    ])

def shipments_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 إرسال مرفقات (صادر)",   callback_data="S-001")],
        [InlineKeyboardButton("📥 استلام شحنة واردة",     callback_data="S-002")],
        [InlineKeyboardButton("🔍 تتبع حالة شحنة",        callback_data="S-003")],
        [InlineKeyboardButton("🔙 رجوع",                  callback_data="MENU-MAIN")],
    ])

def finance_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 طلب عهدة مالية",   callback_data="M-001")],
        [InlineKeyboardButton("💳 تسوية عهدة مالية", callback_data="M-002")],
        [InlineKeyboardButton("🔙 رجوع",              callback_data="MENU-MAIN")],
    ])

def assistants_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ إضافة مساعد جديد",  callback_data="A-001")],
        [InlineKeyboardButton("👤 عرض بيانات مساعد",  callback_data="A-002")],
        [InlineKeyboardButton("🔙 رجوع",              callback_data="MENU-MAIN")],
    ])

def notify_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔔 إشعار للرئيس",   callback_data="N-001")],
        [InlineKeyboardButton("📩 إشعار للعميل",   callback_data="N-002")],
        [InlineKeyboardButton("📋 إشعار للمساعد",  callback_data="N-003")],
        [InlineKeyboardButton("🔙 رجوع",           callback_data="MENU-MAIN")],
    ])

# ─────────────────────────────────────────────
# /start
# ─────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بك في *أمين السر* 🏛️\n\nاختر من لوحة القيادة:",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

# ─────────────────────────────────────────────
# text_router — يستقبل ردود المستخدم
# ─────────────────────────────────────────────
async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    routine = context.user_data.get("routine")
    step    = context.user_data.get("step")
    if not routine or not step:
        return

    text       = update.message.text.strip()
    chat_id    = update.effective_chat.id
    data       = context.user_data.setdefault("data", {})
    back_btn   = [[{"text": "🔙 القائمة", "callback_data": "MENU-MAIN"}]]
    cancel_btn = [[{"text": "❌ إلغاء",   "callback_data": "MENU-MAIN"}]]

    # ═══════════════════════════════════════════
    # F001 — إضافة عميل جديد
    # أعمدة Clients: client_code | client_name | national_id | mobile | address | date_added
    # ═══════════════════════════════════════════
    if routine == "F001":
        if step == "name":
            if not V001(text):
                await T001(context, chat_id, "❌ الاسم قصير. أدخل الاسم كاملاً:")
                return
            data["name"] = text
            context.user_data["step"] = "national_id"
            await T002(context, chat_id, "🪪 أدخل *الرقم القومي* (14 رقم):", cancel_btn)

        elif step == "national_id":
            if not V002(text):
                await T001(context, chat_id, "❌ الرقم القومي يجب أن يكون 14 رقم:")
                return
            data["national_id"] = text
            context.user_data["step"] = "mobile"
            await T002(context, chat_id, "📱 أدخل *رقم الموبايل*:", cancel_btn)

        elif step == "mobile":
            if not V003(text):
                await T001(context, chat_id, "❌ رقم الموبايل غير صحيح:")
                return
            data["mobile"] = text
            context.user_data["step"] = "address"
            await T002(context, chat_id, "🏠 أدخل *العنوان*:", cancel_btn)

        elif step == "address":
            if not V001(text):
                await T001(context, chat_id, "❌ العنوان قصير:")
                return
            data["address"] = text
            code = G001("Cl", "Clients")
            ok = P003("Clients", [
                code,
                data["name"],
                data["national_id"],
                data["mobile"],
                data["address"],
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ])
            context.user_data.clear()
            if ok:
                await T002(context, chat_id,
                    f"✅ *تم إضافة العميل!*\n\n🔹 الكود: `{code}`\n👤 {data['name']}\n📱 {data['mobile']}",
                    back_btn)
            else:
                await T001(context, chat_id, "❌ حدث خطأ في الحفظ.")

    # ═══════════════════════════════════════════
    # F002 — عرض بيانات عميل
    # ═══════════════════════════════════════════
    elif routine == "F002":
        if step == "code":
            client = P002("Clients", text)
            context.user_data.clear()
            if not client:
                await T002(context, chat_id, "❌ كود العميل غير موجود.", back_btn)
                return
            msg = (
                f"👤 *بيانات العميل*\n\n"
                f"🔹 الكود: `{text}`\n"
                f"📛 الاسم: {client.get('client_name', '—')}\n"
                f"🪪 الرقم القومي: {client.get('national_id', '—')}\n"
                f"📱 الموبايل: {client.get('mobile', '—')}\n"
                f"🏠 العنوان: {client.get('address', '—')}\n"
                f"📅 تاريخ الإضافة: {client.get('date_added', '—')}"
            )
            await T002(context, chat_id, msg, back_btn)

    # ═══════════════════════════════════════════
    # F003 — تعديل بيانات عميل
    # ═══════════════════════════════════════════
    elif routine == "F003":
        if step == "code":
            client = P002("Clients", text)
            if not client:
                await T002(context, chat_id, "❌ كود العميل غير موجود.", back_btn)
                context.user_data.clear()
                return
            data["client_code"] = text
            context.user_data["step"] = "field"
            await T002(context, chat_id,
                f"✅ العميل: *{client.get('client_name', '')}*\n\nأي حقل تريد تعديله؟\n"
                f"1️⃣ الاسم\n2️⃣ رقم الموبايل\n3️⃣ العنوان",
                cancel_btn)

        elif step == "field":
            if text not in ("1", "2", "3"):
                await T001(context, chat_id, "❌ أدخل 1 أو 2 أو 3:")
                return
            data["field"] = text
            field_names = {"1": "الاسم", "2": "رقم الموبايل", "3": "العنوان"}
            context.user_data["step"] = "new_value"
            await T002(context, chat_id, f"✏️ أدخل *{field_names[text]}* الجديد:", cancel_btn)

        elif step == "new_value":
            field = data.get("field")
            # عمود A=1:client_code | B=2:client_name | C=3:national_id | D=4:mobile | E=5:address | F=6:date_added
            col_map = {"1": (2, "client_name"), "2": (4, "mobile"), "3": (5, "address")}
            col_num, _ = col_map[field]
            if field == "2" and not V003(text):
                await T001(context, chat_id, "❌ رقم الموبايل غير صحيح:")
                return
            if field in ("1", "3") and not V001(text):
                await T001(context, chat_id, "❌ القيمة قصيرة جداً:")
                return
            records = P005("Clients")
            row_num = None
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(data["client_code"]):
                    row_num = i
                    break
            if not row_num:
                await T001(context, chat_id, "❌ لم يُعثر على العميل.")
                context.user_data.clear()
                return
            ok = P004("Clients", row_num, col_num, text)
            context.user_data.clear()
            if ok:
                await T002(context, chat_id,
                    f"✅ *تم التعديل بنجاح!*\n\n🔹 الكود: `{data['client_code']}`\n📝 القيمة الجديدة: {text}",
                    back_btn)
            else:
                await T001(context, chat_id, "❌ حدث خطأ في التعديل.")

    # ═══════════════════════════════════════════
    # RA001 — إضافة مساعد جديد
    # أعمدة Assistants: assistant_code | assistant_name | mobile | date_added
    # ═══════════════════════════════════════════
    elif routine == "RA001":
        if step == "name":
            if not V001(text):
                await T001(context, chat_id, "❌ الاسم قصير:")
                return
            data["name"] = text
            context.user_data["step"] = "mobile"
            await T002(context, chat_id, "📱 أدخل *رقم الموبايل*:", cancel_btn)

        elif step == "mobile":
            if not V003(text):
                await T001(context, chat_id, "❌ رقم غير صحيح:")
                return
            data["mobile"] = text
            code = G001("As", "Assistants")
            ok = P003("Assistants", [
                code,
                data["name"],
                data["mobile"],
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ])
            context.user_data.clear()
            if ok:
                await T002(context, chat_id,
                    f"✅ *تم إضافة المساعد!*\n\n🔹 الكود: `{code}`\n👤 {data['name']}\n📱 {data['mobile']}",
                    back_btn)
            else:
                await T001(context, chat_id, "❌ حدث خطأ.")

    # ═══════════════════════════════════════════
    # RA002 — عرض بيانات مساعد
    # ═══════════════════════════════════════════
    elif routine == "RA002":
        if step == "code":
            asst = P002("Assistants", text)
            context.user_data.clear()
            if not asst:
                await T002(context, chat_id, "❌ كود المساعد غير موجود.", back_btn)
                return
            msg = (
                f"👤 *بيانات المساعد*\n\n"
                f"🔹 الكود: `{text}`\n"
                f"📛 الاسم: {asst.get('assistant_name', '—')}\n"
                f"📱 الموبايل: {asst.get('mobile', '—')}\n"
                f"📅 تاريخ الإضافة: {asst.get('date_added', '—')}"
            )
            await T002(context, chat_id, msg, back_btn)

    # ═══════════════════════════════════════════
    # RT001 — إضافة موضوع جديد
    # أعمدة Topics: topic_code | client_code | client_name | service_code | service_name | assistant_code | assistant_name | date_opened | status | notes
    # ═══════════════════════════════════════════
    elif routine == "RT001":
        if step == "client_code":
            client = P002("Clients", text)
            if not client:
                await T001(context, chat_id, "❌ كود العميل غير موجود:")
                return
            data["client_code"] = text
            data["client_name"] = client.get("client_name", "")
            context.user_data["step"] = "title"
            await T002(context, chat_id,
                f"✅ العميل: *{data['client_name']}*\n\nأدخل *عنوان الموضوع*:",
                cancel_btn)

        elif step == "title":
            if not V001(text):
                await T001(context, chat_id, "❌ العنوان قصير:")
                return
            data["title"] = text
            context.user_data["step"] = "topic_type"
            await T002(context, chat_id, "📋 أدخل *نوع الموضوع* (مثال: طلاق / ميراث / عقار):", cancel_btn)

        elif step == "topic_type":
            data["topic_type"] = text
            code = G001("Tp", "Topics")
            ok = P003("Topics", [
                code,                                          # A: topic_code
                data["client_code"],                           # B: client_code
                data["client_name"],                           # C: client_name
                "",                                            # D: service_code
                data["title"],                                 # E: service_name (عنوان الموضوع)
                "",                                            # F: assistant_code
                "",                                            # G: assistant_name
                datetime.now().strftime("%Y-%m-%d %H:%M"),    # H: date_opened
                "جديد",                                        # I: status
                data["topic_type"]                             # J: notes (نوع الموضوع)
            ])
            context.user_data.clear()
            if ok:
                await T002(context, chat_id,
                    f"✅ *تم إضافة الموضوع!*\n\n🔹 الكود: `{code}`\n📋 {data['title']}\n📌 النوع: {data['topic_type']}",
                    back_btn)
            else:
                await T001(context, chat_id, "❌ حدث خطأ.")

    # ═══════════════════════════════════════════
    # RT002 — عرض موضوعات عميل
    # ═══════════════════════════════════════════
    elif routine == "RT002":
        if step == "client_code":
            client = P002("Clients", text)
            context.user_data.clear()
            if not client:
                await T002(context, chat_id, "❌ كود العميل غير موجود.", back_btn)
                return
            topics = P006("Topics", "client_code", text)
            if not topics:
                await T002(context, chat_id, f"📋 لا توجد موضوعات للعميل `{text}`.", back_btn)
                return
            msg = f"📋 *موضوعات العميل: {client.get('client_name', '')}*\n\n"
            for t in topics:
                code   = list(t.values())[0]
                title  = t.get("service_name", "—")   # E: عنوان الموضوع
                ntype  = t.get("notes", "—")           # J: نوع الموضوع
                status = t.get("status", "—")          # I: الحالة
                date   = t.get("date_opened", "—")    # H: تاريخ الفتح
                msg += (
                    f"🔹 `{code}`\n"
                    f"   📋 العنوان: {title}\n"
                    f"   📌 النوع: {ntype}\n"
                    f"   🔄 الحالة: {status}\n"
                    f"   📅 التاريخ: {date}\n\n"
                )
            await T002(context, chat_id, msg, back_btn)

    # ═══════════════════════════════════════════
    # RT003 — تغيير حالة موضوع
    # ═══════════════════════════════════════════
    elif routine == "RT003":
        if step == "topic_code":
            topic = P002("Topics", text)
            if not topic:
                await T002(context, chat_id, "❌ كود الموضوع غير موجود.", back_btn)
                context.user_data.clear()
                return
            data["topic_code"]  = text
            data["topic_title"] = topic.get("service_name", "—")
            context.user_data["step"] = "new_status"
            await T002(context, chat_id,
                f"📋 الموضوع: *{data['topic_title']}*\n\nأدخل الحالة الجديدة:\n• جديد\n• قيد النظر\n• منتهي\n• موقوف",
                cancel_btn)

        elif step == "new_status":
            if not V001(text):
                await T001(context, chat_id, "❌ الحالة قصيرة:")
                return
            records = P005("Topics")
            row_num = None
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(data["topic_code"]):
                    row_num = i
                    break
            if not row_num:
                await T001(context, chat_id, "❌ لم يُعثر على الموضوع.")
                context.user_data.clear()
                return
            ok = P004("Topics", row_num, 9, text)  # I: status = عمود 9
            context.user_data.clear()
            if ok:
                await T002(context, chat_id,
                    f"✅ *تم تغيير الحالة!*\n\n📋 {data['topic_title']}\n🔄 الحالة الجديدة: {text}",
                    back_btn)
            else:
                await T001(context, chat_id, "❌ حدث خطأ.")

    # ═══════════════════════════════════════════
    # RT004 — أرشفة موضوع
    # ═══════════════════════════════════════════
    elif routine == "RT004":
        if step == "topic_code":
            topic = P002("Topics", text)
            if not topic:
                await T002(context, chat_id, "❌ كود الموضوع غير موجود.", back_btn)
                context.user_data.clear()
                return
            data["topic_code"]  = text
            data["topic_title"] = topic.get("service_name", "—")
            context.user_data["step"] = "confirm"
            await T002(context, chat_id,
                f"🗄️ هل تريد أرشفة الموضوع: *{data['topic_title']}*؟\n\nاكتب *نعم* للتأكيد أو *لا* للإلغاء:",
                cancel_btn)

        elif step == "confirm":
            if text.strip() != "نعم":
                context.user_data.clear()
                await T002(context, chat_id, "🚫 تم الإلغاء.", back_btn)
                return
            records = P005("Topics")
            row_num = None
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(data["topic_code"]):
                    row_num = i
                    break
            if not row_num:
                await T001(context, chat_id, "❌ لم يُعثر على الموضوع.")
                context.user_data.clear()
                return
            ok = P004("Topics", row_num, 9, "مؤرشف")  # I: status = عمود 9
            context.user_data.clear()
            if ok:
                await T002(context, chat_id,
                    f"✅ *تم أرشفة الموضوع!*\n\n🗄️ {data['topic_title']}",
                    back_btn)
            else:
                await T001(context, chat_id, "❌ حدث خطأ.")

    # ═══════════════════════════════════════════
    # RE001 — إضافة حدث جديد
    # أعمدة Events: event_code | event_date | topic_code | client_name | event_type | event_time | location_court | result | status
    # ═══════════════════════════════════════════
    elif routine == "RE001":
        if step == "title":
            if not V001(text):
                await T001(context, chat_id, "❌ العنوان قصير:")
                return
            data["title"] = text
            context.user_data["step"] = "topic_code"
            await T002(context, chat_id, "📋 أدخل *كود الموضوع* (مثال: Tp-001):", cancel_btn)

        elif step == "topic_code":
            data["topic_code"] = text
            context.user_data["step"] = "client_name"
            await T002(context, chat_id, "👤 أدخل *اسم العميل*:", cancel_btn)

        elif step == "client_name":
            data["client_name"] = text
            context.user_data["step"] = "event_type"
            await T002(context, chat_id, "⚖️ أدخل *نوع الحدث* (مثال: جلسة / موعد / تسليم):", cancel_btn)

        elif step == "event_type":
            data["event_type"] = text
            context.user_data["step"] = "event_date"
            await T002(context, chat_id, "📅 أدخل *تاريخ الحدث* (DD/MM/YYYY):", cancel_btn)

        elif step == "event_date":
            if not V004(text):
                await T001(context, chat_id, "❌ التاريخ غير صحيح. استخدم DD/MM/YYYY:")
                return
            data["event_date"] = text
            context.user_data["step"] = "event_time"
            await T002(context, chat_id, "⏰ أدخل *وقت الحدث* (مثال: 10:00 ص):", cancel_btn)

        elif step == "event_time":
            data["event_time"] = text
            context.user_data["step"] = "location"
            await T002(context, chat_id, "📍 أدخل *مكان الحدث* (المحكمة/الجهة):", cancel_btn)

        elif step == "location":
            data["location"] = text
            code = G001("Ev", "Events")
            ok = P003("Events", [
                code,
                data["event_date"],
                data["topic_code"],
                data["client_name"],
                data["event_type"],
                data["event_time"],
                data["location"],   # location_court
                "",                 # result
                "قادم"              # status
            ])
            context.user_data.clear()
            if ok:
                await T002(context, chat_id,
                    f"✅ *تم إضافة الحدث!*\n\n🔹 الكود: `{code}`\n📅 {data['event_date']} — {data['event_type']}\n📍 {data['location']}",
                    back_btn)
            else:
                await T001(context, chat_id, "❌ حدث خطأ.")

    # ═══════════════════════════════════════════
    # RE002 — تسجيل نتيجة حدث
    # أعمدة Events: event_code(1) | event_date(2) | topic_code(3) | client_name(4) | event_type(5) | event_time(6) | location_court(7) | result(8) | status(9)
    # ═══════════════════════════════════════════
    elif routine == "RE002":
        if step == "event_code":
            event = P002("Events", text)
            if not event:
                await T001(context, chat_id, "❌ كود الحدث غير موجود:")
                return
            data["event_code"] = text
            data["event_type"] = event.get("event_type", "—")
            data["event_date"] = event.get("event_date", "—")
            context.user_data["step"] = "result"
            await T002(context, chat_id,
                f"📅 الحدث: *{data['event_type']}* — {data['event_date']}\n\n📝 أدخل *نتيجة الحدث*:",
                cancel_btn)

        elif step == "result":
            if not V001(text):
                await T001(context, chat_id, "❌ النتيجة قصيرة:")
                return
            records = P005("Events")
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(data["event_code"]):
                    P004("Events", i, 8, text)      # result = عمود 8
                    P004("Events", i, 9, "منتهي")   # status = عمود 9
                    break
            context.user_data.clear()
            await T002(context, chat_id,
                f"✅ *تم تسجيل النتيجة!*\n\n📝 {text}",
                back_btn)

    # ═══════════════════════════════════════════
    # RD001 — رفع مستند وارد
    # أعمدة Documents: doc_code | topic_code | doc_name | doc_source | direction | doc_status | date_added | notes
    # ═══════════════════════════════════════════
    elif routine == "RD001":
        if step == "topic_code":
            topic = P002("Topics", text)
            if not topic:
                await T002(context, chat_id, "❌ كود الموضوع غير موجود.", back_btn)
                context.user_data.clear()
                return
            data["topic_code"]  = text
            data["topic_title"] = topic.get("service_name", "—")
            context.user_data["step"] = "doc_name"
            await T002(context, chat_id,
                f"✅ الموضوع: *{data['topic_title']}*\n\nأدخل *اسم المستند*:",
                cancel_btn)

        elif step == "doc_name":
            if not V001(text):
                await T001(context, chat_id, "❌ الاسم قصير:")
                return
            data["doc_name"] = text
            context.user_data["step"] = "doc_source"
            await T002(context, chat_id, "🏢 أدخل *مصدر المستند* (الجهة المُرسِلة):", cancel_btn)

        elif step == "doc_source":
            if not V001(text):
                await T001(context, chat_id, "❌ المصدر قصير:")
                return
            data["doc_source"] = text
            code = G001("Doc", "Documents")
            ok = P003("Documents", [
                code,
                data["topic_code"],
                data["doc_name"],
                data["doc_source"],
                "وارد",
                "قيد المراجعة",
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                ""
            ])
            context.user_data.clear()
            if ok:
                await T002(context, chat_id,
                    f"✅ *تم تسجيل المستند الوارد!*\n\n🔹 الكود: `{code}`\n📄 {data['doc_name']}\n🏢 من: {data['doc_source']}",
                    back_btn)
            else:
                await T001(context, chat_id, "❌ حدث خطأ.")

    # ═══════════════════════════════════════════
    # RD002 — طلب مستندات من جهة خارجية
    # ═══════════════════════════════════════════
    elif routine == "RD002":
        if step == "entity":
            if not V001(text):
                await T001(context, chat_id, "❌ اسم الجهة قصير:")
                return
            data["entity"] = text
            context.user_data["step"] = "description"
            await T002(context, chat_id, "📄 أدخل *وصف المستندات المطلوبة*:", cancel_btn)

        elif step == "description":
            if not V001(text):
                await T001(context, chat_id, "❌ الوصف قصير:")
                return
            data["description"] = text
            code = G001("Doc", "Documents")
            ok = P003("Documents", [
                code,
                "—",
                data["description"],
                data["entity"],
                "طلب",
                "معلق",
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                ""
            ])
            context.user_data.clear()
            if ok:
                await T002(context, chat_id,
                    f"✅ *تم تسجيل الطلب!*\n\n🔹 الكود: `{code}`\n📤 من: {data['entity']}\n📄 {data['description']}",
                    back_btn)
            else:
                await T001(context, chat_id, "❌ حدث خطأ.")

    # ═══════════════════════════════════════════
    # RD003 — الموافقة على مستند
    # أعمدة Documents: doc_code(1) | topic_code(2) | doc_name(3) | doc_source(4) | direction(5) | doc_status(6) | date_added(7) | notes(8)
    # ═══════════════════════════════════════════
    elif routine == "RD003":
        if step == "doc_code":
            doc = P002("Documents", text)
            if not doc:
                await T002(context, chat_id, "❌ كود المستند غير موجود.", back_btn)
                context.user_data.clear()
                return
            doc_name = doc.get("doc_name", "—")
            records = P005("Documents")
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(text):
                    P004("Documents", i, 6, "موافق عليه")  # doc_status = عمود 6
                    break
            context.user_data.clear()
            await T002(context, chat_id,
                f"✅ *تمت الموافقة على المستند!*\n\n📄 {doc_name}\n🔹 الكود: `{text}`",
                back_btn)

    # ═══════════════════════════════════════════
    # RD004 — رفض مستند
    # ═══════════════════════════════════════════
    elif routine == "RD004":
        if step == "doc_code":
            doc = P002("Documents", text)
            if not doc:
                await T002(context, chat_id, "❌ كود المستند غير موجود.", back_btn)
                context.user_data.clear()
                return
            data["doc_code"] = text
            data["doc_name"] = doc.get("doc_name", "—")
            context.user_data["step"] = "reason"
            await T002(context, chat_id,
                f"📄 المستند: *{data['doc_name']}*\n\n❌ أدخل *سبب الرفض*:",
                cancel_btn)

        elif step == "reason":
            if not V001(text):
                await T001(context, chat_id, "❌ السبب قصير:")
                return
            records = P005("Documents")
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(data["doc_code"]):
                    P004("Documents", i, 6, "مرفوض")  # doc_status = عمود 6
                    P004("Documents", i, 8, text)      # notes = عمود 8
                    break
            context.user_data.clear()
            await T002(context, chat_id,
                f"✅ *تم رفض المستند!*\n\n📄 {data['doc_name']}\n❌ السبب: {text}",
                back_btn)

    # ═══════════════════════════════════════════
    # RD005 — عرض مستندات موضوع
    # ═══════════════════════════════════════════
    elif routine == "RD005":
        if step == "topic_code":
            topic = P002("Topics", text)
            context.user_data.clear()
            if not topic:
                await T002(context, chat_id, "❌ كود الموضوع غير موجود.", back_btn)
                return
            docs = P006("Documents", "topic_code", text)
            if not docs:
                await T002(context, chat_id, f"📂 لا توجد مستندات للموضوع `{text}`.", back_btn)
                return
            title = topic.get("service_name", text)
            msg = f"📂 *مستندات الموضوع: {title}*\n\n"
            for d in docs:
                code   = list(d.values())[0]
                name   = d.get("doc_name", "—")
                status = d.get("doc_status", "—")
                msg += f"🔹 `{code}` — {name} — [{status}]\n"
            await T002(context, chat_id, msg, back_btn)

    # ═══════════════════════════════════════════
    # RD006 — أرشفة مستندات موضوع
    # ═══════════════════════════════════════════
    elif routine == "RD006":
        if step == "topic_code":
            topic = P002("Topics", text)
            if not topic:
                await T002(context, chat_id, "❌ كود الموضوع غير موجود.", back_btn)
                context.user_data.clear()
                return
            data["topic_code"]  = text
            data["topic_title"] = topic.get("service_name", "—")
            context.user_data["step"] = "confirm"
            await T002(context, chat_id,
                f"🗄️ هل تريد أرشفة *كل مستندات* الموضوع: *{data['topic_title']}*؟\n\nاكتب *نعم* للتأكيد:",
                cancel_btn)

        elif step == "confirm":
            if text.strip() != "نعم":
                context.user_data.clear()
                await T002(context, chat_id, "🚫 تم الإلغاء.", back_btn)
                return
            records = P005("Documents")
            count = 0
            for i, r in enumerate(records, start=2):
                if str(r.get("topic_code", "")) == str(data["topic_code"]):
                    P004("Documents", i, 6, "مؤرشف")  # doc_status = عمود 6
                    count += 1
            context.user_data.clear()
            await T002(context, chat_id,
                f"✅ *تم أرشفة {count} مستند!*\n\n🗄️ الموضوع: {data['topic_title']}",
                back_btn)

    # ═══════════════════════════════════════════
    # RS001 — إرسال مرفقات (شحنة صادرة)
    # أعمدة Shipments: shipment_code(1) | topic_code(2) | sender(3) | receiver(4) | send_date(5) | file_name(6) | file_type(7) | pickup_location(8) | receive_status(9) | receive_date(10) | notes(11)
    # ═══════════════════════════════════════════
    elif routine == "RS001":
        if step == "topic_code":
            topic = P002("Topics", text)
            if not topic:
                await T001(context, chat_id, "❌ كود الموضوع غير موجود:")
                return
            data["topic_code"]  = text
            data["topic_title"] = topic.get("service_name", "—")
            context.user_data["step"] = "sender"
            await T002(context, chat_id,
                f"✅ الموضوع: *{data['topic_title']}*\n\n📤 أدخل *اسم المُرسِل*:",
                cancel_btn)

        elif step == "sender":
            if not V001(text):
                await T001(context, chat_id, "❌ الاسم قصير:")
                return
            data["sender"] = text
            context.user_data["step"] = "receiver"
            await T002(context, chat_id, "📥 أدخل *اسم المُستلِم*:", cancel_btn)

        elif step == "receiver":
            if not V001(text):
                await T001(context, chat_id, "❌ الاسم قصير:")
                return
            data["receiver"] = text
            context.user_data["step"] = "file_name"
            await T002(context, chat_id, "📄 أدخل *اسم الملف أو المحتوى*:", cancel_btn)

        elif step == "file_name":
            if not V001(text):
                await T001(context, chat_id, "❌ الاسم قصير:")
                return
            data["file_name"] = text
            context.user_data["step"] = "pickup_location"
            await T002(context, chat_id, "📍 أدخل *مكان التسليم*:", cancel_btn)

        elif step == "pickup_location":
            data["pickup_location"] = text
            code = G001("Sh", "Shipments")
            ok = P003("Shipments", [
                code,
                data["topic_code"],
                data["sender"],
                data["receiver"],
                datetime.now().strftime("%Y-%m-%d %H:%M"),  # send_date
                data["file_name"],
                "",                                          # file_type
                data["pickup_location"],
                "في الطريق",                                 # receive_status
                "",                                          # receive_date
                ""                                           # notes
            ])
            context.user_data.clear()
            if ok:
                await T002(context, chat_id,
                    f"✅ *تم تسجيل الشحنة الصادرة!*\n\n🔹 الكود: `{code}`\n📤 من: {data['sender']}\n📥 إلى: {data['receiver']}\n📄 {data['file_name']}",
                    back_btn)
            else:
                await T001(context, chat_id, "❌ حدث خطأ.")

    # ═══════════════════════════════════════════
    # RS002 — استلام شحنة واردة
    # ═══════════════════════════════════════════
    elif routine == "RS002":
        if step == "shipment_code":
            shipment = P002("Shipments", text)
            if not shipment:
                await T002(context, chat_id, "❌ كود الشحنة غير موجود.", back_btn)
                context.user_data.clear()
                return
            data["shipment_code"] = text
            data["file_name"]     = shipment.get("file_name", "—")
            data["sender"]        = shipment.get("sender", "—")
            context.user_data["step"] = "confirm"
            await T002(context, chat_id,
                f"📥 تأكيد استلام الشحنة:\n\n🔹 الكود: `{text}`\n📄 المحتوى: {data['file_name']}\n📤 المُرسِل: {data['sender']}\n\nاكتب *نعم* للتأكيد:",
                cancel_btn)

        elif step == "confirm":
            if text.strip() != "نعم":
                context.user_data.clear()
                await T002(context, chat_id, "🚫 تم الإلغاء.", back_btn)
                return
            records = P005("Shipments")
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(data["shipment_code"]):
                    P004("Shipments", i, 9,  "مستلم")                              # receive_status = عمود 9
                    P004("Shipments", i, 10, datetime.now().strftime("%Y-%m-%d %H:%M"))  # receive_date = عمود 10
                    break
            context.user_data.clear()
            await T002(context, chat_id,
                f"✅ *تم تسجيل الاستلام!*\n\n📥 الشحنة: `{data['shipment_code']}`\n📄 {data['file_name']}",
                back_btn)

    # ═══════════════════════════════════════════
    # RS003 — تتبع حالة شحنة
    # أعمدة Shipments: shipment_code | topic_code | sender | receiver | send_date | file_name | file_type | pickup_location | receive_status | receive_date | notes
    # ═══════════════════════════════════════════
    elif routine == "RS003":
        if step == "shipment_code":
            shipment = P002("Shipments", text)
            context.user_data.clear()
            if not shipment:
                await T002(context, chat_id, "❌ كود الشحنة غير موجود.", back_btn)
                return
            code            = list(shipment.values())[0]
            topic_code      = shipment.get("topic_code", "—")
            sender          = shipment.get("sender", "—")
            receiver        = shipment.get("receiver", "—")
            send_date       = shipment.get("send_date", "—")
            file_name       = shipment.get("file_name", "—")
            pickup_location = shipment.get("pickup_location", "—")
            receive_status  = shipment.get("receive_status", "—")
            receive_date    = shipment.get("receive_date", "—")
            notes           = shipment.get("notes", "—")
            msg = (
                f"📦 *بيانات الشحنة*\n\n"
                f"🔹 الكود: `{code}`\n"
                f"📋 الموضوع: {topic_code}\n"
                f"📤 المُرسِل: {sender}\n"
                f"📥 المُستلِم: {receiver}\n"
                f"📅 تاريخ الإرسال: {send_date}\n"
                f"📄 المحتوى: {file_name}\n"
                f"📍 مكان التسليم: {pickup_location}\n"
                f"🔄 حالة الاستلام: {receive_status}\n"
                f"📅 تاريخ الاستلام: {receive_date}\n"
                f"📝 ملاحظات: {notes}"
            )
            await T002(context, chat_id, msg, back_btn)

    # ═══════════════════════════════════════════
    # RM001 — طلب عهدة مالية
    # أعمدة Custody: custody_code(1) | responsible_code(2) | amount(3) | payment_due(4) | payment_status(5) | actual_payment_date(6) | notes(7)
    # ═══════════════════════════════════════════
    elif routine == "RM001":
        if step == "amount":
            if not V005(text):
                await T001(context, chat_id, "❌ المبلغ غير صحيح:")
                return
            data["amount"] = text
            context.user_data["step"] = "reason"
            await T002(context, chat_id, "📝 أدخل *سبب العهدة*:", cancel_btn)

        elif step == "reason":
            if not V001(text):
                await T001(context, chat_id, "❌ السبب قصير:")
                return
            data["reason"] = text
            code = G001("Fn", "Custody")
            ok = P003("Custody", [
                code,           # A: custody_code
                "",             # B: responsible_code
                data["amount"], # C: amount
                data["reason"], # D: payment_due (السبب)
                "طلب",          # E: payment_status
                "",             # F: actual_payment_date
                ""              # G: notes
            ])
            context.user_data.clear()
            if ok:
                await T002(context, chat_id,
                    f"✅ *تم طلب العهدة!*\n\n🔹 الكود: `{code}`\n💰 {data['amount']} جنيه\n📝 {data['reason']}",
                    back_btn)
            else:
                await T001(context, chat_id, "❌ حدث خطأ.")

    # ═══════════════════════════════════════════
    # RM002 — تسوية عهدة مالية
    # أعمدة Custody: custody_code(1) | responsible_code(2) | amount(3) | payment_due(4) | payment_status(5) | actual_payment_date(6) | notes(7)
    # ═══════════════════════════════════════════
    elif routine == "RM002":
        if step == "fund_code":
            fund = P002("Custody", text)
            if not fund:
                await T002(context, chat_id, "❌ كود العهدة غير موجود.", back_btn)
                context.user_data.clear()
                return
            data["fund_code"] = text
            data["amount"]    = fund.get("amount", "—")
            data["reason"]    = fund.get("payment_due", "—")
            context.user_data["step"] = "spent"
            await T002(context, chat_id,
                f"💰 *بيانات العهدة*\n\n🔹 الكود: `{text}`\n💵 المبلغ الكلي: {data['amount']} جنيه\n📝 السبب: {data['reason']}\n\n💳 أدخل *المبلغ المصروف فعلياً*:",
                cancel_btn)

        elif step == "spent":
            if not V005(text):
                await T001(context, chat_id, "❌ المبلغ غير صحيح:")
                return
            data["spent"] = text
            context.user_data["step"] = "notes"
            await T002(context, chat_id, "📝 أدخل *ملاحظات التسوية* (أو اكتب — للتخطي):", cancel_btn)

        elif step == "notes":
            data["notes"] = text
            records = P005("Custody")
            row_num = None
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(data["fund_code"]):
                    row_num = i
                    break
            if not row_num:
                await T001(context, chat_id, "❌ لم يُعثر على العهدة.")
                context.user_data.clear()
                return
            P004("Custody", row_num, 5, "مسوّاة")                              # E: payment_status = عمود 5
            P004("Custody", row_num, 6, datetime.now().strftime("%Y-%m-%d %H:%M"))  # F: actual_payment_date = عمود 6
            P004("Custody", row_num, 7, data["notes"])                          # G: notes = عمود 7
            context.user_data.clear()
            await T002(context, chat_id,
                f"✅ *تمت التسوية!*\n\n🔹 الكود: `{data['fund_code']}`\n💰 المبلغ الكلي: {data['amount']} جنيه\n💳 المصروف: {data['spent']} جنيه\n📝 الملاحظات: {data['notes']}",
                back_btn)

    # ═══════════════════════════════════════════
    # RN001 — إشعار للرئيس
    # ═══════════════════════════════════════════
    elif routine == "RN001":
        if step == "text":
            if not V001(text):
                await T001(context, chat_id, "❌ النص قصير:")
                return
            if BOSS_CHAT_ID and BOSS_CHAT_ID != 0:
                await N001(context, BOSS_CHAT_ID, text)
                await T002(context, chat_id,
                    f"✅ *تم إرسال الإشعار للرئيس!*\n\n🔔 {text}",
                    back_btn)
            else:
                await T002(context, chat_id,
                    f"⚠️ *تم تسجيل الإشعار:*\n\n🔔 {text}\n\nلم يُرسَل — BOSS CHAT ID غير مضبوط",
                    back_btn)
            context.user_data.clear()

    # ═══════════════════════════════════════════
    # RN002 — إشعار للعميل
    # أعمدة Notifications: notif_code(1) | target_type(2) | target_code(3) | target_name(4) | message(5) | date_sent(6)
    # ═══════════════════════════════════════════
    elif routine == "RN002":
        if step == "client_code":
            client = P002("Clients", text)
            if not client:
                await T002(context, chat_id, "❌ كود العميل غير موجود.", back_btn)
                context.user_data.clear()
                return
            data["client_code"] = text
            data["client_name"] = client.get("client_name", "—")
            context.user_data["step"] = "message"
            await T002(context, chat_id,
                f"👤 العميل: *{data['client_name']}*\n\n📩 أدخل *نص الرسالة*:",
                cancel_btn)

        elif step == "message":
            if not V001(text):
                await T001(context, chat_id, "❌ الرسالة قصيرة:")
                return
            code = G001("Nt", "Notifications")
            ok = P003("Notifications", [
                code,
                "عميل",
                data["client_code"],
                data["client_name"],
                text,
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ])
            context.user_data.clear()
            if ok:
                await T002(context, chat_id,
                    f"✅ *تم تسجيل الإشعار للعميل!*\n\n🔹 الكود: `{code}`\n👤 {data['client_name']}\n📩 {text}",
                    back_btn)
            else:
                await T001(context, chat_id, "❌ حدث خطأ في الحفظ.")

    # ═══════════════════════════════════════════
    # RN003 — إشعار للمساعد
    # ═══════════════════════════════════════════
    elif routine == "RN003":
        if step == "assistant_code":
            asst = P002("Assistants", text)
            if not asst:
                await T002(context, chat_id, "❌ كود المساعد غير موجود.", back_btn)
                context.user_data.clear()
                return
            data["assistant_code"] = text
            data["assistant_name"] = asst.get("assistant_name", "—")
            context.user_data["step"] = "message"
            await T002(context, chat_id,
                f"👤 المساعد: *{data['assistant_name']}*\n\n📋 أدخل *نص المهمة أو الإشعار*:",
                cancel_btn)

        elif step == "message":
            if not V001(text):
                await T001(context, chat_id, "❌ الرسالة قصيرة:")
                return
            code = G001("Nt", "Notifications")
            ok = P003("Notifications", [
                code,
                "مساعد",
                data["assistant_code"],
                data["assistant_name"],
                text,
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ])
            context.user_data.clear()
            if ok:
                await T002(context, chat_id,
                    f"✅ *تم تسجيل الإشعار للمساعد!*\n\n🔹 الكود: `{code}`\n👤 {data['assistant_name']}\n📋 {text}",
                    back_btn)
            else:
                await T001(context, chat_id, "❌ حدث خطأ في الحفظ.")


# ─────────────────────────────────────────────
# menu_router — يستقبل ضغطات الأزرار
# ─────────────────────────────────────────────
async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cb = query.data

    menus = {
        "MENU-MAIN":       ("لوحة القيادة — *أمين السر* 🏛️\n\nاختر القسم:", main_keyboard()),
        "MENU-CLIENTS":    ("👤 *إدارة العملاء*\nاختر العملية:", clients_keyboard()),
        "MENU-TOPICS":     ("📋 *إدارة الموضوعات*\nاختر العملية:", topics_keyboard()),
        "MENU-EVENTS":     ("📅 *إدارة الأحداث*\nاختر العملية:", events_keyboard()),
        "MENU-DOCS":       ("📁 *إدارة المستندات*\nاختر العملية:", docs_keyboard()),
        "MENU-SHIPMENTS":  ("📦 *إدارة الشحنات*\nاختر العملية:", shipments_keyboard()),
        "MENU-FINANCE":    ("💰 *المالية*\nاختر العملية:", finance_keyboard()),
        "MENU-ASSISTANTS": ("👥 *إدارة المساعدين*\nاختر العملية:", assistants_keyboard()),
        "MENU-NOTIFY":     ("🔔 *الإشعارات*\nاختر نوع الإشعار:", notify_keyboard()),
    }

    if cb in menus:
        txt, kb = menus[cb]
        await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=kb)
    elif cb in ROUTE_MAP:
        await ROUTE_MAP[cb](update, context)
    else:
        await query.edit_message_text(
            f"⏳ الكود *{cb}* قيد التطوير.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="MENU-MAIN")]])
        )


# ─────────────────────────────────────────────
# تشغيل البوت
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
    app.run_polling(drop_pending_updates=True)
