from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
import importlib, os, sys
from routines import *
from primitives import *
from datetime import datetime

TOKEN = "8716122412:AAHREvaHnoYsydnaPevVa5JDrT0wnxzz3Mk"

# ─── خريطة الأكواد ────────────────────────────────────────────────────────────

ROUTE_MAP = {
    "F-001": F001,  "F-002": RA001, "F-003": RT001, "F-004": RT001,
    "F-005": RE001, "F-006": RE002, "F-007": RS001, "F-008": RD002,
    "F-009": RM001, "F-010": RE003,
}

# ─── لوحة القيادة ─────────────────────────────────────────────────────────────

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
        [InlineKeyboardButton("👤 عميل جديد",  callback_data="F-001")],
        [InlineKeyboardButton("🤝 مساعد جديد", callback_data="F-002")],
        [InlineKeyboardButton("🗂️ خدمة جديدة", callback_data="F-003")],
        [InlineKeyboardButton("📁 موضوع جديد", callback_data="F-004")],
        [InlineKeyboardButton("🔙 رجوع",        callback_data="MENU-MAIN")],
    ])

def events_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 عرض الأحداث",     callback_data="F-010")],
        [InlineKeyboardButton("➕ إضافة حدث جديد", callback_data="F-005")],
        [InlineKeyboardButton("🔙 رجوع",             callback_data="MENU-MAIN")],
    ])

def services_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 نتيجة حدث",       callback_data="F-006")],
        [InlineKeyboardButton("📦 تداول مرفقات",    callback_data="F-007")],
        [InlineKeyboardButton("📄 طلب مستندات",     callback_data="F-008")],
        [InlineKeyboardButton("💰 طلب عهدة مالية", callback_data="F-009")],
        [InlineKeyboardButton("🔙 رجوع",             callback_data="MENU-MAIN")],
    ])

# ─── Handlers ─────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بك في *أمين السر* 🏛️\n\nاختر من لوحة القيادة:",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    routine = context.user_data.get("routine")
    step = context.user_data.get("step")
    if not routine or not step:
        return

    text = update.message.text.strip()
    chat_id = update.effective_chat.id
    data = context.user_data.setdefault("data", {})
    cancel_btn = [[{"text": "❌ إلغاء", "callback_data": "MENU-MAIN"}]]

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
                await T002(context, chat_id, f"✅ *تم إضافة العميل!*\n\n🔹 الكود: `{code}`\n👤 {data['name']}\n📱 {data['mobile']}", [[{"text": "🔙 القائمة", "callback_data": "MENU-MAIN"}]])
            else:
                await T001(context, chat_id, "❌ حدث خطأ في الحفظ.")

    # ─── RA001 إضافة مساعد ───
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
            ok = P003("Assistants", [code, data["name"], data["mobile"], datetime.now().strftime("%Y-%m-%d %H:%M")])
            context.user_data.clear()
            if ok:
                await T002(context, chat_id, f"✅ *تم إضافة المساعد!*\n\n🔹 الكود: `{code}`\n👤 {data['name']}", [[{"text": "🔙 القائمة", "callback_data": "MENU-MAIN"}]])
            else:
                await T001(context, chat_id, "❌ حدث خطأ.")

    # ─── RT001 إضافة موضوع ───
    elif routine == "RT001":
        if step == "client_code":
            client = P002("Clients", text)
            if not client:
                await T001(context, chat_id, "❌ كود العميل غير موجود:")
                return
            data["client_code"] = text
            data["client_name"] = client.get("الاسم", "")
            context.user_data["step"] = "title"
            await T002(context, chat_id, f"✅ العميل: {data['client_name']}\n\nأدخل *عنوان الموضوع*:", cancel_btn)
        elif step == "title":
            if not V001(text):
                await T001(context, chat_id, "❌ العنوان قصير:")
                return
            data["title"] = text
            code = G001("Tp", "Topics")
            ok = P003("Topics", [code, data["client_code"], data["title"], "جديد", datetime.now().strftime("%Y-%m-%d %H:%M")])
            context.user_data.clear()
            if ok:
                await T002(context, chat_id, f"✅ *تم إضافة الموضوع!*\n\n🔹 الكود: `{code}`\n📋 {data['title']}", [[{"text": "🔙 القائمة", "callback_data": "MENU-MAIN"}]])
            else:
                await T001(context, chat_id, "❌ حدث خطأ.")

    # ─── RE001 إضافة حدث ───
    elif routine == "RE001":
        if step == "title":
            if not V001(text):
                await T001(context, chat_id, "❌ العنوان قصير:")
                return
            data["title"] = text
            context.user_data["step"] = "date"
            await T002(context, chat_id, "📅 أدخل *تاريخ الحدث* (DD/MM/YYYY):", cancel_btn)
        elif step == "date":
            if not V004(text):
                await T001(context, chat_id, "❌ التاريخ غير صحيح. استخدم DD/MM/YYYY:")
                return
            data["date"] = text
            code = G001("Ev", "Events")
            ok = P003("Events", [code, data["title"], data["date"], "قادم", datetime.now().strftime("%Y-%m-%d %H:%M")])
            context.user_data.clear()
            if ok:
                await T002(context, chat_id, f"✅ *تم إضافة الحدث!*\n\n🔹 الكود: `{code}`\n📅 {data['title']} — {data['date']}", [[{"text": "🔙 القائمة", "callback_data": "MENU-MAIN"}]])
            else:
                await T001(context, chat_id, "❌ حدث خطأ.")

    # ─── RM001 طلب عهدة مالية ───
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
            code = G001("Fn", "Finance")
            ok = P003("Finance", [code, data["amount"], data["reason"], "طلب", datetime.now().strftime("%Y-%m-%d %H:%M")])
            context.user_data.clear()
            if ok:
                await T002(context, chat_id, f"✅ *تم طلب العهدة!*\n\n🔹 الكود: `{code}`\n💰 {data['amount']} جنيه", [[{"text": "🔙 القائمة", "callback_data": "MENU-MAIN"}]])
            else:
                await T001(context, chat_id, "❌ حدث خطأ.")

# ─── menu_router ──────────────────────────────────────────────────────────────

async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "MENU-MAIN":
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
        await query.edit_message_text("💬 بريد الإشعارات — قريباً! 🚧", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="MENU-MAIN")]]))
    elif data in ROUTE_MAP:
        await ROUTE_MAP[data](update, context)
    else:
        await query.edit_message_text(
            f"⏳ الكود *{data}* قيد التطوير.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="MENU-MAIN")]])
        )

# ─── تشغيل البوت ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
    app.run_polling(drop_pending_updates=True)