content = open('amin_alsir_client_dashboard.html', encoding='utf-8').read()

# Step 1: add getClientCode after SCRIPT_URL line
code1 = '\nfunction getClientCode(){const params=new URLSearchParams(window.location.search);const token=params.get(\'t\');if(token){const chatId=atob(token);localStorage.setItem(\'clientChatId\',chatId);return chatId;}return localStorage.getItem(\'clientChatId\')||null;}\nconst CLIENT_CHAT_ID=getClientCode();'

# Step 2: add linkAccount before showToast
fn = 'function linkAccount(){const chatId=CLIENT_CHAT_ID;if(chatId){showToast(\'✅ حسابك مرتبط بالفعل!\');return;}const url=\'https://t.me/amin_alsir_bot?start=client_\'+encodeURIComponent(window.location.search);window.open(url,\'_blank\');}'

# Find SCRIPT_URL line and append after it
import re
result = re.sub(r"(const SCRIPT_URL='[^']*';)", r"\1" + code1, content, count=1)

if result == content:
    print('ERROR: SCRIPT_URL مش موجود!')
else:
    # Add linkAccount before showToast
    old = 'function showToast'
    new = fn + '\n' + old
    result2 = result.replace(old, new, 1)
    if result2 == result:
        print('ERROR: showToast مش موجود!')
    else:
        open('amin_alsir_client_dashboard.html', 'w', encoding='utf-8').write(result2)
        print('Done! الدوال اتضافت بنجاح ✅')
