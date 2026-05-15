import gspread
from google.oauth2.service_account import Credentials
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import os, re, json
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_NAME   = "amin_alsir_cases_new_V2"
CLIENTS_TAB  = "Clients"

def get_sheet():
    creds_json = os.environ.get("GOOGLE_CREDENTIALS")
    creds_dict = json.loads(creds_json)
    creds  = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    sh     = client.open(SHEET_NAME)
    try:
        ws = sh.worksheet(CLIENTS_TAB)
    except:
        ws = sh.add_worksheet(title=CLIENTS_TAB, rows=1000, cols=20)
        ws.append_row(["كود العميل","الاسم","الرقم القومي","الموبايل","العنوان","تاريخ التسجيل"])
    return ws

def generate_client_code(ws):
    records = ws.get_all_records()
    return f"Cl-{len(records)+1:03d}"

STEPS = ["name","national_id","mobile","address"]
PROMPTS = {
    "name":        "👤 أدخل *اسم العميل* كاملاً:",
    "national_id": "🪪 أدخل *الرقم القومي* (14 رقم):",
    "mobile":      "📱 أدخل *رقم الموبايل* (01XXXXXXXXX):",
    "address":     "🏠 أدخل *عنوان العميل*:",
}

async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        context.user_data.clear()
        context.user_data["f001_step"] = "name"
        context.user_data["f001_data"] = {}
        await query.edit_message_text(
            "➕ *إضافة عميل جديد*\n\n" + PROMPTS["name"],
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ إلغاء", callback_data="MENU-MAIN")
            ]])
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("f001_step")
    data = context.user_data.setdefault("f001_data", {})
    text = update.message.text.strip()
    chat_id = update.effective_chat.id

    cancel_btn = InlineKeyboardMarkup([[
        InlineKeyboardButton("❌ إلغاء", callback_data="MENU-MAIN")
    ]])

    if step == "name":
        if len(text) < 3:
            await update.message.reply_text("❌ الاسم قصير جداً. أدخل الاسم كاملاً:", reply_markup=cancel_btn)
            return
        data["name"] = text
        context.user_data["f001_step"] = "national_id"
        await update.message.reply_text(PROMPTS["national_id"], parse_mode="Markdown", reply_markup=cancel_btn)

    elif step == "national_id":
        if not re.match(r'^\d{14}$', text):
            await update.message.reply_text("❌ الرقم القومي يجب أن يكون 14 رقماً:", reply_markup=cancel_btn)
            return
        data["national_id"] = text
        context.user_data["f001_step"] = "mobile"
        await update.message.reply_text(PROMPTS["mobile"], parse_mode="Markdown", reply_markup=cancel_btn)

    elif step == "mobile":
        if not re.match(r'^01[0-9]{9}$', text):
            await update.message.reply_text("❌ رقم الموبايل غير صحيح. أدخل رقماً بصيغة 01XXXXXXXXX:", reply_markup=cancel_btn)
            return
        data["mobile"] = text
        context.user_data["f001_step"] = "address"
        await update.message.reply_text(PROMPTS["address"], parse_mode="Markdown", reply_markup=cancel_btn)

    elif step == "address":
        if len(text) < 3:
            await update.message.reply_text("❌ العنوان قصير جداً:", reply_markup=cancel_btn)
            return
        data["address"] = text

        try:
            ws  = get_sheet()
            code = generate_client_