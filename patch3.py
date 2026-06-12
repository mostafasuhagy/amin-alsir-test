content = open('amin_alsir_client_dashboard.html', encoding='utf-8').read()

btn = '<div style="background:#3D2E00;border-radius:14px;padding:16px;margin-bottom:12px;display:flex;align-items:center;justify-content:space-between;"><div><div style="font-size:14px;font-weight:700;color:#fff;">🔗 ربط حسابي بالبوت</div><div style="font-size:11px;color:rgba(255,255,255,0.5);margin-top:4px;">اربط حسابك لاستقبال الإشعارات</div></div><button onclick="linkAccount()" style="background:linear-gradient(135deg,#F5C518,#E8B400);color:#3D2E00;border:none;border-radius:10px;padding:10px 16px;font-family:Tajawal,sans-serif;font-size:13px;font-weight:800;cursor:pointer;">ربط الآن</button></div>'

old = '<div class="main-content">'
new = old + '\n' + btn

result = content.replace(old, new, 1)

if result == content:
    print('ERROR: النص المطلوب مش موجود في الملف!')
else:
    open('amin_alsir_client_dashboard.html', 'w', encoding='utf-8').write(result)
    print('Done! الزرار اتضاف بنجاح ✅')
