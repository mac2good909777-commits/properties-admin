# -*- coding: utf-8 -*-
"""
ledger.py　—— 台帳表格與摘要自動同步
=====================================

台帳 `index.html` 的說明段落是手寫的，但**表格與頂端摘要改由本模組從 cases.json 產生**，
避免新案加了卻忘了補台帳（先前就漏過 DajiaSRC 與 DayaCrane 兩案）。

只覆寫兩個區塊，其餘內容原封不動：
    <tbody> … </tbody>
    <div class="tally"> … </div>

上架日與更新日取自 properties-src 的 git 紀錄（首次／最後一次 commit）。
"""
import io, json, os, re, subprocess

ADMIN = os.path.dirname(os.path.abspath(__file__))
SRC = r"C:\Users\dell\Documents\Claude-DT\projects\20260904-主題行銷頁\properties-src"
BASE = "https://mac2good909777-commits.github.io/properties/"

STATUS = {"live": ("在售", "t-live"), "quiet": ("潛銷", "t-warm"),
          "done": ("已結案", "t-off"), "other": ("顧問頁", "t-warm")}


def brief_code(code):
    return code + ("-b" if "-" in code else "b")


def colleague_code(code):
    return code + ("-c" if "-" in code else "c")


def _dates(code):
    """回傳 (上架日, 更新日)，格式 MM/DD；取不到就回空字串。"""
    path = "%s/index.html" % code
    try:
        first = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%ad", "--date=format:%m/%d", "--", path],
            cwd=SRC, capture_output=True, text=True, timeout=20).stdout.strip().splitlines()
        last = subprocess.run(
            ["git", "log", "-1", "--format=%ad", "--date=format:%m/%d", "--", path],
            cwd=SRC, capture_output=True, text=True, timeout=20).stdout.strip()
        return (first[-1] if first else last), last
    except Exception:
        return "", ""


def _links(c):
    out = ['<a class="go go-full" href="%s%s/" target="_blank" rel="noopener">'
           '完整版 <span class="n">四卡</span></a>' % (BASE, c["code"])]
    if c.get("brief"):
        out.append('<a class="go go-brief" href="%s%s/" target="_blank" rel="noopener">'
                   '簡版 <span class="n">兩卡</span></a>' % (BASE, brief_code(c["code"])))
        out.append('<a class="go go-col" href="%s%s/" target="_blank" rel="noopener">'
                   '同事版 <span class="n">一卡・無個資</span></a>' % (BASE, colleague_code(c["code"])))
    return "\n        ".join(out)


def _row(c):
    label, cls = STATUS.get(c.get("status", "live"), ("", "t-off"))
    if c.get("kind") == "rent" and c.get("status") == "live":
        label = "在租"
    up, upd = _dates(c["code"])
    note = ('\n      <div class="memo">%s</div>' % c["note"]) if c.get("note") else ""
    past = ' class="past"' if c.get("status") == "done" else ""
    return """<tr data-s="%s"%s>
    <td>
      <div class="case">%s</div>
      <div class="code mono">%s</div>
      <div class="where">%s</div>
    </td>
    <td class="kind">%s</td>
    <td class="spec">%s</td>
    <td class="ask%s">%s</td>
    <td class="date"><b>%s</b>更新 %s</td>
    <td><span class="tag %s">%s</span></td>
    <td>
      <div class="links">
        %s
      </div>%s
    </td>
  </tr>""" % (c.get("status", "live"), past, c["name"], c["code"], c.get("loc", ""),
              c.get("type", ""), c.get("spec", ""),
              "" if re.search(r"\d", c.get("price", "")) and "億" in c.get("price", "") else " q",
              c.get("price", ""), up, upd, cls, label, _links(c), note)


def sync(cases, path=None):
    """把台帳的 <tbody> 與 .tally 依 cases.json 重寫。回傳 (案數, 頁數)。"""
    path = path or os.path.join(ADMIN, "index.html")
    s = io.open(path, encoding="utf-8").read()

    rows = "\n\n  ".join(_row(c) for c in cases)
    a = s.find("<tbody>") + len("<tbody>")
    b = s.find("</tbody>")
    s = s[:a] + "\n\n  " + rows + "\n\n  " + s[b:]

    pages = sum(1 + (2 if c.get("brief") else 0) for c in cases)
    live = sum(1 for c in cases if c.get("status") == "live")
    trio = sum(1 for c in cases if c.get("brief"))
    tally = """<div class="tally">
  <div><b>%d</b><span>案件</span></div>
  <div><b>%d</b><span>頁面上線</span></div>
  <div><b>%d</b><span>在售／在租</span></div>
  <div><b>%d</b><span>完整版＋簡版＋同事版</span></div>
  <div><b>全站</b><span>noindex 不進搜尋</span></div>
</div>""" % (len(cases), pages, live, trio)
    s = re.sub(r'(?s)<div class="tally">.*?</div>\s*</div>', tally, s, count=1)

    # 同事版連結的樣式（只加一次）
    if ".go-col{" not in s:
        s = s.replace(".go-brief{",
                      ".go-col{background:var(--sunk);color:var(--dim);border-color:var(--line)}\n"
                      ".go-col:hover{border-color:var(--gold-bright);color:var(--gold)}\n"
                      ".go-brief{", 1)

    io.open(path, "w", encoding="utf-8").write(s)
    return len(cases), pages
