f = open('amin_alsir_dashboard.html', encoding='utf-8').read()
i = f.find(':root')
print("=== CSS Variables ===")
print(f[i:i+400])
print()
# نشوف لون الـ body
i2 = f.find('body{')
if i2 < 0:
    i2 = f.find('body {')
print("=== Body CSS ===")
print(f[i2:i2+200])
