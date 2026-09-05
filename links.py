# -*- coding: utf-8 -*-
"""
links.py　—— 產生「電子報連結頁」
=================================

給助理做電子報用的頁面：只有物件名稱、完整版／簡版網址，以及一鍵複製按鈕。
不放開價、屋主、規格等內部資訊。

資料來源與台帳相同（cases.json），所以不會脫節。
由 build.py 在建置時呼叫，輸出到 properties-admin/links/index.html。
"""
import io, json, os

ADMIN = os.path.dirname(os.path.abspath(__file__))
BASE = "https://mac2good909777-commits.github.io/properties/"

KIND = {"sale": "售", "rent": "租", "buyer": "買方需求", "advisory": "顧問"}
STATUS = {"live": ("在售／在租", "ok"), "quiet": ("潛銷", "warn"),
          "done": ("已結案", "off"), "other": ("顧問頁", "warn")}


def brief_code(code):
    return code + ("-b" if "-" in code else "b")


PAGE = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>物件連結速查</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&family=Noto+Serif+TC:wght@700;900&display=swap">
<style>
html{color-scheme:light}
:root{--paper:#F7F6F1;--surface:#fff;--sunk:#EFEDE4;--ink:#1E2620;--body:#39433A;
--dim:#67705F;--line:#DEDCD1;--forest:#2B5937;--gold:#8E7318;--gold-b:#C0A434;
--ok:#276033;--ok-bg:#E4EFE6;--warn:#7A5D0E;--warn-bg:#F4EBD4;--off:#6B7268;--off-bg:#E7E6DE}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--body);
font-family:"Noto Sans TC","Microsoft JhengHei",system-ui,sans-serif;font-size:16px;line-height:1.7}
.wrap{max-width:960px;margin:0 auto;padding:40px 20px 90px}
.eyebrow{font-size:14px;letter-spacing:.24em;color:var(--gold);font-weight:700;margin-bottom:8px}
h1{font-family:"Noto Serif TC",serif;font-weight:900;font-size:30px;color:var(--ink);
letter-spacing:.04em;margin:0 0 10px}
.lead{font-size:16px;color:var(--dim);margin-bottom:14px}
.tip{background:var(--sunk);border-left:4px solid var(--gold-b);padding:14px 18px;
border-radius:0 4px 4px 0;font-size:15px;line-height:1.8;margin-bottom:30px}
.tip b{color:var(--ink)}

.case{background:var(--surface);border:1px solid var(--line);border-radius:5px;
padding:22px 24px;margin-bottom:18px}
.case.past{opacity:.62}
.hd{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin-bottom:16px}
.nm{font-family:"Noto Serif TC",serif;font-weight:700;font-size:21px;color:var(--ink);letter-spacing:.02em}
.meta{font-size:14px;color:var(--dim)}
.tag{font-size:14px;font-weight:700;padding:3px 11px;border-radius:4px;margin-left:auto}
.t-ok{background:var(--ok-bg);color:var(--ok)}
.t-warn{background:var(--warn-bg);color:var(--warn)}
.t-off{background:var(--off-bg);color:var(--off)}

.row{display:flex;align-items:center;gap:12px;flex-wrap:wrap;
padding:13px 0;border-top:1px solid #EFEDE4}
.row:first-of-type{border-top:0}
.ver{flex:0 0 96px;font-size:15px;font-weight:700;color:var(--ink)}
.ver small{display:block;font-weight:400;font-size:14px;color:var(--dim);margin-top:1px}
.url{flex:1 1 300px;min-width:0;font-family:ui-monospace,Consolas,monospace;font-size:14px;
color:var(--forest);background:var(--sunk);border-radius:3px;padding:9px 12px;
overflow-x:auto;white-space:nowrap;text-decoration:none;display:block}
.url:hover{color:var(--gold)}
.btn{flex:0 0 auto;font:inherit;font-size:15px;font-weight:700;cursor:pointer;
border:1px solid var(--forest);background:var(--forest);color:#F4F6F0;
padding:10px 20px;border-radius:4px;transition:.15s;white-space:nowrap;min-width:104px}
.btn:hover{background:var(--gold);border-color:var(--gold);color:#FFF9E8}
.btn:focus-visible{outline:3px solid var(--gold-b);outline-offset:2px}
.btn.done{background:var(--ok-bg);border-color:var(--ok);color:var(--ok)}
.btn.open{background:var(--surface);color:var(--forest);min-width:0}
.btn.open:hover{background:var(--sunk);color:var(--gold)}

footer{margin-top:44px;padding-top:18px;border-top:1px solid var(--line);
font-size:14px;color:var(--dim)}
footer a{color:var(--forest)}
@media(max-width:640px){
  .wrap{padding:26px 14px 70px}
  .ver{flex:0 0 100%%}
  .url{flex:1 1 100%%}
  .btn{flex:1 1 auto}
}
</style>
</head>
<body>
<div class="wrap">
  <div class="eyebrow">FOR NEWSLETTER</div>
  <h1>物件連結速查</h1>
  <div class="lead">做電子報時從這裡取連結，按「複製」即可貼上。</div>

  <div class="tip">
    <b>完整版</b>　頁尾有四張團隊卡（關於瑞禾／關於現傑／睦聚現傑／購廠分析）。
    <b>電子報、認識的對象用這個。</b><br>
    <b>簡版</b>　只留關於瑞禾＋關於現傑，不導流到睦聚平台與購廠分析。
    <b>一般散發、同業、屋主用這個。</b>
  </div>

%s
  <footer>共 %d 案　·　資料更新 %s　·　<a href="../">回管理台帳</a></footer>
</div>

<script>
document.addEventListener('click', function(e){
  var b = e.target.closest('.btn[data-url]');
  if(!b) return;
  var url = b.getAttribute('data-url'), old = b.textContent;
  function done(){
    b.textContent = '\\u5df2\\u8907\\u88fd \\u2713';
    b.classList.add('done');
    setTimeout(function(){ b.textContent = old; b.classList.remove('done'); }, 1600);
  }
  if(navigator.clipboard && window.isSecureContext){
    navigator.clipboard.writeText(url).then(done, fallback);
  } else { fallback(); }
  function fallback(){
    var t = document.createElement('textarea');
    t.value = url; t.style.position='fixed'; t.style.opacity='0';
    document.body.appendChild(t); t.select();
    try { document.execCommand('copy'); done(); } catch(err) { window.prompt('請手動複製：', url); }
    document.body.removeChild(t);
  }
});
</script>
</body>
</html>
"""

ROW = """    <div class="row">
      <div class="ver">%s<small>%s</small></div>
      <a class="url" href="%s" target="_blank" rel="noopener">%s</a>
      <button class="btn" data-url="%s">複製連結</button>
      <a class="btn open" href="%s" target="_blank" rel="noopener">開啟</a>
    </div>
"""


def build(cases, out_dir=None, updated=""):
    out_dir = out_dir or os.path.join(ADMIN, "links")
    blocks = []
    for c in cases:
        st, cls = STATUS.get(c.get("status", "live"), ("", "off"))
        rows = ROW % ("完整版", "四卡・電子報",
                      BASE + c["code"] + "/", BASE + c["code"] + "/",
                      BASE + c["code"] + "/", BASE + c["code"] + "/")
        if c.get("brief"):
            bc = brief_code(c["code"])
            rows += ROW % ("簡版", "兩卡・散發",
                           BASE + bc + "/", BASE + bc + "/",
                           BASE + bc + "/", BASE + bc + "/")
        blocks.append(
            '  <div class="case%s">\n'
            '    <div class="hd"><div class="nm">%s</div>'
            '<div class="meta">%s</div>'
            '<span class="tag t-%s">%s</span></div>\n%s  </div>\n'
            % (" past" if c.get("status") in ("done",) else "",
               c["name"], KIND.get(c.get("kind"), ""), cls, st, rows))

    os.makedirs(out_dir, exist_ok=True)
    io.open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8").write(
        PAGE % ("\n".join(blocks), len(cases), updated))
    return len(cases)
