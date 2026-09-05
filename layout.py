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
.uh-txt{min-height:0;background:linear-gradient(150deg,#1B3A24 0%,#2B5937 58%,#22462C 100%)}
.uh-txt .uh-in{padding:70px 24px 66px;align-items:center}
.uh-in{max-width:1120px;margin:0 auto;padding:56px 24px 60px;width:100%;
  display:flex;align-items:flex-end;gap:34px;flex-wrap:wrap}
.uh-logo{background:#fff;border-radius:6px;padding:16px 18px;flex:0 0 auto;
  box-shadow:0 10px 34px rgba(0,0,0,.28)}
.uh-logo img{display:block;width:150px;height:auto}
.uh-body{flex:1 1 460px;min-width:0}
.uh-tag{display:inline-block;border:1px solid rgba(212,184,74,.85);color:#E4CE7C;
  font-size:15px;letter-spacing:.24em;padding:7px 18px;border-radius:2px;margin-bottom:20px}
.uh-w{display:inline-block}
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

.uft{background:#15211A;color:#9DB29A;padding:34px 24px 30px;font-size:15px;line-height:1.85}
.uft-in{max-width:1000px;margin:0 auto;text-align:center}
.uft-co{color:#E7EDE5;font-family:"Noto Serif TC",serif;font-weight:700;font-size:19px;letter-spacing:.05em}
.uft-en{font-size:14px;letter-spacing:.1em;color:#7C8E7C;margin-top:6px}
.uft-addr{margin-top:12px}
.uft-cred{margin-top:26px;font-size:14px;color:#7C8E7C;line-height:2}
.uft-note{margin-top:26px;padding-top:20px;border-top:1px solid #24352A;
  font-size:14px;color:#6E7F6E;line-height:1.85;max-width:74ch;margin-left:auto;margin-right:auto}

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
    # 標題用全形空格分段，各段包成 inline-block，手機才不會從詞中間斷行
    title = "".join('<span class="uh-w">%s</span>' % t
                    for t in h["title"].split("　") if t)
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
""" % (cls, style, LOGO, h["eyebrow"], title, h["sub"],
       TEL_HREF, TEL_DISPLAY, b2, kpis)


IM_CSS = """<style>
/* ===== 統一「完整銷售報告書 備索」（由 layout.py 產生，勿手改） ===== */
.uim{background:linear-gradient(160deg,#15211A 0%,#1D2C23 100%);color:#fff;padding:76px 22px}
.uim-in{max-width:1040px;margin:0 auto}
.uim-head{text-align:center;margin-bottom:34px}
.uim-en{font-size:14px;letter-spacing:.24em;color:#D8BC55;font-weight:700;margin-bottom:10px}
.uim-h2{font-family:"Noto Serif TC",serif;font-weight:700;font-size:clamp(24px,3.4vw,32px);
  color:#fff;letter-spacing:.06em;margin:0}
.uim-lead{margin:14px auto 0;font-size:16px;color:rgba(255,255,255,.72);max-width:60ch;line-height:1.8}
.uim-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:22px}
.uim-item{border:1px solid rgba(255,255,255,.14);border-radius:3px;padding:26px 20px;text-align:center}
.uim-item .ic{width:34px;height:34px;margin:0 auto 12px;border:1px solid #C0A434;color:#D8BC55;
  font-weight:900;font-size:16px;border-radius:50%;display:flex;align-items:center;justify-content:center}
.uim-item h4{font-size:16px;font-weight:700;letter-spacing:.06em;margin:0 0 6px;color:#fff}
.uim-item p{font-size:14.5px;color:rgba(255,255,255,.62);line-height:1.7;margin:0}
.uim-note{text-align:center;font-size:clamp(18px,2.6vw,23px);font-weight:900;letter-spacing:.08em;
  margin-top:30px;color:#fff}
.uim-note em{font-style:normal;color:#D8BC55}
@media(max-width:760px){
  .uim{padding:56px 16px}
  .uim-grid{grid-template-columns:1fr;gap:12px}
}
</style>"""


def im_html(cfg):
    """cfg = cases.json 的 im 設定。items 為三張卡，extra 為可選的附加區塊檔名。"""
    items = "".join(
        '<div class="uim-item"><div class="ic">%s</div><h4>%s</h4><p>%s</p></div>' % (k, h, p)
        for k, h, p in cfg["items"])
    lead = '<div class="uim-lead">%s</div>' % cfg["lead"] if cfg.get("lead") else ""
    extra = ""
    if cfg.get("extra"):
        fp = os.path.join(ADMIN, "assets", cfg["extra"])
        if os.path.isfile(fp):
            extra = io.open(fp, encoding="utf-8").read()
    return """
<section class="uim" id="im">
  <div class="uim-in">
    <div class="uim-head">
      <div class="uim-en">INFORMATION MEMORANDUM</div>
      <h2 class="uim-h2">完整銷售報告書　備索</h2>
      %s
    </div>
    <div class="uim-grid">%s</div>
    %s
    <div class="uim-note">本案採<em>預約制</em>提供資料與帶看，詳見下方專案窗口</div>
  </div>
</section>
""" % (lead, items, extra)


def _drop_im(html):
    """移除各頁原有的備索段（只認 class 含 im 的區塊，避免誤刪其他段落）。"""
    for pat in (r'<section class="im"[^>]*>', r'<section class="uim"[^>]*>'):
        while True:
            m = re.search(pat, html)
            if not m:
                break
            a, b = _cut(html, m.start())
            html = html[:a] + html[b:]
    return html


QR = io.open(os.path.join(ADMIN, "assets", "line-qr.txt"), encoding="utf-8").read().strip()

CONTACT_CSS = """<style>
/* ===== 統一專案窗口卡（由 layout.py 產生，勿手改） ===== */
.uct{background:#F7F6F1;padding:70px 22px}
.uct-head{text-align:center;margin-bottom:34px}
.uct-en{font-size:14px;letter-spacing:.24em;color:#8E7318;font-weight:700;margin-bottom:8px}
.uct-h2{font-family:"Noto Serif TC",serif;font-weight:700;font-size:clamp(24px,3.4vw,30px);
  color:#1E2620;letter-spacing:.06em;margin:0}
.ctc{max-width:660px;margin:0 auto;background:#fff;border:1px solid #DEDCD1;
  border-radius:4px;padding:28px 30px;text-align:left}
.ctc-top{display:flex;gap:28px;align-items:center}
.ctc-who{flex:1 1 auto;min-width:0;padding-right:26px;border-right:1px solid #DEDCD1}
.ctc-eyebrow{font-size:14px;letter-spacing:.24em;color:#8E7318;font-weight:700}
.ctc-name{font-size:28px;font-weight:900;color:#1E2620;letter-spacing:.06em;margin:0;
  line-height:1.25;display:flex;align-items:baseline;gap:14px;flex-wrap:wrap}
.ctc-name span{font-size:15px;font-weight:400;color:#67705F;letter-spacing:.1em}
.ctc-tel{display:inline-block;font-size:33px;font-weight:900;color:#2B5937;text-decoration:none;
  letter-spacing:.01em;margin:16px 0 0;font-variant-numeric:tabular-nums;line-height:1.05}
.ctc-tel:hover{color:#8E7318}
.ctc-qr{flex:0 0 auto;text-align:center}
.ctc-qr img{width:120px;height:120px;border:1px solid #DEDCD1;border-radius:6px;
  padding:6px;background:#fff;display:block}
.ctc-qr span{display:block;margin-top:8px;font-size:14px;color:#67705F;letter-spacing:.08em}
@media(max-width:640px){
  .uct{padding:52px 16px}
  .ctc{padding:24px 20px}
  .ctc-top{flex-direction:column;gap:20px;align-items:flex-start}
  .ctc-who{border-right:0;padding-right:0;border-bottom:1px solid #DEDCD1;padding-bottom:18px;width:100%}
  .ctc-tel{font-size:29px}
}
</style>"""

CONTACT = """
<section class="uct" id="contact">
  <div class="uct-head">
    <div class="uct-en">PROJECT CONTACT</div>
    <h2 class="uct-h2">專案窗口</h2>
  </div>
  <div class="ctc">
    <div class="ctc-top">
      <div class="ctc-who">
        <div class="ctc-name">張現傑<span>瑞禾開發　工業地產部業務總監</span></div>
        <a class="ctc-tel" href="%s">%s</a>
      </div>
      <div class="ctc-qr">
        <img src="%s" alt="加 LINE 張現傑">
        <span>掃碼加 LINE</span>
      </div>
    </div>
  </div>
</section>
""" % (TEL_HREF, TEL_DISPLAY, QR)


def _drop_contact(html):
    """移除各頁原有的聯絡卡（只拿掉卡片本體，保留該段的文案）。"""
    # 整段就是聯絡區的，直接刪整段
    for pat in (r'<section class="contact"[^>]*>', r'<section class="uct"[^>]*>'):
        while True:
            m = re.search(pat, html)
            if not m:
                break
            a, b = _cut(html, m.start())
            html = html[:a] + html[b:]
    # 只是段落裡的一張卡，刪卡就好
    for cls in ("ctc", "ct-card", "contact-card", "qr-row", "ctabox", "r contact"):
        while True:
            m = re.search(r'<div class="%s"[^>]*>' % re.escape(cls), html)
            if not m:
                break
            a, b = _cut(html, m.start())
            html = html[:a] + html[b:]
    return html


FOOTER = """
<footer class="uft">
  <div class="uft-in">
    <div class="uft-co">瑞禾不動產經紀股份有限公司</div>
    <div class="uft-en">RUEI.HE REAL ESTATE BROKERAGE CO., LTD.</div>
    <div class="uft-addr">臺中市南屯區益豐路四段 91 號</div>
    <div class="uft-cred">
      <div>經濟部產業園區管理局 115 年度產業用地媒合專案 委託執行單位</div>
      <div>不動產經紀人（108）中市經紀字第 01847 號</div>
    </div>
    <div class="uft-note">
      本頁資訊依現有資料整理僅供參考，不構成任何要約或承諾。
      面積、使用分區、建物登記等以地政機關登記資料及不動產說明書為準，
      價格與交易條件請洽專案負責人。
    </div>
  </div>
</footer>
"""

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


def apply(html, hero_cfg, im_cfg=None):
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

    # 3b. 移除各頁原有的聯絡卡與備索段
    html = _drop_contact(html)
    html = _drop_im(html)

    # 4. 插入新的
    fonts = "" if "Noto+Serif+TC" in html else FONTS
    html = html.replace("</head>", fonts + CSS + IM_CSS + CONTACT_CSS + "\n</head>", 1)
    m = re.search(r"<body[^>]*>", html)
    html = html[:m.end()] + "\n" + hero_html(cfg) + html[m.end():]
    m = re.search(r"</body>", html)
    # 尾段固定順序：備索 → 專案窗口 →（團隊卡由 build.py 插入）→ footer
    tail = (im_html(im_cfg) if im_cfg else "") + CONTACT + FOOTER
    return html[:m.start()] + tail + "\n" + html[m.start():]


# ---------------------------------------------------------------- 可讀性

MOBILE_CSS = """<style>
/* ===== 可讀性與手機適配（由 layout.py 產生，勿手改） ===== */
html{-webkit-text-size-adjust:100%}
img,svg,video{max-width:100%;height:auto}
.tbl-scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:0 0 18px}
.tbl-scroll>table{min-width:520px}
@media(max-width:640px){
  h1{line-height:1.28}
  h2{line-height:1.36}
  body{line-height:1.75}
}
</style>"""


def _bump(px):
    """把小於 14px 的字級抬到 14 以上，並保留原有大小順序。"""
    if px >= 14:
        return None
    if px <= 11:
        return 14.0
    if px <= 12.5:
        return 14.5
    if px <= 13.5:
        return 15.0
    return 15.5


def readability(html):
    """字級下限 14px、無捲軸的表格包一層、補上手機適配樣式。"""
    def fix(m):
        nv = _bump(float(m.group(1)))
        return m.group(0) if nv is None else "font-size:%gpx" % nv

    html = re.sub(r"font-size:\s*([0-9.]+)px", fix, html)

    spots = []
    for m in re.finditer(r"<table\b", html):
        a = m.start()
        near = html[max(0, a - 260):a]
        if "overflow-x" in near or "tbl-scroll" in near or "tablewrap" in near:
            continue
        spots.append((a, _cut(html, a)[1]))
    for a, e in reversed(spots):
        html = html[:a] + '<div class="tbl-scroll">' + html[a:e] + "</div>" + html[e:]

    if "tbl-scroll{overflow-x" not in html:
        html = html.replace("</head>", MOBILE_CSS + "\n</head>", 1)
    return html
