content = open('amin_alsir_client_dashboard.html', encoding='utf-8').read()

old = 'background:#3D2E00'
new = 'background:#0D1B4B'

result = content.replace(old, new, 1)

if result == content:
    print('ERROR: اللون مش موجود!')
else:
    open('amin_alsir_client_dashboard.html', 'w', encoding='utf-8').write(result)
    print('Done! اللون اتغير بنجاح ✅')
