# -*- coding: utf-8 -*-
"""
copy.py　—— 產生「591／臉書文案速查」頁
=========================================

文案內容寫在 copy.json；本模組只負責排版與一鍵複製。
由 build.py 在建置時呼叫，輸出到 properties-admin/copy/index.html。
"""
import html as _html
import io, json, os

ADMIN = os.path.dirname(os.path.abspath(__file__))
BASE = "https://mac2good909777-commits.github.io/properties/"


def brief_code(code):
    return code + ("-b" if "-" in code else "b")


def esc(t):
    return _html.escape(t)


PAGE = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>591／臉書文案速查</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&family=Noto+Serif+TC:wght@700;900&display=swap">
<style>
html{color-scheme:light}
:root{--paper:#F7F6F1;--surface:#fff;--sunk:#EFEDE4;--ink:#1E2620;--body:#39433A;
--dim:#67705F;--line:#DEDCD1;--forest:#2B5937;--gold:#8E7318;--gold-b:#C0A434;
--ok:#276033;--ok-bg:#E4EFE6;--warn:#7A5D0E;--warn-bg:#F4EBD4}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--body);
font-family:"Noto Sans TC","Microsoft JhengHei",system-ui,sans-serif;font-size:16px;line-height:1.75}
.wrap{max-width:1000px;margin:0 auto;padding:40px 20px 90px}
.eyebrow{font-size:14px;letter-spacing:.24em;color:var(--gold);font-weight:700;margin-bottom:8px}
h1{font-family:"Noto Serif TC",serif;font-weight:900;font-size:30px;color:var(--ink);
letter-spacing:.04em;margin:0 0 10px}
.lead{font-size:16px;color:var(--dim);margin-bottom:16px}
.tip{background:var(--sunk);border-left:4px solid var(--gold-b);padding:15px 18px;
border-radius:0 4px 4px 0;font-size:15px;line-height:1.85;margin-bottom:30px}
.tip b{color:var(--ink)}

.case{background:var(--surface);border:1px solid var(--line);border-radius:5px;
padding:24px 26px;margin-bottom:20px}
.hd{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;
padding-bottom:14px;border-bottom:1px solid var(--line);margin-bottom:18px}
.nm{font-family:"Noto Serif TC",serif;font-weight:700;font-size:21px;color:var(--ink)}
.code{font-family:ui-monospace,Consolas,monospace;font-size:14px;color:var(--dim)}
.price{margin-left:auto;font-size:15px;font-weight:700;color:var(--forest);white-space:nowrap}

.blk{margin-bottom:20px}
.blk:last-child{margin-bottom:0}
.blk-hd{display:flex;align-items:center;gap:12px;margin-bottom:9px}
.blk-t{font-size:15px;font-weight:700;color:var(--ink)}
.blk-n{font-size:14px;color:var(--dim)}
.btn{margin-left:auto;font:inherit;font-size:14px;font-weight:700;cursor:pointer;
border:1px solid var(--forest);background:var(--forest);color:#F4F6F0;
padding:7px 16px;border-radius:4px;transition:.15s;white-space:nowrap}
.btn:hover{background:var(--gold);border-color:var(--gold);color:#FFF9E8}
.btn:focus-visible{outline:3px solid var(--gold-b);outline-offset:2px}
.btn.done{background:var(--ok-bg);border-color:var(--ok);color:var(--ok)}
.txt{background:var(--sunk);border-radius:4px;padding:14px 16px;font-size:15px;
line-height:1.85;white-space:pre-wrap;word-break:break-word}
.txt.one{white-space:nowrap;overflow-x:auto;font-weight:700;color:var(--ink)}
.cnt{font-size:14px;color:var(--dim);margin-top:6px}
.memo{margin-top:14px;font-size:14px;color:var(--warn);line-height:1.7}

footer{margin-top:44px;padding-top:18px;border-top:1px solid var(--line);
font-size:14px;color:var(--dim)}
footer a{color:var(--forest)}
@media(max-width:640px){
  .wrap{padding:26px 14px 70px}
  .case{padding:20px 18px}
  .btn{margin-left:0;width:100%%}
  .blk-hd{flex-wrap:wrap}
}
</style>
</head>
<body>
<div class="wrap">
  <div class="eyebrow">FOR 591 &amp; FACEBOOK</div>
  <h1>591／臉書文案速查</h1>
  <div class="lead">刊登與貼文時從這裡取文案，按「複製」即可貼上。</div>
  <div class="tip">
    <b>寫文案的三條規矩</b><br>
    ① 數據照寫，但<b>不要替數據下因果結論</b>——避免「不是⋯是⋯」「根本沒有」「唯一」「絕對」。<br>
    ② 引用實登只能說「<b>實登揭露資料中查無</b>」。法拍、繼承贈與、股權交易不在實登範圍，
    屋主自租的廠房租賃也不需申報，替市場下結論會折損專業信任。<br>
    ③ 臉書貼文附的是<b>簡版連結</b>，不導流到睦聚平台與購廠分析。
  </div>

%s
  <footer>共 %d 案　·　資料更新 %s　·　文案內容存於 <code>properties-admin/copy.json</code></footer>
</div>

<script>
document.addEventListener('click', function(e){
  var b = e.target.closest('.btn[data-t]');
  if(!b) return;
  var txt = b.getAttribute('data-t'), old = b.textContent;
  function done(){
    b.textContent = '\\u5df2\\u8907\\u88fd \\u2713';
    b.classList.add('done');
    setTimeout(function(){ b.textContent = old; b.classList.remove('done'); }, 1600);
  }
  if(navigator.clipboard && window.isSecureContext){
    navigator.clipboard.writeText(txt).then(done, fallback);
  } else { fallback(); }
  function fallback(){
    var t = document.createElement('textarea');
    t.value = txt; t.style.position='fixed'; t.style.opacity='0';
    document.body.appendChild(t); t.select();
    try { document.execCommand('copy'); done(); } catch(err) { window.prompt('請手動複製：', txt); }
    document.body.removeChild(t);
  }
});
</script>
</body>
</html>
"""


def _blk(title, note, text, one=False):
    return ('    <div class="blk">\n'
            '      <div class="blk-hd"><span class="blk-t">%s</span>'
            '<span class="blk-n">%s</span>'
            '<button class="btn" data-t="%s">複製</button></div>\n'
            '      <div class="txt%s">%s</div>\n'
            '    </div>\n'
            % (title, note, esc(text), " one" if one else "", esc(text)))


def build(cases, out_dir=None, updated=""):
    """依 copy.json 產生文案速查頁；只列有文案的案子。"""
    data = json.load(io.open(os.path.join(ADMIN, "copy.json"), encoding="utf-8"))["items"]
    out_dir = out_dir or os.path.join(ADMIN, "copy")
    blocks, n = [], 0
    for c in cases:
        item = data.get(c["code"])
        if not item:
            continue
        n += 1
        link = BASE + brief_code(c["code"]) + "/"
        fb = item["fb"] + "\n\n詳細資料 👉 " + link
        memo = ('      <div class="memo">※ %s</div>\n' % esc(c["note"])) if c.get("note") else ""
        blocks.append(
            '  <div class="case">\n'
            '    <div class="hd"><span class="nm">%s</span>'
            '<span class="code">%s</span>'
            '<span class="price">591 價格欄：%s</span></div>\n'
            '%s%s%s%s  </div>\n'
            % (c["name"], c["code"], esc(item["price591"]),
               _blk("591 標題", "%d 字" % len(item["title591"]), item["title591"], one=True),
               _blk("591 物件說明", "%d 字" % len(item["body591"]), item["body591"]),
               _blk("臉書貼文", "%d 字・已附簡版連結" % len(fb), fb),
               memo))

    os.makedirs(out_dir, exist_ok=True)
    io.open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8").write(
        PAGE % ("\n".join(blocks), n, updated))
    return n
