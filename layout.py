# -*- coding: utf-8 -*-
"""
layout.py　—— 頁面版型統一：HERO、KPI 條、footer
================================================

各物件專案的原稿版型不一致（八案八種 hero、八種 footer）。客戶從電子報點不同案，
版面一直變會顯得不專業。本模組在建置時把每頁的最上與最下換成同一套。

模板取自：TCIP3464（有底圖）與 WangTian5483（無底圖的文字型）。

- 有底圖：照片 ＋ 深色遮罩，左側瑞禾 LOGO，右側標籤／標題／副標／兩顆按鈕
- 無底圖：同樣結構，背景改深綠漸層
- KPI 條：深綠底四格金色數字
- footer：全站同一份

設定在 cases.json 的 hero 區塊；底圖來源 image 欄位：
    null      文字型
    "keep"    沿用原頁 .hero 的背景圖
    0,1,2…    取頁內第 N 張 base64 圖
"""
import io, os, re

ADMIN = os.path.dirname(os.path.abspath(__file__))
LOGO = io.open(os.path.join(ADMIN, "assets", "ruihe-logo.txt"), encoding="utf-8").read().strip()

TEL_DISPLAY = "0953-909-777"
TEL_HREF = "tel:0953909777"

# ---------------------------------------------------------------- 樣式

CSS = """<style>
/* ===== 統一 HERO／KPI／FOOTER（由 layout.py 產生，勿手改） ===== */
.uh{position:relative;min-height:74vh;display:flex;align-items:flex-end;
  background-size:cover;background-position:center;color:#fff}
.uh-txt{background:linear-gradient(150deg,#1B3A24 0%,#2B5937 58%,#22462C 100%)}
.uh-in{max-width:1120px;margin:0 auto;padding:56px 24px 60px;width:100%;
  display:flex;align-items:flex-end;gap:34px;flex-wrap:wrap}
.uh-logo{background:#fff;border-radius:6px;padding:16px 18px;flex:0 0 auto;
  box-shadow:0 10px 34px rgba(0,0,0,.28)}
.uh-logo img{display:block;width:150px;height:auto}
.uh-body{flex:1 1 460px;min-width:0}
.uh-tag{display:inline-block;border:1px solid rgba(212,184,74,.85);color:#E4CE7C;
  font-size:15px;letter-spacing:.24em;padding:7px 18px;border-radius:2px;margin-bottom:20px}
.uh-h1{font-family:"Noto Serif TC",serif;font-weight:900;letter-spacing:.03em;
  font-size:clamp(34px,5.4vw,58px);line-height:1.16;margin:0;color:#fff;
  text-shadow:0 2px 18px rgba(0,0,0,.4);text-wrap:balance}
.uh-sub{margin-top:18px;font-size:18px;line-height:1.75;color:rgba(255,255,255,.94);
  max-width:60ch;text-shadow:0 1px 10px rgba(0,0,0,.35)}
.uh-cta{display:flex;flex-wrap:wrap;gap:14px;margin-top:30px}
.uh-btn{display:inline-block;text-decoration:none;font-size:17px;font-weight:700;
  padding:15px 30px;border-radius:3px;letter-spacing:.04em;transition:.2s;border:1px solid transparent}
.uh-b1{background:#C0A434;color:#1B2A18}
.uh-b1:hover{background:#D8BC55}
.uh-b2{border-color:rgba(255,255,255,.62);color:#fff}
.uh-b2:hover{background:rgba(255,255,255,.14);border-color:#fff}
.uh-btn:focus-visible{outline:3px solid #E4CE7C;outline-offset:3px}

.ukpi{background:#2B5937;color:#fff}
.ukpi-in{max-width:1120px;margin:0 auto;padding:34px 24px;display:grid;
  grid-template-columns:repeat(4,1fr);gap:22px;text-align:center}
.ukpi .n{font-family:"Noto Serif TC",serif;font-weight:900;color:#D8BC55;
  font-size:clamp(30px,3.6vw,42px);line-height:1.15;font-variant-numeric:tabular-nums}
.ukpi .n em{font-style:normal;font-size:.5em;margin-left:5px;letter-spacing:.06em}
.ukpi .l{margin-top:8px;font-size:15px;color:rgba(255,255,255,.86);letter-spacing:.03em;line-height:1.55}

.uft{background:#15211A;color:#9DB29A;padding:52px 24px 44px;font-size:15px;line-height:1.9}
.uft-in{max-width:1000px;margin:0 auto;text-align:center}
.uft-co{color:#E7EDE5;font-family:"Noto Serif TC",serif;font-weight:700;font-size:19px;letter-spacing:.05em}
.uft-en{font-size:14px;letter-spacing:.14em;color:#7C8E7C;margin-top:5px}
.uft-line{margin-top:18px}
.uft-line b{color:#D8BC55;font-weight:700}
.uft-line a{color:#D8BC55;text-decoration:none;font-weight:700}
.uft-line a:hover{text-decoration:underline}
.uft-note{margin-top:22px;padding-top:20px;border-top:1px solid #24352A;
  font-size:14px;color:#7C8E7C;line-height:1.85;max-width:74ch;margin-left:auto;margin-right:auto}

@media(max-width:820px){
  .uh{min-height:auto}
  .uh-in{padding:40px 18px 44px;gap:22px}
  .uh-logo img{width:112px}
  .ukpi-in{grid-template-columns:repeat(2,1fr);gap:26px 16px}
}
@media(prefers-reduced-motion:reduce){.uh-btn{transition:none}}
</style>"""

FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Noto+Sans+TC:wght@400;500;700;900&family=Noto+Serif+TC:wght@700;900&display=swap">')

MASK = "linear-gradient(rgba(16,26,15,.42),rgba(16,26,15,.80))"

# ---------------------------------------------------------------- 組件

def hero_html(h):
    """h = cases.json 的 hero 設定 dict（image 已解析成實際 data URI 或 None）"""
    bg = h.get("_uri")
    style = ' style="background-image:%s,url(\'%s\')"' % (MASK, bg) if bg else ""
    cls = "uh" if bg else "uh uh-txt"
    cta2 = h.get("cta2") or {}
    b2 = ('<a class="uh-btn uh-b2" href="%s">%s</a>' % (cta2["href"], cta2["label"])) if cta2 else ""
    kpis = "".join(
        '<div><div class="n">%s<em>%s</em></div><div class="l">%s</div></div>' % (n, u, l)
        for n, u, l in h["kpis"])
    return """
<section class="%s"%s>
  <div class="uh-in">
    <div class="uh-logo"><img src="%s" alt="瑞禾開發"></div>
    <div class="uh-body">
      <div class="uh-tag">%s</div>
      <h1 class="uh-h1">%s</h1>
      <div class="uh-sub">%s</div>
      <div class="uh-cta">
        <a class="uh-btn uh-b1" href="%s">&#9742;　專案負責人 %s</a>
        %s
      </div>
    </div>
  </div>
</section>
<div class="ukpi"><div class="ukpi-in">%s</div></div>
""" % (cls, style, LOGO, h["eyebrow"], h["title"], h["sub"],
       TEL_HREF, TEL_DISPLAY, b2, kpis)


FOOTER = """
<footer class="uft">
  <div class="uft-in">
    <div class="uft-co">瑞禾不動產經紀股份有限公司</div>
    <div class="uft-en">RUEI.HE REAL ESTATE BROKERAGE CO., LTD.</div>
    <div class="uft-line">臺中市南屯區益豐路四段 91 號</div>
    <div class="uft-line">專案負責人　<b>張現傑</b>　<a href="%s">%s</a><br>
      不動產經紀人（108）中市經紀字第 01847 號</div>
    <div class="uft-note">
      本頁資訊依現有資料善意整理，僅供參考，不構成任何要約或承諾。
      面積、使用分區、建物登記等以地政機關登記資料及不動產說明書為準；
      價格與交易條件請洽專案負責人。
    </div>
  </div>
</footer>
""" % (TEL_HREF, TEL_DISPLAY)

# ---------------------------------------------------------------- 切割

def _cut(html, i):
    """從 i（元素起始 '<'）回傳該元素的 (起, 迄)"""
    tag = re.match(r"<(\w+)", html[i:]).group(1)
    depth = 0
    for m in re.finditer(r"<(/?)%s\b" % tag, html[i:], re.I):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return i, html.find(">", i + m.start()) + 1
    return i, len(html)


def _hero_bg_from_css(html):
    """取原頁 .hero 規則裡的背景圖 data URI"""
    css = " ".join(re.findall(r"(?is)<style[^>]*>(.*?)</style>", html))
    m = re.search(r"\.hero\s*\{([^}]*)\}", css)
    if not m:
        return None
    u = re.search(r"url\(['\"]?(data:image/[^'\")]+)", m.group(1))
    return u.group(1) if u else None


def _nth_image(html, n):
    imgs = re.findall(r"data:image/\w+;base64,[A-Za-z0-9+/=]{200,}", html)
    return imgs[n] if n < len(imgs) else None


def apply(html, hero_cfg):
    """換掉原頁的 hero（含緊接的 KPI 條）與 footer，插入統一版型。"""
    cfg = dict(hero_cfg)

    # 1. 決定底圖
    img = cfg.get("image")
    if img == "keep":
        cfg["_uri"] = _hero_bg_from_css(html)
    elif isinstance(img, int):
        cfg["_uri"] = _nth_image(html, img)
    else:
        cfg["_uri"] = None

    # 2. 移除舊 hero（含其後緊接的 stats／kpis 條）
    html = re.sub(r"(?s)\n?<section class=\"uh( uh-txt)?\".*?</section>\s*"
                  r"<div class=\"ukpi\">.*?</div>\s*</div>\n?", "\n", html)
    m = re.search(r'<(?:header|div|section)[^>]*class="[^"]*\bhero\b[^"]*"', html)
    if m:
        a, b = _cut(html, m.start())
        tail = html[b:b + 300]
        nx = re.match(r'\s*<(\w+)[^>]*class="[^"]*\b(?:stats|kpis)\b[^"]*"', tail)
        if nx:
            _, b2 = _cut(html, b + tail.index("<"))
            b = b2
        html = html[:a] + html[b:]

    # 3. 移除舊 footer
    html = re.sub(r"(?s)\n?<footer.*?</footer>\s*", "\n", html)

    # 4. 插入新的
    fonts = "" if "Noto+Serif+TC" in html else FONTS
    html = html.replace("</head>", fonts + CSS + "\n</head>", 1)
    m = re.search(r"<body[^>]*>", html)
    html = html[:m.end()] + "\n" + hero_html(cfg) + html[m.end():]
    m = re.search(r"</body>", html)
    return html[:m.start()] + FOOTER + "\n" + html[m.start():]
