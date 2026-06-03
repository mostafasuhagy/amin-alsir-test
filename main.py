from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
from routines import *
from primitives import *
from datetime import datetime
import time

TOKEN = "8716122412:AAHREvaHnoYsydnaPevVa5JDrT0wnxzz3Mk"
BOSS_CHAT_ID = 8653723225

ROUTE_MAP = {
    "F-001": F001,   # إضافة عميل
    "F-002": F002,   # عرض عميل
    "F-003": F003,   # تعديل عميل
    "F-004": RT001,  # إضافة موضوع
    "F-005": RE001,  # إضافة حدث
    "F-006": RE002,  # نتيجة حدث
    "F-007": RS001,  # إرسال مرفقات
    "F-008": RD002,  # طلب مستندات
    "F-009": RM001,  # طلب عهدة
    "F-010": RE003,  # عرض أحداث
    "A-001": RA001,  # إضافة مساعد
    "A-002": RA002,  # عرض مساعد
    "T-002": RT002,  # عرض موضوعات عميل
    "T-003": RT003,  # تغيير حالة موضوع
    "T-004": RT004,  # أرشفة موضوع
    "S-002": RS002,  # استلام شحنة
    "S-003": RS003,  # تتبع شحنة
    "M-002": RM002,  # تسوية عهدة
    "N-001": RN001,  # إشعار للرئيس
    "N-002": RN002,  # إشعار للعميل
    "N-003": RN003,  # إشعار للمساعد
    "D-001": RD001,  # رفع مستند وارد
}

# ═══════════════════════════════════════
# لوحات القيادة
# ═══════════════════════════════════════
def main_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚙️ الإعدادات", callback_data="MENU-SETTINGS"),
            InlineKeyboardButton("📅 الأحداث",    callback_data="MENU-EVENTS"),
        ],
        [
            InlineKeyboardButton("📋 الخدمات",    callback_data="MENU-SERVICES"),
            InlineKeyboardButton("📊 التقارير",   callback_data="MENU-REPORTS"),
        ],
        [
            InlineKeyboardButton("💬 بريد الإشعارات", callback_data="MENU-INBOX"),
        ],
    ])

def settings_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 عميل جديد",    callback_data="F-001")],
        [InlineKeyboardButton("🔍 عرض عميل",     callback_data="F-002")],
        [InlineKeyboardButton("✏️ تعديل عميل",   callback_data="F-003")],
        [InlineKeyboardButton("🤝 مساعد جديد",   callback_data="A-001")],
        [InlineKeyboardButton("👤 عرض مساعد",    callback_data="A-002")],
        [InlineKeyboardButton("📁 موضوع جديد",   callback_data="F-004")],
        [InlineKeyboardButton("📋 موضوعات عميل", callback_data="T-002")],
        [InlineKeyboardButton("🔄 تغيير حالة موضوع", callback_data="T-003")],
        [InlineKeyboardButton("🗄️ أرشفة موضوع",  callback_data="T-004")],
        [InlineKeyboardButton("🔙 رجوع",          callback_data="MENU-MAIN")],
    ])

def events_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 عرض الأحداث",      callback_data="F-010")],
        [InlineKeyboardButton("➕ إضافة حدث جديد",  callback_data="F-005")],
        [InlineKeyboardButton("📢 نتيجة حدث",        callback_data="F-006")],
        [InlineKeyboardButton("🔙 رجوع",              callback_data="MENU-MAIN")],
    ])

def services_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 إرسال مرفقات",     callback_data="F-007")],
        [InlineKeyboardButton("📥 استلام شحنة",      callback_data="S-002")],
        [InlineKeyboardButton("🔍 تتبع شحنة",        callback_data="S-003")],
        [InlineKeyboardButton("📁 رفع مستند وارد",   callback_data="D-001")],
        [InlineKeyboardButton("📄 طلب مستندات",      callback_data="F-008")],
        [InlineKeyboardButton("💰 طلب عهدة مالية",  callback_data="F-009")],
        [InlineKeyboardButton("💳 تسوية عهدة",       callback_data="M-002")],
        [InlineKeyboardButton("🔙 رجوع",              callback_data="MENU-MAIN")],
    ])

def notifications_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔔 إشعار للرئيس",   callback_data="N-001")],
        [InlineKeyboardButton("📩 إشعار للعميل",   callback_data="N-002")],
        [InlineKeyboardButton("📋 إشعار للمساعد",  callback_data="N-003")],
        [InlineKeyboardButton("🔙 رجوع",            callback_data="MENU-MAIN")],
    ])

# ═══════════════════════════════════════
# Post Init — مسح الـ Webhook ومنع الـ Conflict
# ═══════════════════════════════════════
async def post_init(application):
    await application.bot.delete_webhook(drop_pending_updates=True)
    print("✅ Webhook deleted — bot started clean")

# ═══════════════════════════════════════
# Start
# ═══════════════════════════════════════
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"🆔 CHAT ID: {update.effective_chat.id}")
    await update.message.reply_text(
        "أهلاً بك في *أمين السر* 🏛️\n\nاختر من لوحة القيادة:",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

# ═══════════════════════════════════════
# Text Router
# ═══════════════════════════════════════
async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    routine = context.user_data.get("routine")
    step    = context.user_data.get("step")
    if not routine or not step:
        return

    text     = update.message.text.strip()
    chat_id  = update.effective_chat.id
    data     = context.user_data.setdefault("data", {})
    cancel_btn = [[{"text": "❌ إلغاء", "callback_data": "MENU-MAIN"}]]
    back_btn   = [[{"text": "🔙 القائمة", "callback_data": "MENU-MAIN"}]]

    # ─── F001 إضافة عميل ───
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
                await T001(context, chat_id, "❌ الرقم القومي يجب 14 رقم:")
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
            ok = P003("Clients", [code, data["name"], data["national_id"], data["mobile"], data["address"], datetime.now().strftime("%Y-%m-%d %H:%M")])
            context.user_data.clear()
            if ok:
                await T002(context, chat_id, f"✅ *تم إضافة العميل!*\n\n🔹 الكود: `{code}`\n👤 {data['name']}\n📱 {data['mobile']}", back_btn)
                await N001(context, BOSS_CHAT_ID, f"👤 عميل جديد: {data['name']}\n🔹 الكود: {code}")
            else:
                await T001(context, chat_id, "❌ حدث خطأ في الحفظ.")

    # ─── F002 عرض بيانات عميل ───
    elif routine == "F002":
        if step == "code":
            client = P002("Clients", text)
            context.user_data.clear()
            if not client:
                await T002(context, chat_id, "❌ كود العميل غير موجود.", back_btn)
                return
            msg = (
                f"👤 *بيانات العميل*\n\n"
                f"🔹 الكود: `{client.get('client_code', text)}`\n"
                f"👤 الاسم: {client.get('client_name', '—')}\n"
                f"🪪 الرقم القومي: {client.get('national_id', '—')}\n"
                f"📱 الموبايل: {client.get('mobile', '—')}\n"
                f"🏠 العنوان: {client.get('address', '—')}\n"
                f"📅 تاريخ التسجيل: {client.get('date_added', '—')}"
            )
            await T002(context, chat_id, msg, back_btn)

    # ─── F003 تعديل بيانات عميل ───
    elif routine == "F003":
        if step == "code":
            client = P002("Clients", text)
            if not client:
                await T002(context, chat_id, "❌ كود العميل غير موجود.", back_btn)
                context.user_data.clear()
                return
            data["client_code"] = text
            data["client"] = client
            context.user_data["step"] = "field"
            await T002(context, chat_id,
                f"✅ العميل: *{client.get('client_name', '')}*\n\nاختر الحقل للتعديل:",
                [
                    [{"text": "👤 الاسم", "callback_data": "EDIT-name"}],
                    [{"text": "📱 الموبايل", "callback_data": "EDIT-mobile"}],
                    [{"text": "🏠 العنوان", "callback_data": "EDIT-address"}],
                    [{"text": "❌ إلغاء", "callback_data": "MENU-MAIN"}],
                ]
            )

    # ─── RA001 إضافة مساعد ───
    elif routine == "RA001":
        if step == "name":
            if not V001(text):
                await T001(context, chat_id, "❌ الاسم قصير:")
                return
            data["name"] = text
            context.user_data["step"] = "bar_number"
            await T002(context, chat_id, "🔢 أدخل *رقم النقابة*:", cancel_btn)
        elif step == "bar_number":
            data["bar_number"] = text
            context.user_data["step"] = "mobile"
            await T002(context, chat_id, "📱 أدخل *رقم الموبايل*:", cancel_btn)
        elif step == "mobile":
            if not V003(text):
                await T001(context, chat_id, "❌ رقم غير صحيح:")
                return
            data["mobile"] = text
            code = G001("As", "Assistants")
            ok = P003("Assistants", [code, data["name"], data["bar_number"], data["mobile"], datetime.now().strftime("%Y-%m-%d %H:%M")])
            context.user_data.clear()
            if ok:
                await T002(context, chat_id, f"✅ *تم إضافة المساعد!*\n\n🔹 الكود: `{code}`\n👤 {data['name']}\n🔢 {data['bar_number']}\n📱 {data['mobile']}", back_btn)
                await N001(context, BOSS_CHAT_ID, f"👥 مساعد جديد: {data['name']}\n🔹 الكود: {code}")
            else:
                await T001(context, chat_id, "❌ حدث خطأ.")

    # ─── RA002 عرض بيانات مساعد ───
    elif routine == "RA002":
        if step == "code":
            assistant = P002("Assistants", text)
            context.user_data.clear()
            if not assistant:
                await T002(context, chat_id, "❌ كود المساعد غير موجود.", back_btn)
                return
            msg = (
                f"👥 *بيانات المساعد*\n\n"
                f"🔹 الكود: `{assistant.get('assistant_code', text)}`\n"
                f"👤 الاسم: {assistant.get('assistant_name', '—')}\n"
                f"🔢 رقم النقابة: {assistant.get('bar_number', '—')}\n"
                f"📱 الموبايل: {assistant.get('mobile', '—')}\n"
                f"📅 تاريخ التسجيل: {assistant.get('date_added', '—')}"
            )
            await T002(context, chat_id, msg, back_btn)

    # ─── RT001 إضافة موضوع ───
    elif routine == "RT001":
        if step == "client_code":
            client = P002("Clients", text)
            if not client:
                await T001(context, chat_id, "❌ كود العميل غير موجود:")
                return
            data["client_code"] = text
            data["client_name"] = client.get("client_name", "")
            context.user_data["step"] = "title"
            await T002(context, chat_id, f"✅ العميل: {data['client_name']}\n\nأدخل *عنوان الموضوع*:", cancel_btn)
        elif step == "title":
            if not V001(text):
                await T001(context, chat_id, "❌ العنوان قصير:")
                return
            data["title"] = text
            context.user_data["step"] = "event_type"
            await T002(context, chat_id, "📋 أدخل *نوع الموضوع* (مثال: طلاق / ميراث / عقار):", cancel_btn)
        elif step == "event_type":
            data["event_type"] = text
            code = G001("Tp", "Topics")
            ok = P003("Topics", [code, data["client_code"], data["client_name"], data["title"], data["event_type"], "جديد", datetime.now().strftime("%Y-%m-%d %H:%M")])
            context.user_data.clear()
            if ok:
                await T002(context, chat_id, f"✅ *تم إضافة الموضوع!*\n\n🔹 الكود: `{code}`\n📋 {data['title']}\n👤 {data['client_name']}", back_btn)
                await N001(context, BOSS_CHAT_ID, f"📁 موضوع جديد: {data['title']}\n🔹 الكود: {code}\n👤 العميل: {data['client_name']}")
            else:
                await T001(context, chat_id, "❌ حدث خطأ.")

    # ─── RT002 عرض موضوعات عميل ───
    elif routine == "RT002":
        if step == "client_code":
            topics = P006("Topics", "client_code", text)
            context.user_data.clear()
            if not topics:
                await T002(context, chat_id, "❌ لا توجد موضوعات لهذا العميل.", back_btn)
                return
            msg = f"📋 *موضوعات العميل* `{text}`:\n\n"
            for t in topics:
                msg += f"🔹 `{t.get('topic_code','—')}` — {t.get('service_name', t.get('title','—'))} [{t.get('status','—')}]\n"
            await T002(context, chat_id, msg, back_btn)

    # ─── RT003 تغيير حالة موضوع ───
    elif routine == "RT003":
        if step == "topic_code":
            topic = P002("Topics", text)
            if not topic:
                await T002(context, chat_id, "❌ كود الموضوع غير موجود.", back_btn)
                context.user_data.clear()
                return
            data["topic_code"] = text
            data["topic_name"] = topic.get("service_name", topic.get("title", ""))
            context.user_data["step"] = "status"
            await T002(context, chat_id,
                f"📋 الموضوع: *{data['topic_name']}*\n\nاختر الحالة الجديدة:",
                [
                    [{"text": "🆕 جديد",        "callback_data": "STATUS-جديد"}],
                    [{"text": "⚖️ قيد النظر",   "callback_data": "STATUS-قيد النظر"}],
                    [{"text": "✅ منتهي",        "callback_data": "STATUS-منتهي"}],
                    [{"text": "🗄️ مؤرشف",       "callback_data": "STATUS-مؤرشف"}],
                    [{"text": "❌ إلغاء",        "callback_data": "MENU-MAIN"}],
                ]
            )

    # ─── RT004 أرشفة موضوع ───
    elif routine == "RT004":
        if step == "topic_code":
            topic = P002("Topics", text)
            if not topic:
                await T002(context, chat_id, "❌ كود الموضوع غير موجود.", back_btn)
                context.user_data.clear()
                return
            data["topic_code"] = text
            data["topic_name"] = topic.get("service_name", topic.get("title", ""))
            context.user_data["step"] = "confirm"
            await T002(context, chat_id,
                f"🗄️ الموضوع: *{data['topic_name']}*\n\nهل تريد أرشفة هذا الموضوع؟",
                [
                    [{"text": "✅ تأكيد الأرشفة", "callback_data": "ARCHIVE-CONFIRM"}],
                    [{"text": "❌ إلغاء",          "callback_data": "MENU-MAIN"}],
                ]
            )

    # ─── RE001 إضافة حدث ───
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
            await T002(context, chat_id, "⏰ أدخل *وقت الحدث* (مثال: 10:00):", cancel_btn)
        elif step == "event_time":
            data["event_time"] = text
            context.user_data["step"] = "location"
            await T002(context, chat_id, "📍 أدخل *مكان الحدث*:", cancel_btn)
        elif step == "location":
            data["location"] = text
            code = G001("Ev", "Events")
            ok = P003("Events", [code, data["event_date"], data["topic_code"], data["client_name"], data["event_type"], data["event_time"], data["location"]])
            context.user_data.clear()
            if ok:
                await T002(context, chat_id, f"✅ *تم إضافة الحدث!*\n\n🔹 الكود: `{code}`\n📅 {data['event_date']} — {data['event_type']}\n📍 {data['location']}", back_btn)
                await N001(context, BOSS_CHAT_ID, f"📅 حدث جديد: {data['event_type']}\n📅 {data['event_date']} — {data['location']}\n👤 {data['client_name']}")
            else:
                await T001(context, chat_id, "❌ حدث خطأ.")

    # ─── RE002 نتيجة حدث ───
    elif routine == "RE002":
        if step == "event_code":
            event = P002("Events", text)
            if not event:
                await T001(context, chat_id, "❌ كود الحدث غير موجود:")
                return
            data["event_code"] = text
            data["event_type"] = event.get("event_type", "")
            data["event_date"] = event.get("event_date", "")
            context.user_data["step"] = "result"
            await T002(context, chat_id, f"📅 الحدث: {data['event_type']} — {data['event_date']}\n\n📝 أدخل *نتيجة الحدث*:", cancel_btn)
        elif step == "result":
            if not V001(text):
                await T001(context, chat_id, "❌ النتيجة قصيرة:")
                return
            data["result"] = text
            records = P005("Events")
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(data["event_code"]):
                    P004("Events", i, 8, text)
                    P004("Events", i, 9, "منتهي")
                    break
            context.user_data.clear()
            await T002(context, chat_id, f"✅ *تم تسجيل النتيجة!*\n\n📝 {data['result']}", back_btn)

    # ─── RS001 إرسال مرفقات ───
    # أعمدة Shipments: shipment_code | topic_code | sender | receiver | send_date | file_name | file_type | pickup_location | receive_status | receive_date | notes
    elif routine == "RS001":
        if step == "topic_code":
            topic = P002("Topics", text)
            if not topic:
                await T001(context, chat_id, "❌ كود الموضوع غير موجود:")
                return
            data["topic_code"] = text
            context.user_data["step"] = "description"
            await T002(context, chat_id, "📦 أدخل *وصف المرفقات*:", cancel_btn)
        elif step == "description":
            if not V001(text):
                await T001(context, chat_id, "❌ الوصف قصير:")
                return
            data["description"] = text
            code = G001("Sh", "Shipments")
            ok = P003("Shipments", [
                code,                                       # shipment_code
                data["topic_code"],                         # topic_code
                data["description"],                        # sender (وصف المرفقات)
                "",                                         # receiver
                datetime.now().strftime("%Y-%m-%d %H:%M"),  # send_date
                "",                                         # file_name
                "",                                         # file_type
                "",                                         # pickup_location
                "صادر",                                     # receive_status
            ])
            context.user_data.clear()
            if ok:
                await T002(context, chat_id, f"✅ *تم تسجيل الشحنة!*\n\n🔹 الكود: `{code}`\n📦 {data['description']}", back_btn)
            else:
                await T001(context, chat_id, "❌ حدث خطأ.")

    # ─── RS002 استلام شحنة ───
    elif routine == "RS002":
        if step == "shipment_code":
            shipment = P002("Shipments", text)
            if not shipment:
                await T002(context, chat_id, "❌ رقم الشحنة غير موجود.", back_btn)
                context.user_data.clear()
                return
            data["shipment_code"] = text
            records = P005("Shipments")
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(text):
                    P004("Shipments", i, 9, "مستلم")   # receive_status — العمود 9
                    P004("Shipments", i, 10, datetime.now().strftime("%Y-%m-%d %H:%M"))  # receive_date — العمود 10
                    break
            context.user_data.clear()
            await T002(context, chat_id, f"✅ *تم تسجيل استلام الشحنة!*\n\n🔹 الكود: `{text}`\n📦 {shipment.get('sender','—')}", back_btn)

    # ─── RS003 تتبع شحنة ───
    # أعمدة: shipment_code | topic_code | sender | receiver | send_date | file_name | file_type | pickup_location | receive_status | receive_date | notes
    elif routine == "RS003":
        if step == "shipment_code":
            shipment = P002("Shipments", text)
            context.user_data.clear()
            if not shipment:
                await T002(context, chat_id, "❌ رقم الشحنة غير موجود.", back_btn)
                return
            msg = (
                f"📦 *تتبع الشحنة*\n\n"
                f"🔹 الكود: `{text}`\n"
                f"📋 الموضوع: {shipment.get('topic_code','—')}\n"
                f"📝 المحتوى: {shipment.get('sender','—')}\n"
                f"🔄 الحالة: {shipment.get('receive_status','—')}\n"
                f"📅 تاريخ الإرسال: {shipment.get('send_date','—')}"
            )
            await T002(context, chat_id, msg, back_btn)

    # ─── RD002 طلب مستندات ───
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
            ok = P003("Documents", [code, data["entity"], data["description"], "طلب", datetime.now().strftime("%Y-%m-%d %H:%M")])
            context.user_data.clear()
            if ok:
                await T002(context, chat_id, f"✅ *تم تسجيل الطلب!*\n\n🔹 الكود: `{code}`\n📄 من: {data['entity']}", back_btn)
            else:
                await T001(context, chat_id, "❌ حدث خطأ.")

    # ─── RM001 طلب عهدة ───
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
            ok = P003("Custody", [code, data["amount"], data["reason"], "طلب", datetime.now().strftime("%Y-%m-%d %H:%M")])
            context.user_data.clear()
            if ok:
                await T002(context, chat_id, f"✅ *تم طلب العهدة!*\n\n🔹 الكود: `{code}`\n💰 {data['amount']} جنيه\n📝 {data['reason']}", back_btn)
                await N001(context, BOSS_CHAT_ID, f"💰 طلب عهدة جديد\n🔹 الكود: {code}\n💰 المبلغ: {data['amount']} جنيه\n📝 {data['reason']}")
            else:
                await T001(context, chat_id, "❌ حدث خطأ.")

    # ─── RM002 تسوية عهدة ───
    elif routine == "RM002":
        if step == "fund_code":
            fund = P002("Custody", text)
            if not fund:
                await T002(context, chat_id, "❌ كود العهدة غير موجود.", back_btn)
                context.user_data.clear()
                return
            data["fund_code"] = text
            data["amount"] = fund.get("amount", "—")
            context.user_data["step"] = "notes"
            await T002(context, chat_id, f"💰 العهدة: {data['amount']} جنيه\n\n📝 أدخل *ملاحظات التسوية*:", cancel_btn)
        elif step == "notes":
            data["notes"] = text
            records = P005("Custody")
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(data["fund_code"]):
                    P004("Custody", i, 4, "مسوّاة")
                    P004("Custody", i, 6, text)
                    P004("Custody", i, 7, datetime.now().strftime("%Y-%m-%d %H:%M"))
                    break
            context.user_data.clear()
            await T002(context, chat_id, f"✅ *تم تسوية العهدة!*\n\n🔹 الكود: `{data['fund_code']}`\n💰 {data['amount']} جنيه", back_btn)

    # ─── RN001 إشعار للرئيس ───
    elif routine == "RN001":
        if step == "text":
            if not V001(text):
                await T001(context, chat_id, "❌ النص قصير:")
                return
            await N001(context, BOSS_CHAT_ID, text)
            context.user_data.clear()
            await T002(context, chat_id, "✅ *تم إرسال الإشعار للرئيس!*", back_btn)

    # ─── RN002 إشعار للعميل ───
    elif routine == "RN002":
        if step == "client_code":
            client = P002("Clients", text)
            if not client:
                await T002(context, chat_id, "❌ كود العميل غير موجود.", back_btn)
                context.user_data.clear()
                return
            data["client_code"] = text
            data["client_name"] = client.get("client_name", "")
            chat_id_client = client.get("telegram_chat_id", "")
            if not chat_id_client:
                await T002(context, chat_id, f"❌ العميل {data['client_name']} ليس لديه Chat ID مسجل.", back_btn)
                context.user_data.clear()
                return
            data["client_chat_id"] = chat_id_client
            context.user_data["step"] = "message"
            await T002(context, chat_id, f"✅ العميل: *{data['client_name']}*\n\n📝 أدخل *نص الإشعار*:", cancel_btn)
        elif step == "message":
            if not V001(text):
                await T001(context, chat_id, "❌ النص قصير:")
                return
            await N002(context, data["client_chat_id"], text)
            context.user_data.clear()
            await T002(context, chat_id, "✅ *تم إرسال الإشعار للعميل!*", back_btn)

    # ─── RD001 رفع مستند وارد ───
    elif routine == "RD001":
        if step == "topic_code":
            topic = P002("Topics", text)
            if not topic:
                await T001(context, chat_id, "❌ كود الموضوع غير موجود:")
                return
            data["topic_code"] = text
            data["topic_name"] = topic.get("service_name", topic.get("title", ""))
            context.user_data["step"] = "doc_name"
            await T002(context, chat_id, f"✅ الموضوع: *{data['topic_name']}*\n\n📄 أدخل *اسم المستند*:", cancel_btn)
        elif step == "doc_name":
            if not V001(text):
                await T001(context, chat_id, "❌ الاسم قصير:")
                return
            data["doc_name"] = text
            context.user_data["step"] = "file"
            await T002(context, chat_id, "📎 أرسل *الملف أو الصورة* الآن:", cancel_btn)

    # ─── RN003 إشعار للمساعد ───
    elif routine == "RN003":
        if step == "assistant_code":
            assistant = P002("Assistants", text)
            if not assistant:
                await T002(context, chat_id, "❌ كود المساعد غير موجود.", back_btn)
                context.user_data.clear()
                return
            data["assistant_code"] = text
            data["assistant_name"] = assistant.get("assistant_name", "")
            chat_id_assistant = assistant.get("telegram_chat_id", "")
            if not chat_id_assistant:
                await T002(context, chat_id, f"❌ المساعد {data['assistant_name']} ليس لديه Chat ID مسجل.", back_btn)
                context.user_data.clear()
                return
            data["assistant_chat_id"] = chat_id_assistant
            context.user_data["step"] = "message"
            await T002(context, chat_id, f"✅ المساعد: *{data['assistant_name']}*\n\n📝 أدخل *نص الإشعار*:", cancel_btn)
        elif step == "message":
            if not V001(text):
                await T001(context, chat_id, "❌ النص قصير:")
                return
            await N003(context, data["assistant_chat_id"], text)
            context.user_data.clear()
            await T002(context, chat_id, "✅ *تم إرسال الإشعار للمساعد!*", back_btn)

# ═══════════════════════════════════════
# Callback Router
# ═══════════════════════════════════════
async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "ARCHIVE-CONFIRM":
        topic_code = context.user_data.get("data", {}).get("topic_code", "")
        topic_name = context.user_data.get("data", {}).get("topic_name", "")
        if topic_code:
            records = P005("Topics")
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(topic_code):
                    P004("Topics", i, 6, "مؤرشف")
                    P004("Topics", i, 7, datetime.now().strftime("%Y-%m-%d %H:%M"))
                    break
        context.user_data.clear()
        await query.edit_message_text(
            f"✅ تم أرشفة الموضوع `{topic_code}` — *{topic_name}*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 القائمة", callback_data="MENU-MAIN")]])
        )
        await N001(context, BOSS_CHAT_ID, f"🗄️ تم أرشفة الموضوع\n🔹 الكود: {topic_code}\n📋 {topic_name}")
        return

    if data.startswith("STATUS-"):
        new_status = data.replace("STATUS-", "")
        topic_code = context.user_data.get("data", {}).get("topic_code", "")
        if topic_code:
            records = P005("Topics")
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(topic_code):
                    P004("Topics", i, 6, new_status)
                    break
        context.user_data.clear()
        await query.edit_message_text(
            f"✅ تم تغيير حالة الموضوع `{topic_code}` إلى *{new_status}*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 القائمة", callback_data="MENU-MAIN")]])
        )
        return

    if data.startswith("EDIT-"):
        field = data.replace("EDIT-", "")
        field_names = {"name": "الاسم", "mobile": "الموبايل", "address": "العنوان"}
        context.user_data["step"] = f"edit_{field}"
        await query.edit_message_text(
            f"✏️ أدخل *{field_names.get(field, field)}* الجديد:",
            parse_mode="Markdown"
        )
        return

    if data == "MENU-MAIN":
        context.user_data.clear()
        await query.edit_message_text("لوحة القيادة:", reply_markup=main_keyboard())
    elif data == "MENU-SETTINGS":
        await query.edit_message_text("⚙️ *الإعدادات*\nاختر العملية:", parse_mode="Markdown", reply_markup=settings_keyboard())
    elif data == "MENU-EVENTS":
        await query.edit_message_text("📅 *الأحداث*\nاختر العملية:", parse_mode="Markdown", reply_markup=events_keyboard())
    elif data == "MENU-SERVICES":
        await query.edit_message_text("📋 *الخدمات*\nاختر الخدمة:", parse_mode="Markdown", reply_markup=services_keyboard())
    elif data == "MENU-REPORTS":
        await query.edit_message_text("📊 التقارير — قريباً! 🚧", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="MENU-MAIN")]]))
    elif data == "MENU-INBOX":
        await query.edit_message_text("💬 *بريد الإشعارات*\nاختر نوع الإشعار:", parse_mode="Markdown", reply_markup=notifications_keyboard())
    elif data in ROUTE_MAP:
        await ROUTE_MAP[data](update, context)
    else:
        await query.edit_message_text(
            f"⏳ الكود *{data}* قيد التطوير.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="MENU-MAIN")]])
        )

# ═══════════════════════════════════════
# File Router
# ═══════════════════════════════════════
async def file_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    routine = context.user_data.get("routine")
    step    = context.user_data.get("step")
    if not routine or step != "file":
        return

    chat_id  = update.effective_chat.id
    data     = context.user_data.setdefault("data", {})
    back_btn = [[{"text": "🔙 القائمة", "callback_data": "MENU-MAIN"}]]

    if routine == "RD001":
        msg = update.message
        if msg.document:
            file_obj  = msg.document
            file_name = file_obj.file_name or data.get("doc_name", "document")
            file_id   = file_obj.file_id
        elif msg.photo:
            file_obj  = msg.photo[-1]
            file_name = f"{data.get('doc_name', 'photo')}.jpg"
            file_id   = file_obj.file_id
        else:
            await T001(context, chat_id, "❌ أرسل ملفاً أو صورة صالحة:")
            return

        await T001(context, chat_id, "⏳ جاري رفع الملف...")

        try:
            import tempfile, os
            tg_file = await context.bot.get_file(file_id)
            suffix  = os.path.splitext(file_name)[-1] or ".bin"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp_path = tmp.name
            await tg_file.download_to_drive(tmp_path)

            topic_code = data.get("topic_code", "GENERAL")
            drive_link = DRV001(tmp_path, file_name, topic_code)
            os.unlink(tmp_path)

            if not drive_link:
                await T002(context, chat_id, "❌ فشل رفع الملف على Drive.", back_btn)
                context.user_data.clear()
                return

            code = G001("Doc", "Documents")
            P003("Documents", [
                code, topic_code, data.get("doc_name", file_name),
                file_name, drive_link, "وارد", "TRANSIT",
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ])

            context.user_data.clear()
            await T002(context, chat_id,
                f"✅ *تم رفع المستند!*\n\n"
                f"🔹 الكود: `{code}`\n"
                f"📄 الاسم: {data.get('doc_name', file_name)}\n"
                f"📋 الموضوع: {topic_code}\n"
                f"🔗 [فتح الملف]({drive_link})",
                back_btn
            )
            await N001(context, BOSS_CHAT_ID,
                f"📁 مستند وارد جديد\n🔹 الكود: {code}\n"
                f"📄 {data.get('doc_name', file_name)}\n"
                f"📋 الموضوع: {topic_code}\n🔗 {drive_link}"
            )

        except Exception as e:
            print(f"❌ file_router RD001: {e}")
            await T002(context, chat_id, "❌ حدث خطأ أثناء الرفع.", back_btn)
            context.user_data.clear()

# ═══════════════════════════════════════
# Main
# ═══════════════════════════════════════
if __name__ == "__main__":
    time.sleep(5)
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, file_router))
    app.run_polling(drop_pending_updates=True)