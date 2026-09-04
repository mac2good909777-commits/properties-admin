# -*- coding: utf-8 -*-
"""
build.py　—— 由原稿 A 產生成品 B
=================================

    A  properties-src   (public)  各專案 push 原稿到這裡，只有內容
    B  properties       (public)  成品，GitHub Pages，只有本工具寫入
    C  properties-admin (private) 本工具 + cases.json + 管理台帳

流程
----
    python build.py            檢查：列出 A 有異動、尚未反映到 B 的案子
    python build.py --build    重建全部
    python build.py --build Industrial21 TCIP2098   只重建指定案

--build 會做：
    1. 讀 A/<code>/index.html 原稿
    2. 依 cases.json 套「認識專案團隊」完整版四卡 → 寫 B/<code>/index.html
    3. brief=true 者產簡版兩卡 + noindex → 寫 B/<code>b/index.html
    4. noindex_main=true 者主版也加 noindex
    5. on_index=true 者收進 B/index.html 公開總覽（自動重生）
    6. 記錄原稿 sha256 到 manifest.json，供下次比對

原稿內若自帶「認識專案團隊」區塊會被整段移除再換上標準版。
"""
import hashlib, io, json, os, re, sys

ADMIN = os.path.dirname(os.path.abspath(__file__))
SRC   = r"C:\Claude\projects\properties-src"
DST   = r"C:\Claude\projects\properties"
MANIFEST = os.path.join(ADMIN, "manifest.json")

# ---------------------------------------------------------------- 團隊區塊

STYLE = """  <style>
  .kya{background:#FAF9F6;padding:78px 0;border-top:1px solid #E8E6E1}
  .kya-in{max-width:1040px;margin:0 auto;padding:0 22px}
  .kya-head{text-align:center;margin-bottom:52px}
  .kya-en{font-size:12px;letter-spacing:6px;color:#C0A434;font-weight:700;margin-bottom:10px}
  .kya-h2{font-size:clamp(26px,4vw,36px);font-weight:900;color:#26302A;letter-spacing:2px;margin:0}
  .kya-lead{margin:14px auto 0;font-size:15px;color:#77806F;max-width:640px;line-height:1.75}
  .kya-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:18px;max-width:820px;margin:0 auto}
  .kya-card{display:block;background:#fff;border:1px solid #E8E6E1;border-radius:3px;
    padding:26px 24px;text-decoration:none;transition:.25s;position:relative}
  .kya-card:hover{transform:translateY(-3px);box-shadow:0 12px 30px rgba(43,89,55,.12);
    border-color:rgba(75,135,47,.4)}
  .kya-tag{font-size:11px;letter-spacing:3px;color:#C0A434;font-weight:700;margin-bottom:8px}
  .kya-card h4{font-size:17px;font-weight:900;color:#26302A;margin:0 0 6px;letter-spacing:.5px}
  .kya-card p{font-size:14px;color:#77806F;line-height:1.65;margin:0}
  .kya-go{position:absolute;right:20px;top:24px;color:#C0A434;font-weight:900;font-size:16px}
  @media(max-width:760px){.kya{padding:56px 0}.kya-grid{grid-template-columns:1fr}}
  </style>
"""

CARDS = [
 ("COMPANY",  "https://reihe-industrial.github.io/web/index.html", "關於瑞禾",
  "瑞禾開發｜建築、房產整合團隊——產業用地媒合的公司主體與服務總覽。"),
 ("AGENT",    "https://mac2good909777-commits.github.io/about-mac/", "關於現傑",
  "17+ 年工業不動產實務，從物件媒合延伸到前期評估與規劃的整合服務。"),
 ("PLATFORM", "https://mac2good909777-commits.github.io/about/", "睦聚現傑",
  "中台灣產業用地買賣租賃的專業夥伴，產業資訊與行情分析平台。"),
 ("SERVICE",  "https://mac2good909777-commits.github.io/service-demo/", "購廠分析",
  "買廠房、賣廠房之前，先評估清楚：區位、行情對標、稅務與法規風險四大構面。"),
]


def team_block(full=True):
    cs = CARDS if full else CARDS[:2]
    cards = "".join(
        '      <a class="kya-card" href="%s" target="_blank" rel="noopener">\n'
        '        <div class="kya-tag">%s</div><h4>%s</h4>\n'
        '        <p>%s</p>\n'
        '        <span class="kya-go">&#8594;</span>\n'
        '      </a>\n' % (u, t, h, p) for t, u, h, p in cs)
    return ('<section class="kya">\n' + STYLE +
            '  <div class="kya-in">\n'
            '    <div class="kya-head">\n'
            '      <div class="kya-en">KNOW YOUR AGENT</div>\n'
            '      <h2 class="kya-h2">認識專案團隊</h2>\n'
            '      <div class="kya-lead">買廠賣廠是重大決策──先了解我們怎麼做評估，再談物件。</div>\n'
            '    </div>\n'
            '    <div class="kya-grid">\n' + cards +
            '    </div>\n  </div>\n</section>\n\n')


def strip_team(html):
    html = re.sub(r'(?s)\n?<section class="kya">.*?</section>\n?', '\n', html)
    for m in list(re.finditer('認識專案團隊', html))[::-1]:
        s = html.rfind('<section', 0, m.start())
        e = html.find('</section>', m.start())
        if s >= 0 and e > 0:
            html = html[:s] + html[e + 10:]
    return html


def with_team(html, full):
    html = strip_team(html)
    m = re.search(r'<footer', html)
    if not m:
        raise RuntimeError("找不到 <footer>，無法決定插入位置")
    return html[:m.start()] + team_block(full) + html[m.start():]


def with_noindex(html):
    if "noindex" in html:
        return html
    return re.sub(r'(<meta charset="[^"]+"\s*/?>)',
                  r'\1\n<meta name="robots" content="noindex,nofollow">',
                  html, count=1)


def brief_code(code):
    """簡版目錄：一般接 b；含「-」亂碼後綴者接 -b。"""
    return code + ("-b" if "-" in code else "b")

# ---------------------------------------------------------------- 公開總覽

INDEX_TPL = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>物件介紹｜瑞禾・睦聚</title>
<meta name="robots" content="noindex">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700;900&display=swap" rel="stylesheet">
<style>
:root{--forest:#2B5937;--gold:#C0A434;--ink:#26302A;--muted:#77806F;--border:#E8E6E1}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:"Noto Sans TC","Microsoft JhengHei",sans-serif;background:#FDFCFA;color:#333;line-height:1.7}
.wrap{max-width:760px;margin:0 auto;padding:64px 24px}
.eyebrow{font-size:12px;letter-spacing:5px;color:var(--gold);font-weight:700;margin-bottom:10px}
h1{font-size:30px;font-weight:900;color:var(--ink);letter-spacing:2px;margin-bottom:6px}
.lead{font-size:14px;color:var(--muted);margin-bottom:40px}
a.card{display:block;border:1px solid var(--border);border-radius:3px;padding:24px 26px;text-decoration:none;margin-bottom:16px;transition:.2s;background:#fff}
a.card:hover{border-color:var(--gold);box-shadow:0 10px 26px rgba(43,89,55,.10);transform:translateY(-2px)}
a.card .t{font-size:19px;font-weight:900;color:var(--ink);letter-spacing:1px}
a.card .s{font-size:13px;color:var(--muted);margin-top:4px}
a.card .go{float:right;color:var(--gold);font-weight:900}
footer{margin-top:56px;font-size:12px;color:#AAA;letter-spacing:1px}
</style>
</head>
<body>
<div class="wrap">
  <div class="eyebrow">PROPERTY LISTINGS</div>
  <h1>物件介紹</h1>
  <div class="lead">各物件詳細資料與完整銷售報告書，請洽各頁專案窗口。</div>

%s
  <footer>&copy; 瑞禾不動產經紀股份有限公司｜TEL 04-2380-3560</footer>
</div>
</body>
</html>
"""

CARD_TPL = """  <a class="card" href="./%s/">
    <span class="go">&rarr;</span>
    <div class="t">%s</div>
    <div class="s">%s</div>
  </a>
"""

# ---------------------------------------------------------------- 主流程

def load_cases():
    d = json.load(io.open(os.path.join(ADMIN, "cases.json"), encoding="utf-8"))
    return [c for c in d["cases"] if not c.get("_disabled")]


def sha(path):
    return hashlib.sha256(io.open(path, "rb").read()).hexdigest()


def load_manifest():
    if os.path.isfile(MANIFEST):
        return json.load(io.open(MANIFEST, encoding="utf-8"))
    return {}


def check(cases):
    man, rows = load_manifest(), []
    for c in cases:
        src = os.path.join(SRC, c["code"], "index.html")
        if not os.path.isfile(src):
            rows.append((c["code"], "原稿不存在於 A"))
            continue
        h = sha(src)
        was = man.get(c["code"], {}).get("src_sha256")
        if was is None:
            rows.append((c["code"], "尚未建置"))
        elif was != h:
            rows.append((c["code"], "A 已異動，需重建"))
    extra = [d for d in os.listdir(SRC)
             if os.path.isdir(os.path.join(SRC, d)) and not d.startswith((".", "_"))
             and d not in {c["code"] for c in cases}]
    for d in extra:
        rows.append((d, "A 有新案，cases.json 尚未登錄"))
    return rows


def build(cases, only=None):
    man, done = load_manifest(), []
    for c in cases:
        if only and c["code"] not in only:
            continue
        src = os.path.join(SRC, c["code"], "index.html")
        if not os.path.isfile(src):
            print("略過 %-16s 原稿不存在" % c["code"]); continue
        raw = io.open(src, encoding="utf-8").read()

        full = with_team(raw, True) if c.get("team") == "full" else strip_team(raw)
        if c.get("noindex_main"):
            full = with_noindex(full)
        os.makedirs(os.path.join(DST, c["code"]), exist_ok=True)
        io.open(os.path.join(DST, c["code"], "index.html"), "w", encoding="utf-8").write(full)
        made = [c["code"]]

        if c.get("brief"):
            bc = brief_code(c["code"])
            os.makedirs(os.path.join(DST, bc), exist_ok=True)
            io.open(os.path.join(DST, bc, "index.html"), "w", encoding="utf-8"
                    ).write(with_noindex(with_team(raw, False)))
            made.append(bc)

        man[c["code"]] = {"src_sha256": sha(src), "outputs": made}
        done.append((c["code"], made))

    json.dump(man, io.open(MANIFEST, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2, sort_keys=True)
    return done


def build_index(cases):
    cards = "".join(CARD_TPL % (c["code"], c["card"]["title"], c["card"]["sub"])
                    for c in cases if c.get("on_index") and c.get("card"))
    io.open(os.path.join(DST, "index.html"), "w", encoding="utf-8").write(INDEX_TPL % cards)
    return cards.count('<a class="card"')


if __name__ == "__main__":
    cases = load_cases()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--build" in sys.argv:
        for code, made in build(cases, args or None):
            print("建置 %-16s -> %s" % (code, "、".join(made)))
        print("公開總覽 %d 張卡片" % build_index(cases))
    else:
        rows = check(cases)
        if not rows:
            print("A 與 B 一致，無須重建。")
        for code, why in rows:
            print("待處理 %-16s %s" % (code, why))
