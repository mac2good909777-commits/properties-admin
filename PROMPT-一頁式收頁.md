# 一頁式行銷頁　製作與收頁

分工：**各物件專案做內容並自行 push；一致化、簡版、總覽、台帳由「主題行銷頁」對話統一處理。**

repo 本身就是交件通道，不需要另外交路徑。各專案 push 完什麼都不用管。

---

## A. 給各物件專案的提示詞（複製這段）

```
產出這個物件的一頁式行銷頁，做完直接 push 到公開 repo。
簡版分身、公開總覽卡片、管理台帳都不用做 —— 那些由「主題行銷頁」對話統一處理。

【案名與代號】
案名：[中文案名]
PropCode：[英文目錄代號]
類型：[售／租／買方需求／顧問提案]

【產出規格】
- 單一自足的 index.html，照片一律 base64 內嵌，不放獨立圖檔
  （單檔要能直接寄送、離線可讀）
- 外部相依只允許 Google Fonts，其餘一律內嵌
- 品牌配色瑞禾綠金：--forest:#2B5937 / --gold:#C0A434 / --ink:#26302A
  / --muted:#77806F / --border:#E8E6E1
- 版型基準參考 C:\Claude\projects\properties\Guanlian766\index.html
  hero 滿版 → KPI 數字條 → WHY 區位論證 → WHAT 標的內容 → 規格表
  → 現場相簿燈箱 → 專案窗口 CTA → footer
- 不露價的案子寫「備索」，不要留空
- 頁尾不用自己做「認識專案團隊」區塊，收頁時會統一套上
  （自己做的殘缺版會被整段換掉，白做）

【目錄命名】
- 一般案：地名英拼＋關鍵數字，例 WangTian5483、Guanlian766、TCIP3464
- 潛銷案：再加「-」四碼亂碼，例 ct1300-e58a（網址不可被猜到）
- 不要用結尾 b 或 -b（那是簡版分身保留的）
- 一經上線不改名、不刪除、不搬家（連結已發出去，斷了就是客戶開到 404）

【鐵則】
- 不得連回根 index.html，也不得連回任何索引或管理頁
- 對外導流只允許這四個：
  reihe-industrial（關於瑞禾）、about-mac（關於現傑）、
  about（睦聚現傑，不要用 mac-chang-hub）、service-demo（購廠分析）

【部署】
cd C:\Claude\projects\properties
git pull --rebase origin main   ← 一定先 pull，兩台機器都會動這個 repo
git add -A
git commit -m "新增 [案名]（[PropCode]）一頁式物件頁"
git push origin main
推完 curl 確認回 200。然後到「主題行銷頁」對話說一聲「收頁」即可。
```

---

## B. 收頁（在「主題行銷頁」對話執行）

```bash
cd C:/Claude/projects/properties && git pull --rebase origin main && python C:/Claude/projects/properties-admin/collect.py
```

先乾跑看有哪些不合規，再實際套用：

```bash
cd C:/Claude/projects/properties && python C:/Claude/projects/properties-admin/collect.py --fix
```

`collect.py` 會自動完成：

1. 掃出缺完整版四卡或缺簡版分身的目錄
2. 主版套上「認識專案團隊」完整版四卡（自帶 style、`kya-` 前綴、零 CSS 相依，插在 `<footer>` 前）
3. 產出簡版分身 `<PropCode>b`（亂碼後綴目錄用 `-b`），只留 關於瑞禾＋關於現傑
4. 簡版加 `noindex,nofollow`，避免與主版重複內容
5. 各 session 自己做的殘缺團隊區塊會被整段移除後換上標準版

例外清單寫在 `collect.py` 的 `SKIP`：顧問頁、已結案、以及使用原生 `.more-card` 實作的 `WangTian5483(+b)`。

收完再手動處理兩件事：

- **公開總覽**：在售／在租案在 `properties\index.html` 補一張 `<a class="card">`，
  文案格式「分區・一句話賣點｜規模｜交流道距離」。潛銷、已結案、顧問頁、簡版分身都不補。
- **台帳**：`properties-admin\index.html` 補列，完整版與簡版各一列。

---

## C. 版本用途

| 版本 | 卡片 | 目錄 | 用途 |
|---|---|---|---|
| 完整版 | COMPANY 關於瑞禾／AGENT 關於現傑／PLATFORM 睦聚現傑／SERVICE 購廠分析 | `<PropCode>/` | 電子報、已知對象（可安心導流） |
| 簡版 | 只留 關於瑞禾＋關於現傑 | `<PropCode>b/` | 一般散發、同業、屋主（不導流睦聚平台與購廠分析） |
