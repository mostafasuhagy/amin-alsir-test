import re, base64

with open('amin_alsir_assistant_dashboard.html', encoding='utf-8') as f:
    c = f.read()

b = open('icon_assistant.png', 'rb').read()
b64 = 'data:image/png;base64,' + base64.b64encode(b).decode()
c = re.sub(r'data:image/png;base64,[A-Za-z0-9+/=]+', b64, c)

with open('amin_alsir_assistant_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('Done!')
