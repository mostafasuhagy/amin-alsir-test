# ═══════════════════════════════════════
# patch_start_function.ps1
# تعديل دالة start() في main.py لإضافة دعم plan_ deep link
# (اختيار باقة شهري/سنوي من صفحة الهبوط)
# ═══════════════════════════════════════

$filePath = ".\main.py"

$content = [IO.File]::ReadAllText($filePath)
$content = $content -replace "`r`n", "`n"

# ─────────────────────────────────────
# النص القديم: دالة start() بالكامل كما هي حالياً
# ─────────────────────────────────────
$oldFunction = @'
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    print(f"🆔 CHAT ID: {chat_id}")

    # ── التحقق من Deep Link (تسجيل عميل أو مساعد) ──
    args = context.args
    if args:
        param = args[0]

        # ── تسجيل عميل ──
        if param.startswith("client_"):
            ref_code = param.replace("client_", "")
            client = P002("Clients", ref_code)
            if client:
                records = P005("Clients")
                for i, r in enumerate(records, start=2):
                    if str(list(r.values())[0]).strip().lower() == str(ref_code).strip().lower():
                        P004("Clients", i, 8, str(chat_id))
                        break
                await update.message.reply_text(
                    f"✅ *تم ربط حسابك بنجاح!*\n\n"
                    f"👤 {client.get('client_name', '')}\n"
                    f"🔹 الكود: `{ref_code}`\n\n"
                    f"ستصلك إشعارات مكتب المحاماة هنا مباشرة.",
                    parse_mode="Markdown"
                )
                await context.bot.send_message(
                    chat_id=BOSS_CHAT_ID,
                    text=f"🔔 *إشعار — أمين السر*\n\n📱 عميل ربط حسابه بالبوت\n👤 {client.get('client_name','')}\n🔹 {ref_code}",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text("❌ كود العميل غير صحيح. تواصل مع المكتب.")
            return

        # ── تسجيل مساعد ──
        elif param.startswith("assistant_"):
            ref_code = param.replace("assistant_", "")
            assistant = P002("Assistants", ref_code)
            if assistant:
                records = P005("Assistants")
                for i, r in enumerate(records, start=2):
                    if str(list(r.values())[0]).strip().lower() == str(ref_code).strip().lower():
                        P004("Assistants", i, 6, str(chat_id))
                        break
                await update.message.reply_text(
                    f"✅ *تم ربط حسابك بنجاح!*\n\n"
                    f"👥 {assistant.get('assistant_name', '')}\n"
                    f"🔹 الكود: `{ref_code}`\n\n"
                    f"ستصلك مهامك ومستجدات المكتب هنا مباشرة.",
                    parse_mode="Markdown"
                )
                token = base64.b64encode(str(chat_id).encode()).decode()
                dashboard_url = f"https://aminalserr.com/amin_alsir_assistant_dashboard.html?t={token}"
                await update.message.reply_text(
                    f"🔗 *رابط لوحة القيادة الخاصة بك:*\n{dashboard_url}\n\n📌 احفظ هذا الرابط في مفضلاتك",
                    parse_mode="Markdown"
                )
                await context.bot.send_message(
                    chat_id=BOSS_CHAT_ID,
                    text=f"🔔 *إشعار — أمين السر*\n\n📱 مساعد ربط حسابه بالبوت\n👥 {assistant.get('assistant_name','')}\n🔹 {ref_code}",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text("❌ كود المساعد غير صحيح. تواصل مع المكتب.")
            return

    # ── التحقق من الاشتراك ──
    tenant = MT001(chat_id)

    if tenant and tenant.get("status") == "active":
        # مكتب مشترك — فتح الداشبورد
        office_name = tenant.get("office_name", "المكتب")
        country = tenant.get("country", "مصر")
        context.user_data["tenant"] = tenant
        await update.message.reply_text(
            f"أهلاً بك في *أمين السر* 🏛️\n\n"
            f"🏢 {office_name}\n"
            f"🌍 {country}\n\n"
            f"اختر من لوحة القيادة:",
            parse_mode="Markdown",
            reply_markup=main_keyboard()
        )
    else:
        # مكتب جديد — بدء التسجيل التلقائي
        context.user_data["routine"] = "REG"
        context.user_data["step"] = "office_name"
        context.user_data["data"] = {}
        await update.message.reply_text(
            "🏛️ *أهلاً بك في أمين السر!*\n\n"
            "نظام إدارة مكتب المحاماة للوطن العربي 🌍\n\n"
            "للبدء، أدخل *اسم مكتبك*:",
            parse_mode="Markdown"
        )
'@

# ─────────────────────────────────────
# النص الجديد: نفس الدالة + شرط plan_ الجديد
# ─────────────────────────────────────
$newFunction = @'
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    print(f"🆔 CHAT ID: {chat_id}")

    # ── التحقق من Deep Link (تسجيل عميل أو مساعد أو اختيار باقة) ──
    args = context.args
    if args:
        param = args[0]

        # ── تسجيل عميل ──
        if param.startswith("client_"):
            ref_code = param.replace("client_", "")
            client = P002("Clients", ref_code)
            if client:
                records = P005("Clients")
                for i, r in enumerate(records, start=2):
                    if str(list(r.values())[0]).strip().lower() == str(ref_code).strip().lower():
                        P004("Clients", i, 8, str(chat_id))
                        break
                await update.message.reply_text(
                    f"✅ *تم ربط حسابك بنجاح!*\n\n"
                    f"👤 {client.get('client_name', '')}\n"
                    f"🔹 الكود: `{ref_code}`\n\n"
                    f"ستصلك إشعارات مكتب المحاماة هنا مباشرة.",
                    parse_mode="Markdown"
                )
                await context.bot.send_message(
                    chat_id=BOSS_CHAT_ID,
                    text=f"🔔 *إشعار — أمين السر*\n\n📱 عميل ربط حسابه بالبوت\n👤 {client.get('client_name','')}\n🔹 {ref_code}",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text("❌ كود العميل غير صحيح. تواصل مع المكتب.")
            return

        # ── تسجيل مساعد ──
        elif param.startswith("assistant_"):
            ref_code = param.replace("assistant_", "")
            assistant = P002("Assistants", ref_code)
            if assistant:
                records = P005("Assistants")
                for i, r in enumerate(records, start=2):
                    if str(list(r.values())[0]).strip().lower() == str(ref_code).strip().lower():
                        P004("Assistants", i, 6, str(chat_id))
                        break
                await update.message.reply_text(
                    f"✅ *تم ربط حسابك بنجاح!*\n\n"
                    f"👥 {assistant.get('assistant_name', '')}\n"
                    f"🔹 الكود: `{ref_code}`\n\n"
                    f"ستصلك مهامك ومستجدات المكتب هنا مباشرة.",
                    parse_mode="Markdown"
                )
                token = base64.b64encode(str(chat_id).encode()).decode()
                dashboard_url = f"https://aminalserr.com/amin_alsir_assistant_dashboard.html?t={token}"
                await update.message.reply_text(
                    f"🔗 *رابط لوحة القيادة الخاصة بك:*\n{dashboard_url}\n\n📌 احفظ هذا الرابط في مفضلاتك",
                    parse_mode="Markdown"
                )
                await context.bot.send_message(
                    chat_id=BOSS_CHAT_ID,
                    text=f"🔔 *إشعار — أمين السر*\n\n📱 مساعد ربط حسابه بالبوت\n👥 {assistant.get('assistant_name','')}\n🔹 {ref_code}",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text("❌ كود المساعد غير صحيح. تواصل مع المكتب.")
            return

        # ── اختيار باقة من صفحة الهبوط (شهري/سنوي) ──
        # 🆕 الرابط الجاي من index.html شكله: ?start=plan_monthly أو ?start=plan_yearly
        elif param.startswith("plan_"):
            billing_cycle = param.replace("plan_", "")
            if billing_cycle not in ("monthly", "yearly"):
                billing_cycle = "monthly"

            context.user_data["selected_billing_cycle"] = billing_cycle
            cycle_label = "شهري" if billing_cycle == "monthly" else "سنوي (الباقة الذهبية)"

            tenant = MT001(chat_id)
            if tenant and tenant.get("status") == "active":
                office_name = tenant.get("office_name", "المكتب")
                country = tenant.get("country", "مصر")
                context.user_data["tenant"] = tenant
                await update.message.reply_text(
                    f"أهلاً بك مجدداً في *أمين السر* 🏛️\n\n"
                    f"🏢 {office_name}\n"
                    f"🌍 {country}\n\n"
                    f"اختر من لوحة القيادة:",
                    parse_mode="Markdown",
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

    # ── التحقق من الاشتراك (الحالة العادية، بدون Deep Link) ──
    tenant = MT001(chat_id)

    if tenant and tenant.get("status") == "active":
        # مكتب مشترك — فتح الداشبورد
        office_name = tenant.get("office_name", "المكتب")
        country = tenant.get("country", "مصر")
        context.user_data["tenant"] = tenant
        await update.message.reply_text(
            f"أهلاً بك في *أمين السر* 🏛️\n\n"
            f"🏢 {office_name}\n"
            f"🌍 {country}\n\n"
            f"اختر من لوحة القيادة:",
            parse_mode="Markdown",
            reply_markup=main_keyboard()
        )
    else:
        # مكتب جديد — بدء التسجيل التلقائي
        context.user_data["routine"] = "REG"
        context.user_data["step"] = "office_name"
        context.user_data["data"] = {}
        await update.message.reply_text(
            "🏛️ *أهلاً بك في أمين السر!*\n\n"
            "نظام إدارة مكتب المحاماة للوطن العربي 🌍\n\n"
            "للبدء، أدخل *اسم مكتبك*:",
            parse_mode="Markdown"
        )
'@

# ─────────────────────────────────────
# تطبيق الاستبدال والتحقق
# ─────────────────────────────────────
if ($content.Contains($oldFunction)) {
    $content = $content.Replace($oldFunction, $newFunction)
    $content = $content -replace "`n", "`r`n"
    [IO.File]::WriteAllText($filePath, $content)
    Write-Host "DONE: start() function updated successfully in main.py" -ForegroundColor Green
} else {
    Write-Host "ERROR: Old function text not found exactly. Check the file manually." -ForegroundColor Red
    Write-Host "Make sure the file you are running the script on matches the version shown in chat." -ForegroundColor Yellow
}
