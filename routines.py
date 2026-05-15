from primitives import *

BOSS_CHAT_ID = 0  # يتغير لكل مكتب

# ═══════════════════════════════════════════════
# F001 — إضافة عميل جديد
# ═══════════════════════════════════════════════
async def F001(update, context):
    await T001(context, update.effective_chat.id, "👤 *إضافة عميل جديد*\n\nأدخل اسم العميل:")
    context.user_data["routine"] = "F001"
    context.user_data["step"] = "name"

# ═══════════════════════════════════════════════
# F002 — عرض بيانات عميل
# ═══════════════════════════════════════════════
async def F002(update, context):
    await T001(context, update.effective_chat.id, "🔍 *عرض بيانات عميل*\n\nأدخل كود العميل:")
    context.user_data["routine"] = "F002"
    context.user_data["step"] = "code"

# ═══════════════════════════════════════════════
# F003 — تعديل بيانات عميل
# ═══════════════════════════════════════════════
async def F003(update, context):
    await T001(context, update.effective_chat.id, "✏️ *تعديل بيانات عميل*\n\nأدخل كود العميل:")
    context.user_data["routine"] = "F003"
    context.user_data["step"] = "code"

# ═══════════════════════════════════════════════
# T001_R — إضافة موضوع جديد
# ═══════════════════════════════════════════════
async def RT001(update, context):
    await T001(context, update.effective_chat.id, "📋 *إضافة موضوع جديد*\n\nأدخل كود العميل:")
    context.user_data["routine"] = "RT001"
    context.user_data["step"] = "client_code"

# ═══════════════════════════════════════════════
# RT002 — عرض موضوعات عميل
# ═══════════════════════════════════════════════
async def RT002(update, context):
    await T001(context, update.effective_chat.id, "📋 *عرض موضوعات عميل*\n\nأدخل كود العميل:")
    context.user_data["routine"] = "RT002"
    context.user_data["step"] = "client_code"

# ═══════════════════════════════════════════════
# RT003 — تغيير حالة موضوع
# ═══════════════════════════════════════════════
async def RT003(update, context):
    await T001(context, update.effective_chat.id, "🔄 *تغيير حالة موضوع*\n\nأدخل كود الموضوع:")
    context.user_data["routine"] = "RT003"
    context.user_data["step"] = "topic_code"

# ═══════════════════════════════════════════════
# RT004 — أرشفة موضوع
# ═══════════════════════════════════════════════
async def RT004(update, context):
    await T001(context, update.effective_chat.id, "🗄️ *أرشفة موضوع*\n\nأدخل كود الموضوع:")
    context.user_data["routine"] = "RT004"
    context.user_data["step"] = "topic_code"

# ═══════════════════════════════════════════════
# RE001 — إضافة حدث جديد
# ═══════════════════════════════════════════════
async def RE001(update, context):
    await T001(context, update.effective_chat.id, "📅 *إضافة حدث جديد*\n\nأدخل عنوان الحدث:")
    context.user_data["routine"] = "RE001"
    context.user_data["step"] = "title"

# ═══════════════════════════════════════════════
# RE002 — إشعار بنتيجة حدث
# ═══════════════════════════════════════════════
async def RE002(update, context):
    await T001(context, update.effective_chat.id, "📢 *إشعار بنتيجة حدث*\n\nأدخل كود الحدث:")
    context.user_data["routine"] = "RE002"
    context.user_data["step"] = "event_code"

# ═══════════════════════════════════════════════
# RE003 — عرض الأحداث تحت المتابعة
# ═══════════════════════════════════════════════
async def RE003(update, context):
    events = C003()
    if not events:
        await T001(context, update.effective_chat.id, "📅 لا توجد أحداث قادمة.")
        await N001(context, BOSS_CHAT_ID, "تم عرض الأحداث — لا توجد أحداث قادمة")
        return
    text = "📅 *الأحداث القادمة:*\n\n"
    for e in events:
        text += f"• {e.get('title','')} — {e.get('date','')}\n"
    await T001(context, update.effective_chat.id, text)
    await N001(context, BOSS_CHAT_ID, "تم عرض الأحداث القادمة")

# ═══════════════════════════════════════════════
# RD001 — رفع مستند وارد
# ═══════════════════════════════════════════════
async def RD001(update, context):
    await T001(context, update.effective_chat.id, "📁 *رفع مستند وارد*\n\nأرسل الملف:")
    context.user_data["routine"] = "RD001"
    context.user_data["step"] = "file"

# ═══════════════════════════════════════════════
# RD002 — طلب مستندات من جهة خارجية
# ═══════════════════════════════════════════════
async def RD002(update, context):
    await T001(context, update.effective_chat.id, "📤 *طلب مستندات*\n\nأدخل اسم الجهة:")
    context.user_data["routine"] = "RD002"
    context.user_data["step"] = "entity"

# ═══════════════════════════════════════════════
# RD003 — الموافقة على مستند
# ═══════════════════════════════════════════════
async def RD003(update, context):
    await T001(context, update.effective_chat.id, "✅ *الموافقة على مستند*\n\nأدخل كود المستند:")
    context.user_data["routine"] = "RD003"
    context.user_data["step"] = "doc_code"

# ═══════════════════════════════════════════════
# RD004 — رفض مستند
# ═══════════════════════════════════════════════
async def RD004(update, context):
    await T001(context, update.effective_chat.id, "❌ *رفض مستند*\n\nأدخل كود المستند:")
    context.user_data["routine"] = "RD004"
    context.user_data["step"] = "doc_code"

# ═══════════════════════════════════════════════
# RD005 — عرض مستندات موضوع
# ═══════════════════════════════════════════════
async def RD005(update, context):
    await T001(context, update.effective_chat.id, "📂 *عرض مستندات موضوع*\n\nأدخل كود الموضوع:")
    context.user_data["routine"] = "RD005"
    context.user_data["step"] = "topic_code"

# ═══════════════════════════════════════════════
# RD006 — أرشفة مستندات
# ═══════════════════════════════════════════════
async def RD006(update, context):
    await T001(context, update.effective_chat.id, "🗄️ *أرشفة مستندات*\n\nأدخل كود الموضوع:")
    context.user_data["routine"] = "RD006"
    context.user_data["step"] = "topic_code"

# ═══════════════════════════════════════════════
# RS001 — إرسال مرفقات (شحنة صادرة)
# ═══════════════════════════════════════════════
async def RS001(update, context):
    await T001(context, update.effective_chat.id, "📦 *إرسال مرفقات*\n\nأدخل كود الموضوع:")
    context.user_data["routine"] = "RS001"
    context.user_data["step"] = "topic_code"

# ═══════════════════════════════════════════════
# RS002 — استلام شحنة واردة
# ═══════════════════════════════════════════════
async def RS002(update, context):
    await T001(context, update.effective_chat.id, "📥 *استلام شحنة واردة*\n\nأدخل رقم الشحنة:")
    context.user_data["routine"] = "RS002"
    context.user_data["step"] = "shipment_code"

# ═══════════════════════════════════════════════
# RS003 — تتبع حالة شحنة
# ═══════════════════════════════════════════════
async def RS003(update, context):
    await T001(context, update.effective_chat.id, "🔍 *تتبع حالة شحنة*\n\nأدخل رقم الشحنة:")
    context.user_data["routine"] = "RS003"
    context.user_data["step"] = "shipment_code"

# ═══════════════════════════════════════════════
# RM001 — طلب عهدة مالية
# ═══════════════════════════════════════════════
async def RM001(update, context):
    await T001(context, update.effective_chat.id, "💰 *طلب عهدة مالية*\n\nأدخل المبلغ المطلوب:")
    context.user_data["routine"] = "RM001"
    context.user_data["step"] = "amount"

# ═══════════════════════════════════════════════
# RM002 — تسوية عهدة مالية
# ═══════════════════════════════════════════════
async def RM002(update, context):
    await T001(context, update.effective_chat.id, "💳 *تسوية عهدة مالية*\n\nأدخل كود العهدة:")
    context.user_data["routine"] = "RM002"
    context.user_data["step"] = "fund_code"

# ═══════════════════════════════════════════════
# RA001 — إضافة مساعد جديد
# ═══════════════════════════════════════════════
async def RA001(update, context):
    await T001(context, update.effective_chat.id, "👥 *إضافة مساعد جديد*\n\nأدخل اسم المساعد:")
    context.user_data["routine"] = "RA001"
    context.user_data["step"] = "name"

# ═══════════════════════════════════════════════
# RA002 — عرض بيانات مساعد
# ═══════════════════════════════════════════════
async def RA002(update, context):
    await T001(context, update.effective_chat.id, "👤 *عرض بيانات مساعد*\n\nأدخل كود المساعد:")
    context.user_data["routine"] = "RA002"
    context.user_data["step"] = "code"

# ═══════════════════════════════════════════════
# RN001 — إشعار للرئيس
# ═══════════════════════════════════════════════
async def RN001(update, context):
    await T001(context, update.effective_chat.id, "🔔 *إشعار للرئيس*\n\nأدخل نص الإشعار:")
    context.user_data["routine"] = "RN001"
    context.user_data["step"] = "text"

# ═══════════════════════════════════════════════
# RN002 — إشعار للعميل
# ═══════════════════════════════════════════════
async def RN002(update, context):
    await T001(context, update.effective_chat.id, "📩 *إشعار للعميل*\n\nأدخل كود العميل:")
    context.user_data["routine"] = "RN002"
    context.user_data["step"] = "client_code"

# ═══════════════════════════════════════════════
# RN003 — إشعار للمساعد
# ═══════════════════════════════════════════════
async def RN003(update, context):
    await T001(context, update.effective_chat.id, "📋 *إشعار للمساعد*\n\nأدخل كود المساعد:")
    context.user_data["routine"] = "RN003"
    context.user_data["step"] = "assistant_code"