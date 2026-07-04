from PIL import Image, ImageDraw
import base64, io, re

logo = Image.open('amin_alsir_icon_yellow2.png').convert('RGBA')

size = 512
img = Image.new('RGBA', (size, size), (255, 230, 0, 255))
logo_size = int(size * 0.82)
logo_resized = logo.resize((logo_size, logo_size), Image.LANCZOS)
offset = (size - logo_size) // 2
img.paste(logo_resized, (offset, offset), logo_resized)

buf = io.BytesIO()
img.save(buf, 'PNG', optimize=True)
new_icon = base64.b64encode(buf.getvalue()).decode()

with open('amin_alsir_dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = re.sub(r'data:image/png;base64,[A-Za-z0-9+/=]+', f'data:image/png;base64,{new_icon}', html)

with open('amin_alsir_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done!')
