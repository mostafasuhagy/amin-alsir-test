content = open('amin_alsir_assistant_dashboard.html', encoding='utf-8').read()

fn = 'function linkAccount(){const chatId=ASSISTANT_CHAT_ID;if(chatId){showToast(\'✅ حسابك مرتبط بالفعل!\');return;}const url=\'https://t.me/amin_alsir_bot?start=assistant_\'+encodeURIComponent(window.location.search);window.open(url,\'_blank\');}'

old = 'function showToast'
new = fn + '\n' + old

result = content.replace(old, new, 1)

if result == content:
    print('ERROR: النص المطلوب مش موجود في الملف!')
else:
    open('amin_alsir_assistant_dashboard.html', 'w', encoding='utf-8').write(result)
    print('Done! الدالة اتضافت بنجاح ✅')
