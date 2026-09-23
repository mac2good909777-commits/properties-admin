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

自家流量排除
------------
沒有固定 IP，所以不用 GA 的 IP 規則（IP 會變，會誤殺真客戶）。改用官方的
`traffic_type` 參數：在任一頁網址後面加 `?ga=off` 造訪一次，該瀏覽器就會被
記成內部流量（localStorage，per-origin），GA 端再用「內部流量」資料篩選器排除。
`?ga=on` 解除。手機也適用，換 IP 不受影響。
"""
import re

MEASUREMENT_ID = "G-H5VLHW8761"

SNIPPET = """<!-- Google tag (gtag.js) — GA4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  // 自家裝置標記：任一頁加 ?ga=off 造訪一次，之後該瀏覽器的流量都標成 internal，
  // 由 GA 的「內部流量」資料篩選器排除；?ga=on 解除。
  (function(){
    var K='ga_internal', q=location.search, internal=false;
    try{
      if(q.indexOf('ga=off')>-1){ localStorage.setItem(K,'1'); }
      if(q.indexOf('ga=on')>-1){ localStorage.removeItem(K); }
      internal = localStorage.getItem(K)==='1';
    }catch(e){}
    gtag('config','%s', internal ? {traffic_type:'internal'} : {});
  })();
</script>
""" % (MEASUREMENT_ID, MEASUREMENT_ID)

_OLD = re.compile(
    r'<!--\s*Google tag \(gtag\.js\).*?-->\s*'
    r'<script async src="https://www\.googletagmanager\.com/gtag/js\?id=G-[^"]+"></script>\s*'
    r'<script>.*?</script>\s*',
    re.S | re.I)


def strip(html):
    """移除既有的 GA4 區塊（含舊版片段），讓 inject 永遠寫入最新版本。"""
    return _OLD.sub("", html)


def inject(html):
    """把最新版 GA4 代碼寫進 <head>。既有片段會先被換掉，可重複套用。"""
    html = strip(html)
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
