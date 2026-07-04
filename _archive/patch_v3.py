import sys, re

def patch(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    original = content

    # CSS
    content = re.sub(
        r"html,\s*body\s*\{[^}]*overscroll-behavior[^}]*\}",
        "html, body { overscroll-behavior: contain; touch-action: pan-y; }",
        content
    )
    if "overscroll-behavior" not in content:
        content = re.sub(r"(<style>)",
            r"\1\nhtml, body { overscroll-behavior: contain; touch-action: pan-y; }",
            content, count=1)

    # حذف JS القديم كله
    content = re.sub(
        r'<script>\s*(?:/\*[^*]*\*+(?:[^/*][^*]*\*+)*/\s*)?\(function\(\)\s*\{.*?history\.pushState.*?\}\)\(\);\s*</script>',
        '', content, flags=re.DOTALL)
    content = re.sub(
        r'<script>\s*window\.addEventListener\(\'pageshow\'.*?</script>',
        '', content, flags=re.DOTALL)

    new_js = """
<script>
/* منع الرجوع للصفحات القديمة على متصفحات الموبايل
   الطريقة: history.go(1) يرجع للأمام فور ما المتصفح يحاول الرجوع */
(function() {
  history.pushState(null, null, window.location.href);

  window.addEventListener('popstate', function() {
    history.go(1);
  });

  window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
      window.location.reload();
    }
  });
})();
</script>
"""
    content = content.replace("</body>", new_js + "</body>")

    if content == original:
        print(f"⚠️ لم يتغير شيء في {path}")
        return

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ {path}")
    print(f"   history.go(1): ", "موجود" if "history.go(1)" in content else "غائب ⚠️")
    print(f"   pageshow:      ", "موجود" if "pageshow" in content else "غائب ⚠️")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python patch_v3.py <file.html>")
        sys.exit(1)
    patch(sys.argv[1])
