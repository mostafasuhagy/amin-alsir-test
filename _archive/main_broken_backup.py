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

# â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
# Paymob Webhook â€” ظ…ظƒطھط¨ط§طھ ط¥ط¶ط§ظپظٹط©
# â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
import hmac
import hashlib
import threading
import asyncio
import json
import requests
from flask import Flask, request, jsonify

TOKEN = os.environ.get("BOT_TOKEN", "")
BOSS_CHAT_ID = int(os.environ.get("BOSS_CHAT_ID", "8653723225"))  # v2.1

# ط£ظٹ ط­ط§ظ„ط© ط؛ظٹط± ظپط§ط¶ظٹط© (trial / pending_payment / active) طھط¹ظ†ظٹ ط¥ظ† ط§ظ„ظ…ظƒطھط¨
# ظ…ط³ط¬ظ‘ظ„ ظپط¹ظ„ط§ظ‹ ظˆظ„ط§ ظٹط­طھط§ط¬ طھط³ط¬ظٹظ„ط§ظ‹ ط¬ط¯ظٹط¯ظ‹ط§ ظپظٹ start(). ظ‚ط¨ظ„ ظ‡ط°ط§ ط§ظ„طھطµط­ظٹط­ ظƒط§ظ†
# ط§ظ„ط´ط±ط· = "active" ظپظ‚ط·طŒ ظپظƒظ„ ظ…ظƒطھط¨ ظ„ط³ظ‡ ظپظٹ ظپطھط±ط© ط§ظ„طھط¬ط±ط¨ط© ط§ظ„ظ…ط¬ط§ظ†ظٹط© (trial)
# ط£ظˆ ظ…ظ†طھط¸ط± ط§ظ„ط¯ظپط¹ (pending_payment) ظƒط§ظ† ظٹظڈط¹ط§ظ…ظ„ ظƒظ…ظƒطھط¨ ط¬ط¯ظٹط¯ ظˆظٹظڈط·ظ„ط¨ ظ…ظ†ظ‡
# ط§ظ„طھط³ط¬ظٹظ„ ظ…ظ† ط§ظ„طµظپط± ظپظٹ ظƒظ„ /startطŒ ط±ط؛ظ… ظˆط¬ظˆط¯ظ‡ ظپط¹ظ„ط§ظ‹.
EXISTING_TENANT_STATUSES = {"trial", "pending_payment", "active"}

# â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
# Paymob â€” ظ…طھط؛ظٹط±ط§طھ ط§ظ„ط¥ط¹ط¯ط§ط¯ (ظ…ظ† Railway Variables)
# â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
PAYMOB_API_KEY         = os.environ.get("PAYMOB_API_KEY", "")
PAYMOB_SECRET_KEY      = os.environ.get("PAYMOB_SECRET_KEY", "")
PAYMOB_PUBLIC_KEY      = os.environ.get("PAYMOB_PUBLIC_KEY", "")
PAYMOB_HMAC            = os.environ.get("PAYMOB_HMAC", "")
PAYMOB_INTEGRATION_ID  = os.environ.get("PAYMOB_INTEGRATION_ID", "")
SUBSCRIPTION_MONTHLY   = float(os.environ.get("SUBSCRIPTION_MONTHLY", "135"))
SUBSCRIPTION_YEARLY    = float(os.environ.get("SUBSCRIPTION_YEARLY", "1200"))
PAYMOB_INTENTION_URL   = "https://accept.paymob.com/v1/intention/"


def create_payment_link(tenant_code: str, billing_cycle: str, office_name: str = ""):
    """
    طھط·ظ„ط¨ ظ…ظ† Paymob ط±ط§ط¨ط· ط¯ظپط¹ ظ…ط®طµطµ ظ„ظ…ظƒطھط¨ ظ…ط¹ظٹظ‘ظ† (tenant_code).
    billing_cycle: "monthly" ط£ظˆ "yearly"
    ط¨طھط±ط¬ط¹: ط±ط§ط¨ط· ط§ظ„ط¯ظپط¹ (string) ط£ظˆ None ظ„ظˆ ظپط´ظ„طھ.
    """
    amount_egp = SUBSCRIPTION_MONTHLY if billing_cycle == "monthly" else SUBSCRIPTION_YEARLY
    amount_cents = int(round(amount_egp * 100))

    payload = {
        "amount": amount_cents,
        "currency": "EGP",
        "payment_methods": [int(PAYMOB_INTEGRATION_ID)] if PAYMOB_INTEGRATION_ID else ["card"],
        "items": [
            {
                "name": f"ط§ط´طھط±ط§ظƒ ط£ظ…ظٹظ† ط§ظ„ط³ط± - {billing_cycle}",
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

        # â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
        # ًں†• ظ…ط¤ظ‚طھ: ظ†ط·ط¨ط¹ ط±ط¯ Paymob ط§ظ„ظƒط§ظ…ظ„ ط¯ط§ظٹظ…ط§ظ‹ (ظ†ط¬ط­ ط£ظˆ ظپط´ظ„)
        # ط¹ط´ط§ظ† ظ†ط´ظˆظپ طھظپط§طµظٹظ„ ط§ظ„ظ€ Intention ط§ظ„ط­ظ‚ظٹظ‚ظٹط©. ظ‡ظ†ط´ظٹظ„ ط§ظ„ط³ط·ط± ط¯ظ‡ ط¨ط¹ط¯ ط§ظ„طھط´ط®ظٹطµ.
        # â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
        print(f"ًں“¦ Paymob intention FULL response: {json.dumps(data, indent=2, ensure_ascii=False)}")

        client_secret = data.get("client_secret")
        if not client_secret:
            print(f"â‌Œ Paymob intention response missing client_secret: {data}")
            return None
        return f"https://accept.paymob.com/unifiedcheckout/?publicKey={PAYMOB_PUBLIC_KEY}&clientSecret={client_secret}"
    except Exception as e:
        print(f"â‌Œ create_payment_link error: {e}")
        return None


# â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
# Flask App â€” ظ„ط§ط³طھظ‚ط¨ط§ظ„ Webhook ظ…ظ† Paymob
# â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
flask_app = Flask(__name__)


def verify_hmac(data: dict, received_hmac: str) -> bool:
    """
    ظٹطھط­ظ‚ظ‚ ط¥ظ† ط§ظ„ط·ظ„ط¨ ط¬ط§ظٹ ظپط¹ظ„ط§ظ‹ ظ…ظ† Paymob ظˆظ…ط´ ظ…ط²ظˆظ‘ط±.
    ط­ط³ط¨ ط§ظ„ظ€ documentation ط§ظ„ط±ط³ظ…ظٹ ظ„ظ€ Paymob (transaction callback HMAC):
    https://docs.paymob.com/docs/hmac-calculation
    """
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

        # â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
        # ًں”چ ظ…ط¤ظ‚طھ: ظ†ط·ط¨ط¹ ط§ظ„ظ€ payload ظƒط§ظ…ظ„ ط¹ط´ط§ظ† ظ†ط´ظˆظپ ط´ظƒظ„ظ‡ ط§ظ„ط­ظ‚ظٹظ‚ظٹ
        # (ظ‡ظ†ط´ظٹظ„ ط§ظ„ط³ط·ط±ظٹظ† ط¯ظˆظ„ ط¨ط¹ط¯ ظ…ط§ ظ†طھط£ظƒط¯ ظ…ظ† ظ…ظƒط§ظ† tenant_code)
        # â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
        print("â•گ" * 50)
        print("ًں“¦ PAYMOB WEBHOOK â€” FULL PAYLOAD RECEIVED:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("â•گ" * 50)

        obj = payload.get("obj", {})

        received_hmac = request.args.get("hmac", "")
        if not verify_hmac(obj, received_hmac):
            print("â‌Œ Webhook HMAC mismatch â€” طھط¬ط§ظ‡ظ„ظ†ط§ ط§ظ„ط·ظ„ط¨ (ظ…ظ…ظƒظ† ظٹظƒظˆظ† ظ…ط²ظˆظ‘ط±)")
            return jsonify({"status": "invalid_hmac"}), 400

        success = obj.get("success", False)
        extras = obj.get("payment_key_claims", {}).get("extra", {}) or obj.get("order", {}).get("extras", {})
        tenant_code = extras.get("tenant_code", "")
        billing_cycle = extras.get("billing_cycle", "")

        if success and tenant_code:
            activate_tenant(tenant_code, billing_cycle)
            print(f"âœ… Webhook: طھظ… طھظپط¹ظٹظ„ {tenant_code} ({billing_cycle})")
        else:
            print(f"âڑ ï¸ڈ Webhook: ط¯ظپط¹ ط؛ظٹط± ظ†ط§ط¬ط­ ط£ظˆ tenant_code ظ…ظپظ‚ظˆط¯ â€” {obj.get('id')}")

        return jsonify({"status": "received"}), 200

    except Exception as e:
        print(f"â‌Œ paymob_webhook error: {e}")
        return jsonify({"status": "error"}), 500


def activate_tenant(tenant_code: str, billing_cycle: str):
    """
    ظٹظپط¹ظ‘ظ„ ط§ظ„ظ…ظƒطھط¨ ظپظٹ ط´ظٹطھ Tenants: ظٹط؛ظٹظ‘ط± status ظ„ظ€ activeطŒ ظˆظٹط¨ط¹طھ ط±ط³ط§ظ„ط© طھط£ظƒظٹط¯ ظ„ظ„ط¹ظ…ظٹظ„.
    """
    try:
        records = P005("Tenants")
        for i, r in enumerate(records, start=2):
            if str(r.get("tenant_code", "")).strip() == str(tenant_code).strip():
                P004("Tenants", i, 9, "active")  # ط§ظ„ط¹ظ…ظˆط¯ I = status
                chat_id = r.get("chat_id", "")
                if chat_id:
                    send_telegram_message_sync(
                        chat_id,
                        "âœ… *طھظ… طھظپط¹ظٹظ„ ط§ط´طھط±ط§ظƒظƒ ط¨ظ†ط¬ط§ط­!*\n\nظ…ط±ط­ط¨ط§ظ‹ ط¨ظƒ ظپظٹ ط£ظ…ظٹظ† ط§ظ„ط³ط± ًںڈ›ï¸ڈ",
                    )
                break
    except Exception as e:
        print(f"â‌Œ activate_tenant error: {e}")


def send_telegram_message_sync(chat_id, text: str):
    """
    ظٹط¨ط¹طھ ط±ط³ط§ظ„ط© طھظٹظ„ظٹط¬ط±ط§ظ… ظ…ط¨ط§ط´ط±ط© ط¹ظ† ط·ط±ظٹظ‚ HTTP request ط¨ط³ظٹط· (ط¨ط¯ظˆظ† ط¹ظ…ظ„ Application instance ط¬ط¯ظٹط¯).
    ط£ط®ظپ ظˆط£ظƒط«ط± ط£ظ…ط§ظ†ط§ظ‹ ظ…ظ† ط¬ظˆظ‡ Flask threadطŒ ظˆظ…ط§ ظٹطھط¹ط§ط±ط¶ ظ…ط¹ event loop ط§ظ„ط¨ظˆطھ ط§ظ„ط£ط³ط§ط³ظٹ.
    """
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": int(chat_id),
            "text": text,
            "parse_mode": "Markdown",
        }, timeout=10)
    except Exception as e:
        print(f"â‌Œ send_telegram_message_sync error: {e}")


def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

ROUTE_MAP = {
    "F-001": F001,   # ط¥ط¶ط§ظپط© ط¹ظ…ظٹظ„
    "F-002": F002,   # ط¹ط±ط¶ ط¹ظ…ظٹظ„
    "F-003": F003,   # طھط¹ط¯ظٹظ„ ط¹ظ…ظٹظ„
    "F-004": RT001,  # ط¥ط¶ط§ظپط© ظ…ظˆط¶ظˆط¹
    "F-005": RE001,  # ط¥ط¶ط§ظپط© ط­ط¯ط«
    "F-006": RE002,  # ظ†طھظٹط¬ط© ط­ط¯ط«
    "F-007": RS001,  # ط¥ط±ط³ط§ظ„ ظ…ط±ظپظ‚ط§طھ
    "F-008": RD002,  # ط·ظ„ط¨ ظ…ط³طھظ†ط¯ط§طھ
    "F-009": RM001,  # ط·ظ„ط¨ ط¹ظ‡ط¯ط©
    "F-010": RE003,  # ط¹ط±ط¶ ط£ط­ط¯ط§ط«
    "A-001": RA001,  # ط¥ط¶ط§ظپط© ظ…ط³ط§ط¹ط¯
    "A-002": RA002,  # ط¹ط±ط¶ ظ…ط³ط§ط¹ط¯
    "T-002": RT002,  # ط¹ط±ط¶ ظ…ظˆط¶ظˆط¹ط§طھ ط¹ظ…ظٹظ„
    "T-003": RT003,  # طھط؛ظٹظٹط± ط­ط§ظ„ط© ظ…ظˆط¶ظˆط¹
    "T-004": RT004,  # ط£ط±ط´ظپط© ظ…ظˆط¶ظˆط¹
    "S-002": RS002,  # ط§ط³طھظ„ط§ظ… ط´ط­ظ†ط©
    "S-003": RS003,  # طھطھط¨ط¹ ط´ط­ظ†ط©
    "M-002": RM002,  # طھط³ظˆظٹط© ط¹ظ‡ط¯ط©
    "N-001": RN001,  # ط¥ط´ط¹ط§ط± ظ„ظ„ط±ط¦ظٹط³
    "N-002": RN002,  # ط¥ط´ط¹ط§ط± ظ„ظ„ط¹ظ…ظٹظ„
    "N-003": RN003,  # ط¥ط´ط¹ط§ط± ظ„ظ„ظ…ط³ط§ط¹ط¯
    "D-001": RD001,  # ط±ظپط¹ ظ…ط³طھظ†ط¯ ظˆط§ط±ط¯
    "D-003": RD003,  # ط§ظ„ظ…ظˆط§ظپظ‚ط© ط¹ظ„ظ‰ ظ…ط³طھظ†ط¯
    "D-004": RD004,  # ط±ظپط¶ ظ…ط³طھظ†ط¯
    "D-005": RD005,  # ط¹ط±ط¶ ظ…ط³طھظ†ط¯ط§طھ ظ…ظˆط¶ظˆط¹
    "D-006": RD006,  # ط£ط±ط´ظپط© ظ…ط³طھظ†ط¯ط§طھ
}

# â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
# ط¯ط§ظ„ط© ظ…ط³ط§ط¹ط¯ط© â€” ط¬ظ„ط¨ boss_chat_id ظ…ظ† ط§ظ„ظ€ tenant
# â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
def get_boss_id(context):
    """ط¥ط±ط¬ط§ط¹ boss_chat_id ط§ظ„ط®ط§طµ ط¨ط§ظ„ظ…ظƒطھط¨طŒ ط£ظˆ طµط§ط­ط¨ ط§ظ„ظ…ظ†طµط© ظƒظ€ fallback"""
    tenant = context.user_data.get("tenant", {})
    boss = tenant.get("boss_chat_id", "")
    if boss:
        try:
            return int(boss)
        except:
            pass
    return BOSS_CHAT_ID

def get_tenant_sheet(context, chat_id):
    """
    ط¥ط±ط¬ط§ط¹ sheet_name ط§ظ„ط®ط§طµ ط¨ظ…ظƒطھط¨ ط§ظ„ظ…ط³طھط®ط¯ظ… ط§ظ„ط­ط§ظ„ظٹ (Tenant) ظ…ظ† context.user_data.
    ظ„ظˆ ظ„ط£ظٹ ط³ط¨ط¨ ط؛ظٹط± ظ…طھظˆظپط± (ظ…ط«ظ„ط§ظ‹ ط­ط§ظ„ط© ظ‚ط¯ظٹظ…ط© ط£ظˆ ط®ط·ط£ ط؛ظٹط± ظ…طھظˆظ‚ط¹)طŒ ظٹط±ط¬ط¹ SHEET_NAME
    ط§ظ„ط§ظپطھط±ط§ط¶ظٹ (ط´ظٹطھ ظ…ط³طھط± ط¬ظ…ط§ظ„ Of-001) ظƒظ€ fallback ط¢ظ…ظ† ط¨ط¯ظ„ ظ…ط§ ظٹظپط´ظ„ ط§ظ„ظƒظˆط¯ ط¨ط§ظ„ظƒط§ظ…ظ„.
    """
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
    """
    ظٹط¨ظ†ظٹ ط±ط§ط¨ط· ظ„ظˆط­ط© ظ‚ظٹط§ط¯ط© ط§ظ„ط±ط¦ظٹط³ ط§ظ„ط®ط§طµط© ط¨ظ…ظƒطھط¨ ظ…ط¹ظٹظ‘ظ†طŒ ظ…ط¹ sheet_id ط§ظ„ط¯ظٹظ†ط§ظ…ظٹظƒظٹ.
    """
    token = base64.b64encode(str(chat_id).encode()).decode()
    sheet_id = tenant.get("sheet_id", "")
    return f"https://aminalserr.com/amin_alsir_dashboard.html?t={token}&sid={sheet_id}"

# â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
# ظ„ظˆط­ط§طھ ط§ظ„ظ‚ظٹط§ط¯ط©
# â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
def main_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("âڑ™ï¸ڈ ط§ظ„ط¥ط¹ط¯ط§ط¯ط§طھ", callback_data="MENU-SETTINGS"),
            InlineKeyboardButton("ًں“… ط§ظ„ط£ط­ط¯ط§ط«",    callback_data="MENU-EVENTS"),
        ],
        [
            InlineKeyboardButton("ًں“‹ ط§ظ„ط®ط¯ظ…ط§طھ",    callback_data="MENU-SERVICES"),
            InlineKeyboardButton("ًں“ٹ ط§ظ„طھظ‚ط§ط±ظٹط±",   callback_data="MENU-REPORTS"),
        ],
        [
            InlineKeyboardButton("ًں’¬ ط¨ط±ظٹط¯ ط§ظ„ط¥ط´ط¹ط§ط±ط§طھ", callback_data="MENU-INBOX"),
        ],
    ])

def settings_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("ًں‘¤ ط¹ظ…ظٹظ„ ط¬ط¯ظٹط¯",    callback_data="F-001")],
        [InlineKeyboardButton("ًں”چ ط¹ط±ط¶ ط¹ظ…ظٹظ„",     callback_data="F-002")],
        [InlineKeyboardButton("âœڈï¸ڈ طھط¹ط¯ظٹظ„ ط¹ظ…ظٹظ„",   callback_data="F-003")],
        [InlineKeyboardButton("ًں¤‌ ظ…ط³ط§ط¹ط¯ ط¬ط¯ظٹط¯",   callback_data="A-001")],
        [InlineKeyboardButton("ًں‘¤ ط¹ط±ط¶ ظ…ط³ط§ط¹ط¯",    callback_data="A-002")],
        [InlineKeyboardButton("ًں“پ ظ…ظˆط¶ظˆط¹ ط¬ط¯ظٹط¯",   callback_data="F-004")],
        [InlineKeyboardButton("ًں“‹ ظ…ظˆط¶ظˆط¹ط§طھ ط¹ظ…ظٹظ„", callback_data="T-002")],
        [InlineKeyboardButton("ًں”„ طھط؛ظٹظٹط± ط­ط§ظ„ط© ظ…ظˆط¶ظˆط¹", callback_data="T-003")],
        [InlineKeyboardButton("ًں—„ï¸ڈ ط£ط±ط´ظپط© ظ…ظˆط¶ظˆط¹",  callback_data="T-004")],
        [InlineKeyboardButton("ًں”™ ط±ط¬ظˆط¹",          callback_data="MENU-MAIN")],
    ])

def events_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("ًں“… ط¹ط±ط¶ ط§ظ„ط£ط­ط¯ط§ط«",      callback_data="F-010")],
        [InlineKeyboardButton("â‍• ط¥ط¶ط§ظپط© ط­ط¯ط« ط¬ط¯ظٹط¯",  callback_data="F-005")],
        [InlineKeyboardButton("ًں“¢ ظ†طھظٹط¬ط© ط­ط¯ط«",        callback_data="F-006")],
        [InlineKeyboardButton("ًں”™ ط±ط¬ظˆط¹",              callback_data="MENU-MAIN")],
    ])

def services_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("ًں“¦ ط¥ط±ط³ط§ظ„ ظ…ط±ظپظ‚ط§طھ",     callback_data="F-007")],
        [InlineKeyboardButton("ًں“¥ ط§ط³طھظ„ط§ظ… ط´ط­ظ†ط©",      callback_data="S-002")],
        [InlineKeyboardButton("ًں”چ طھطھط¨ط¹ ط´ط­ظ†ط©",        callback_data="S-003")],
        [InlineKeyboardButton("ًں“پ ط±ظپط¹ ظ…ط³طھظ†ط¯ ظˆط§ط±ط¯",   callback_data="D-001")],
        [InlineKeyboardButton("âœ… ظ…ظˆط§ظپظ‚ط© ط¹ظ„ظ‰ ظ…ط³طھظ†ط¯", callback_data="D-003")],
        [InlineKeyboardButton("â‌Œ ط±ظپط¶ ظ…ط³طھظ†ط¯",        callback_data="D-004")],
        [InlineKeyboardButton("ًں“‚ ط¹ط±ط¶ ظ…ط³طھظ†ط¯ط§طھ",      callback_data="D-005")],
        [InlineKeyboardButton("ًں—„ï¸ڈ ط£ط±ط´ظپط© ظ…ط³طھظ†ط¯ط§طھ",   callback_data="D-006")],
        [InlineKeyboardButton("ًں“„ ط·ظ„ط¨ ظ…ط³طھظ†ط¯ط§طھ",      callback_data="F-008")],
        [InlineKeyboardButton("ًں’° ط·ظ„ط¨ ط¹ظ‡ط¯ط© ظ…ط§ظ„ظٹط©",  callback_data="F-009")],
        [InlineKeyboardButton("ًں’³ طھط³ظˆظٹط© ط¹ظ‡ط¯ط©",       callback_data="M-002")],
        [InlineKeyboardButton("ًں”™ ط±ط¬ظˆط¹",              callback_data="MENU-MAIN")],
    ])

def notifications_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("ًں”” ط¥ط´ط¹ط§ط± ظ„ظ„ط±ط¦ظٹط³",   callback_data="N-001")],
        [InlineKeyboardButton("ًں“© ط¥ط´ط¹ط§ط± ظ„ظ„ط¹ظ…ظٹظ„",   callback_data="N-002")],
        [InlineKeyboardButton("ًں“‹ ط¥ط´ط¹ط§ط± ظ„ظ„ظ…ط³ط§ط¹ط¯",  callback_data="N-003")],
        [InlineKeyboardButton("ًں”™ ط±ط¬ظˆط¹",            callback_data="MENU-MAIN")],
    ])

def countries_keyboard():
    """ط£ط²ط±ط§ط± ط§ظ„ط¯ظˆظ„ ط§ظ„ط¹ط±ط¨ظٹط© ظ„ظ„طھط³ط¬ظٹظ„"""
    countries = [
        "ظ…طµط±", "ط§ظ„ط³ط¹ظˆط¯ظٹط©", "ط§ظ„ط¥ظ…ط§ط±ط§طھ", "ط§ظ„ظƒظˆظٹطھ",
        "ظ‚ط·ط±", "ط§ظ„ط¨ط­ط±ظٹظ†", "ط§ظ„ط£ط±ط¯ظ†", "ظ„ط¨ظ†ط§ظ†",
        "ط§ظ„ظ…ط؛ط±ط¨", "طھظˆظ†ط³", "ط§ظ„ط¬ط²ط§ط¦ط±", "ظ„ظٹط¨ظٹط§",
        "ط§ظ„ط¹ط±ط§ظ‚", "ط³ظˆط±ظٹط§", "ط§ظ„ظٹظ…ظ†", "ط¹ظ…ط§ظ†",
        "ط§ظ„ط³ظˆط¯ط§ظ†", "ظپظ„ط³ط·ظٹظ†",
    ]
    rows = []
    for i in range(0, len(countries), 2):
        row = [InlineKeyboardButton(countries[i], callback_data=f"COUNTRY-{countries[i]}")]
        if i + 1 < len(countries):
            row.append(InlineKeyboardButton(countries[i+1], callback_data=f"COUNTRY-{countries[i+1]}"))
        rows.append(row)
    return InlineKeyboardMarkup(rows)

# â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
# Post Init
# â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
async def post_init(application):
    await application.bot.delete_webhook(drop_pending_updates=True)
    print("âœ… Webhook deleted â€” bot started clean")

# â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
# Start
# â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    print(f"ًں†” CHAT ID: {chat_id}")

    # â”€â”€ ط§ظ„طھط­ظ‚ظ‚ ظ…ظ† Deep Link (طھط³ط¬ظٹظ„ ط¹ظ…ظٹظ„ ط£ظˆ ظ…ط³ط§ط¹ط¯ ط£ظˆ ط§ط®طھظٹط§ط± ط¨ط§ظ‚ط©) â”€â”€
    args = context.args
    if args:
        param = args[0]

        # â”€â”€ طھط³ط¬ظٹظ„ ط¹ظ…ظٹظ„ â”€â”€
        # ط´ظƒظ„ ط§ظ„ط±ط§ط¨ط·: client_{tenant_code}_{ref_code} â€” ظ…ط«ط§ظ„: client_Of-005_Cl-003
        if param.startswith("client_"):
            parts = param.replace("client_", "").split("_")
            if len(parts) < 2:
                await update.message.reply_text("â‌Œ ط±ط§ط¨ط· ط؛ظٹط± طµط­ظٹط­. طھظˆط§طµظ„ ظ…ط¹ ط§ظ„ظ…ظƒطھط¨.")
                return
            tenant_code, ref_code = parts[0], "_".join(parts[1:])

            tenant_row = P002("Tenants", tenant_code, TENANTS_SHEET)
            if not tenant_row:
                await update.message.reply_text("â‌Œ ط§ظ„ظ…ظƒطھط¨ ط؛ظٹط± ظ…ظˆط¬ظˆط¯. طھظˆط§طµظ„ ظ…ط¹ ط§ظ„ظ…ظƒطھط¨.")
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
                    f"âœ… *طھظ… ط±ط¨ط· ط­ط³ط§ط¨ظƒ ط¨ظ†ط¬ط§ط­!*\n\n"
                    f"ًں‘¤ {client.get('client_name', '')}\n"
                    f"ًں”¹ ط§ظ„ظƒظˆط¯: `{ref_code}`\n\n"
                    f"ط³طھطµظ„ظƒ ط¥ط´ط¹ط§ط±ط§طھ ظ…ظƒطھط¨ ط§ظ„ظ…ط­ط§ظ…ط§ط© ظ‡ظ†ط§ ظ…ط¨ط§ط´ط±ط©.",
                    parse_mode="Markdown"
                )
                token = base64.b64encode(str(chat_id).encode()).decode()
                dashboard_url = f"https://aminalserr.com/amin_alsir_client_dashboard.html?t={token}&sid={sheet_id}"
                await update.message.reply_text(
                    f"ًں”— <b>ط±ط§ط¨ط· ظ„ظˆط­ط© ط§ظ„ظ‚ظٹط§ط¯ط© ط§ظ„ط®ط§طµط© ط¨ظƒ:</b>\n<a href=\"{dashboard_url}\">{dashboard_url}</a>\n\nًں“Œ ط§ط­ظپط¸ ظ‡ط°ط§ ط§ظ„ط±ط§ط¨ط· ظپظٹ ظ…ظپط¶ظ„ط§طھظƒ",
                    parse_mode="HTML"
                )
                await context.bot.send_message(
                    chat_id=boss_id,
                    text=f"ًں”” *ط¥ط´ط¹ط§ط± â€” ط£ظ…ظٹظ† ط§ظ„ط³ط±*\n\nًں“± ط¹ظ…ظٹظ„ ط±ط¨ط· ط­ط³ط§ط¨ظ‡ ط¨ط§ظ„ط¨ظˆطھ\nًں‘¤ {client.get('client_name','')}\nًں”¹ {ref_code}",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text("â‌Œ ظƒظˆط¯ ط§ظ„ط¹ظ…ظٹظ„ ط؛ظٹط± طµط­ظٹط­. طھظˆط§طµظ„ ظ…ط¹ ط§ظ„ظ…ظƒطھط¨.")
            return

        # â”€â”€ طھط³ط¬ظٹظ„ ظ…ط³ط§ط¹ط¯ â”€â”€
        # ط´ظƒظ„ ط§ظ„ط±ط§ط¨ط·: assistant_{tenant_code}_{ref_code} â€” ظ…ط«ط§ظ„: assistant_Of-005_As-002
        elif param.startswith("assistant_"):
            parts = param.replace("assistant_", "").split("_")
            if len(parts) < 2:
                await update.message.reply_text("â‌Œ ط±ط§ط¨ط· ط؛ظٹط± طµط­ظٹط­. طھظˆط§طµظ„ ظ…ط¹ ط§ظ„ظ…ظƒطھط¨.")
                return
            tenant_code, ref_code = parts[0], "_".join(parts[1:])

            tenant_row = P002("Tenants", tenant_code, TENANTS_SHEET)
            if not tenant_row:
                await update.message.reply_text("â‌Œ ط§ظ„ظ…ظƒطھط¨ ط؛ظٹط± ظ…ظˆط¬ظˆط¯. طھظˆط§طµظ„ ظ…ط¹ ط§ظ„ظ…ظƒطھط¨.")
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
                    f"âœ… *طھظ… ط±ط¨ط· ط­ط³ط§ط¨ظƒ ط¨ظ†ط¬ط§ط­!*\n\n"
                    f"ًں‘¥ {assistant.get('assistant_name', '')}\n"
                    f"ًں”¹ ط§ظ„ظƒظˆط¯: `{ref_code}`\n\n"
                    f"ط³طھطµظ„ظƒ ظ…ظ‡ط§ظ…ظƒ ظˆظ…ط³طھط¬ط¯ط§طھ ط§ظ„ظ…ظƒطھط¨ ظ‡ظ†ط§ ظ…ط¨ط§ط´ط±ط©.",
                    parse_mode="Markdown"
                )
                token = base64.b64encode(str(chat_id).encode()).decode()
                dashboard_url = f"https://aminalserr.com/amin_alsir_assistant_dashboard.html?t={token}&sid={sheet_id}"
                await update.message.reply_text(
                    f"ًں”— <b>ط±ط§ط¨ط· ظ„ظˆط­ط© ط§ظ„ظ‚ظٹط§ط¯ط© ط§ظ„ط®ط§طµط© ط¨ظƒ:</b>\n<a href=\"{dashboard_url}\">{dashboard_url}</a>\n\nًں“Œ ط§ط­ظپط¸ ظ‡ط°ط§ ط§ظ„ط±ط§ط¨ط· ظپظٹ ظ…ظپط¶ظ„ط§طھظƒ",
                    parse_mode="HTML"
                )
                await context.bot.send_message(
                    chat_id=boss_id,
                    text=f"ًں”” *ط¥ط´ط¹ط§ط± â€” ط£ظ…ظٹظ† ط§ظ„ط³ط±*\n\nًں“± ظ…ط³ط§ط¹ط¯ ط±ط¨ط· ط­ط³ط§ط¨ظ‡ ط¨ط§ظ„ط¨ظˆطھ\nًں‘¥ {assistant.get('assistant_name','')}\nًں”¹ {ref_code}",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text("â‌Œ ظƒظˆط¯ ط§ظ„ظ…ط³ط§ط¹ط¯ ط؛ظٹط± طµط­ظٹط­. طھظˆط§طµظ„ ظ…ط¹ ط§ظ„ظ…ظƒطھط¨.")
            return

        # â”€â”€ ط§ط®طھظٹط§ط± ط¨ط§ظ‚ط© ظ…ظ† طµظپط­ط© ط§ظ„ظ‡ط¨ظˆط· (ط´ظ‡ط±ظٹ/ط³ظ†ظˆظٹ) â”€â”€
        # ًں†• ط§ظ„ط±ط§ط¨ط· ط§ظ„ط¬ط§ظٹ ظ…ظ† index.html ط´ظƒظ„ظ‡: ?start=plan_monthly ط£ظˆ ?start=plan_yearly
        elif param.startswith("plan_"):
            billing_cycle = param.replace("plan_", "")
            if billing_cycle not in ("monthly", "yearly"):
                billing_cycle = "monthly"

            context.user_data["selected_billing_cycle"] = billing_cycle
            cycle_label = "ط´ظ‡ط±ظٹ" if billing_cycle == "monthly" else "ط³ظ†ظˆظٹ (ط§ظ„ط¨ط§ظ‚ط© ط§ظ„ط°ظ‡ط¨ظٹط©)"

            tenant = MT001(chat_id)
            if tenant and tenant.get("status") in EXISTING_TENANT_STATUSES:
                office_name = tenant.get("office_name", "ط§ظ„ظ…ظƒطھط¨")
                country = tenant.get("country", "ظ…طµط±")
                context.user_data["tenant"] = tenant
                dashboard_url = build_boss_dashboard_url(chat_id, tenant)
                await update.message.reply_text(
                    f"ط£ظ‡ظ„ط§ظ‹ ط¨ظƒ ظ…ط¬ط¯ط¯ط§ظ‹ ظپظٹ <b>ط£ظ…ظٹظ† ط§ظ„ط³ط±</b> ًںڈ›ï¸ڈ\n\n"
                    f"ًںڈ¢ {office_name}\n"
                    f"ًںŒچ {country}\n\n"
                    f"ًں”— ظ„ظˆط­ط© ط§ظ„ظ‚ظٹط§ط¯ط© ط§ظ„ظƒط§ظ…ظ„ط©:\n<a href=\"{dashboard_url}\">{dashboard_url}</a>\n\n"
                    f"ط§ط®طھط± ظ…ظ† ظ„ظˆط­ط© ط§ظ„ظ‚ظٹط§ط¯ط©:",
                    parse_mode="HTML",
                    reply_markup=main_keyboard()
                )
            else:
                context.user_data["routine"] = "REG"
                context.user_data["step"] = "office_name"
                context.user_data["data"] = {}
                await update.message.reply_text(
                    f"ًںڈ›ï¸ڈ *ط£ظ‡ظ„ط§ظ‹ ط¨ظƒ ظپظٹ ط£ظ…ظٹظ† ط§ظ„ط³ط±!*\n\n"
                    f"âœ… طھظ… طھط³ط¬ظٹظ„ ط§ط®طھظٹط§ط±ظƒ: *ط§ظ„ط¨ط§ظ‚ط© {cycle_label}*\n\n"
                    f"ظ†ط¸ط§ظ… ط¥ط¯ط§ط±ط© ظ…ظƒطھط¨ ط§ظ„ظ…ط­ط§ظ…ط§ط© ظ„ظ„ظˆط·ظ† ط§ظ„ط¹ط±ط¨ظٹ ًںŒچ\n\n"
                    f"ظ„ظ„ط¨ط¯ط،طŒ ط£ط¯ط®ظ„ *ط§ط³ظ… ظ…ظƒطھط¨ظƒ*:",
                    parse_mode="Markdown"
                )
            return

    # â”€â”€ ط§ظ„طھط­ظ‚ظ‚ ظ…ظ† ط§ظ„ط§ط´طھط±ط§ظƒ (ط§ظ„ط­ط§ظ„ط© ط§ظ„ط¹ط§ط¯ظٹط©طŒ ط¨ط¯ظˆظ† Deep Link) â”€â”€
    tenant = MT001(chat_id)

    if tenant and tenant.get("status") in EXISTING_TENANT_STATUSES:
        # ظ…ظƒطھط¨ ظ…ظˆط¬ظˆط¯ ظپط¹ظ„ط§ظ‹ â€” ظپطھط­ ط§ظ„ط¯ط§ط´ط¨ظˆط±ط¯
        office_name = tenant.get("office_name", "ط§ظ„ظ…ظƒطھط¨")
        country = tenant.get("country", "ظ…طµط±")
        context.user_data["tenant"] = tenant
        dashboard_url = build_boss_dashboard_url(chat_id, tenant)
        await update.message.reply_text(
            f"ط£ظ‡ظ„ط§ظ‹ ط¨ظƒ ظپظٹ <b>ط£ظ…ظٹظ† ط§ظ„ط³ط±</b> ًںڈ›ï¸ڈ\n\n"
            f"ًںڈ¢ {office_name}\n"
            f"ًںŒچ {country}\n\n"
            f"ًں”— ظ„ظˆط­ط© ط§ظ„ظ‚ظٹط§ط¯ط© ط§ظ„ظƒط§ظ…ظ„ط©:\n<a href=\"{dashboard_url}\">{dashboard_url}</a>\n\n"
            f"ط§ط®طھط± ظ…ظ† ظ„ظˆط­ط© ط§ظ„ظ‚ظٹط§ط¯ط©:",
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )
    else:
        # ظ…ظƒطھط¨ ط¬ط¯ظٹط¯ â€” ط¨ط¯ط، ط§ظ„طھط³ط¬ظٹظ„ ط§ظ„طھظ„ظ‚ط§ط¦ظٹ
        context.user_data["routine"] = "REG"
        context.user_data["step"] = "office_name"
        context.user_data["data"] = {}
        await update.message.reply_text(
            "ًںڈ›ï¸ڈ *ط£ظ‡ظ„ط§ظ‹ ط¨ظƒ ظپظٹ ط£ظ…ظٹظ† ط§ظ„ط³ط±!*\n\n"
            "ظ†ط¸ط§ظ… ط¥ط¯ط§ط±ط© ظ…ظƒطھط¨ ط§ظ„ظ…ط­ط§ظ…ط§ط© ظ„ظ„ظˆط·ظ† ط§ظ„ط¹ط±ط¨ظٹ ًںŒچ\n\n"
            "ظ„ظ„ط¨ط¯ط،طŒ ط£ط¯ط®ظ„ *ط§ط³ظ… ظ…ظƒطھط¨ظƒ*:",
            parse_mode="Markdown"
        )

# â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
# ًں”چ ط£ظ…ط± ط§ط®طھط¨ط§ط±ظٹ ظ…ط¤ظ‚طھ â€” /testpay
# ظٹط·ظ„ط¨ ط±ط§ط¨ط· ط¯ظپط¹ طھط¬ط±ظٹط¨ظٹ ظ…ظ† Paymob (Test mode) ط¹ط´ط§ظ† ظ†طھط£ظƒط¯
# ط¥ظ† create_payment_link() ط´ط؛ط§ظ„ط©طŒ ظˆظ†ط´ظˆظپ ط´ظƒظ„ ط§ظ„ظ€ webhook ط§ظ„ط­ظ‚ظٹظ‚ظٹ.
# (ظ‡ظ†ط´ظٹظ„ ط§ظ„ط£ظ…ط± ط¯ظ‡ ط¨ط¹ط¯ ظ…ط§ ظ†ط®ظ„طµ ط§ظ„ط§ط®طھط¨ط§ط±)
# â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
async def testpay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    test_tenant_code = "TEST-001"
    await update.message.reply_text("âڈ³ ط¨ط·ظ„ط¨ ط±ط§ط¨ط· ط¯ظپط¹ طھط¬ط±ظٹط¨ظٹ ظ…ظ† Paymob...")
    link = create_payment_link(test_tenant_code, "monthly", "ظ…ظƒطھط¨ طھط¬ط±ظٹط¨ظٹ")
    if link:
        await update.message.reply_text(
            f"âœ… *طھظ… ط¥ظ†ط´ط§ط، ط±ط§ط¨ط· ط§ظ„ط¯ظپط¹ ط§ظ„طھط¬ط±ظٹط¨ظٹ!*\n\n"
            f"ًں”¹ Tenant Code: `{test_tenant_code}`\n"
            f"ًں”— {link}\n\n"
            f"ط¯ظˆط³ ط¹ظ„ظ‰ ط§ظ„ط±ط§ط¨ط· ظˆط¬ط±ظ‘ط¨ ط§ظ„ط¯ظپط¹ ط¨ط¨ظٹط§ظ†ط§طھ ظƒط§ط±طھ طھط¬ط±ظٹط¨ظٹ ظ…ظ† Paymob.",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("â‌Œ ظپط´ظ„ ط¥ظ†ط´ط§ط، ط±ط§ط¨ط· ط§ظ„ط¯ظپط¹. ط´ظˆظپ ط§ظ„ظ€ Logs ط¹ظ„ظ‰ Railway ظ„ظ…ط¹ط±ظپط© ط§ظ„ط³ط¨ط¨.")

# â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
# Text Router
# â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    routine = context.user_data.get("routine")
    step    = context.user_data.get("step")
    if not routine or not step:
        return

    text     = update.message.text.strip()
    chat_id  = update.effective_chat.id
    data     = context.user_data.setdefault("data", {})
    cancel_btn = [[{"text": "â‌Œ ط¥ظ„ط؛ط§ط،", "callback_data": "MENU-MAIN"}]]
    back_btn   = [[{"text": "ًں”™ ط§ظ„ظ‚ط§ط¦ظ…ط©", "callback_data": "MENU-MAIN"}]]

    # â”€â”€â”€ REG طھط³ط¬ظٹظ„ ظ…ظƒطھط¨ ط¬ط¯ظٹط¯ â”€â”€â”€
    if routine == "REG":
        if step == "office_name":
            if not V001(text):
                await T001(context, chat_id, "â‌Œ ط§ظ„ط§ط³ظ… ظ‚طµظٹط±. ط£ط¯ط®ظ„ ط§ط³ظ… ط§ظ„ظ…ظƒطھط¨ ظƒط§ظ…ظ„ط§ظ‹:")
                return
            data["office_name"] = text
            context.user_data["step"] = "country"
            await update.message.reply_text(
                f"âœ… ط§ط³ظ… ط§ظ„ظ…ظƒطھط¨: *{text}*\n\nًںŒچ ط§ط®طھط± *ط¯ظˆظ„طھظƒ*:",
                parse_mode="Markdown",
                reply_markup=countries_keyboard()
            )

    # â”€â”€â”€ F001 ط¥ط¶ط§ظپط© ط¹ظ…ظٹظ„ â”€â”€â”€
    elif routine == "F001":
        if step == "name":
            if not V001(text):
                await T001(context, chat_id, "â‌Œ ط§ظ„ط§ط³ظ… ظ‚طµظٹط±. ط£ط¯ط®ظ„ ط§ظ„ط§ط³ظ… ظƒط§ظ…ظ„ط§ظ‹:")
                return
            data["name"] = text
            context.user_data["step"] = "national_id"
            await T002(context, chat_id, "ًںھھ ط£ط¯ط®ظ„ *ط§ظ„ط±ظ‚ظ… ط§ظ„ظ‚ظˆظ…ظٹ* (14 ط±ظ‚ظ…):", cancel_btn)
        elif step == "national_id":
            if not V002(text):
                await T001(context, chat_id, "â‌Œ ط§ظ„ط±ظ‚ظ… ط§ظ„ظ‚ظˆظ…ظٹ ظٹط¬ط¨ 14 ط±ظ‚ظ…:")
                return
            data["national_id"] = text
            context.user_data["step"] = "mobile"
            await T002(context, chat_id, "ًں“± ط£ط¯ط®ظ„ *ط±ظ‚ظ… ط§ظ„ظ…ظˆط¨ط§ظٹظ„*:", cancel_btn)
        elif step == "mobile":
            if not V003(text):
                await T001(context, chat_id, "â‌Œ ط±ظ‚ظ… ط§ظ„ظ…ظˆط¨ط§ظٹظ„ ط؛ظٹط± طµط­ظٹط­:")
                return
            data["mobile"] = text
            context.user_data["step"] = "address"
            await T002(context, chat_id, "ًںڈ  ط£ط¯ط®ظ„ *ط§ظ„ط¹ظ†ظˆط§ظ†*:", cancel_btn)
        elif step == "address":
            if not V001(text):
                await T001(context, chat_id, "â‌Œ ط§ظ„ط¹ظ†ظˆط§ظ† ظ‚طµظٹط±:")
                return
            data["address"] = text
            sheet_name = get_tenant_sheet(context, chat_id)
            tenant_code = context.user_data.get("tenant", {}).get("tenant_code", "")
            code = G001("Cl", "Clients", sheet_name)
            ok = P003("Clients", [code, data["name"], data["national_id"], data["mobile"], data["address"], datetime.now().strftime("%Y-%m-%d %H:%M")], sheet_name)
            context.user_data.clear()
            if ok:
                client_link = f"https://t.me/amin_alsir_bot?start=client_{tenant_code}_{code}"
                share_text = f"ط±ط§ط¨ط· ط±ط¨ط· ط­ط³ط§ط¨ظƒ ط¨ظ…ظƒطھط¨ظ†ط§ ط¹ظ„ظ‰ ط£ظ…ظٹظ† ط§ظ„ط³ط±:\n{client_link}"
                share_url = f"https://t.me/share/url?url={client_link}&text={share_text}"
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"âœ… *طھظ… ط¥ط¶ط§ظپط© ط§ظ„ط¹ظ…ظٹظ„!*\n\nًں”¹ ط§ظ„ظƒظˆط¯: `{code}`\nًں‘¤ {data['name']}\nًں“± {data['mobile']}",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("ًں“¤ ظ…ط´ط§ط±ظƒط© ط§ظ„ط±ط§ط¨ط· ظ…ط¹ ط§ظ„ط¹ظ…ظٹظ„", url=share_url)],
                        [InlineKeyboardButton("ًں”™ ط§ظ„ظ‚ط§ط¦ظ…ط©", callback_data="MENU-MAIN")],
                    ])
                )
                await N001(context, get_boss_id(context), f"ًں‘¤ ط¹ظ…ظٹظ„ ط¬ط¯ظٹط¯: {data['name']}\nًں”¹ ط§ظ„ظƒظˆط¯: {code}")
            else:
                await T001(context, chat_id, "â‌Œ ط­ط¯ط« ط®ط·ط£ ظپظٹ ط§ظ„ط­ظپط¸.")

    # â”€â”€â”€ F002 ط¹ط±ط¶ ط¨ظٹط§ظ†ط§طھ ط¹ظ…ظٹظ„ â”€â”€â”€
    elif routine == "F002":
        if step == "code":
            sheet_name = get_tenant_sheet(context, chat_id)
            client = P002("Clients", text, sheet_name)
            context.user_data.clear()
            if not client:
                await T002(context, chat_id, "â‌Œ ظƒظˆط¯ ط§ظ„ط¹ظ…ظٹظ„ ط؛ظٹط± ظ…ظˆط¬ظˆط¯.", back_btn)
                return
            msg = (
                f"ًں‘¤ *ط¨ظٹط§ظ†ط§طھ ط§ظ„ط¹ظ…ظٹظ„*\n\n"
                f"ًں”¹ ط§ظ„ظƒظˆط¯: `{client.get('client_code', text)}`\n"
                f"ًں‘¤ ط§ظ„ط§ط³ظ…: {client.get('client_name', 'â€”')}\n"
                f"ًںھھ ط§ظ„ط±ظ‚ظ… ط§ظ„ظ‚ظˆظ…ظٹ: {client.get('national_id', 'â€”')}\n"
                f"ًں“± ط§ظ„ظ…ظˆط¨ط§ظٹظ„: {client.get('mobile', 'â€”')}\n"
                f"ًںڈ  ط§ظ„ط¹ظ†ظˆط§ظ†: {client.get('address', 'â€”')}\n"
                f"ًں“… طھط§ط±ظٹط® ط§ظ„طھط³ط¬ظٹظ„: {client.get('date_added', 'â€”')}"
            )
            await T002(context, chat_id, msg, back_btn)

    # â”€â”€â”€ F003 طھط¹ط¯ظٹظ„ ط¨ظٹط§ظ†ط§طھ ط¹ظ…ظٹظ„ â”€â”€â”€
    elif routine == "F003":
        if step == "code":
            sheet_name = get_tenant_sheet(context, chat_id)
            client = P002("Clients", text, sheet_name)
            if not client:
                await T002(context, chat_id, "â‌Œ ظƒظˆط¯ ط§ظ„ط¹ظ…ظٹظ„ ط؛ظٹط± ظ…ظˆط¬ظˆط¯.", back_btn)
                context.user_data.clear()
                return
            data["client_code"] = text
            data["client"] = client
            context.user_data["step"] = "field"
            await T002(context, chat_id,
                f"âœ… ط§ظ„ط¹ظ…ظٹظ„: *{client.get('client_name', '')}*\n\nط§ط®طھط± ط§ظ„ط­ظ‚ظ„ ظ„ظ„طھط¹ط¯ظٹظ„:",
                [
                    [{"text": "ًں‘¤ ط§ظ„ط§ط³ظ…", "callback_data": "EDIT-name"}],
                    [{"text": "ًں“± ط§ظ„ظ…ظˆط¨ط§ظٹظ„", "callback_data": "EDIT-mobile"}],
                    [{"text": "ًںڈ  ط§ظ„ط¹ظ†ظˆط§ظ†", "callback_data": "EDIT-address"}],
                    [{"text": "â‌Œ ط¥ظ„ط؛ط§ط،", "callback_data": "MENU-MAIN"}],
                ]
            )
        elif step == "edit_name":
            if not V001(text):
                await T001(context, chat_id, "â‌Œ ط§ظ„ط§ط³ظ… ظ‚طµظٹط±:")
                return
            sheet_name = get_tenant_sheet(context, chat_id)
            client_code = data.get("client_code")
            records = P005("Clients", sheet_name)
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(client_code):
                    P004("Clients", i, 2, text, sheet_name)
                    break
            context.user_data.clear()
            await T002(context, chat_id, f"âœ… *طھظ… طھط¹ط¯ظٹظ„ ط§ظ„ط§ط³ظ…!*\n\nًں‘¤ {text}", back_btn)
            await N001(context, get_boss_id(context), f"âœڈï¸ڈ طھط¹ط¯ظٹظ„ ط¹ظ…ظٹظ„ {client_code}\nًں‘¤ ط§ظ„ط§ط³ظ… ط§ظ„ط¬ط¯ظٹط¯: {text}")
        elif step == "edit_mobile":
            if not V003(text):
                await T001(context, chat_id, "â‌Œ ط±ظ‚ظ… ط§ظ„ظ…ظˆط¨ط§ظٹظ„ ط؛ظٹط± طµط­ظٹط­:")
                return
            sheet_name = get_tenant_sheet(context, chat_id)
            client_code = data.get("client_code")
            records = P005("Clients", sheet_name)
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(client_code):
                    P004("Clients", i, 4, text, sheet_name)
                    break
            context.user_data.clear()
            await T002(context, chat_id, f"âœ… *طھظ… طھط¹ط¯ظٹظ„ ط§ظ„ظ…ظˆط¨ط§ظٹظ„!*\n\nًں“± {text}", back_btn)
            await N001(context, get_boss_id(context), f"âœڈï¸ڈ طھط¹ط¯ظٹظ„ ط¹ظ…ظٹظ„ {client_code}\nًں“± ط§ظ„ظ…ظˆط¨ط§ظٹظ„ ط§ظ„ط¬ط¯ظٹط¯: {text}")
        elif step == "edit_address":
            if not V001(text):
                await T001(context, chat_id, "â‌Œ ط§ظ„ط¹ظ†ظˆط§ظ† ظ‚طµظٹط±:")
                return
            sheet_name = get_tenant_sheet(context, chat_id)
            client_code = data.get("client_code")
            records = P005("Clients", sheet_name)
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(client_code):
                    P004("Clients", i, 5, text, sheet_name)
                    break
            context.user_data.clear()
            await T002(context, chat_id, f"âœ… *طھظ… طھط¹ط¯ظٹظ„ ط§ظ„ط¹ظ†ظˆط§ظ†!*\n\nًںڈ  {text}", back_btn)
            await N001(context, get_boss_id(context), f"âœڈï¸ڈ طھط¹ط¯ظٹظ„ ط¹ظ…ظٹظ„ {client_code}\nًںڈ  ط§ظ„ط¹ظ†ظˆط§ظ† ط§ظ„ط¬ط¯ظٹط¯: {text}")

    # â”€â”€â”€ RA001 ط¥ط¶ط§ظپط© ظ…ط³ط§ط¹ط¯ â”€â”€â”€
    elif routine == "RA001":
        if step == "name":
            if not V001(text):
                await T001(context, chat_id, "â‌Œ ط§ظ„ط§ط³ظ… ظ‚طµظٹط±:")
                return
            data["name"] = text
            context.user_data["step"] = "bar_number"
            await T002(context, chat_id, "ًں”¢ ط£ط¯ط®ظ„ *ط±ظ‚ظ… ط§ظ„ظ†ظ‚ط§ط¨ط©*:", cancel_btn)
        elif step == "bar_number":
            data["bar_number"] = text
            context.user_data["step"] = "mobile"
            await T002(context, chat_id, "ًں“± ط£ط¯ط®ظ„ *ط±ظ‚ظ… ط§ظ„ظ…ظˆط¨ط§ظٹظ„*:", cancel_btn)
        elif step == "mobile":
            if not V003(text):
                await T001(context, chat_id, "â‌Œ ط±ظ‚ظ… ط؛ظٹط± طµط­ظٹط­:")
                return
            data["mobile"] = text
            sheet_name = get_tenant_sheet(context, chat_id)
            tenant_code = context.user_data.get("tenant", {}).get("tenant_code", "")
            code = G001("As", "Assistants", sheet_name)
            ok = P003("Assistants", [code, data["name"], data["bar_number"], data["mobile"], datetime.now().strftime("%Y-%m-%d %H:%M")], sheet_name)
            context.user_data.clear()
            if ok:
                assistant_link = f"https://t.me/amin_alsir_bot?start=assistant_{tenant_code}_{code}"
                share_text = f"ط±ط§ط¨ط· ط±ط¨ط· ط­ط³ط§ط¨ظƒ ظƒظ…ط³ط§ط¹ط¯ ط¨ظ…ظƒطھط¨ظ†ط§ ط¹ظ„ظ‰ ط£ظ…ظٹظ† ط§ظ„ط³ط±:\n{assistant_link}"
                share_url = f"https://t.me/share/url?url={assistant_link}&text={share_text}"
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"âœ… *طھظ… ط¥ط¶ط§ظپط© ط§ظ„ظ…ط³ط§ط¹ط¯!*\n\nًں”¹ ط§ظ„ظƒظˆط¯: `{code}`\nًں‘¤ {data['name']}\nًں”¢ {data['bar_number']}\nًں“± {data['mobile']}",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("ًں“¤ ظ…ط´ط§ط±ظƒط© ط§ظ„ط±ط§ط¨ط· ظ…ط¹ ط§ظ„ظ…ط³ط§ط¹ط¯", url=share_url)],
                        [InlineKeyboardButton("ًں”™ ط§ظ„ظ‚ط§ط¦ظ…ط©", callback_data="MENU-MAIN")],
                    ])
                )
                await N001(context, get_boss_id(context), f"ًں‘¥ ظ…ط³ط§ط¹ط¯ ط¬ط¯ظٹط¯: {data['name']}\nًں”¹ ط§ظ„ظƒظˆط¯: {code}")
            else:
                await T001(context, chat_id, "â‌Œ ط­ط¯ط« ط®ط·ط£.")

    # â”€â”€â”€ RA002 ط¹ط±ط¶ ط¨ظٹط§ظ†ط§طھ ظ…ط³ط§ط¹ط¯ â”€â”€â”€
    elif routine == "RA002":
        if step == "code":
            sheet_name = get_tenant_sheet(context, chat_id)
            assistant = P002("Assistants", text, sheet_name)
            context.user_data.clear()
            if not assistant:
                await T002(context, chat_id, "â‌Œ ظƒظˆط¯ ط§ظ„ظ…ط³ط§ط¹ط¯ ط؛ظٹط± ظ…ظˆط¬ظˆط¯.", back_btn)
                return
            msg = (
                f"ًں‘¥ *ط¨ظٹط§ظ†ط§طھ ط§ظ„ظ…ط³ط§ط¹ط¯*\n\n"
                f"ًں”¹ ط§ظ„ظƒظˆط¯: `{assistant.get('assistant_code', text)}`\n"
                f"ًں‘¤ ط§ظ„ط§ط³ظ…: {assistant.get('assistant_name', 'â€”')}\n"
                f"ًں”¢ ط±ظ‚ظ… ط§ظ„ظ†ظ‚ط§ط¨ط©: {assistant.get('bar_number', 'â€”')}\n"
                f"ًں“± ط§ظ„ظ…ظˆط¨ط§ظٹظ„: {assistant.get('mobile', 'â€”')}\n"
                f"ًں“… طھط§ط±ظٹط® ط§ظ„طھط³ط¬ظٹظ„: {assistant.get('date_added', 'â€”')}"
            )
            await T002(context, chat_id, msg, back_btn)

    # â”€â”€â”€ RT001 ط¥ط¶ط§ظپط© ظ…ظˆط¶ظˆط¹ â”€â”€â”€
    elif routine == "RT001":
        if step == "client_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            client = P002("Clients", text, sheet_name)
            if not client:
                await T001(context, chat_id, "â‌Œ ظƒظˆط¯ ط§ظ„ط¹ظ…ظٹظ„ ط؛ظٹط± ظ…ظˆط¬ظˆط¯:")
                return
            data["client_code"] = text
            data["client_name"] = client.get("client_name", "")
            context.user_data["step"] = "title"
            await T002(context, chat_id, f"âœ… ط§ظ„ط¹ظ…ظٹظ„: {data['client_name']}\n\nط£ط¯ط®ظ„ *ط¹ظ†ظˆط§ظ† ط§ظ„ظ…ظˆط¶ظˆط¹*:", cancel_btn)
        elif step == "title":
            if not V001(text):
                await T001(context, chat_id, "â‌Œ ط§ظ„ط¹ظ†ظˆط§ظ† ظ‚طµظٹط±:")
                return
            data["title"] = text
            context.user_data["step"] = "event_type"
            await T002(context, chat_id, "ًں“‹ ط£ط¯ط®ظ„ *ظ†ظˆط¹ ط§ظ„ظ…ظˆط¶ظˆط¹* (ظ…ط«ط§ظ„: ط·ظ„ط§ظ‚ / ظ…ظٹط±ط§ط« / ط¹ظ‚ط§ط±):", cancel_btn)
        elif step == "event_type":
            data["event_type"] = text
            sheet_name = get_tenant_sheet(context, chat_id)
            code = G001("Tp", "Topics", sheet_name)
            ok = P003("Topics", [code, data["client_code"], data["client_name"], data["title"], data["event_type"], "ط¬ط¯ظٹط¯", datetime.now().strftime("%Y-%m-%d %H:%M")], sheet_name)
            context.user_data.clear()
            if ok:
                await T002(context, chat_id, f"âœ… *طھظ… ط¥ط¶ط§ظپط© ط§ظ„ظ…ظˆط¶ظˆط¹!*\n\nًں”¹ ط§ظ„ظƒظˆط¯: `{code}`\nًں“‹ {data['title']}\nًں‘¤ {data['client_name']}", back_btn)
                await N001(context, get_boss_id(context), f"ًں“پ ظ…ظˆط¶ظˆط¹ ط¬ط¯ظٹط¯: {data['title']}\nًں”¹ ط§ظ„ظƒظˆط¯: {code}\nًں‘¤ ط§ظ„ط¹ظ…ظٹظ„: {data['client_name']}")
            else:
                await T001(context, chat_id, "â‌Œ ط­ط¯ط« ط®ط·ط£.")

    # â”€â”€â”€ RT002 ط¹ط±ط¶ ظ…ظˆط¶ظˆط¹ط§طھ ط¹ظ…ظٹظ„ â”€â”€â”€
    elif routine == "RT002":
        if step == "client_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            topics = P006("Topics", "client_code", text, sheet_name)
            context.user_data.clear()
            if not topics:
                await T002(context, chat_id, "â‌Œ ظ„ط§ طھظˆط¬ط¯ ظ…ظˆط¶ظˆط¹ط§طھ ظ„ظ‡ط°ط§ ط§ظ„ط¹ظ…ظٹظ„.", back_btn)
                return
            msg = f"ًں“‹ *ظ…ظˆط¶ظˆط¹ط§طھ ط§ظ„ط¹ظ…ظٹظ„* `{text}`:\n\n"
            for t in topics:
                msg += f"ًں”¹ `{t.get('topic_code','â€”')}` â€” {t.get('service_name', t.get('title','â€”'))} [{t.get('status','â€”')}]\n"
            await T002(context, chat_id, msg, back_btn)

    # â”€â”€â”€ RT003 طھط؛ظٹظٹط± ط­ط§ظ„ط© ظ…ظˆط¶ظˆط¹ â”€â”€â”€
    elif routine == "RT003":
        if step == "topic_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            topic = P002("Topics", text, sheet_name)
            if not topic:
                await T002(context, chat_id, "â‌Œ ظƒظˆط¯ ط§ظ„ظ…ظˆط¶ظˆط¹ ط؛ظٹط± ظ…ظˆط¬ظˆط¯.", back_btn)
                context.user_data.clear()
                return
            data["topic_code"] = text
            data["topic_name"] = topic.get("service_name", topic.get("title", ""))
            context.user_data["step"] = "status"
            await T002(context, chat_id,
                f"ًں“‹ ط§ظ„ظ…ظˆط¶ظˆط¹: *{data['topic_name']}*\n\nط§ط®طھط± ط§ظ„ط­ط§ظ„ط© ط§ظ„ط¬ط¯ظٹط¯ط©:",
                [
                    [{"text": "ًں†• ط¬ط¯ظٹط¯",        "callback_data": "STATUS-ط¬ط¯ظٹط¯"}],
                    [{"text": "âڑ–ï¸ڈ ظ‚ظٹط¯ ط§ظ„ظ†ط¸ط±",   "callback_data": "STATUS-ظ‚ظٹط¯ ط§ظ„ظ†ط¸ط±"}],
                    [{"text": "âœ… ظ…ظ†طھظ‡ظٹ",        "callback_data": "STATUS-ظ…ظ†طھظ‡ظٹ"}],
                    [{"text": "ًں—„ï¸ڈ ظ…ط¤ط±ط´ظپ",       "callback_data": "STATUS-ظ…ط¤ط±ط´ظپ"}],
                    [{"text": "â‌Œ ط¥ظ„ط؛ط§ط،",        "callback_data": "MENU-MAIN"}],
                ]
            )

    # â”€â”€â”€ RT004 ط£ط±ط´ظپط© ظ…ظˆط¶ظˆط¹ â”€â”€â”€
    elif routine == "RT004":
        if step == "topic_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            topic = P002("Topics", text, sheet_name)
            if not topic:
                await T002(context, chat_id, "â‌Œ ظƒظˆط¯ ط§ظ„ظ…ظˆط¶ظˆط¹ ط؛ظٹط± ظ…ظˆط¬ظˆط¯.", back_btn)
                context.user_data.clear()
                return
            data["topic_code"] = text
            data["topic_name"] = topic.get("service_name", topic.get("title", ""))
            context.user_data["step"] = "confirm"
            await T002(context, chat_id,
                f"ًں—„ï¸ڈ ط§ظ„ظ…ظˆط¶ظˆط¹: *{data['topic_name']}*\n\nظ‡ظ„ طھط±ظٹط¯ ط£ط±ط´ظپط© ظ‡ط°ط§ ط§ظ„ظ…ظˆط¶ظˆط¹طں",
                [
                    [{"text": "âœ… طھط£ظƒظٹط¯ ط§ظ„ط£ط±ط´ظپط©", "callback_data": "ARCHIVE-CONFIRM"}],
                    [{"text": "â‌Œ ط¥ظ„ط؛ط§ط،",          "callback_data": "MENU-MAIN"}],
                ]
            )

    # â”€â”€â”€ RE001 ط¥ط¶ط§ظپط© ط­ط¯ط« â”€â”€â”€
    elif routine == "RE001":
        if step == "title":
            if not V001(text):
                await T001(context, chat_id, "â‌Œ ط§ظ„ط¹ظ†ظˆط§ظ† ظ‚طµظٹط±:")
                return
            data["title"] = text
            context.user_data["step"] = "topic_code"
            await T002(context, chat_id, "ًں“‹ ط£ط¯ط®ظ„ *ظƒظˆط¯ ط§ظ„ظ…ظˆط¶ظˆط¹* (ظ…ط«ط§ظ„: Tp-001):", cancel_btn)
        elif step == "topic_code":
            data["topic_code"] = text
            context.user_data["step"] = "client_name"
            await T002(context, chat_id, "ًں‘¤ ط£ط¯ط®ظ„ *ط§ط³ظ… ط§ظ„ط¹ظ…ظٹظ„*:", cancel_btn)
        elif step == "client_name":
            data["client_name"] = text
            context.user_data["step"] = "event_type"
            await T002(context, chat_id, "âڑ–ï¸ڈ ط£ط¯ط®ظ„ *ظ†ظˆط¹ ط§ظ„ط­ط¯ط«* (ظ…ط«ط§ظ„: ط¬ظ„ط³ط© / ظ…ظˆط¹ط¯ / طھط³ظ„ظٹظ…):", cancel_btn)
        elif step == "event_type":
            data["event_type"] = text
            context.user_data["step"] = "event_date"
            await T002(context, chat_id, "ًں“… ط£ط¯ط®ظ„ *طھط§ط±ظٹط® ط§ظ„ط­ط¯ط«* (DD/MM/YYYY):", cancel_btn)
        elif step == "event_date":
            if not V004(text):
                await T001(context, chat_id, "â‌Œ ط§ظ„طھط§ط±ظٹط® ط؛ظٹط± طµط­ظٹط­. ط§ط³طھط®ط¯ظ… DD/MM/YYYY:")
                return
            data["event_date"] = text
            context.user_data["step"] = "event_time"
            await T002(context, chat_id, "âڈ° ط£ط¯ط®ظ„ *ظˆظ‚طھ ط§ظ„ط­ط¯ط«* (ظ…ط«ط§ظ„: 10:00):", cancel_btn)
        elif step == "event_time":
            data["event_time"] = text
            context.user_data["step"] = "location"
            await T002(context, chat_id, "ًں“چ ط£ط¯ط®ظ„ *ظ…ظƒط§ظ† ط§ظ„ط­ط¯ط«*:", cancel_btn)
        elif step == "location":
            data["location"] = text
            sheet_name = get_tenant_sheet(context, chat_id)
            code = G001("Ev", "Events", sheet_name)
            ok = P003("Events", [code, data["event_date"], data["topic_code"], data["client_name"], data["event_type"], data["event_time"], data["location"]], sheet_name)
            context.user_data.clear()
            if ok:
                await T002(context, chat_id, f"âœ… *طھظ… ط¥ط¶ط§ظپط© ط§ظ„ط­ط¯ط«!*\n\nًں”¹ ط§ظ„ظƒظˆط¯: `{code}`\nًں“… {data['event_date']} â€” {data['event_type']}\nًں“چ {data['location']}", back_btn)
                await N001(context, get_boss_id(context), f"ًں“… ط­ط¯ط« ط¬ط¯ظٹط¯: {data['event_type']}\nًں“… {data['event_date']} â€” {data['location']}\nًں‘¤ {data['client_name']}")
            else:
                await T001(context, chat_id, "â‌Œ ط­ط¯ط« ط®ط·ط£.")

    # â”€â”€â”€ RE002 ظ†طھظٹط¬ط© ط­ط¯ط« â”€â”€â”€
    elif routine == "RE002":
        if step == "event_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            event = P002("Events", text, sheet_name)
            if not event:
                await T001(context, chat_id, "â‌Œ ظƒظˆط¯ ط§ظ„ط­ط¯ط« ط؛ظٹط± ظ…ظˆط¬ظˆط¯:")
                return
            data["event_code"] = text
            data["event_type"] = event.get("event_type", "")
            data["event_date"] = event.get("event_date", "")
            context.user_data["step"] = "result"
            await T002(context, chat_id, f"ًں“… ط§ظ„ط­ط¯ط«: {data['event_type']} â€” {data['event_date']}\n\nًں“‌ ط£ط¯ط®ظ„ *ظ†طھظٹط¬ط© ط§ظ„ط­ط¯ط«*:", cancel_btn)
        elif step == "result":
            if not V001(text):
                await T001(context, chat_id, "â‌Œ ط§ظ„ظ†طھظٹط¬ط© ظ‚طµظٹط±ط©:")
                return
            data["result"] = text
            sheet_name = get_tenant_sheet(context, chat_id)
            records = P005("Events", sheet_name)
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(data["event_code"]):
                    P004("Events", i, 8, text, sheet_name)
                    P004("Events", i, 9, "ظ…ظ†طھظ‡ظٹ", sheet_name)
                    break
            context.user_data.clear()
            await T002(context, chat_id, f"âœ… *طھظ… طھط³ط¬ظٹظ„ ط§ظ„ظ†طھظٹط¬ط©!*\n\nًں“‌ {data['result']}", back_btn)

    # â”€â”€â”€ RS001 ط¥ط±ط³ط§ظ„ ظ…ط±ظپظ‚ط§طھ â”€â”€â”€
    elif routine == "RS001":
        if step == "topic_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            topic = P002("Topics", text, sheet_name)
            if not topic:
                await T001(context, chat_id, "â‌Œ ظƒظˆط¯ ط§ظ„ظ…ظˆط¶ظˆط¹ ط؛ظٹط± ظ…ظˆط¬ظˆط¯:")
                return
            data["topic_code"] = text
            context.user_data["step"] = "description"
            await T002(context, chat_id, "ًں“¦ ط£ط¯ط®ظ„ *ظˆطµظپ ط§ظ„ظ…ط±ظپظ‚ط§طھ*:", cancel_btn)
        elif step == "description":
            if not V001(text):
                await T001(context, chat_id, "â‌Œ ط§ظ„ظˆطµظپ ظ‚طµظٹط±:")
                return
            data["description"] = text
            sheet_name = get_tenant_sheet(context, chat_id)
            code = G001("Sh", "Shipments", sheet_name)
            ok = P003("Shipments", [
                code, data["topic_code"], data["description"],
                "", datetime.now().strftime("%Y-%m-%d %H:%M"),
                "", "", "", "طµط§ط¯ط±",
            ], sheet_name)
            context.user_data.clear()
            if ok:
                await T002(context, chat_id, f"âœ… *طھظ… طھط³ط¬ظٹظ„ ط§ظ„ط´ط­ظ†ط©!*\n\nًں”¹ ط§ظ„ظƒظˆط¯: `{code}`\nًں“¦ {data['description']}", back_btn)
            else:
                await T001(context, chat_id, "â‌Œ ط­ط¯ط« ط®ط·ط£.")

    # â”€â”€â”€ RS002 ط§ط³طھظ„ط§ظ… ط´ط­ظ†ط© â”€â”€â”€
    elif routine == "RS002":
        if step == "shipment_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            shipment = P002("Shipments", text, sheet_name)
            if not shipment:
                await T002(context, chat_id, "â‌Œ ط±ظ‚ظ… ط§ظ„ط´ط­ظ†ط© ط؛ظٹط± ظ…ظˆط¬ظˆط¯.", back_btn)
                context.user_data.clear()
                return
            data["shipment_code"] = text
            records = P005("Shipments", sheet_name)
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(text):
                    P004("Shipments", i, 9, "ظ…ط³طھظ„ظ…", sheet_name)
                    P004("Shipments", i, 10, datetime.now().strftime("%Y-%m-%d %H:%M"), sheet_name)
                    break
            context.user_data.clear()
            await T002(context, chat_id, f"âœ… *طھظ… طھط³ط¬ظٹظ„ ط§ط³طھظ„ط§ظ… ط§ظ„ط´ط­ظ†ط©!*\n\nًں”¹ ط§ظ„ظƒظˆط¯: `{text}`\nًں“¦ {shipment.get('sender','â€”')}", back_btn)

    # â”€â”€â”€ RS003 طھطھط¨ط¹ ط´ط­ظ†ط© â”€â”€â”€
    elif routine == "RS003":
        if step == "shipment_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            shipment = P002("Shipments", text, sheet_name)
            context.user_data.clear()
            if not shipment:
                await T002(context, chat_id, "â‌Œ ط±ظ‚ظ… ط§ظ„ط´ط­ظ†ط© ط؛ظٹط± ظ…ظˆط¬ظˆط¯.", back_btn)
                return
            msg = (
                f"ًں“¦ *طھطھط¨ط¹ ط§ظ„ط´ط­ظ†ط©*\n\n"
                f"ًں”¹ ط§ظ„ظƒظˆط¯: `{text}`\n"
                f"ًں“‹ ط§ظ„ظ…ظˆط¶ظˆط¹: {shipment.get('topic_code','â€”')}\n"
                f"ًں“‌ ط§ظ„ظ…ط­طھظˆظ‰: {shipment.get('sender','â€”')}\n"
                f"ًں”„ ط§ظ„ط­ط§ظ„ط©: {shipment.get('receive_status','â€”')}\n"
                f"ًں“… طھط§ط±ظٹط® ط§ظ„ط¥ط±ط³ط§ظ„: {shipment.get('send_date','â€”')}"
            )
            await T002(context, chat_id, msg, back_btn)

    # â”€â”€â”€ RD002 ط·ظ„ط¨ ظ…ط³طھظ†ط¯ط§طھ â”€â”€â”€
    elif routine == "RD002":
        if step == "entity":
            if not V001(text):
                await T001(context, chat_id, "â‌Œ ط§ط³ظ… ط§ظ„ط¬ظ‡ط© ظ‚طµظٹط±:")
                return
            data["entity"] = text
            context.user_data["step"] = "description"
            await T002(context, chat_id, "ًں“„ ط£ط¯ط®ظ„ *ظˆطµظپ ط§ظ„ظ…ط³طھظ†ط¯ط§طھ ط§ظ„ظ…ط·ظ„ظˆط¨ط©*:", cancel_btn)
        elif step == "description":
            if not V001(text):
                await T001(context, chat_id, "â‌Œ ط§ظ„ظˆطµظپ ظ‚طµظٹط±:")
                return
            data["description"] = text
            sheet_name = get_tenant_sheet(context, chat_id)
            code = G001("Doc", "Documents", sheet_name)
            ok = P003("Documents", [code, data["entity"], data["description"], "ط·ظ„ط¨", datetime.now().strftime("%Y-%m-%d %H:%M")], sheet_name)
            context.user_data.clear()
            if ok:
                await T002(context, chat_id, f"âœ… *طھظ… طھط³ط¬ظٹظ„ ط§ظ„ط·ظ„ط¨!*\n\nًں”¹ ط§ظ„ظƒظˆط¯: `{code}`\nًں“„ ظ…ظ†: {data['entity']}", back_btn)
            else:
                await T001(context, chat_id, "â‌Œ ط­ط¯ط« ط®ط·ط£.")

    # â”€â”€â”€ RD003 ط§ظ„ظ…ظˆط§ظپظ‚ط© ط¹ظ„ظ‰ ظ…ط³طھظ†ط¯ â”€â”€â”€
    elif routine == "RD003":
        if step == "doc_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            doc = P002("Documents", text, sheet_name)
            if not doc:
                await T002(context, chat_id, "â‌Œ ظƒظˆط¯ ط§ظ„ظ…ط³طھظ†ط¯ ط؛ظٹط± ظ…ظˆط¬ظˆط¯.", back_btn)
                context.user_data.clear()
                return
            records = P005("Documents", sheet_name)
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(text):
                    P004("Documents", i, 6, "ظ…ظˆط§ظپظ‚ ط¹ظ„ظٹظ‡", sheet_name)
                    break
            context.user_data.clear()
            await T002(context, chat_id, f"âœ… *طھظ…طھ ط§ظ„ظ…ظˆط§ظپظ‚ط© ط¹ظ„ظ‰ ط§ظ„ظ…ط³طھظ†ط¯!*\n\nًں”¹ ط§ظ„ظƒظˆط¯: `{text}`\nًں“„ {doc.get('doc_name','â€”')}", back_btn)
            await N001(context, get_boss_id(context), f"âœ… ظ…ظˆط§ظپظ‚ط© ط¹ظ„ظ‰ ظ…ط³طھظ†ط¯\nًں”¹ ط§ظ„ظƒظˆط¯: {text}\nًں“„ {doc.get('doc_name','â€”')}")

    # â”€â”€â”€ RD004 ط±ظپط¶ ظ…ط³طھظ†ط¯ â”€â”€â”€
    elif routine == "RD004":
        if step == "doc_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            doc = P002("Documents", text, sheet_name)
            if not doc:
                await T002(context, chat_id, "â‌Œ ظƒظˆط¯ ط§ظ„ظ…ط³طھظ†ط¯ ط؛ظٹط± ظ…ظˆط¬ظˆط¯.", back_btn)
                context.user_data.clear()
                return
            data["doc_code"] = text
            data["doc_name"] = doc.get("doc_name", "â€”")
            context.user_data["step"] = "reason"
            await T002(context, chat_id, f"ًں“„ ط§ظ„ظ…ط³طھظ†ط¯: *{data['doc_name']}*\n\nًں“‌ ط£ط¯ط®ظ„ *ط³ط¨ط¨ ط§ظ„ط±ظپط¶*:", cancel_btn)
        elif step == "reason":
            if not V001(text):
                await T001(context, chat_id, "â‌Œ ط§ظ„ط³ط¨ط¨ ظ‚طµظٹط±:")
                return
            sheet_name = get_tenant_sheet(context, chat_id)
            records = P005("Documents", sheet_name)
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(data["doc_code"]):
                    P004("Documents", i, 6, "ظ…ط±ظپظˆط¶", sheet_name)
                    P004("Documents", i, 7, text, sheet_name)
                    break
            context.user_data.clear()
            await T002(context, chat_id, f"âœ… *طھظ… ط±ظپط¶ ط§ظ„ظ…ط³طھظ†ط¯!*\n\nًں”¹ ط§ظ„ظƒظˆط¯: `{data['doc_code']}`\nًں“‌ ط§ظ„ط³ط¨ط¨: {text}", back_btn)
            await N001(context, get_boss_id(context), f"â‌Œ ط±ظپط¶ ظ…ط³طھظ†ط¯\nًں”¹ ط§ظ„ظƒظˆط¯: {data['doc_code']}\nًں“‌ ط§ظ„ط³ط¨ط¨: {text}")

    # â”€â”€â”€ RD005 ط¹ط±ط¶ ظ…ط³طھظ†ط¯ط§طھ ظ…ظˆط¶ظˆط¹ â”€â”€â”€
    elif routine == "RD005":
        if step == "topic_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            docs = P006("Documents", "topic_code", text, sheet_name)
            context.user_data.clear()
            if not docs:
                await T002(context, chat_id, "â‌Œ ظ„ط§ طھظˆط¬ط¯ ظ…ط³طھظ†ط¯ط§طھ ظ„ظ‡ط°ط§ ط§ظ„ظ…ظˆط¶ظˆط¹.", back_btn)
                return
            msg = f"ًں“پ *ظ…ط³طھظ†ط¯ط§طھ ط§ظ„ظ…ظˆط¶ظˆط¹* `{text}`:\n\n"
            for d in docs:
                link = d.get("drive_link", "")
                name = d.get("doc_name", "â€”")
                status = d.get("status", "â€”")
                if link:
                    msg += f"ًں”¹ [{name}]({link}) â€” {status}\n"
                else:
                    msg += f"ًں”¹ {name} â€” {status}\n"
            await T002(context, chat_id, msg, back_btn)

    # â”€â”€â”€ RD006 ط£ط±ط´ظپط© ظ…ط³طھظ†ط¯ط§طھ â”€â”€â”€
    elif routine == "RD006":
        if step == "topic_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            docs = P006("Documents", "topic_code", text, sheet_name)
            if not docs:
                await T002(context, chat_id, "â‌Œ ظ„ط§ طھظˆط¬ط¯ ظ…ط³طھظ†ط¯ط§طھ ظ„ظ‡ط°ط§ ط§ظ„ظ…ظˆط¶ظˆط¹.", back_btn)
                context.user_data.clear()
                return
            data["topic_code"] = text
            data["doc_count"] = len(docs)
            context.user_data["step"] = "confirm"
            await T002(context, chat_id,
                f"ًں—„ï¸ڈ ط§ظ„ظ…ظˆط¶ظˆط¹: `{text}`\nًں“„ ط¹ط¯ط¯ ط§ظ„ظ…ط³طھظ†ط¯ط§طھ: {len(docs)}\n\nظ‡ظ„ طھط±ظٹط¯ ط£ط±ط´ظپط© ظƒظ„ ط§ظ„ظ…ط³طھظ†ط¯ط§طھطں",
                [
                    [{"text": "âœ… طھط£ظƒظٹط¯ ط§ظ„ط£ط±ط´ظپط©", "callback_data": "ARCHIVE-DOCS-CONFIRM"}],
                    [{"text": "â‌Œ ط¥ظ„ط؛ط§ط،",          "callback_data": "MENU-MAIN"}],
                ]
            )

    # â”€â”€â”€ RM001 ط·ظ„ط¨ ط¹ظ‡ط¯ط© â”€â”€â”€
    elif routine == "RM001":
        if step == "amount":
            if not V005(text):
                await T001(context, chat_id, "â‌Œ ط§ظ„ظ…ط¨ظ„ط؛ ط؛ظٹط± طµط­ظٹط­:")
                return
            data["amount"] = text
            context.user_data["step"] = "reason"
            await T002(context, chat_id, "ًں“‌ ط£ط¯ط®ظ„ *ط³ط¨ط¨ ط§ظ„ط¹ظ‡ط¯ط©*:", cancel_btn)
        elif step == "reason":
            if not V001(text):
                await T001(context, chat_id, "â‌Œ ط§ظ„ط³ط¨ط¨ ظ‚طµظٹط±:")
                return
            data["reason"] = text
            sheet_name = get_tenant_sheet(context, chat_id)
            code = G001("Fn", "Custody", sheet_name)
            ok = P003("Custody", [code, data["amount"], data["reason"], "ط·ظ„ط¨", datetime.now().strftime("%Y-%m-%d %H:%M")], sheet_name)
            context.user_data.clear()
            if ok:
                await T002(context, chat_id, f"âœ… *طھظ… ط·ظ„ط¨ ط§ظ„ط¹ظ‡ط¯ط©!*\n\nًں”¹ ط§ظ„ظƒظˆط¯: `{code}`\nًں’° {data['amount']} ط¬ظ†ظٹظ‡\nًں“‌ {data['reason']}", back_btn)
                await N001(context, get_boss_id(context), f"ًں’° ط·ظ„ط¨ ط¹ظ‡ط¯ط© ط¬ط¯ظٹط¯\nًں”¹ ط§ظ„ظƒظˆط¯: {code}\nًں’° ط§ظ„ظ…ط¨ظ„ط؛: {data['amount']} ط¬ظ†ظٹظ‡\nًں“‌ {data['reason']}")
            else:
                await T001(context, chat_id, "â‌Œ ط­ط¯ط« ط®ط·ط£.")

    # â”€â”€â”€ RM002 طھط³ظˆظٹط© ط¹ظ‡ط¯ط© â”€â”€â”€
    elif routine == "RM002":
        if step == "fund_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            fund = P002("Custody", text, sheet_name)
            if not fund:
                await T002(context, chat_id, "â‌Œ ظƒظˆط¯ ط§ظ„ط¹ظ‡ط¯ط© ط؛ظٹط± ظ…ظˆط¬ظˆط¯.", back_btn)
                context.user_data.clear()
                return
            data["fund_code"] = text
            data["amount"] = fund.get("amount", "â€”")
            context.user_data["step"] = "notes"
            await T002(context, chat_id, f"ًں’° ط§ظ„ط¹ظ‡ط¯ط©: {data['amount']} ط¬ظ†ظٹظ‡\n\nًں“‌ ط£ط¯ط®ظ„ *ظ…ظ„ط§ط­ط¸ط§طھ ط§ظ„طھط³ظˆظٹط©*:", cancel_btn)
        elif step == "notes":
            data["notes"] = text
            sheet_name = get_tenant_sheet(context, chat_id)
            records = P005("Custody", sheet_name)
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(data["fund_code"]):
                    P004("Custody", i, 4, "ظ…ط³ظˆظ‘ط§ط©", sheet_name)
                    P004("Custody", i, 6, text, sheet_name)
                    P004("Custody", i, 7, datetime.now().strftime("%Y-%m-%d %H:%M"), sheet_name)
                    break
            context.user_data.clear()
            await T002(context, chat_id, f"âœ… *طھظ… طھط³ظˆظٹط© ط§ظ„ط¹ظ‡ط¯ط©!*\n\nًں”¹ ط§ظ„ظƒظˆط¯: `{data['fund_code']}`\nًں’° {data['amount']} ط¬ظ†ظٹظ‡", back_btn)

    # â”€â”€â”€ RN001 ط¥ط´ط¹ط§ط± ظ„ظ„ط±ط¦ظٹط³ â”€â”€â”€
    elif routine == "RN001":
        if step == "text":
            if not V001(text):
                await T001(context, chat_id, "â‌Œ ط§ظ„ظ†طµ ظ‚طµظٹط±:")
                return
            await N001(context, get_boss_id(context), text)
            context.user_data.clear()
            await T002(context, chat_id, "âœ… *طھظ… ط¥ط±ط³ط§ظ„ ط§ظ„ط¥ط´ط¹ط§ط± ظ„ظ„ط±ط¦ظٹط³!*", back_btn)

    # â”€â”€â”€ RN002 ط¥ط´ط¹ط§ط± ظ„ظ„ط¹ظ…ظٹظ„ â”€â”€â”€
    elif routine == "RN002":
        if step == "client_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            client = P002("Clients", text, sheet_name)
            if not client:
                await T002(context, chat_id, "â‌Œ ظƒظˆط¯ ط§ظ„ط¹ظ…ظٹظ„ ط؛ظٹط± ظ…ظˆط¬ظˆط¯.", back_btn)
                context.user_data.clear()
                return
            data["client_code"] = text
            data["client_name"] = client.get("client_name", "")
            chat_id_client = client.get("telegram_chat_id", "")
            if not chat_id_client:
                await T002(context, chat_id, f"â‌Œ ط§ظ„ط¹ظ…ظٹظ„ {data['client_name']} ظ„ظٹط³ ظ„ط¯ظٹظ‡ Chat ID ظ…ط³ط¬ظ„.", back_btn)
                context.user_data.clear()
                return
            data["client_chat_id"] = chat_id_client
            context.user_data["step"] = "message"
            await T002(context, chat_id, f"âœ… ط§ظ„ط¹ظ…ظٹظ„: *{data['client_name']}*\n\nًں“‌ ط£ط¯ط®ظ„ *ظ†طµ ط§ظ„ط¥ط´ط¹ط§ط±*:", cancel_btn)
        elif step == "message":
            if not V001(text):
                await T001(context, chat_id, "â‌Œ ط§ظ„ظ†طµ ظ‚طµظٹط±:")
                return
            await N002(context, data["client_chat_id"], text)
            context.user_data.clear()
            await T002(context, chat_id, "âœ… *طھظ… ط¥ط±ط³ط§ظ„ ط§ظ„ط¥ط´ط¹ط§ط± ظ„ظ„ط¹ظ…ظٹظ„!*", back_btn)

    # â”€â”€â”€ RN003 ط¥ط´ط¹ط§ط± ظ„ظ„ظ…ط³ط§ط¹ط¯ â”€â”€â”€
    elif routine == "RN003":
        if step == "assistant_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            assistant = P002("Assistants", text, sheet_name)
            if not assistant:
                await T002(context, chat_id, "â‌Œ ظƒظˆط¯ ط§ظ„ظ…ط³ط§ط¹ط¯ ط؛ظٹط± ظ…ظˆط¬ظˆط¯.", back_btn)
                context.user_data.clear()
                return
            data["assistant_code"] = text
            data["assistant_name"] = assistant.get("assistant_name", "")
            chat_id_assistant = assistant.get("telegram_chat_id", "")
            if not chat_id_assistant:
                await T002(context, chat_id, f"â‌Œ ط§ظ„ظ…ط³ط§ط¹ط¯ {data['assistant_name']} ظ„ظٹط³ ظ„ط¯ظٹظ‡ Chat ID ظ…ط³ط¬ظ„.", back_btn)
                context.user_data.clear()
                return
            data["assistant_chat_id"] = chat_id_assistant
            context.user_data["step"] = "message"
            await T002(context, chat_id, f"âœ… ط§ظ„ظ…ط³ط§ط¹ط¯: *{data['assistant_name']}*\n\nًں“‌ ط£ط¯ط®ظ„ *ظ†طµ ط§ظ„ط¥ط´ط¹ط§ط±*:", cancel_btn)
        elif step == "message":
            if not V001(text):
                await T001(context, chat_id, "â‌Œ ط§ظ„ظ†طµ ظ‚طµظٹط±:")
                return
            await N003(context, data["assistant_chat_id"], text)
            context.user_data.clear()
            await T002(context, chat_id, "âœ… *طھظ… ط¥ط±ط³ط§ظ„ ط§ظ„ط¥ط´ط¹ط§ط± ظ„ظ„ظ…ط³ط§ط¹ط¯!*", back_btn)

    # â”€â”€â”€ RD001 ط±ظپط¹ ظ…ط³طھظ†ط¯ ظˆط§ط±ط¯ â”€â”€â”€
    elif routine == "RD001":
        if step == "topic_code":
            sheet_name = get_tenant_sheet(context, chat_id)
            topic = P002("Topics", text, sheet_name)
            if not topic:
                await T001(context, chat_id, "â‌Œ ظƒظˆط¯ ط§ظ„ظ…ظˆط¶ظˆط¹ ط؛ظٹط± ظ…ظˆط¬ظˆط¯:")
                return
            data["topic_code"] = text
            data["topic_name"] = topic.get("service_name", topic.get("title", ""))
            context.user_data["step"] = "doc_name"
            await T002(context, chat_id, f"âœ… ط§ظ„ظ…ظˆط¶ظˆط¹: *{data['topic_name']}*\n\nًں“„ ط£ط¯ط®ظ„ *ط§ط³ظ… ط§ظ„ظ…ط³طھظ†ط¯*:", cancel_btn)
        elif step == "doc_name":
            if not V001(text):
                await T001(context, chat_id, "â‌Œ ط§ظ„ط§ط³ظ… ظ‚طµظٹط±:")
                return
            data["doc_name"] = text
            context.user_data["step"] = "file"
            await T002(context, chat_id, "ًں“ژ ط£ط±ط³ظ„ *ط§ظ„ظ…ظ„ظپ ط£ظˆ ط§ظ„طµظˆط±ط©* ط§ظ„ط¢ظ†:", cancel_btn)

# â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
# Callback Router
# â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat_id

    # â”€â”€â”€ ط§ط®طھظٹط§ط± ط§ظ„ط¯ظˆظ„ط© â€” ط¥ظƒظ…ط§ظ„ طھط³ط¬ظٹظ„ ظ…ظƒطھط¨ ط¬ط¯ظٹط¯ â”€â”€â”€
    if data.startswith("COUNTRY-"):
        country = data.replace("COUNTRY-", "")
        office_name = context.user_data.get("data", {}).get("office_name", "")

        # NEW: create a dedicated Sheet + Drive folder for this new tenant
        sheet_name, sheet_id = MT006(office_name, str(chat_id))
        folder_id = MT007(str(chat_id))

        if not sheet_name or not folder_id:
            print(f"FAIL: tenant resources not created for chat_id={chat_id} (sheet_name={sheet_name}, folder_id={folder_id})")
            await query.edit_message_text(
                "ط­ط¯ط« ط®ط·ط£ ظپظٹ ط¥ظ†ط´ط§ط، ط§ظ„ظ…ظˆط§ط±ط¯ ط§ظ„ط®ط§طµط© ط¨ظ…ظƒطھط¨ظƒ. ط­ط§ظˆظ„ ظ…ط±ط© ط£ط®ط±ظ‰ ظ„ط§ط­ظ‚ط§ظ‹."
            )
            return

        # â”€â”€ طھط­ط¯ظٹط¯ ط­ط§ظ„ط© ط§ظ„طھط³ط¬ظٹظ„: trial ط£ظ… pending_payment â”€â”€
        # ظ„ظˆ ط§ظ„ظ…ط³طھط®ط¯ظ… ط¬ط§ظٹ ظ…ظ† ظƒط§ط±طھ ط¨ط§ظ‚ط© ظ…ط­ط¯ط¯ط© (plan_monthly / plan_yearly) ظ‡طھظƒظˆظ†
        # selected_billing_cycle ظ…ظˆط¬ظˆط¯ط© ظپظٹ user_data (ط§طھط³ط¬ظ„طھ ظپظٹ ط¯ط§ظ„ط© start()).
        # ظ„ظˆ ط¬ط§ظٹ ظ…ظ† "ط§ط¨ط¯ط£ ط§ظ„ط¢ظ† ظ…ط¬ط§ظ†ط§ظ‹" ظ‡طھظƒظˆظ† ط؛ظٹط± ظ…ظˆط¬ظˆط¯ط©طŒ ظپط§ظ„ط­ط§ظ„ط© ط§ظ„ط§ظپطھط±ط§ط¶ظٹط© trial.
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
                # طھظˆظ„ظٹط¯ ط±ط§ط¨ط· ط¯ظپط¹ Paymob ظپط¹ظ„ظٹ ظ…ط¨ط§ط´ط± (ط¨ط¯ظˆظ† ط£ظٹ طµظپط­ط© ظˆط³ظٹط·ط©)
                pay_link = create_payment_link(code, billing_cycle, office_name)
                cycle_label = "ط´ظ‡ط±ظٹ" if billing_cycle == "monthly" else "ط³ظ†ظˆظٹ (ط§ظ„ط¨ط§ظ‚ط© ط§ظ„ط°ظ‡ط¨ظٹط©)"

                if pay_link:
                    await query.edit_message_text(
                        f"âœ… *طھظ… طھط³ط¬ظٹظ„ ظ…ظƒطھط¨ظƒ ط¨ظ†ط¬ط§ط­!*\n\n"
                        f"ًںڈ¢ {office_name}\n"
                        f"ًںŒچ {country}\n"
                        f"ًں”¹ ط§ظ„ظƒظˆط¯: `{code}`\n"
                        f"ًں“¦ ط§ظ„ط¨ط§ظ‚ط© ط§ظ„ظ…ط®طھط§ط±ط©: {cycle_label}\n\n"
                        f"ظ„ظ„ظ…طھط§ط¨ط¹ط©طŒ ظٹط±ط¬ظ‰ ط¥ظƒظ…ط§ظ„ ط§ظ„ط¯ظپط¹ ط¹ط¨ط± ط§ظ„ط±ط§ط¨ط· ط§ظ„طھط§ظ„ظٹ:\n"
                        f"ًں”— {pay_link}\n\n"
                        f"ط¨ط¹ط¯ ط¥طھظ…ط§ظ… ط§ظ„ط¯ظپط¹ ط¨ظ†ط¬ط§ط­طŒ ط³ظٹطھظ… طھظپط¹ظٹظ„ ط­ط³ط§ط¨ظƒ ظپظˆط±ط§ظ‹ ظˆطھظ„ظ‚ط§ط¦ظٹط§ظ‹.",
                        parse_mode="Markdown",
                    )
                else:
                    # ظپط´ظ„ طھظˆظ„ظٹط¯ ط±ط§ط¨ط· ط§ظ„ط¯ظپط¹ â€” ظ†ظˆط¶ط­ ظ„ظ„ط¹ظ…ظٹظ„ ظˆظ†ظˆط¬ظ‡ظ‡ ظ„ط¥ط¹ط§ط¯ط© ط§ظ„ظ…ط­ط§ظˆظ„ط©
                    await query.edit_message_text(
                        f"âœ… طھظ… طھط³ط¬ظٹظ„ ظ…ظƒطھط¨ظƒ ط¨ظ†ط¬ط§ط­ (ط§ظ„ظƒظˆط¯: `{code}`)\n\n"
                        f"âڑ ï¸ڈ ط­ط¯ط« ط®ط·ط£ ظ…ط¤ظ‚طھ ظپظٹ طھظˆظ„ظٹط¯ ط±ط§ط¨ط· ط§ظ„ط¯ظپط¹. "
                        f"ظٹط±ط¬ظ‰ ط§ظ„ظ…ط­ط§ظˆظ„ط© ظ…ط±ط© ط£ط®ط±ظ‰ ظ…ظ† ط®ظ„ط§ظ„ ط§ظ„ط£ظ…ط± /pay ط£ظˆ ط§ظ„طھظˆط§طµظ„ ظ…ط¹ ط§ظ„ط¯ط¹ظ….",
                        parse_mode="Markdown",
                    )
            else:
                # trial â€” ظٹط³طھط®ط¯ظ… ط§ظ„ط¨ظˆطھ ط¨ط§ظ„ظƒط§ظ…ظ„ ظ„ظ…ط¯ط© TRIAL_DAYS ط£ظٹط§ظ…
                dashboard_url = build_boss_dashboard_url(chat_id, tenant)
                await query.edit_message_text(
                    f"âœ… <b>طھظ… طھط³ط¬ظٹظ„ ظ…ظƒطھط¨ظƒ ط¨ظ†ط¬ط§ط­!</b>\n\n"
                    f"ًںڈ¢ {office_name}\n"
                    f"ًںŒچ {country}\n"
                    f"ًں”¹ ط§ظ„ظƒظˆط¯: <code>{code}</code>\n\n"
                    f"ًںژپ ظ„ط¯ظٹظƒ <b>{TRIAL_DAYS} ط£ظٹط§ظ… ظ…ط¬ط§ظ†ظٹط©</b> ظ„طھط¬ط±ط¨ط© ط§ظ„ظ†ط¸ط§ظ… ط¨ط§ظ„ظƒط§ظ…ظ„.\n\n"
                    f"ًں”— ظ„ظˆط­ط© ط§ظ„ظ‚ظٹط§ط¯ط© ط§ظ„ظƒط§ظ…ظ„ط©:\n<a href=\"{dashboard_url}\">{dashboard_url}</a>\n\n"
                    f"ط§ط®طھط± ظ…ظ† ظ„ظˆط­ط© ط§ظ„ظ‚ظٹط§ط¯ط©:",
                    parse_mode="HTML",
                    reply_markup=main_keyboard(),
                )

            await context.bot.send_message(
                chat_id=BOSS_CHAT_ID,
                text=(
                    f"ًں”” *ط¥ط´ط¹ط§ط± â€” ط£ظ…ظٹظ† ط§ظ„ط³ط±*\n\n"
                    f"ًںڈ¢ ظ…ظƒطھط¨ ط¬ط¯ظٹط¯ ط§ظ†ط¶ظ… ظ„ظ„ظ…ظ†طµط©!\n"
                    f"ًںڈ›ï¸ڈ {office_name}\n"
                    f"ًںŒچ {country}\n"
                    f"ًں”¹ ط§ظ„ظƒظˆط¯: {code}\n"
                    f"ًں“‹ ط§ظ„ط­ط§ظ„ط©: {'ظپظٹ ط§ظ†طھط¸ط§ط± ط§ظ„ط¯ظپط¹' if initial_status == 'pending_payment' else 'طھط¬ط±ط¨ط© ظ…ط¬ط§ظ†ظٹط©'}"
                ),
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                "â‌Œ ط­ط¯ط« ط®ط·ط£ ظپظٹ ط§ظ„طھط³ط¬ظٹظ„. ط£ط±ط³ظ„ /start ظ„ظ„ظ…ط­ط§ظˆظ„ط© ظ…ط±ط© ط£ط®ط±ظ‰."
            )
        return

    # â”€â”€â”€ ط£ط±ط´ظپط© ظ…ط³طھظ†ط¯ط§طھ ظ…ظˆط¶ظˆط¹ â”€â”€â”€
    if data == "ARCHIVE-DOCS-CONFIRM":
        sheet_name = get_tenant_sheet(context, chat_id)
        topic_code = context.user_data.get("data", {}).get("topic_code", "")
        if topic_code:
            records = P005("Documents", sheet_name)
            for i, r in enumerate(records, start=2):
                if str(r.get("topic_code", "")) == str(topic_code):
                    P004("Documents", i, 6, "ظ…ط¤ط±ط´ظپ", sheet_name)
        context.user_data.clear()
        await query.edit_message_text(
            f"âœ… طھظ… ط£ط±ط´ظپط© ظ…ط³طھظ†ط¯ط§طھ ط§ظ„ظ…ظˆط¶ظˆط¹ `{topic_code}`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ًں”™ ط§ظ„ظ‚ط§ط¦ظ…ط©", callback_data="MENU-MAIN")]])
        )
        await N001(context, get_boss_id(context), f"ًں—„ï¸ڈ طھظ… ط£ط±ط´ظپط© ظ…ط³طھظ†ط¯ط§طھ ط§ظ„ظ…ظˆط¶ظˆط¹: {topic_code}")
        return

    # â”€â”€â”€ ط£ط±ط´ظپط© ظ…ظˆط¶ظˆط¹ â”€â”€â”€
    if data == "ARCHIVE-CONFIRM":
        sheet_name = get_tenant_sheet(context, chat_id)
        topic_code = context.user_data.get("data", {}).get("topic_code", "")
        topic_name = context.user_data.get("data", {}).get("topic_name", "")
        if topic_code:
            records = P005("Topics", sheet_name)
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(topic_code):
                    P004("Topics", i, 6, "ظ…ط¤ط±ط´ظپ", sheet_name)
                    P004("Topics", i, 7, datetime.now().strftime("%Y-%m-%d %H:%M"), sheet_name)
                    break
        context.user_data.clear()
        await query.edit_message_text(
            f"âœ… طھظ… ط£ط±ط´ظپط© ط§ظ„ظ…ظˆط¶ظˆط¹ `{topic_code}` â€” *{topic_name}*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ًں”™ ط§ظ„ظ‚ط§ط¦ظ…ط©", callback_data="MENU-MAIN")]])
        )
        await N001(context, get_boss_id(context), f"ًں—„ï¸ڈ طھظ… ط£ط±ط´ظپط© ط§ظ„ظ…ظˆط¶ظˆط¹\nًں”¹ ط§ظ„ظƒظˆط¯: {topic_code}\nًں“‹ {topic_name}")
        return

    if data.startswith("STATUS-"):
        sheet_name = get_tenant_sheet(context, chat_id)
        new_status = data.replace("STATUS-", "")
        topic_code = context.user_data.get("data", {}).get("topic_code", "")
        if topic_code:
            records = P005("Topics", sheet_name)
            for i, r in enumerate(records, start=2):
                if str(list(r.values())[0]) == str(topic_code):
                    P004("Topics", i, 6, new_status, sheet_name)
                    break
        context.user_data.clear()
        await query.edit_message_text(
            f"âœ… طھظ… طھط؛ظٹظٹط± ط­ط§ظ„ط© ط§ظ„ظ…ظˆط¶ظˆط¹ `{topic_code}` ط¥ظ„ظ‰ *{new_status}*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ًں”™ ط§ظ„ظ‚ط§ط¦ظ…ط©", callback_data="MENU-MAIN")]])
        )
        return

    if data.startswith("EDIT-"):
        field = data.replace("EDIT-", "")
        field_names = {"name": "ط§ظ„ط§ط³ظ…", "mobile": "ط§ظ„ظ…ظˆط¨ط§ظٹظ„", "address": "ط§ظ„ط¹ظ†ظˆط§ظ†"}
        context.user_data["step"] = f"edit_{field}"
        await query.edit_message_text(
            f"âœڈï¸ڈ ط£ط¯ط®ظ„ *{field_names.get(field, field)}* ط§ظ„ط¬ط¯ظٹط¯:",
            parse_mode="Markdown"
        )
        return

    if data == "MENU-MAIN":
        context.user_data.pop("routine", None)
        context.user_data.pop("step", None)
        context.user_data.pop("data", None)
        await query.edit_message_text("ظ„ظˆط­ط© ط§ظ„ظ‚ظٹط§ط¯ط©:", reply_markup=main_keyboard())
    elif data == "MENU-SETTINGS":
        await query.edit_message_text("âڑ™ï¸ڈ *ط§ظ„ط¥ط¹ط¯ط§ط¯ط§طھ*\nط§ط®طھط± ط§ظ„ط¹ظ…ظ„ظٹط©:", parse_mode="Markdown", reply_markup=settings_keyboard())
    elif data == "MENU-EVENTS":
        await query.edit_message_text("ًں“… *ط§ظ„ط£ط­ط¯ط§ط«*\nط§ط®طھط± ط§ظ„ط¹ظ…ظ„ظٹط©:", parse_mode="Markdown", reply_markup=events_keyboard())
    elif data == "MENU-SERVICES":
        await query.edit_message_text("ًں“‹ *ط§ظ„ط®ط¯ظ…ط§طھ*\nط§ط®طھط± ط§ظ„ط®ط¯ظ…ط©:", parse_mode="Markdown", reply_markup=services_keyboard())
    elif data == "MENU-REPORTS":
        await query.edit_message_text("ًں“ٹ ط§ظ„طھظ‚ط§ط±ظٹط± â€” ظ‚ط±ظٹط¨ط§ظ‹! ًںڑ§", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ًں”™ ط±ط¬ظˆط¹", callback_data="MENU-MAIN")]]))
    elif data == "MENU-INBOX":
        await query.edit_message_text("ًں’¬ *ط¨ط±ظٹط¯ ط§ظ„ط¥ط´ط¹ط§ط±ط§طھ*\nط§ط®طھط± ظ†ظˆط¹ ط§ظ„ط¥ط´ط¹ط§ط±:", parse_mode="Markdown", reply_markup=notifications_keyboard())
    elif data in ROUTE_MAP:
        await ROUTE_MAP[data](update, context)
    else:
        await query.edit_message_text(
            f"âڈ³ ط§ظ„ظƒظˆط¯ *{data}* ظ‚ظٹط¯ ط§ظ„طھط·ظˆظٹط±.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ًں”™ ط±ط¬ظˆط¹", callback_data="MENU-MAIN")]])
        )

# â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
# File Router
# â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
async def file_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    routine = context.user_data.get("routine")
    step    = context.user_data.get("step")
    if not routine or step != "file":
        return

    chat_id  = update.effective_chat.id
    data     = context.user_data.setdefault("data", {})
    back_btn = [[{"text": "ًں”™ ط§ظ„ظ‚ط§ط¦ظ…ط©", "callback_data": "MENU-MAIN"}]]

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
            await T001(context, chat_id, "â‌Œ ط£ط±ط³ظ„ ظ…ظ„ظپط§ظ‹ ط£ظˆ طµظˆط±ط© طµط§ظ„ط­ط©:")
            return

        await T001(context, chat_id, "âڈ³ ط¬ط§ط±ظٹ ط±ظپط¹ ط§ظ„ظ…ظ„ظپ...")

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
                await T002(context, chat_id, "â‌Œ ظپط´ظ„ ط±ظپط¹ ط§ظ„ظ…ظ„ظپ ط¹ظ„ظ‰ Drive.", back_btn)
                context.user_data.clear()
                return

            code = G001("Doc", "Documents", sheet_name)
            P003("Documents", [
                code, topic_code, data.get("doc_name", file_name),
                file_name, drive_link, "ظˆط§ط±ط¯", "TRANSIT",
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ], sheet_name)

            context.user_data.clear()
            await T002(context, chat_id,
                f"âœ… *طھظ… ط±ظپط¹ ط§ظ„ظ…ط³طھظ†ط¯!*\n\n"
                f"ًں”¹ ط§ظ„ظƒظˆط¯: `{code}`\n"
                f"ًں“„ ط§ظ„ط§ط³ظ…: {data.get('doc_name', file_name)}\n"
                f"ًں“‹ ط§ظ„ظ…ظˆط¶ظˆط¹: {topic_code}\n"
                f"ًں”— [ظپطھط­ ط§ظ„ظ…ظ„ظپ]({drive_link})",
                back_btn
            )
            await N001(context, get_boss_id(context),
                f"ًں“پ ظ…ط³طھظ†ط¯ ظˆط§ط±ط¯ ط¬ط¯ظٹط¯\nًں”¹ ط§ظ„ظƒظˆط¯: {code}\n"
                f"ًں“„ {data.get('doc_name', file_name)}\n"
                f"ًں“‹ ط§ظ„ظ…ظˆط¶ظˆط¹: {topic_code}\nًں”— {drive_link}"
            )

        except Exception as e:
            print(f"â‌Œ file_router RD001: {e}")
            await T002(context, chat_id, "â‌Œ ط­ط¯ط« ط®ط·ط£ ط£ط«ظ†ط§ط، ط§ظ„ط±ظپط¹.", back_btn)
            context.user_data.clear()

# â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
# Main
# â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
if __name__ == "__main__":
    time.sleep(5)
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("testpay", testpay))  # ًں”چ ظ…ط¤ظ‚طھ â€” ظ„ظ„ط§ط®طھط¨ط§ط± ظپظ‚ط·
    app.add_handler(CallbackQueryHandler(menu_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, file_router))

    # â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
    # طھط´ط؛ظٹظ„ Flask (Paymob webhook) ظپظٹ Thread ظ…ظ†ظپطµظ„طŒ ط¬ظ†ط¨ ط§ظ„ط¨ظˆطھ
    # â•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گâ•گ
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("âœ… Flask webhook thread started")

    app.run_polling(drop_pending_updates=True)



