# patch_dashboard_back_gesture.py
#
# يضيف حل قاطع لمشكلة "السحب لتحت = رجوع للصفحة القديمة" على متصفحات الموبايل:
#   1. CSS: overscroll-behavior-y: contain  (يمنع المتصفح من تفسير السحب كإيماءة رجوع)
#   2. JS: pageshow listener يجبر إعادة تحميل البيانات من الشيت لو الصفحة رجعت من
#      الكاش (bfcache) بدل ما تعرض بيانات قديمة محفوظة محليًا
#
# الاستخدام:
#   python patch_dashboard_back_gesture.py amin_alsir_dashboard.html
#   python patch_dashboard_back_gesture.py amin_alsir_client_dashboard.html
#   python patch_dashboard_back_gesture.py amin_alsir_assistant_dashboard.html
#
# الناتج: نسخة جديدة بنفس الاسم + _patched.html (الأصل مايتلمسش)

import sys
import re

def patch(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    changed = False

    # 1. إضافة CSS overscroll-behavior فور بداية الـ <style> الموجود
    if "overscroll-behavior" not in content:
        content_new = re.sub(
            r"(<style>)",
            r"\1\nhtml, body { overscroll-behavior-y: contain; }",
            content,
            count=1
        )
        if content_new != content:
            content = content_new
            changed = True
            print("✅ CSS overscroll-behavior تم إضافته بعد <style>")
        else:
            print("⚠️ لم يتم العثور على <style> لإضافة CSS — راجع يدويًا")

    # 2. إضافة JS pageshow listener قبل </body>
    pageshow_snippet = """
<script>
window.addEventListener('pageshow', function(event) {
  if (event.persisted) {
    // الصفحة رجعت من كاش المتصفح (bfcache) — نجبر إعادة تحميل كاملة
    // عشان نضمن إن البيانات المعروضة هي أحدث بيانات من الشيت ومش
    // نسخة قديمة محفوظة محليًا لمكتب تاني
    window.location.reload();
  }
});
</script>
"""
    if "addEventListener('pageshow'" not in content:
        content_new = content.replace("</body>", pageshow_snippet + "</body>")
        if content_new != content:
            content = content_new
            changed = True
            print("✅ JS pageshow listener تم إضافته قبل </body>")
        else:
            print("⚠️ لم يتم العثور على </body> لإضافة JS — راجع يدويًا")

    if not changed:
        print("⚠️ لم يتم تعديل أي شيء — الملف ممكن يكون اتعدل قبل كده")
        return

    out_path = path.rsplit(".", 1)[0] + "_patched.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"تم الحفظ في: {out_path}")
    print(f"عدد الأسطر — الأصل: {open(path, encoding='utf-8').read().count(chr(10))+1}, "
          f"الجديد: {content.count(chr(10))+1}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python patch_dashboard_back_gesture.py <file.html>")
        sys.exit(1)
    patch(sys.argv[1])
