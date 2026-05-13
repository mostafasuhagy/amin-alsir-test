import gspread
from google.oauth2.service_account import Credentials
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import os, re
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_NAME   = "amin_alsir_cases_new_V2"
CLIENTS_TAB  = "Clients"

def get_sheet():
    creds_path = os.path.join(os.path.dirname(__file__), "..", "credentials.json")
    creds  = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    client = gspread.authorize(creds)
    sh     = client.open(SHEET_NAME)
    try:
        ws = sh.worksheet(CLIENTS_TAB)
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=CLIENTS_TAB, rows=1000, cols=10)
        ws.append_row(["كود العميل", "الاسم", "الرقم القومي", "الموبايل", "تاريخ الإضافة"])
    return ws

def next_client_code(ws) -> str:
    all_values = ws.col_values(1)
    codes = [v for v in all_values[1:] if v.startswith("Cl-")]
    if not codes:
        return "Cl-001"
    last_num = max(int(c.split("-")[1]) for c in codes)
    return f"Cl-{last_num + 1:03d}"

WAIT_NAME, WAIT_ID, WAIT_PHONE = range(3)

async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نقطة الدخول — تُستدعى من main.py عند الضغط على زر F001"""
    context.user_data["f001_step"] = WAIT_NAME
    context.user_data["f001_data"] = {}
    await update.callback_query.edit_message_text(
        "👤 *إضافة عميل جديد*\n\n"
        "الخطوة 1 من 3\n"
        "اكتب اسم العميل كاملاً:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ إلغاء", callback_data="MENU-MAIN")]
        ])
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """تُستدعى من main.py لكل رسالة نصية — ترجع True لو هي شغلتها"""
    step = context.user_data.get("f001_step")
    if step is None:
        return False

    text = update.message.text.strip()
    data = context.user_data.setdefault("f001_data", {})

    # ── خطوة 1: الاسم ──────────────────────────────────────────────
    if step == WAIT_NAME:
        if len(text) < 3:
            await update.message.reply_text("❌ الاسم قصير جداً، اكتب الاسم كاملاً:")
            return True
        data["name"] = text
        context.user_data["f001_step"] = WAIT_ID
        await update.message.reply_text(
            "✅ تم حفظ الاسم.\n\n"
            "الخطوة 2 من 3\n"
            "اكتب الرقم القومي (14 رقم):",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ إلغاء", callback_data="MENU-MAIN")]
            ])
        )
        return True

    # ── خطوة 2: الرقم القومي ───────────────────────────────────────
    if step == WAIT_ID:
        if not re.fullmatch(r"\d{14}", text):
            await update.message.reply_text("❌ الرقم القومي يجب أن يكون 14 رقم بالظبط، حاول تاني:")
            return True
        data["national_id"] = text
        context.user_data["f001_step"] = WAIT_PHONE
        await update.message.reply_text(
            "✅ تم حفظ الرقم القومي.\n\n"
            "الخطوة 3 من 3\n"
            "اكتب رقم الموبايل:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ إلغاء", callback_data="MENU-MAIN")]
            ])
        )
        return True

    # ── خطوة 3: الموبايل ───────────────────────────────────────────
    if step == WAIT_PHONE:
        if not re.fullmatch(r"01[0125]\d{8}", text):
            await update.message.reply_text("❌ رقم الموبايل غير صحيح، اكتب رقم مصري صحيح:")
            return True
        data["phone"] = text
        context.user_data["f001_step"] = None

        # ── حفظ في الشيت ───────────────────────────────────────────
        try:
            ws   = get_sheet()
            code = next_client_code(ws)
            date = datetime.now().strftime("%Y-%m-%d %H:%M")
            ws.append_row([code, data["name"], data["national_id"], data["phone"], date])

            await update.message.reply_text(
                f"✅ *تمت إضافة العميل بنجاح!*\n\n"
                f"🔑 الكود: `{code}`\n"
                f"👤 الاسم: {data['name']}\n"
                f"🪪 الرقم القومي: {data['national_id']}\n"
                f"📱 الموبايل: {data['phone']}\n"
                f"📅 التاريخ: {date}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ إضافة عميل آخر", callback_data="F001")],
                    [InlineKeyboardButton("🔙 رجوع", callback_data="MENU-MAIN")]
                ])
            )
        except Exception as e:
            await update.message.reply_text(
                f"❌ *حدث خطأ أثناء الحفظ:*\n`{type(e).__name__}: {e}`",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 رجوع", callback_data="MENU-MAIN")]
                ])
            )
        return True

    return False
