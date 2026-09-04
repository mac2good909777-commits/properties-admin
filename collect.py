# -*- coding: utf-8 -*-
"""
收頁一致化工具
================
各物件專案自行把一頁式 push 到 public repo `properties` 後，在這裡執行本工具，
自動完成：套「認識專案團隊」完整版四卡 → 產簡版 b 兩卡 → 簡版加 noindex → 回報。

用法
----
    python collect.py            只檢查，列出不合規的頁面（不改任何檔）
    python collect.py --fix      實際套用
    python collect.py --fix TCIP2098 Industrial21   只處理指定目錄

不處理的目錄寫在 SKIP（顧問頁、已結案、原生實作的例外）。
"""
import io, os, re, sys

REPO = r"C:\Claude\projects\properties"

# 不套用本規則的目錄
SKIP = {
    "TCIP38-parking": "顧問提案頁，非物件銷售頁",
    "HotaChiayi3":    "一次性物件已結案，不再上架",
    "WangTian5483":   "使用該頁原生 .more-card 實作，視覺一致，不改寫",
    "WangTian5483b":  "同上（簡版）",
}

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


def block(full=True):
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


def strip_old(html):
    """移除本工具先前插入的區塊，以及各 session 自行做的殘缺團隊區塊。"""
    html = re.sub(r'(?s)\n?<section class="kya">.*?</section>\n?', '\n', html)
    # 殘缺版：有「認識專案團隊」標題但不是 kya 區塊者，整段 <section> 拔掉
    for m in list(re.finditer(r'認識專案團隊', html))[::-1]:
        s = html.rfind('<section', 0, m.start())
        e = html.find('</section>', m.start())
        if s >= 0 and e > 0:
            html = html[:s] + html[e + 10:]
    return html


def insert(html, full):
    html = strip_old(html)
    m = re.search(r'<footer', html)
    if not m:
        raise RuntimeError("找不到 <footer>，無法決定插入位置")
    return html[:m.start()] + block(full) + html[m.start():]


def add_noindex(html):
    if "noindex" in html:
        return html
    return re.sub(r'(<meta charset="[^"]+"\s*/?>)',
                  r'\1\n<meta name="robots" content="noindex,nofollow">',
                  html, count=1)


def brief_dir(name):
    """簡版目錄名：一般接 b；主目錄已含「-」亂碼後綴者接 -b。"""
    return name + ("-b" if "-" in name else "b")


def scan():
    """回傳 [(主版目錄, 簡版目錄, 問題清單)]"""
    out = []
    for d in sorted(os.listdir(REPO)):
        p = os.path.join(REPO, d, "index.html")
        if not os.path.isfile(p) or d.startswith((".", "_")):
            continue
        if d in SKIP or d.endswith("b") and os.path.isdir(os.path.join(REPO, d[:-1])):
            continue
        if d.endswith("-b") and os.path.isdir(os.path.join(REPO, d[:-2])):
            continue
        h = io.open(p, encoding="utf-8").read()
        bd = brief_dir(d)
        bp = os.path.join(REPO, bd, "index.html")
        probs = []
        if h.count('a class="kya-card"') != 4:
            probs.append("主版缺完整版四卡")
        if not os.path.isfile(bp):
            probs.append("缺簡版 %s" % bd)
        else:
            b = io.open(bp, encoding="utf-8").read()
            if b.count('a class="kya-card"') != 2:
                probs.append("簡版卡片數不對")
            if "noindex" not in b:
                probs.append("簡版缺 noindex")
        if probs:
            out.append((d, bd, probs))
    return out


def fix(dirs=None):
    done = []
    for d, bd, probs in scan():
        if dirs and d not in dirs:
            continue
        src = os.path.join(REPO, d, "index.html")
        h = io.open(src, encoding="utf-8").read()
        io.open(src, "w", encoding="utf-8").write(insert(h, True))
        os.makedirs(os.path.join(REPO, bd), exist_ok=True)
        io.open(os.path.join(REPO, bd, "index.html"), "w", encoding="utf-8"
                ).write(add_noindex(insert(h, False)))
        done.append((d, bd, probs))
    return done


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--fix" in sys.argv:
        done = fix(args or None)
        if not done:
            print("沒有需要處理的頁面。")
        for d, bd, probs in done:
            print("修正  %-16s -> %-18s （原因：%s）" % (d, bd, "、".join(probs)))
    else:
        rows = scan()
        if not rows:
            print("全部合規，無須處理。")
        for d, bd, probs in rows:
            print("待處理 %-16s 簡版應為 %-18s %s" % (d, bd, "、".join(probs)))
        for d, why in sorted(SKIP.items()):
            print("略過   %-16s %s" % (d, why))
