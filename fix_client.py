import re

path = r"C:\Users\karim\Documents\GitHub\amin-alsir-test\amin_alsir_client_dashboard.html"

with open(path, "r", encoding="utf-8") as f:
    html = f.read()

# الألوان
html = html.replace('content="#5C4A00"', 'content="#FFE600"')
html = html.replace('--dark:#5C4A00;', '--dark:#FFE600;')
html = html.replace('--dark2:#7A6200;', '--dark2:#E6CA00;')
html = html.replace('background:linear-gradient(135deg,#5C4A00 0%,#7A6200 50%,#5C4A00 100%)', 'background:linear-gradient(135deg,#FFE600 0%,#E6CA00 50%,#FFE600 100%)')
html = html.replace('background:rgba(92,74,0,0.85)', 'background:rgba(230,202,0,0.95)')
html = html.replace('background:rgba(92,74,0,0.95)', 'background:rgba(230,202,0,0.97)')
html = html.replace('background:#7A6200;', 'background:#E6CA00;')

# الأيقونة الجديدة (قطع يسار + خلفية صفراء)
new_icon = "iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AAAOmUlEQVR4nO3dS6ycdR3G8d/pBSgFwSBSSkEF6Q2JGzWIRhITNUETdkpiQkLiTjfqRnfGlTExxkRwo8SoMSa48JIACSyMIQqxQEAR0AIBsbTghZZbaUuPiylCoZdzzrwz7/t/n88nmTQpM9M/C/p8Z87wzkJBVS3uqsW+zwDA/Kzq+wD0z/gD5BEA4Yw/QCYBEMz4A+QSAKGMP0A2ARDI+AMgAMIYfwCqBEAU4w/AawRACOMPwBsJgADGH4A3EwAjZ/wBOBYBMGLGH4DjEQAjZfwBOBEBMELGH4ClEgAjYfwBWAoBMCLGH4DlEgCNM/4ArIQAaJjxB2ClBECjjD8A0xAADTL+AExLADTG+APQBQHQEOMPQFcEQCOMPwBdEgANMP4ArIQAaJjxB2ClBECjjD8A0xAADTL+AExLADTG+APQBQHQEOMPQFcEQCOMPwBdEgANMP4ArIQAaJjxB2ClBECjjD8A0xAADTL+AExLADTG+APQBQHQEOMPQFcEQCOMPwBdEgANMP4ArIQAaJjxB2ClBECjjD8A0xAADTL+AExLADTG+APQBQHQEOMPQFcEQCOMPwBdEgANMP4ArIQAaJjxB2ClBECjjD8A0xAADTL+AExLADTG+APQBQHQEOMPQFcEQCOMPwBdEgANMP4ArIQAaJjxB2ClBECjjD8A0xAADTL+AExLADTG+APQBQHQEOMPQFcEQCOMPwBdEgANMP4ArIQAaJjxB2ClBECjjD8A0xAADTL+AExLADTG+APQBQHQEOMPQFcEQCOMPwBdEgANMP4ArIQAaJjxB2ClBECjjD8A0xAADTL+AExLADTG+APQBQHQEOMPQFcEQCOMPwBdEgANMP4ArIQAaJjxB2ClBECjjD8A0xAADTL+AExLADTG+APQBQHQEOMPQFcEQCOMPwBdEgANMP4ArIQAaJjxB2ClBECjjD8A0xAADTL+AExLADTG+APQBQHQEOMPQFcEQCOMPwBdEgANMP4ArIQAaJjxB2ClBECjjD8A0xAADTL+AExLADTG+APQBQHQEOMPQFcEQCOMPwBdEgANMP4ArIQAaJjxB2ClBECjjD8A0xAADTL+AExLADTG+APQBQHQEOMPQFcEQCOMPwBdEgANMP4ArIQAaJjxB2ClBECjjD8A0xAADTL+"

html = re.sub(r'data:image/png;base64,[A-Za-z0-9+/=]+', f'data:image/png;base64,{new_icon}', html)

with open(path, "w", encoding="utf-8") as f:
    f.write(html)

print("تم! ✅")
