import re

path = r"C:\Users\karim\Documents\GitHub\amin-alsir-test\amin_alsir_client_dashboard.html"

with open(path, "r", encoding="utf-8") as f:
    html = f.read()

print(f"قبل: {len(html)} حرف")

# --- ألوان CSS ---
# 1. theme-color في meta tag
html = html.replace('#5C4A00"', '#FFE600"')

# 2. CSS variables
html = html.replace('--dark:#5C4A00;', '--dark:#FFE600;')
html = html.replace('--dark2:#7A6200;', '--dark2:#E6CA00;')

# 3. gradient الخلفية
html = html.replace('#5C4A00 0%,#7A6200 50%,#5C4A00 100%', '#FFE600 0%,#E6CA00 50%,#FFE600 100%')

# 4. header rgba
html = html.replace('rgba(92,74,0,0.85)', 'rgba(230,202,0,0.95)')

# 5. bottom-nav rgba
html = html.replace('rgba(92,74,0,0.95)', 'rgba(230,202,0,0.97)')

# 6. modal background
html = html.replace('background:#7A6200;', 'background:#E6CA00;')

# 7. أي لون #5C4A00 متبقي في CSS
html = html.replace('#5C4A00', '#FFE600')
html = html.replace('#7A6200', '#E6CA00')

# --- الأيقونة: base64 جديدة بقطع يسار + خلفية صفراء ---
new_icon = "iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AAAOmUlEQVR4nO3dS6ycdR3G8d/pBSgFwSBSSkEF6Q2JGzWIRhITNUETdkpiQkLiTjfqRnfGlTExxkRwo8SoMSa48JIACSyMIQqxQEAR0AIBsbTghZZbaUuPiylCoZdzzrwz7/t/n88nmTQpM9M/C/p8Z87wzkJBVS3uqsW+zwDA/Kzq+wD0z/gD5BEA4Yw/QCYBEMz4A+QSAKGMP0A2ARDI+AMgAMIYfwCqBEAU4w/AawRACOMPwBsJgADGH4A3EwAjZ/wBOBYBMGLGH4DjEQAjZfwBOBEBMELGH4ClEgAjYfwBWAoBMCLGH4DlEgCNM/4ArIQAaJjxB2ClBECjjD8A0xAADTL+AExLADTG+APQBQHQEOMPQFcEQCOMPwBdEgANMP4ArIQAaJjxB2ClBECjjD8A0xAADTL+AExLADTG+APQBQHQEOMPQFcEQCOMPwBdEgANMP4ArIQAaJjxB2ClBECjjD8A0xAADTL+AExLADTG+APQBQHQEOMPQFcEQCOMPwBdEgANMP4ArIQAaJjxB2ClBECjjD8A0xAADTL+AExLADTG+APQBQHQEOMPQFcEQCOMPwBdEgANMP4ArIQAaJjxB2ClBECjjD8A0xAADTL+AExLADTG+APQBQHQEOMPQFcEQCOMPwBdEgANMP4ArIQAaJjxB2ClBECjjD8A0xAADTL+AExLADTG+APQBQHQEOMPQFcEQCOMPwBdEgANMP4ArIQAaJjxB2ClBECjjD8A0xAADTL+AExLADTG+APQBQHQEOMPQFcEQCOMPwBdEgANMP4ArIQAaJjxB2ClBECjjD8A0xAADTL+"

html = re.sub(r'data:image/png;base64,[A-Za-z0-9+/=]+', f'data:image/png;base64,{new_icon}', html)

print(f"بعد: {len(html)} حرف")

# تحقق من التغييرات
checks = [
    ('#FFE600', 'الأصفر موجود ✅'),
    ('#5C4A00', 'البني القديم لسه موجود ❌'),
    ('#7A6200', 'البني الغامق القديم لسه موجود ❌'),
]
for color, msg in checks:
    count = html.count(color)
    print(f"{msg}: {count} مرة")

with open(path, "w", encoding="utf-8") as f:
    f.write(html)

print("\nتم الحفظ! ✅")
