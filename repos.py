# -*- coding: utf-8 -*-
"""找出 A／B 兩個 repo 在本機的位置。

為什麼（2026-10-24）：
  本機資料夾要改成中文名，但 DT／NB 兩台的資料夾名稱不一定同步改。
  所以不靠資料夾名稱，改看每個資料夾的 git remote 連到哪個 GitHub repo。
  GitHub repo 名稱（properties-src／properties）是網址的一部分，永遠不改。

找法：在 properties-admin 的上一層，逐一檢查兄弟資料夾的 .git/config。
"""
import io, os, re

ADMIN = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(ADMIN)


def _remote(path):
    cfg = os.path.join(path, ".git", "config")
    if not os.path.isfile(cfg):
        return None
    m = re.search(r"url\s*=\s*\S*?/([^/\s]+?)(?:\.git)?\s*$",
                  io.open(cfg, encoding="utf-8").read(), re.M)
    return m.group(1) if m else None


def find(repo):
    """回傳 GitHub repo 名稱為 repo 的本機資料夾絕對路徑。"""
    hits = [os.path.join(PARENT, d) for d in sorted(os.listdir(PARENT))
            if os.path.isdir(os.path.join(PARENT, d)) and _remote(os.path.join(PARENT, d)) == repo]
    if len(hits) != 1:
        raise RuntimeError("在 %s 找到 %d 個連到 %s 的資料夾：%s"
                           % (PARENT, len(hits), repo, hits or "無"))
    return hits[0]


SRC = find("properties-src")   # A 原稿
DST = find("properties")       # B 成品
