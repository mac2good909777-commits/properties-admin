# 一頁式行銷頁　A / B / C 三層架構

```
A  properties-src    public，不開 Pages   原稿。各專案 push 到這裡
        │
        │  build.py（在 C）依 cases.json 建置
        ▼
B  properties        public，開 Pages     成品。只有「主題行銷頁」對話寫入
                                          網址 https://mac2good909777-commits.github.io/properties/<PropCode>/

C  properties-admin  private，不開 Pages  build.py + cases.json + manifest.json + 管理台帳
```

各專案只碰 A，B 的網址永遠不變。C 是私人的，只有本人看得到。

---

## A 段　給各物件專案的提示詞（複製這段）

```
產出這個物件的一頁式行銷頁，做完 push 到「原稿庫」repo。
成品頁、簡版分身、公開總覽、管理台帳都不用做 ——
那些由「主題行銷頁」對話從原稿建置。

【原稿庫位置】
GitHub：mac2good909777-commits/properties-src（public）
本機：  C:\Users\dell\Documents\Claude-DT\projects\20260904-主題行銷頁\properties-src
沒有的話先 clone：
  git clone https://github.com/mac2good909777-commits/properties-src C:\Users\dell\Documents\Claude-DT\projects\20260904-主題行銷頁\properties-src

【案名與代號】
案名：[中文案名]
PropCode：[英文目錄代號]
類型：[售／租／買方需求／顧問提案]

【產出規格】
- 檔案位置：properties-src\<PropCode>\index.html
- 單一自足的 index.html，照片一律 base64 內嵌，不放獨立圖檔
  （單檔要能直接寄送、離線可讀）
- 外部相依只允許 Google Fonts，其餘一律內嵌
- 品牌配色瑞禾綠金：--forest:#2B5937 / --gold:#C0A434 / --ink:#26302A
  / --muted:#77806F / --border:#E8E6E1
- 版型基準參考 properties-src\Guanlian766\index.html
  hero 滿版 → KPI 數字條 → WHY 區位論證 → WHAT 標的內容 → 規格表
  → 現場相簿燈箱 → 專案窗口 CTA → footer
- 不露價的案子寫「備索」，不要留空

【目錄命名】
- 一般案：地名英拼＋關鍵數字，例 WangTian5483、Guanlian766、TCIP3464
- 潛銷案：再加「-」四碼亂碼，例 ct1300-e58a（網址不可被猜到）
- 不要用結尾 b 或 -b（那是成品端簡版分身保留的）
- 一經上線不改名、不刪除、不搬家（連結已發出去，斷了就是客戶開到 404）

【不要做的】
- 不要做頁尾「認識專案團隊」區塊 —— 建置時統一套上，自己做的會被整段換掉
- 不要做簡版分身、不要改公開總覽、不要動 properties repo
- 不要連回任何索引或管理頁

【對外導流只允許這四個】
關於瑞禾  reihe-industrial.github.io/web/
關於現傑  mac2good909777-commits.github.io/about-mac/
睦聚現傑  mac2good909777-commits.github.io/about/   ← 不要用 mac-chang-hub
購廠分析  mac2good909777-commits.github.io/service-demo/

【部署】
cd C:\Users\dell\Documents\Claude-DT\projects\20260904-主題行銷頁\properties-src
git pull --rebase origin main
git add -A
git commit -m "新增/更新 [案名]（[PropCode]）"
git push origin main

推完到「主題行銷頁」對話說一聲「更新 [PropCode]」即可，其餘不用管。
```

---

## B 段　建置（在「主題行銷頁」對話執行）

**檢查 A 有哪些異動尚未反映到 B：**

```bash
cd C:/Users/dell/Documents/Claude-DT/projects/20260904-主題行銷頁/properties-src && git pull --rebase origin main && python C:/Users/dell/Documents/Claude-DT/projects/20260904-主題行銷頁/properties-admin/build.py
```

會列出四種狀況：`尚未建置`／`A 已異動，需重建`／`原稿不存在於 A`／`A 有新案，cases.json 尚未登錄`。

**重建：**

```bash
cd C:/Users/dell/Documents/Claude-DT/projects/20260904-主題行銷頁/properties && python C:/Users/dell/Documents/Claude-DT/projects/20260904-主題行銷頁/properties-admin/build.py --build
```

只重建指定案：`--build Industrial21 TCIP2098`

`build.py` 依 `cases.json` 自動完成：

1. 讀 A 的原稿，移除任何自帶的團隊區塊
2. `team:full` → 主版插入完整版四卡；`team:none` → 不插（顧問頁、已結案）
3. `brief:true` → 產簡版分身 `<PropCode>b`（亂碼後綴目錄用 `-b`），兩卡＋`noindex`
4. `noindex_main:true` → 主版也加 `noindex`
5. `on_index:true` → 收進公開總覽 `properties/index.html`（**整份自動重生**，不要手改）
6. 記錄原稿 `sha256` 到 `manifest.json`，供下次比對

**推送：**

```bash
cd C:/Users/dell/Documents/Claude-DT/projects/20260904-主題行銷頁/properties && git add -A && git commit -m "重建 [案名]" && git push origin main
```

---

## C 段　新案要做的兩件事

1. 在 `cases.json` 的 `cases` 補一筆（`code` / `name` / `loc` / `kind` / `status` /
   `team` / `brief` / `on_index` / `noindex_main` / `price` / `type` / `spec` / `card` / `note`）
2. 在管理台帳 `properties-admin/index.html` 補列，完整版與簡版各一列

沒登錄 `cases.json` 的案子，`build.py` 檢查時會報「A 有新案，cases.json 尚未登錄」，不會漏掉。

---

## 版本用途

| 版本 | 卡片 | 目錄 | 用途 |
|---|---|---|---|
| 完整版 | COMPANY 關於瑞禾／AGENT 關於現傑／PLATFORM 睦聚現傑／SERVICE 購廠分析 | `<PropCode>/` | 電子報、已知對象（可安心導流） |
| 簡版 | 只留 關於瑞禾＋關於現傑 | `<PropCode>b/` | 一般散發、同業、屋主（不導流睦聚平台與購廠分析） |
