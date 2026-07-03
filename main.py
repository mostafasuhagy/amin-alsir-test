from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
from routines import *
from primitives import *
from datetime import datetime
import time
import base64

# ═══════════════════════════════════════
# Paymob Webhook — مكتبات إضافية
# ═══════════════════════════════════════
import hmac
import hashlib
import threading
import asyncio
import json
import requests
from flask import Flask, request, jsonify

TOKEN = os.environ.get("BOT_TOKEN", "")
BOSS_CHAT_ID = int(os.environ.get("BOSS_CHAT_ID", "8653723225"))  # v2.1

EXISTING_TENANT_STATUSES = {"trial", "pending_payment", "active"}

PAYMOB_API_KEY         = os.environ.get("PAYMOB_API_KEY", "")
PAYMOB_SECRET_KEY      = os.environ.get("PAYMOB_SECRET_KEY", "")
PAYMOB_PUBLIC_KEY      = os.environ.get("PAYMOB_PUBLIC_KEY", "")
PAYMOB_HMAC            = os.environ.get("PAYMOB_HMAC", "")
PAYMOB_INTEGRATION_ID  = os.environ.get("PAYMOB_INTEGRATION_ID", "")
SUBSCRIPTION_MONTHLY   = float(os.environ.get("SUBSCRIPTION_MONTHLY", "135"))
SUBSCRIPTION_YEARLY    = float(os.environ.get("SUBSCRIPTION_YEARLY", "1200"))
PAYMOB_INTENTION_URL   = "https://accept.paymob.com/v1/intention/"


def create_payment_link(tenant_code: str, billing_cycle: str, office_name: str = ""):
    amount_egp = SUBSCRIPTION_MONTHLY if billing_cycle == "monthly" else SUBSCRIPTION_YEARLY
    amount_cents = int(round(amount_egp * 100))

    payload = {
        "amount": amount_cents,
        "currency": "EGP",
        "payment_methods": [int(PAYMOB_INTEGRATION_ID)] if PAYMOB_INTEGRATION_ID else ["card"],
        "items": [
            {
                "name": f"اشتراك أمين السر - {billing_cycle}",
                "amount": amount_cents,
                "description": f"Tenant: {tenant_code}",
                "quantity": 1,
            }
        ],
        "billing_data": {
            "apartment": "NA", "floor": "NA", "street": "NA",
            "building": "NA", "shipping_method": "NA",
            "postal_code": "NA", "city": "NA", "country": "EG",
            "state": "NA",
            "first_name": office_name or "Tenant",
            "last_name": tenant_code,
            "email": f"{tenant_code}@aminalserr.com",
            "phone_number": "+201000000000",
        },
        "extras": {
            "tenant_code": tenant_code,
            "billing_cycle": billing_cycle,
        },
    }

    headers = {
        "Authorization": f"Token {PAYMOB_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(PAYMOB_INTENTION_URL, json=payload, headers=headers, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        print(f"📦 Paymob intention FULL response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        client_secret = data.get("client_secret")
        if not client_secret:
            print(f"❌ Paymob intention response missing client_secret: {data}")
            return None
        return f"https://accept.paymob.com/unifiedcheckout/?publicKey={PAYMOB_PUBLIC_KEY}&clientSecret={client_secret}"
    except Exception as e:
        print(f"❌ create_payment_link error: {e}")
        return None


flask_app = Flask(__name__)


def verify_hmac(data: dict, received_hmac: str) -> bool:
    ordered_fields = [
        "amount_cents", "created_at", "currency", "error_occured",
        "has_parent_transaction", "id", "integration_id", "is_3d_secure",
        "is_auth", "is_capture", "is_refunded", "is_standalone_payment",
        "is_voided", "order.id", "owner", "pending", "source_data.pan",
        "source_data.sub_type", "source_data.type", "success",
    ]

    def get_nested(d, key):
        if "." in key:
            parent, child = key.split(".", 1)
            return d.get(parent, {}).get(child, "")
        return d.get(key, "")

    concatenated = "".join(str(get_nested(data, f)) for f in ordered_fields)

    calculated_hmac = hmac.new(
        PAYMOB_HMAC.encode("utf-8"),
        concatenated.encode("utf-8"),
        hashlib.sha512,
    ).hexdigest()

    return hmac.compare_digest(calculated_hmac, received_hmac or "")


@flask_app.route("/webhook/paymob", methods=["POST"])
def paymob_webhook():
    try:
        payload = request.get_json(force=True)
        print("═" * 50)
        print("📦 PAYMOB WEBHOOK — FULL PAYLOAD RECEIVED:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("═" * 50)

        obj = payload.get("obj", {})

        received_hmac = request.args.get("hmac", "")
        if not verify_hmac(obj, received_hmac):
            print("❌ Webhook HMAC mismatch — تجاهلنا الطلب (ممكن يكون مزوّر)")
            return jsonify({"status": "invalid_hmac"}), 400

        success = obj.get("success", False)
        extras = obj.get("payment_key_claims", {}).get("extra", {}) or obj.get("order", {}).get("extras", {})
        tenant_code = extras.get("tenant_code", "")
        billing_cycle = extras.get("billing_cycle", "")

        if success and tenant_code:
            activate_tenant(tenant_code, billing_cycle)
            print(f"✅ Webhook: تم تفعيل {tenant_code} ({billing_cycle})")
        else:
            print(f"⚠️ Webhook: دفع غير ناجح أو tenant_code مفقود — {obj.get('id')}")

        return jsonify({"status": "received"}), 200

    except Exception as e:
        print(f"❌ paymob_webhook error: {e}")
        return jsonify({"status": "error"}), 500


def activate_tenant(tenant_code: str, billing_cycle: str):
    try:
        records = P005("Tenants")
        for i, r in enumerate(records, start=2):
            if str(r.get("tenant_code", "")).strip() == str(tenant_code).strip():
                P004("Tenants", i, 9, "active")  # العمود I = status
                chat_id = r.get("chat_id", "")
                if chat_id:
                    send_telegram_message_sync(
                        chat_id,
                        "✅ *تم تفعيل اشتراكك بنجاح!*\n\nمرحباً بك في أمين السر 🏛️",
                    )
                break
    except Exception as e:
        print(f"❌ activate_tenant error: {e}")


def send_telegram_message_sync(chat_id, text: str):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": int(chat_id),
            "text": text,
            "parse_mode": "Markdown",
        }, timeout=10)
    except Exception as e:
        print(f"❌ send_telegram_message_sync error: {e}")


def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

ROUTE_MAP = {
    "F-001": F001,
    "F-002": F002,
    "F-003": F003,
    "F-004": RT001,
    "F-005": RE001,
    "F-006": RE002,
    "F-007": RS001,
    "F-008": RD002,
    "F-009": RM001,
    "F-010": RE003,
    "A-001": RA001,
    "A-002": RA002,
    "T-002": RT002,
    "T-003": RT003,
    "T-004": RT004,
    "S-002": RS002,
    "S-003": RS003,
    "M-002": RM002,
    "N-001": RN001,
    "N-002": RN002,
    "N-003": RN003,
    "D-001": RD001,
    "D-003": RD003,
    "D-004": RD004,
    "D-005": RD005,
    "D-006": RD006,
}

def get_boss_id(context):
    tenant = context.user_data.get("tenant", {})
    boss = tenant.get("boss_chat_id", "")
    if boss:
        try:
            return int(boss)
        except:
            pass
    return BOSS_CHAT_ID

def get_tenant_sheet(context, chat_id):
    tenant = context.user_data.get("tenant", {})
    sheet_name = tenant.get("sheet_name", "")
    if sheet_name:
        return sheet_name

    if chat_id:
        reloaded = MT001(chat_id)
        if reloaded:
            context.user_data["tenant"] = reloaded
            reloaded_name = reloaded.get("sheet_name", "")
            if reloaded_name:
                return reloaded_name

    return SHEET_NAME

def build_boss_dashboard_url(chat_id, tenant):
    token = base64.b64encode(str(chat_id).encode()).decode()
    sheet_id = tenant.get("sheet_id", "")
    return f"https://aminalserr.com/amin_alsir_dashboard.html?t={token}&sid={sheet_id}"

# ═══════════════════════════════════════
# فحص الاشتراك قبل أي عملية حساسة
# ═══════════════════════════════════════
async def check_subscription_or_block(update, context, chat_id) -> bool:
    """
    True = مسموح بالاستمرار. False = اتبعتت رسالة منع، يوقف الكولر فورًا.
    """
    result = MT008(chat_id)

    if result["valid"]:
        tenant = result.get("tenant") or {}
        days_left = result.get("days_left")
        if days_left is not None and days_left <= 2 and str(tenant.get("reminder_sent", "")).lower() != "yes":
            billing_cycle = tenant.get("billing_cycle", "") or "monthly"
            pay_link = create_payment_link(
                tenant.get("tenant_code", ""), billing_cycle, tenant.get("office_name", "")
            )
            period_label = "فترتك التجريبية" if result["status"] == "trial" else "اشتراكك"
            warn_text = f"⚠️ *تنبيه*\n\nباقي {days_left} يوم على انتهاء {period_label}."
            if pay_link:
                kb = InlineKeyboardMarkup([[InlineKeyboardButton("💳 اشترك دلوقتي", url=pay_link)]])
                await context.bot.send_message(chat_id=chat_id, text=warn_text, parse_mode="Markdown", reply_markup=kb)
            else:
                await context.bot.send_message(chat_id=chat_id, text=warn_text, parse_mode="Markdown")
            _mark_reminder_sent(chat_id)
        return True

    status = result["status"]
    tenant = result.get("tenant") or {}

    if status in ("trial_expired", "subscription_expired"):
        billing_cycle = tenant.get("billing_cycle", "") or "monthly"
        pay_link = create_payment_link(
            tenant.get("tenant_code", ""), billing_cycle, tenant.get("office_name", "")
        )
        label = "انتهت فترتك التجريبية" if status == "trial_expired" else "انتهى اشتراكك"
        text = f"⏰ *{label}*\n\nللاستمرار في استخدام أمين السر، يرجى الاشتراك."
        if pay_link:
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("💳 اشترك الآن", url=pay_link)]])
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown", reply_markup=kb)
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=text + "\n\n(تعذر توليد رابط الدفع، تواصل مع الدعم)",
                parse_mode="Markdown",
            )
    elif status == "pending_payment":
        await context.bot.send_message(
            chat_id=chat_id,
            text="⏳ حسابك في انتظار تأكيد الدفع. أرسل /start لمتابعة الدفع.",
            parse_mode="Markdown",
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ تعذر التحقق من حالة اشتراكك. تواصل مع الدعم.",
        )
    return False

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
        [InlineKeyboardButton("✅ موافقة على مستند", callback_data="D-003")],
        [InlineKeyboardButton("❌ رفض مستند",        callback_data="D-004")],
        [InlineKeyboardButton("📂 عرض مستندات",      callback_data="D-005")],
        [InlineKeyboardButton("🗄️ أرشفة مستندات",   callback_data="D-006")],
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

def countries_keyboard():
    countries = [
        "مصر", "السعودية", "الإمارات", "الكويت",
        "قطر", "البحرين", "الأردن", "لبنان",
        "المغرب", "تونس", "الجزائر", "ليبيا",
        "العراق", "سوريا", "اليمن", "عمان",
        "السودان", "فلسطين",
    ]
    rows = []
    for i in range(0, len(countries), 2):
        row = [InlineKeyboardButton(countries[i], callback_data=f"COUNTRY-{countries[i]}")]
        if i + 1 < len(countries):
            row.append(InlineKeyboardButton(countries[i+1], callback_data=f"COUNTRY-{countries[i+1]}"))
        rows.append(row)
    return InlineKeyboardMarkup(rows)

async def post_init(application):
    await application.bot.delete_webhook(drop_pending_updates=True)
    print("✅ Webhook deleted — bot started clean")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    print(f"🆔 CHAT ID: {chat_id}")

    args = context.args
    if args:
        param = args[0]

        if param.startswith("client_"):
            parts = param.replace("client_", "").split("_")
            if len(parts) < 2:
                await update.message.reply_text("❌ رابط غير صحيح. تواصل مع المكتب.")
                return
            tenant_code, ref_code = parts[0], "_".join(parts[1:])

            tenant_row = P002("Tenants", tenant_code, TENANTS_SHEET)
            if not tenant_row:
                await update.message.reply_text("❌ المكتب غير موجود. تواصل مع المكتب.")
                return
            sheet_name = tenant_row.get("sheet_name", "")
            sheet_id = tenant_row.get("sheet_id", "")
            boss_id = tenant_row.get("boss_chat_id", "") or BOSS_CHAT_ID

            client = P002("Clients", ref_code, sheet_name)
            if client:
                records = P005("Clients", sheet_name)
                for i, r in enumerate(records, start=2):
                    if str(list(r.values())[0]).strip().lower() == str(ref_code).strip().lower():
                        P004("Clients", i, 8, str(chat_id), sheet_name)
                        break
                await update.message.reply_text(
                    f"✅ *تم ربط حسابك بنجاح!*\n\n"
                    f"👤 {client.get('client_name', '')}\n"
                    f"🔹 الكود: `{ref_code}`\n\n"
                    f"ستصلك إشعارات مكتب المحاماة هنا مباشرة.",
                    parse_mode="Markdown"
                )
                token = base64.b64encode(str(chat_id).encode()).decode()
                # ── إضافة client_code (c) صراحة في الرابط ──
                # هذا يمنع أي التباس لو نفس حساب التليجرام مرتبط
                # بأكثر من عميل (كحالة اختبار)، ويجعل الداشبورد يتعرف
                # على العميل الصحيح بشكل مؤكد بدل الاعتماد على chat_id فقط.
                dashboard_url = f"https://aminalserr.com/amin_alsir_client_dashboard.html?t={token}&sid={sheet_id}&c={ref_code}"
                await update.message.reply_text(
                    f"🔗 <b>رابط لوحة القيادة الخاصة بك:</b>\n<a href=\"{dashboard_url}\">{dashboard_url}</a>\n\n📌 احفظ هذا الرابط في مفضلاتك",
                    parse_mode="HTML"
                )
                await context.bot.send_message(
                    chat_id=boss_id,
                    text=f"🔔 *إشعار — أمين السر*\n\n📱 عميل ربط حسابه بالبوت\n👤 {client.get('client_name','')}\n🔹 {ref_code}",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text("❌ كود العميل غير صحيح. تواصل مع المكتب.")
            return

        elif param.startswith("assistant_"):
            parts = param.replace("assistant_", "").split("_")
            if len(parts) < 2:
                await update.message.reply_text("❌ رابط غير صحيح. تواصل مع المكتب.")
                return
            tenant_code, ref_code = parts[0], "_".join(parts[1:])

            tenant_row = P002("Tenants", tenant_code, TENANTS_SHEET)
            if not tenant_row:
                await update.message.reply_text("❌ المكتب غير موجود. تواصل مع المكتب.")
                return
            sheet_name = tenant_row.get("sheet_name", "")
            sheet_id = tenant_row.get("sheet_id", "")
            boss_id = tenant_row.get("boss_chat_id", "") or BOSS_CHAT_ID

            assistant = P002("Assistants", ref_code, sheet_name)
            if assistant:
                records = P005("Assistants", sheet_name)
                for i, r in enumerate(records, start=2):
                    if str(list(r.values())[0]).strip().lower() == str(ref_code).strip().lower():
                        P004("Assistants", i, 6, str(chat_id), sheet_name)
                        break
                await update.message.reply_text(
                    f"✅ *تم ربط حسابك بنجاح!*\n\n"
                    f"👥 {assistant.get('assistant_name', '')}\n"
                    f"🔹 الكود: `{ref_code}`\n\n"
                    f"ستصلك مهامك ومستجدات المكتب هنا مباشرة.",
                    parse_mode="Markdown"
                )
                token = base64.b64encode(str(chat_id).encode()).decode()
                # ── إضافة assistant_code (c) صراحة في الرابط ──
                # نفس منطق حماية لوحة العميل، لتفادي أي التباس بين المساعدين.
                dashboard_url = f"https://aminalserr.com/amin_alsir_assistant_dashboard.html?t={token}&sid={sheet_id}&c={ref_code}"
                await update.message.reply_text(
                    f"🔗 <b>رابط لوحة القيادة الخاصة بك:</b>\n<a href=\"{dashboard_url}\">{dashboard_url}</a>\n\n📌 احفظ هذا الرابط في مفضلاتك",
                    parse_mode="HTML"
                )
                await context.bot.send_message(
                    chat_id=boss_id,
                    text=f"🔔 *إشعار — أمين السر*\n\n📱 مساعد ربط حسابه بالبوت\n👥 {assistant.get('assistant_name','')}\n🔹 {ref_code}",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text("❌ كود المساعد غير صحيح. تواصل مع المكتب.")
            return

        elif param.startswith("plan_"):
            billing_cycle = param.replace("plan_", "")
            if billing_cycle not in ("monthly", "yearly"):
                billing_cycle = "monthly"

            context.user_data["selected_billing_cycle"] = billing_cycle
            cycle_label = "شهري" if billing_cycle == "monthly" else "سنوي (الباقة الذهبية)"

            tenant = MT001(chat_id)
            if tenant and tenant.get("status") in EXISTING_TENANT_STATUSES:
                office_name = tenant.get("office_name", "المكتب")
                country = tenant.get("country", "مصر")
                context.user_data["tenant"] = tenant
                dashboard_url = build_boss_dashboard_url(chat_id, tenant)
                await update.message.reply_text(
                    f"أهلاً بك مجدداً في <b>أمين السر</b> 🏛️\n\n"
                    f"🏢 {office_name}\n"
                    f"🌍 {country}\n\n"
                    f"🔗 لوحة القيادة الكاملة:\n<a href=\"{dashboard_url}\">{dashboard_url}</a>\n\n"
                    f"اختر من لوحة القيادة:",
                    parse_mode="HTML",
                    reply_markup=main_keyboard()
                )
            else:
                context.user_data["routine"] = "REG"
                context.user_data["step"] = "office_name"
                context.user_data["data"] = {}
                await update.message.reply_text(
                    f"🏛️ *أهلاً بك في أمين السر!*\n\n"
                    f"✅ تم تسجيل اختيارك: *الباقة {cycle_label}*\n\n"
                    f"نظام إدارة مكتب المحاماة للوطن العربي 🌍\n\n"
                    f"للبدء، أدخل *اسم مكتبك*:",
                    parse_mode="Markdown"
                )
            return

    tenant = MT001(chat_id)

    if tenant and tenant.get("status") in EXISTING_TENANT_STATUSES:
        office_name = tenant.get("office_name", "المكتب")
        country = tenant.get("country", "مصر")
        context.user_data["tenant"] = tenant
        dashboard_url = build_boss_dashboard_url(chat_id, tenant)
        await update.message.reply_text(
            f"أهلاً بك في <b>أمين السر</b> 🏛️\n\n"
            f"🏢 {office_name}\n"
            f"🌍 {country}\n\n"
            f"🔗 لوحة القيادة الكاملة:\n<a href=\"{dashboard_url}\">{dashboard_url}</a>\n\n"
            f"اختر من لوحة القيادة:",
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )
    else:
        context.user_data["routine"] = "REG"
        context.user_data["step"] = "office_name"
        context.user_data["data"] = {}
        await update.message.reply_text(
            "🏛️ *أهلاً بك في أمين السر!*\n\n"
            "نظام إدارة مكتب المحاماة للوطن العربي 🌍\n\n"
            "للبدء، أدخل *اسم مكتبك*:",
            parse_mode="Markdown"
        )

async def testpay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    test_tenant_code = "TEST-001"
    await update.message.reply_text("⏳ بطلب رابط دفع تجريبي من Paymob...")
    link = create_payment_link(test_tenant_code, "monthly", "مكتب تجريبي")
    if link:
        await update.message.reply_text(
            f"✅ *تم إنشاء رابط الدفع التجريبي!*\n\n"
            f"🔹 Tenant Code: `{test_tenant_code}`\n"
            f"🔗 {link}\n\n"
            f"دوس على الرابط وجرّب الدفع ببيانات كارت تجريبي من Paymob.",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ فشل إنشاء رابط الدفع. شوف الـ Logs على Railway لمعرفة السبب.")

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

    if routine == "REG":
        if step == "office_name":
            if not V001(text):
                await T001(context, chat_id, "❌ الاسم قصير. أدخل اسم المكتب كاملاً:")
                return
            data["office_name"] = text
            context.user_data["step"] = "country"
            await update.message.reply_text(
                f"✅ اسم المكتب: *{text}*\n\n🌍 اختر *دولتك*:",
                parse_mode="Markdown",
                reply_markup=countries_keyboard()
            )

    elif routine == "F001":
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
            sheet_name = get_tenant_sheet(context, chat_id)
            tenant_code = context.user_data.get("tenant", {}).get("tenant_code", "")
            code = G001("Cl", "Clients", sheet_name)
            ok = P003("Clients", [code, data["name"], data["national_id"], data["mobile"], data["address"], datetime.now().strftime("%Y-%m-%d %H:%M")], sheet_name)
            context.user_data.clear()
            if ok:
                client_link = f"https://t.me/amin_alsir_bot?start=client_{tenant_code}_{code}"
                share_text = f"رابط ربط حسابك بمكتبنا على أمين السر:\n{client_link}"
                share_url = f"https://t.me/share/url?url={client_link}&text={share_text}"
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"✅ *تم إضافة العميل!*\n\n🔹 الكود: `{code}`\n👤 {data['name']}\n📱 {data['mobile']}",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📤 مشاركة الرابط مع العميل", url=share_url)],
                        [InlineKeyboardButton("🔙 القائمة", callback_data="MENU-MAIN")],
                    ])
                )
                await N001(context, get_boss_id(context), f"👤 عميل جديد: {data['name']}\n🔹 الكود: {code}")
            else:
                await T001(context, chat_id, "❌ حدث خطأ في الحفظ.")

    elif routine == "F002":
        if step == "code":
            sheet_name = get_tenant_sheet(context, chat_id)
            client = P002("Clients", text, sheet_name)
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

    elif routine == "F003":
        if step == "code":
            sheet_name = get_tenant_sheet(context, chat_id)
            client = P002("Clients", text, sheet_name)
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
        elif step == "edit_name":
            if not V001(text):
                await T001(context, chat_id, "❌ الاسم قصير:")
                return
            sheet_name = get_tenant_sheet(context, chat_id)
            client_code = data.get("client_code")
            records = P005("Clients", sheet_name)
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(client_code):
                    P004("Clients", i, 2, text, sheet_name)
                    break
            context.user_data.clear()
            await T002(context, chat_id, f"✅ *تم تعديل الاسم!*\n\n👤 {text}", back_btn)
            await N001(context, get_boss_id(context), f"✏️ تعديل عميل {client_code}\n👤 الاسم الجديد: {text}")
        elif step == "edit_mobile":
            if not V003(text):
                await T001(context, chat_id, "❌ رقم الموبايل غير صحيح:")
                return
            sheet_name = get_tenant_sheet(context, chat_id)
            client_code = data.get("client_code")
            records = P005("Clients", sheet_name)
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(client_code):
                    P004("Clients", i, 4, text, sheet_name)
                    break
            context.user_data.clear()
            await T002(context, chat_id, f"✅ *تم تعديل الموبايل!*\n\n📱 {text}", back_btn)
            await N001(context, get_boss_id(context), f"✏️ تعديل عميل {client_code}\n📱 الموبايل الجديد: {text}")
        elif step == "edit_address":
            if not V001(text):
                await T001(context, chat_id, "❌ العنوان قصير:")
                return
            sheet_name = get_tenant_sheet(context, chat_id)
            client_code = data.get("client_code")
            records = P005("Clients", sheet_name)
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(client_code):
                    P004("Clients", i, 5, text, sheet_name)
                    break
            context.user_data.clear()
            await T002(context, chat_id, f"✅ *تم تعديل العنوان!*\n\n🏠 {text}", back_btn)
            await N001(context, get_boss_id(context), f"✏️ تعديل عميل {client_code}\n🏠 العنوان الجديد: {text}")

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
            sheet_name = get_tenant_sheet(context, chat_id)
            tenant_code = context.user_data.get("tenant", {}).get("tenant_code", "")
            code = G001("As", "Assistants", sheet_name)
            ok = P003("Assistants", [code, data["name"], data["bar_number"], data["mobile"], datetime.now().strftime("%Y-%m-%d %H:%M")], sheet_name)
            context.user_data.clear()
            if ok:
                assistant_link = f"https://t.me/amin_alsir_bot?start=assistant_{tenant_code}_{code}"
                share_text = f"رابط ربط حسابك كمساعد بمكتبنا على أمين السر:\n{assistant_link}"
                share_url = f"https://t.me/share/url?url={assistant_link}&text={share_text}"
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"✅ *تم إضافة المساعد!*\n\n🔹 الكود: `{code}`\n👤 {data['name']}\n🔢 {data['bar_number']}\n📱 {data['mobile']}",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📤 مشاركة الرابط مع المساعد", url=share_url)],
                        [InlineKeyboardButton("🔙 القائمة", callback_data="MENU-MAIN")],
                    ])
                )
                await N001(context, get_boss_id(context), f"👥 مساعد جديد: {data['name']}\n🔹 الكود: {code}")
            else:
                await T001(context, chat_id, "❌ حدث خطأ.")

    elif routine == "RA002":
        if step == "code":
            sheet_name = get_tenant_sheet(context, chat_id)
            assistant = P002("Assistants", text, sheet_name)
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

    elif routine == "RT001":
        if step == "client_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            client = P002("Clients", text, sheet_name)
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
            sheet_name = get_tenant_sheet(context, chat_id)
            code = G001("Tp", "Topics", sheet_name)
            # ترتيب الأعمدة هنا لازم يطابق عناوين شيت Topics الفعلية بالظبط:
            # topic_code | client_code | client_name | service_code | service_name |
            # assistant_code | assistant_name | date_opened | status | notes
            ok = P003("Topics", [
                code,                     # A topic_code
                data["client_code"],      # B client_code
                data["client_name"],      # C client_name
                "",                       # D service_code (غير مستخدم حاليًا)
                data["title"],            # E service_name (عنوان الموضوع)
                "",                       # F assistant_code (غير مستخدم حاليًا)
                "",                       # G assistant_name (غير مستخدم حاليًا)
                datetime.now().strftime("%Y-%m-%d %H:%M"),  # H date_opened
                "جديد",                   # I status
                data["event_type"],       # J notes (نوع الموضوع)
            ], sheet_name)
            context.user_data.clear()
            if ok:
                await T002(context, chat_id, f"✅ *تم إضافة الموضوع!*\n\n🔹 الكود: `{code}`\n📋 {data['title']}\n👤 {data['client_name']}", back_btn)
                await N001(context, get_boss_id(context), f"📁 موضوع جديد: {data['title']}\n🔹 الكود: {code}\n👤 العميل: {data['client_name']}")
            else:
                await T001(context, chat_id, "❌ حدث خطأ.")

    elif routine == "RT002":
        if step == "client_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            topics = P006("Topics", "client_code", text, sheet_name)
            context.user_data.clear()
            if not topics:
                await T002(context, chat_id, "❌ لا توجد موضوعات لهذا العميل.", back_btn)
                return
            msg = f"📋 *موضوعات العميل* `{text}`:\n\n"
            for t in topics:
                msg += f"🔹 `{t.get('topic_code','—')}` — {t.get('service_name', t.get('title','—'))} [{t.get('status','—')}]\n"
            await T002(context, chat_id, msg, back_btn)

    elif routine == "RT003":
        if step == "topic_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            topic = P002("Topics", text, sheet_name)
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

    elif routine == "RT004":
        if step == "topic_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            topic = P002("Topics", text, sheet_name)
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
            sheet_name = get_tenant_sheet(context, chat_id)
            code = G001("Ev", "Events", sheet_name)
            ok = P003("Events", [code, data["event_date"], data["topic_code"], data["client_name"], data["event_type"], data["event_time"], data["location"]], sheet_name)
            context.user_data.clear()
            if ok:
                await T002(context, chat_id, f"✅ *تم إضافة الحدث!*\n\n🔹 الكود: `{code}`\n📅 {data['event_date']} — {data['event_type']}\n📍 {data['location']}", back_btn)
                await N001(context, get_boss_id(context), f"📅 حدث جديد: {data['event_type']}\n📅 {data['event_date']} — {data['location']}\n👤 {data['client_name']}")
            else:
                await T001(context, chat_id, "❌ حدث خطأ.")

    elif routine == "RE002":
        if step == "event_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            event = P002("Events", text, sheet_name)
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
            sheet_name = get_tenant_sheet(context, chat_id)
            records = P005("Events", sheet_name)
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(data["event_code"]):
                    P004("Events", i, 8, text, sheet_name)
                    P004("Events", i, 9, "منتهي", sheet_name)
                    break
            context.user_data.clear()
            await T002(context, chat_id, f"✅ *تم تسجيل النتيجة!*\n\n📝 {data['result']}", back_btn)

    elif routine == "RS001":
        if step == "topic_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            topic = P002("Topics", text, sheet_name)
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
            sheet_name = get_tenant_sheet(context, chat_id)
            code = G001("Sh", "Shipments", sheet_name)
            ok = P003("Shipments", [
                code, data["topic_code"], data["description"],
                "", datetime.now().strftime("%Y-%m-%d %H:%M"),
                "", "", "", "صادر",
            ], sheet_name)
            context.user_data.clear()
            if ok:
                await T002(context, chat_id, f"✅ *تم تسجيل الشحنة!*\n\n🔹 الكود: `{code}`\n📦 {data['description']}", back_btn)
            else:
                await T001(context, chat_id, "❌ حدث خطأ.")

    elif routine == "RS002":
        if step == "shipment_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            shipment = P002("Shipments", text, sheet_name)
            if not shipment:
                await T002(context, chat_id, "❌ رقم الشحنة غير موجود.", back_btn)
                context.user_data.clear()
                return
            data["shipment_code"] = text
            records = P005("Shipments", sheet_name)
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(text):
                    P004("Shipments", i, 9, "مستلم", sheet_name)
                    P004("Shipments", i, 10, datetime.now().strftime("%Y-%m-%d %H:%M"), sheet_name)
                    break
            context.user_data.clear()
            await T002(context, chat_id, f"✅ *تم تسجيل استلام الشحنة!*\n\n🔹 الكود: `{text}`\n📦 {shipment.get('sender','—')}", back_btn)

    elif routine == "RS003":
        if step == "shipment_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            shipment = P002("Shipments", text, sheet_name)
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
            sheet_name = get_tenant_sheet(context, chat_id)
            code = G001("Doc", "Documents", sheet_name)
            ok = P003("Documents", [code, data["entity"], data["description"], "طلب", datetime.now().strftime("%Y-%m-%d %H:%M")], sheet_name)
            context.user_data.clear()
            if ok:
                await T002(context, chat_id, f"✅ *تم تسجيل الطلب!*\n\n🔹 الكود: `{code}`\n📄 من: {data['entity']}", back_btn)
            else:
                await T001(context, chat_id, "❌ حدث خطأ.")

    elif routine == "RD003":
        if step == "doc_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            doc = P002("Documents", text, sheet_name)
            if not doc:
                await T002(context, chat_id, "❌ كود المستند غير موجود.", back_btn)
                context.user_data.clear()
                return
            records = P005("Documents", sheet_name)
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(text):
                    P004("Documents", i, 6, "موافق عليه", sheet_name)
                    break
            context.user_data.clear()
            await T002(context, chat_id, f"✅ *تمت الموافقة على المستند!*\n\n🔹 الكود: `{text}`\n📄 {doc.get('doc_name','—')}", back_btn)
            await N001(context, get_boss_id(context), f"✅ موافقة على مستند\n🔹 الكود: {text}\n📄 {doc.get('doc_name','—')}")

    elif routine == "RD004":
        if step == "doc_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            doc = P002("Documents", text, sheet_name)
            if not doc:
                await T002(context, chat_id, "❌ كود المستند غير موجود.", back_btn)
                context.user_data.clear()
                return
            data["doc_code"] = text
            data["doc_name"] = doc.get("doc_name", "—")
            context.user_data["step"] = "reason"
            await T002(context, chat_id, f"📄 المستند: *{data['doc_name']}*\n\n📝 أدخل *سبب الرفض*:", cancel_btn)
        elif step == "reason":
            if not V001(text):
                await T001(context, chat_id, "❌ السبب قصير:")
                return
            sheet_name = get_tenant_sheet(context, chat_id)
            records = P005("Documents", sheet_name)
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(data["doc_code"]):
                    P004("Documents", i, 6, "مرفوض", sheet_name)
                    P004("Documents", i, 7, text, sheet_name)
                    break
            context.user_data.clear()
            await T002(context, chat_id, f"✅ *تم رفض المستند!*\n\n🔹 الكود: `{data['doc_code']}`\n📝 السبب: {text}", back_btn)
            await N001(context, get_boss_id(context), f"❌ رفض مستند\n🔹 الكود: {data['doc_code']}\n📝 السبب: {text}")

    elif routine == "RD005":
        if step == "topic_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            docs = P006("Documents", "topic_code", text, sheet_name)
            context.user_data.clear()
            if not docs:
                await T002(context, chat_id, "❌ لا توجد مستندات لهذا الموضوع.", back_btn)
                return
            msg = f"📁 *مستندات الموضوع* `{text}`:\n\n"
            for d in docs:
                link = d.get("drive_link", "")
                name = d.get("doc_name", "—")
                status = d.get("status", "—")
                if link:
                    msg += f"🔹 [{name}]({link}) — {status}\n"
                else:
                    msg += f"🔹 {name} — {status}\n"
            await T002(context, chat_id, msg, back_btn)

    elif routine == "RD006":
        if step == "topic_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            docs = P006("Documents", "topic_code", text, sheet_name)
            if not docs:
                await T002(context, chat_id, "❌ لا توجد مستندات لهذا الموضوع.", back_btn)
                context.user_data.clear()
                return
            data["topic_code"] = text
            data["doc_count"] = len(docs)
            context.user_data["step"] = "confirm"
            await T002(context, chat_id,
                f"🗄️ الموضوع: `{text}`\n📄 عدد المستندات: {len(docs)}\n\nهل تريد أرشفة كل المستندات؟",
                [
                    [{"text": "✅ تأكيد الأرشفة", "callback_data": "ARCHIVE-DOCS-CONFIRM"}],
                    [{"text": "❌ إلغاء",          "callback_data": "MENU-MAIN"}],
                ]
            )

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
            sheet_name = get_tenant_sheet(context, chat_id)
            code = G001("Fn", "Custody", sheet_name)
            ok = P003("Custody", [code, data["amount"], data["reason"], "طلب", datetime.now().strftime("%Y-%m-%d %H:%M")], sheet_name)
            context.user_data.clear()
            if ok:
                await T002(context, chat_id, f"✅ *تم طلب العهدة!*\n\n🔹 الكود: `{code}`\n💰 {data['amount']} جنيه\n📝 {data['reason']}", back_btn)
                await N001(context, get_boss_id(context), f"💰 طلب عهدة جديد\n🔹 الكود: {code}\n💰 المبلغ: {data['amount']} جنيه\n📝 {data['reason']}")
            else:
                await T001(context, chat_id, "❌ حدث خطأ.")

    elif routine == "RM002":
        if step == "fund_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            fund = P002("Custody", text, sheet_name)
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
            sheet_name = get_tenant_sheet(context, chat_id)
            records = P005("Custody", sheet_name)
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(data["fund_code"]):
                    P004("Custody", i, 4, "مسوّاة", sheet_name)
                    P004("Custody", i, 6, text, sheet_name)
                    P004("Custody", i, 7, datetime.now().strftime("%Y-%m-%d %H:%M"), sheet_name)
                    break
            context.user_data.clear()
            await T002(context, chat_id, f"✅ *تم تسوية العهدة!*\n\n🔹 الكود: `{data['fund_code']}`\n💰 {data['amount']} جنيه", back_btn)

    elif routine == "RN001":
        if step == "text":
            if not V001(text):
                await T001(context, chat_id, "❌ النص قصير:")
                return
            await N001(context, get_boss_id(context), text)
            context.user_data.clear()
            await T002(context, chat_id, "✅ *تم إرسال الإشعار للرئيس!*", back_btn)

    elif routine == "RN002":
        if step == "client_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            client = P002("Clients", text, sheet_name)
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

    elif routine == "RN003":
        if step == "assistant_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            assistant = P002("Assistants", text, sheet_name)
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

    elif routine == "RD001":
        if step == "topic_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            topic = P002("Topics", text, sheet_name)
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

async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat_id

    if data.startswith("COUNTRY-"):
        country = data.replace("COUNTRY-", "")
        office_name = context.user_data.get("data", {}).get("office_name", "")

        sheet_name, sheet_id = MT006(office_name, str(chat_id))
        folder_id = MT007(str(chat_id))

        if not sheet_name or not folder_id:
            print(f"FAIL: tenant resources not created for chat_id={chat_id} (sheet_name={sheet_name}, folder_id={folder_id})")
            await query.edit_message_text(
                "حدث خطأ في إنشاء الموارد الخاصة بمكتبك. حاول مرة أخرى لاحقاً."
            )
            return

        billing_cycle = context.user_data.get("selected_billing_cycle", "")
        if billing_cycle:
            initial_status = "pending_payment"
        else:
            initial_status = "trial"

        code = MT002(
            chat_id, office_name, country, chat_id, sheet_name, folder_id,
            status=initial_status, billing_cycle=billing_cycle, sheet_id=sheet_id,
        )

        if code:
            tenant = MT001(chat_id)
            context.user_data.clear()
            context.user_data["tenant"] = tenant

            if initial_status == "pending_payment":
                pay_link = create_payment_link(code, billing_cycle, office_name)
                cycle_label = "شهري" if billing_cycle == "monthly" else "سنوي (الباقة الذهبية)"

                if pay_link:
                    await query.edit_message_text(
                        f"✅ *تم تسجيل مكتبك بنجاح!*\n\n"
                        f"🏢 {office_name}\n"
                        f"🌍 {country}\n"
                        f"🔹 الكود: `{code}`\n"
                        f"📦 الباقة المختارة: {cycle_label}\n\n"
                        f"للمتابعة، يرجى إكمال الدفع عبر الرابط التالي:\n"
                        f"🔗 {pay_link}\n\n"
                        f"بعد إتمام الدفع بنجاح، سيتم تفعيل حسابك فوراً وتلقائياً.",
                        parse_mode="Markdown",
                    )
                else:
                    await query.edit_message_text(
                        f"✅ تم تسجيل مكتبك بنجاح (الكود: `{code}`)\n\n"
                        f"⚠️ حدث خطأ مؤقت في توليد رابط الدفع. "
                        f"يرجى المحاولة مرة أخرى من خلال الأمر /pay أو التواصل مع الدعم.",
                        parse_mode="Markdown",
                    )
            else:
                dashboard_url = build_boss_dashboard_url(chat_id, tenant)
                await query.edit_message_text(
                    f"✅ <b>تم تسجيل مكتبك بنجاح!</b>\n\n"
                    f"🏢 {office_name}\n"
                    f"🌍 {country}\n"
                    f"🔹 الكود: <code>{code}</code>\n\n"
                    f"🎁 لديك <b>{TRIAL_DAYS} أيام مجانية</b> لتجربة النظام بالكامل.\n\n"
                    f"🔗 لوحة القيادة الكاملة:\n<a href=\"{dashboard_url}\">{dashboard_url}</a>\n\n"
                    f"اختر من لوحة القيادة:",
                    parse_mode="HTML",
                    reply_markup=main_keyboard(),
                )

            await context.bot.send_message(
                chat_id=BOSS_CHAT_ID,
                text=(
                    f"🔔 *إشعار — أمين السر*\n\n"
                    f"🏢 مكتب جديد انضم للمنصة!\n"
                    f"🏛️ {office_name}\n"
                    f"🌍 {country}\n"
                    f"🔹 الكود: {code}\n"
                    f"📋 الحالة: {'في انتظار الدفع' if initial_status == 'pending_payment' else 'تجربة مجانية'}"
                ),
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                "❌ حدث خطأ في التسجيل. أرسل /start للمحاولة مرة أخرى."
            )
        return

    if data == "ARCHIVE-DOCS-CONFIRM":
        sheet_name = get_tenant_sheet(context, chat_id)
        topic_code = context.user_data.get("data", {}).get("topic_code", "")
        if topic_code:
            records = P005("Documents", sheet_name)
            for i, r in enumerate(records, start=2):
                if str(r.get("topic_code", "")) == str(topic_code):
                    P004("Documents", i, 6, "مؤرشف", sheet_name)
        context.user_data.clear()
        await query.edit_message_text(
            f"✅ تم أرشفة مستندات الموضوع `{topic_code}`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 القائمة", callback_data="MENU-MAIN")]])
        )
        await N001(context, get_boss_id(context), f"🗄️ تم أرشفة مستندات الموضوع: {topic_code}")
        return

    if data == "ARCHIVE-CONFIRM":
        sheet_name = get_tenant_sheet(context, chat_id)
        topic_code = context.user_data.get("data", {}).get("topic_code", "")
        topic_name = context.user_data.get("data", {}).get("topic_name", "")
        if topic_code:
            records = P005("Topics", sheet_name)
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(topic_code):
                    P004("Topics", i, 9, "مؤرشف", sheet_name)  # عمود I = status
                    break
        context.user_data.clear()
        await query.edit_message_text(
            f"✅ تم أرشفة الموضوع `{topic_code}` — *{topic_name}*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 القائمة", callback_data="MENU-MAIN")]])
        )
        await N001(context, get_boss_id(context), f"🗄️ تم أرشفة الموضوع\n🔹 الكود: {topic_code}\n📋 {topic_name}")
        return

    if data.startswith("STATUS-"):
        sheet_name = get_tenant_sheet(context, chat_id)
        new_status = data.replace("STATUS-", "")
        topic_code = context.user_data.get("data", {}).get("topic_code", "")
        if topic_code:
            records = P005("Topics", sheet_name)
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(topic_code):
                    P004("Topics", i, 9, new_status, sheet_name)  # عمود I = status
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
        context.user_data.pop("routine", None)
        context.user_data.pop("step", None)
        context.user_data.pop("data", None)
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
        if not await check_subscription_or_block(update, context, chat_id):
            return
        await ROUTE_MAP[data](update, context)
    else:
        await query.edit_message_text(
            f"⏳ الكود *{data}* قيد التطوير.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="MENU-MAIN")]])
        )

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

            sheet_name = get_tenant_sheet(context, chat_id)
            folder_id = context.user_data.get("tenant", {}).get("drive_folder_id", "") or DRIVE_FOLDER_ID
            topic_code = data.get("topic_code", "GENERAL")
            drive_link = DRV001(tmp_path, file_name, topic_code, folder_id)
            os.unlink(tmp_path)

            if not drive_link:
                await T002(context, chat_id, "❌ فشل رفع الملف على Drive.", back_btn)
                context.user_data.clear()
                return

            code = G001("Doc", "Documents", sheet_name)
            P003("Documents", [
                code, topic_code, data.get("doc_name", file_name),
                file_name, drive_link, "وارد", "TRANSIT",
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ], sheet_name)

            context.user_data.clear()
            await T002(context, chat_id,
                f"✅ *تم رفع المستند!*\n\n"
                f"🔹 الكود: `{code}`\n"
                f"📄 الاسم: {data.get('doc_name', file_name)}\n"
                f"📋 الموضوع: {topic_code}\n"
                f"🔗 [فتح الملف]({drive_link})",
                back_btn
            )
            await N001(context, get_boss_id(context),
                f"📁 مستند وارد جديد\n🔹 الكود: {code}\n"
                f"📄 {data.get('doc_name', file_name)}\n"
                f"📋 الموضوع: {topic_code}\n🔗 {drive_link}"
            )

        except Exception as e:
            print(f"❌ file_router RD001: {e}")
            await T002(context, chat_id, "❌ حدث خطأ أثناء الرفع.", back_btn)
            context.user_data.clear()

if __name__ == "__main__":
    time.sleep(5)
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("testpay", testpay))  # 🔍 مؤقت — للاختبار فقط
    app.add_handler(CallbackQueryHandler(menu_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, file_router))

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("✅ Flask webhook thread started")

    app.run_polling(drop_pending_updates=True)
