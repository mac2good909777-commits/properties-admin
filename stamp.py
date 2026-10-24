# -*- coding: utf-8 -*-
"""頁面「本頁更新」日期戳記。

為什麼（2026-10-24）：
  DT／NB 兩台都會改這些頁面。DT 本機曾落後 GitHub 16 個 commit 還不自知，
  若在舊版上改完再推，就會把另一台的新版蓋掉。每頁標上最後更新時間，
  一眼就能比對本機與線上哪一版比較新。

規則：
  - 日期代表「內容最後一次真的改變」，不是「最後一次建置」。
    重新建置但內容沒變 → 沿用舊日期；否則全站重建會讓每頁都變成今天，失去比較意義。
  - 第一次蓋章（舊檔沒有戳記）且內容相同 → 用該檔在 git 的最後 commit 時間。
  - 戳記包在 <!--stamp--> … <!--/stamp--> 之間，可重複套用、可整段剝除。
"""
import datetime, io, os, re, subprocess

TAG = re.compile(r"<!--stamp-->.*?<!--/stamp-->\n?", re.S)
FMT = "%Y-%m-%d %H:%M"


def strip(html):
    return TAG.sub("", html)


def _norm(html):
    """比對用：去戳記、去 GA 碼、去 \\r。
    GA 碼不算內容 —— 2026-10-20 改 GA 片段時全站重建，若算進去，每頁日期都會被刷成那天。
    \\r：Windows autocrlf 會讓同內容的檔指紋不同。"""
    import ga
    return ga.strip(strip(html)).replace("\r", "")


def read(html):
    """讀出頁面上的戳記時間字串；沒有就回 None。"""
    m = re.search(r'<meta name="page-updated" content="([^"]+)"', html)
    return m.group(1) if m else None


def _git_time(path):
    """往回翻 git 歷史，找出「目前這份內容」第一次出現的 commit 時間。
    只有 GA 碼或換行不同的 commit 視為同一份內容，繼續往前找。"""
    try:
        d = os.path.dirname(os.path.abspath(path))
        name = os.path.basename(os.path.dirname(path)) + "/" + os.path.basename(path)
        root = os.path.dirname(d)
        cur = _norm(io.open(path, encoding="utf-8").read())
        log = subprocess.run(
            ["git", "log", "--format=%H %cd", "--date=format:" + FMT, "--", name],
            cwd=root, capture_output=True, text=True, encoding="utf-8").stdout.splitlines()
        when = None
        for row in log:                       # 新 → 舊
            h, t = row.split(" ", 1)
            old = subprocess.run(["git", "show", "%s:%s" % (h, name)], cwd=root,
                                 capture_output=True, text=True, encoding="utf-8").stdout
            if _norm(old) != cur:
                break
            when = t
        return when
    except Exception:
        return None


def _now():
    return datetime.datetime.now().strftime(FMT)


def _insert(html, when):
    """只寫進原始碼（<head> 裡的註解＋meta），頁面上不顯示 —— 這是給維護者比對用的，不是給讀者看的。"""
    tag = ('<!--stamp--><!-- 本頁更新 %s --><meta name="page-updated" content="%s"><!--/stamp-->\n'
           % (when, when))
    html, n = re.subn(r"(<head[^>]*>\n?)", lambda m: m.group(1) + tag, html, count=1, flags=re.I)
    if not n:
        raise RuntimeError("找不到 <head>，無法插入更新日期")
    return html


def write(path, html):
    """蓋上更新日期後寫檔。回傳 (時間字串, 內容是否有變)。"""
    html = strip(html)
    when, changed = None, True
    if os.path.isfile(path):
        old = io.open(path, encoding="utf-8").read()
        if _norm(old) == _norm(html):
            changed = False
            when = read(old) or _git_time(path)
    when = when or _now()
    io.open(path, "w", encoding="utf-8").write(_insert(html, when))
    return when, changed
