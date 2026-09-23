# -*- coding: utf-8 -*-
"""
ga.py　—— Google Analytics 4 埋碼
=================================

資源　睦聚地產 / 工業地產網頁　（a404037525 p549142372）
串流　睦聚官網群組　　　　　　　（ID 15403110531）
評估 ID　G-H5VLHW8761

同一組評估 ID 貼在所有網站即可，GA4 一個串流就收得到跨網域流量：

    industrialrepro.com                              （WordPress，後台另裝）
    mac2good909777-commits.github.io/about-mac/      （已內建）
    mac2good909777-commits.github.io/about/          （已內建）
    mac2good909777-commits.github.io/properties/*    （build.py 產出時注入）
    mac2good909777-commits.github.io/properties-admin/*（台帳／連結頁／文案頁）

各案分頁的點閱數不需要任何自訂事件，GA4 報表
「參與 → 網頁和畫面 → 網頁路徑」就會依 /properties/<案碼>/ 自動分列。
"""
import re

MEASUREMENT_ID = "G-H5VLHW8761"

SNIPPET = """<!-- Google tag (gtag.js) — GA4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', '%s');
</script>
""" % (MEASUREMENT_ID, MEASUREMENT_ID)


def inject(html):
    """把 GA4 代碼插進 <head>。已經有碼就原封不動（可重複套用）。"""
    if MEASUREMENT_ID in html:
        return html
    new, n = re.subn(r'(<meta\s+charset="[^"]+"\s*/?>)',
                     lambda m: m.group(1) + "\n" + SNIPPET,
                     html, count=1, flags=re.I)
    if n:
        return new
    new, n = re.subn(r'(<head[^>]*>)',
                     lambda m: m.group(1) + "\n" + SNIPPET,
                     html, count=1, flags=re.I)
    if not n:
        raise RuntimeError("找不到 <head>，無法插入 GA 代碼")
    return new
