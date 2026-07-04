import re

path = r"C:\Users\karim\Documents\GitHub\amin-alsir-test\amin_alsir_client_dashboard.html"

with open(path, "r", encoding="utf-8") as f:
    html = f.read()

print(f"حجم الملف: {len(html)} حرف")
print()

# نبحث عن الألوان القريبة من اللي عايزين نغيرها
colors_to_find = ['5C4A', '7A62', 'FFE6', 'E6CA', '92,74', '230,202']
for c in colors_to_find:
    idx = html.find(c)
    if idx > 0:
        print(f"✅ وجد '{c}' في موضع {idx}:")
        print(f"   ...{html[max(0,idx-30):idx+50]}...")
    else:
        print(f"❌ مش موجود '{c}'")
    print()
