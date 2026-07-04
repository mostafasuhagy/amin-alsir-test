import sys, re

STORAGE_KEYS = {
    "amin_alsir_dashboard.html":           "aminalsir_boss_url",
    "amin_alsir_client_dashboard.html":    "aminalsir_client_url",
    "amin_alsir_assistant_dashboard.html": "aminalsir_assistant_url",
}
ERROR_MESSAGES = {
    "amin_alsir_dashboard.html":           "يرجى فتح لوحة قيادة المكتب من رابط تيليجرام الخاص بك",
    "amin_alsir_client_dashboard.html":    "يرجى فتح لوحة العميل من الرابط الذي أرسله لك المكتب عبر تيليجرام",
    "amin_alsir_assistant_dashboard.html": "يرجى فتح لوحة المساعد من الرابط الذي أرسله لك المكتب عبر تيليجرام",
}

def patch(path):
    filename = path.split("\\")[-1].split("/")[-1]
    storage_key = STORAGE_KEYS.get(filename, "aminalsir_url")
    error_msg   = ERROR_MESSAGES.get(filename, "يرجى فتح الرابط من تيليجرام")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    original = content
    content = re.sub(r"html,\s*body\s*\{[^}]*overscroll-behavior[^}]*\}",
        "html, body { overscroll-behavior: contain; touch-action: pan-y; }", content)
    if "overscroll-behavior" not in content:
        content = re.sub(r"(<style>)",
            r"\1\nhtml, body { overscroll-behavior: contain; touch-action: pan-y; }",
            content, count=1)
    content = re.sub(r'<script>\s*\(function\(\)\s*\{.*?\}\)\(\);\s*</script>', '', content, flags=re.DOTALL)
    content = re.sub(r'<script>\s*window\.addEventListener\(\'pageshow\'.*?</script>', '', content, flags=re.DOTALL)
    new_js = f"""
<script>
(function() {{
  var STORAGE_KEY = '{storage_key}';
  var params = new URLSearchParams(window.location.search);
  var t = params.get('t'); var sid = params.get('sid');
  if (t && sid) {{
    try {{ localStorage.setItem(STORAGE_KEY, window.location.href); }} catch(e) {{}}
  }} else {{
    var savedUrl = null;
    try {{ savedUrl = localStorage.getItem(STORAGE_KEY); }} catch(e) {{}}
    if (savedUrl) {{ window.location.replace(savedUrl); return; }}
    else {{
      document.addEventListener('DOMContentLoaded', function() {{
        document.body.style.cssText = 'margin:0;background:#ffd700;display:flex;align-items:center;justify-content:center;min-height:100vh;font-family:Arial,sans-serif;direction:rtl';
        document.body.innerHTML = '<div style="text-align:center;padding:30px;max-width:320px"><div style="font-size:60px;margin-bottom:20px">🔐</div><h2 style="color:#0D1B4B;margin-bottom:15px">أمين السر</h2><p style="color:#333;font-size:16px;line-height:1.6">{error_msg}</p></div>';
      }});
      return;
    }}
  }}
  history.pushState(null, null, window.location.href);
  window.addEventListener('popstate', function() {{ history.go(1); }});
  window.addEventListener('pageshow', function(event) {{ if (event.persisted) {{ window.location.reload(); }} }});
}})();
</script>
"""
    content = content.replace("</body>", new_js + "</body>")
    if content == original:
        print(f"لم يتغير شيء في {filename}"); return
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ {filename}")
    print(f"   localStorage: ", "✅" if "localStorage.setItem" in content else "❌")
    print(f"   redirect:     ", "✅" if "location.replace" in content else "❌")
    print(f"   error page:   ", "✅" if error_msg in content else "❌")
    print(f"   history.go:   ", "✅" if "history.go(1)" in content else "❌")

if __name__ == "__main__":
    if len(sys.argv) != 2: print("Usage: python patch_final.py <file>"); sys.exit(1)
    patch(sys.argv[1])
