from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
import importlib, os, sys

TOKEN = "8716122412:AAHREvaHnoYsydnaPevVa5JDrT0wnxzz3Mk"

# ─── مكتبة الأكواد المرجعية ───────────────────────────────────────────────────

LIBRARY = {}

def load_library():
    lib_path = os.path.join(os.path.dirname(__file__), "library")
    if not os.path.exists(lib_path):
        os.makedirs(lib_path)
        return
    sys.path.insert(0, lib_path)
    for filename in sorted(os.listdir(lib_path)):
        if filename.endswith(".py") and filename[0] != "_":
            module_name = filename[:-3]
            parts = module_name.split("_", 1)
            if parts and len(parts[0]) == 4:
                ref = parts[0][:1] + "-" + parts[0][1:]
                try:
                    mod = importlib.import_module(module_name)
                    if hasattr(mod, "handler"):
                        LIBRARY[ref] = mod.handler
                        print(f"✅ تم تحميل الكود: {ref}")
                except Exception as e:
                    print(f"❌ خطأ في تحميل {module_name}: {e}")

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
        [InlineKeyboardButton("📅 عرض التقويم",     callback_data="F-010")],
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
    if context.user_data.get("f001_step") is not None:
        from library.F001_add_client import handle_text
        await handle_text(update, context)
        return

async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "MENU-MAIN":
        await query.edit_message_text(
            "لوحة القيادة:",
            reply_markup=main_keyboard()
        )
    elif data == "MENU-SETTINGS":
        await query.edit_message_text(
            "⚙️ *الإعدادات*\nاختر العملية:",
            parse_mode="Markdown",
            reply_markup=settings_keyboard()
        )
    elif data == "MENU-EVENTS":
        await query.edit_message_text(
            "📅 *الأحداث*\nاختر العملية:",
            parse_mode="Markdown",
            reply_markup=events_keyboard()
        )
    elif data == "MENU-SERVICES":
        await query.edit_message_text(
            "📋 *الخدمات*\nاختر الخدمة:",
            parse_mode="Markdown",
            reply_markup=services_keyboard()
        )
    elif data == "MENU-REPORTS":
        await query.edit_message_text(
            "📊 التقارير — قريباً! 🚧",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 رجوع", callback_data="MENU-MAIN")]
            ])
        )
    elif data == "MENU-INBOX":
        await query.edit_message_text(
            "💬 بريد الإشعارات — قريباً! 🚧",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 رجوع", callback_data="MENU-MAIN")]
            ])
        )
    elif data in LIBRARY:
        await LIBRARY[data](update, context)
    else:
        await query.edit_message_text(
            f"⏳ الكود *{data}* قيد التطوير.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 رجوع", callback_data="MENU-MAIN")]
            ])
        )

# ─── تشغيل البوت ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    load_library()
    print(f"📚 الأكواد المحملة: {list(LIBRARY.keys())}")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
    app.run_polling()