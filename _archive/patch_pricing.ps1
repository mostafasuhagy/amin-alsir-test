# ═══════════════════════════════════════
# patch_pricing.ps1
# تعديل قسم الـ Pricing في index.html
# من 3 باقات (الاقوى/محترف/أساسي) إلى باقتين (شهري/الباقة الذهبية)
# ═══════════════════════════════════════

$filePath = ".\index.html"

# قراءة الملف مع تطبيع line endings (حسب التعليمات المعتمدة في المشروع)
$content = [IO.File]::ReadAllText($filePath)
$content = $content -replace "`r`n", "`n"

# ─────────────────────────────────────
# النص القديم المطلوب استبداله (القسم كامل من <!-- PRICING --> لحد نهاية الـ script بتاعه)
# ─────────────────────────────────────
$oldSection = @'
<!-- PRICING -->
<section class="pricing">
  <p class="sec-title">باقات الاشتراك</p>
  <div class="gold-line"></div>
  <p class="sec-sub">اختر الباقة المناسبة لمكتبك</p>
  <div class="price-grid" id="price-grid">
    <div style="color:#c4a04c;text-align:center;padding:3rem;font-size:1.1rem;">جاري تحميل الباقات...</div>
  </div>
</section>

<script>
(function() {
  var SCRIPT_URL = "https://script.google.com/macros/s/AKfycbymzKVmGgxqgJBFVf91HGzieUsNJQtEU9E1xu97Jkb73Q9VxycorCXDca1laq3Uwdfw/exec";

  function toArabicNums(n) {
    return String(n).replace(/\d/g, function(d) {
      return '٠١٢٣٤٥٦٧٨٩'[d];
    });
  }

  function buildCard(plan, index) {
    var isHot = index === 1;
    var features = (plan.features || '').split('-').map(function(f) {
      return f.trim();
    }).filter(function(f) { return f; });

    var featuresHTML = features.map(function(f) {
      return '<li>' + f + '</li>';
    }).join('');

    var hotBadge = isHot ? '<div class="hot-badge">الأكثر طلباً</div>' : '';
    var hotClass = isHot ? ' hot' : '';

    return '<div class="price-card' + hotClass + '">' +
      hotBadge +
      '<h3>' + (plan.plan_name || '') + '</h3>' +
      '<div class="price-num">' + toArabicNums(plan.price_monthly || 0) + '</div>' +
      '<p class="price-period">جنيه / شهرياً</p>' +
      '<ul class="price-list">' + featuresHTML + '</ul>' +
      '<button class="btn-gold" style="width:100%;font-size:1rem;" onclick="contactUs()">اشترك الآن</button>' +
      '</div>';
  }

  function loadPlans() {
    fetch(SCRIPT_URL + "?action=getPlans")
      .then(function(r) { return r.json(); })
      .then(function(data) {
        var grid = document.getElementById('price-grid');
        if (!data || !data.plans || data.plans.length === 0) {
          grid.innerHTML = '<div style="color:#c4a04c;text-align:center;padding:3rem;">تواصل معنا للاطلاع على الأسعار</div>';
          return;
        }
        grid.innerHTML = data.plans.map(function(plan, i) {
          return buildCard(plan, i);
        }).join('');
      })
      .catch(function() {
        var grid = document.getElementById('price-grid');
        grid.innerHTML = '<div style="color:#c4a04c;text-align:center;padding:3rem;">طھظˆط§طµظ„ ظ…ط¹ظ†ط§ ظ„ظ„ط§ط·ظ„ط§ط¹ ط¹ظ„ظ‰ ط§ظ„ط£ط³ط¹ط§ط±</div>';
      });
  }

  function contactUs() {
    window.open('https://t.me/amin_alsir_bot', '_blank');
  }
  window.contactUs = contactUs;

  loadPlans();
})();
</script>
'@

# ─────────────────────────────────────
# النص الجديد (كارتين: شهري + الباقة الذهبية، مع ربط Deep Link)
# ─────────────────────────────────────
$newSection = @'
<!-- PRICING — معدّل: باقتين (شهري / الباقة الذهبية) مع ربط Deep Link -->
<section class="pricing">
  <p class="sec-title">باقات الاشتراك</p>
  <div class="gold-line"></div>
  <p class="sec-sub">اختر المدة المناسبة لمكتبك</p>
  <div class="price-grid" id="price-grid">
    <div style="color:#c4a04c;text-align:center;padding:3rem;font-size:1.1rem;">جاري تحميل الباقات...</div>
  </div>
</section>

<script>
(function() {
  var SCRIPT_URL = "https://script.google.com/macros/s/AKfycbymzKVmGgxqgJBFVf91HGzieUsNJQtEU9E1xu97Jkb73Q9VxycorCXDca1laq3Uwdfw/exec";

  function toArabicNums(n) {
    return String(n).replace(/\d/g, function(d) {
      return '٠١٢٣٤٥٦٧٨٩'[d];
    });
  }

  function buildMonthlyCard(priceMonthly) {
    return '<div class="price-card">' +
      '<h3>الباقة الشهرية</h3>' +
      '<div class="price-num">' + toArabicNums(priceMonthly) + '</div>' +
      '<p class="price-period">جنيه / شهرياً</p>' +
      '<ul class="price-list">' +
        '<li>كل مميزات النظام كاملة</li>' +
        '<li>عدد غير محدود من العملاء والقضايا</li>' +
        '<li>دعم فني مباشر عبر تيليجرام</li>' +
        '<li>إلغاء أو تجديد في أي وقت</li>' +
      '</ul>' +
      '<button class="btn-gold" style="width:100%;font-size:1rem;" onclick="subscribeNow(\'monthly\')">اشترك الآن</button>' +
      '</div>';
  }

  function buildYearlyCard(priceMonthly, priceYearly) {
    var savings = (priceMonthly * 12) - priceYearly;
    var savingsText = savings > 0 ? 'وفّر ' + toArabicNums(savings) + ' جنيه سنوياً' : 'الأكثر توفيراً';

    return '<div class="price-card hot">' +
      '<div class="hot-badge">' + savingsText + '</div>' +
      '<h3>الباقة الذهبية</h3>' +
      '<div class="price-num">' + toArabicNums(priceYearly) + '</div>' +
      '<p class="price-period">جنيه / سنوياً</p>' +
      '<ul class="price-list">' +
        '<li>كل مميزات النظام كاملة</li>' +
        '<li>عدد غير محدود من العملاء والقضايا</li>' +
        '<li>أولوية في الدعم الفني</li>' +
        '<li>أوفر بشكل ملحوظ من الاشتراك الشهري</li>' +
      '</ul>' +
      '<button class="btn-gold" style="width:100%;font-size:1rem;" onclick="subscribeNow(\'yearly\')">اشترك الآن</button>' +
      '</div>';
  }

  function loadPlans() {
    fetch(SCRIPT_URL + "?action=getPlans")
      .then(function(r) { return r.json(); })
      .then(function(data) {
        var grid = document.getElementById('price-grid');
        var plan = (data && data.plans && data.plans.length > 0) ? data.plans[0] : null;

        if (!plan) {
          grid.innerHTML = '<div style="color:#c4a04c;text-align:center;padding:3rem;">تواصل معنا للاطلاع على الأسعار</div>';
          return;
        }

        var priceMonthly = plan.price_monthly || 135;
        var priceYearly = plan.price_yearly || 1200;

        grid.innerHTML = buildMonthlyCard(priceMonthly) + buildYearlyCard(priceMonthly, priceYearly);
      })
      .catch(function() {
        var grid = document.getElementById('price-grid');
        grid.innerHTML = buildMonthlyCard(135) + buildYearlyCard(135, 1200);
      });
  }

  function subscribeNow(cycle) {
    window.open('https://t.me/amin_alsir_bot?start=plan_' + cycle, '_blank');
  }
  window.subscribeNow = subscribeNow;

  loadPlans();
})();
</script>
'@

# ─────────────────────────────────────
# تطبيق الاستبدال والتحقق
# ─────────────────────────────────────
if ($content.Contains($oldSection)) {
    $content = $content.Replace($oldSection, $newSection)
    $content = $content -replace "`n", "`r`n"
    [IO.File]::WriteAllText($filePath, $content)
    Write-Host "DONE: Pricing section updated successfully in index.html" -ForegroundColor Green
} else {
    Write-Host "ERROR: Old section text not found exactly. Check the file manually." -ForegroundColor Red
    Write-Host "Make sure the file you are running the script on matches the version shown in chat." -ForegroundColor Yellow
}
