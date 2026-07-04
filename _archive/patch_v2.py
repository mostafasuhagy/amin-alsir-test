# patch_v2.py — حل قاطع لمشكلة back-gesture على موبايل
# يشغّل على amin_alsir_dashboard.html و client و assistant
# الاستخدام: python patch_v2.py <filename>

import sys, re

def patch(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # 1. تحديث CSS: نغيّر overscroll-behavior-y إلى overscroll-behavior (الاتجاهين)
    content = re.sub(
        r"html,\s*body\s*\{\s*overscroll-behavior-y:\s*contain;\s*\}",
        "html, body { overscroll-behavior: contain; touch-action: pan-y; }",
        content
    )

    # 2. لو مفيش CSS أصلاً (للوحات اللي لم تُعدَّل بعد)
    if "overscroll-behavior" not in content:
        content = re.sub(
            r"(<style>)",
            r"\1\nhtml, body { overscroll-behavior: contain; touch-action: pan-y; }",
            content, count=1
        )

    # 3. تحديث JS: نستبدل الـ pageshow البسيط بحل كامل يشمل history.pushState
    new_js = """
<script>
/* =========================================================
   منع إيماءة الرجوع في متصفحات الموبايل
   الطبقة 1: overscroll-behavior في CSS (أعلاه)
   الطبقة 2: history.pushState يمنع الرجوع في التاريخ
   الطبقة 3: pageshow يجبر reload لو الصفحة رجعت من كاش
   ========================================================= */
(function() {
  // الطبقة 2: اضغط على التاريخ عشان ميرجعش للصفحة اللي قبلها
  history.pushState(null, null, window.location.href);
  window.addEventListener('popstate', function() {
    history.pushState(null, null, window.location.href);
  });

  // الطبقة 3: لو رجع من bfcache، اجبر إعادة التحميل
  window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
      window.location.reload();
    }
  });
})();
</script>
"""

    # احذف الـ pageshow القديم لو موجود وحطّ الجديد مكانه
    content = re.sub(
        r'<script>\s*window\.addEventListener\(\'pageshow\'.*?</script>',
        '',
        content,
        flags=re.DOTALL
    )

    if "</body>" in content:
        content = content.replace("</body>", new_js + "</body>")
    else:
        print("⚠️ لم يتم العثور على </body>")

    if content == original:
        print("⚠️ لم يتغير شيء — راجع الملف يدويًا")
        return

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ تم تحديث {path}")
    print(f"   overscroll-behavior: contain  → ", "موجود" if "overscroll-behavior: contain" in content else "غائب ⚠️")
    print(f"   history.pushState              → ", "موجود" if "history.pushState" in content else "غائب ⚠️")
    print(f"   pageshow listener              → ", "موجود" if "pageshow" in content else "غائب ⚠️")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python patch_v2.py <file.html>")
        sys.exit(1)
    patch(sys.argv[1])
