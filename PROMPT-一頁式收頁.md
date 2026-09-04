# 提示詞　—— 一頁式行銷頁的產出與收頁

物件資料夾各自製作一頁式後，把下面整段貼給該 session（或貼給行銷企劃 skill），
它就知道版型規格、完整版／簡版、repo 安排、部署與台帳更新。

方括號 `[ ]` 內是每次要換掉的部分，其餘照抄。

---

## 貼這段

```
產出這個物件的一頁式行銷頁，並依下列規範收進 GitHub Pages。

【案名與代號】
案名：[中文案名]
PropCode：[英文目錄代號]
類型：[售／租／買方需求／顧問提案]
狀態：[在售／在租／潛銷／已結案]

【產出規格】
- 單一自足的 index.html，照片一律 base64 內嵌，不放獨立圖檔（單檔要能直接寄送、離線可讀）
- 外部相依只允許 Google Fonts，其餘一律內嵌
- 品牌配色：瑞禾綠金 --forest:#2B5937 / --gold:#C0A434 / --ink:#26302A / --muted:#77806F / --border:#E8E6E1
- 版型基準參考 C:\Claude\projects\properties\Guanlian766\index.html
  （hero 滿版 → KPI 數字條 → WHY 區位論證 → WHAT 標的內容 → 規格表 → 現場相簿燈箱 → 專案窗口 CTA → 認識專案團隊 → footer）
- 不露價的案子用「備索」，不要留空

【完整版／簡版　一定要兩份】
頁尾固定放「KNOW YOUR AGENT・認識專案團隊」區塊，兩個版本：

- 完整版（四卡）→ 放在 <PropCode>/index.html
  COMPANY 關於瑞禾｜AGENT 關於現傑｜PLATFORM 睦聚現傑｜SERVICE 購廠分析
  用途：電子報、已知對象（可安心導流）

- 簡版（兩卡）→ 放在 <PropCode>b/index.html
  只留 COMPANY 關於瑞禾 + AGENT 關於現傑
  用途：一般散發、同業、屋主（不導流睦聚平台與購廠分析）
  作法：完整版刪掉 PLATFORM 與 SERVICE 兩個 <a class="kya-card"> 即可，其餘完全不動
  簡版必須加 <meta name="robots" content="noindex,nofollow">，避免與主版重複內容

區塊原始碼直接取用（自帶 <style>、kya- 前綴、顏色寫死、零 CSS 相依，貼在 <footer> 前即可）：
C:\Claude\projects\properties-admin\snippets\know-your-agent.html
（本機沒有的話先 git clone https://github.com/mac2good909777-commits/properties-admin）

不要改寫成該頁既有的 class 名稱 —— 各物件頁 CSS 詞彙不一致，硬接會撞版。

【REPO 安排】
公開 repo：mac2good909777-commits/properties（PUBLIC，GitHub Pages）
本機路徑：C:\Claude\projects\properties\

- 目錄命名 PropCode：地名英拼＋關鍵數字，例 WangTian5483、Guanlian766、TCIP3464
- 潛銷案：再加「-」四碼亂碼，例 ct1300-e58a（網址不可被猜到）
- 簡版分身：主目錄名後接 b，例 Guanlian766b；主目錄已含亂碼後綴者用 -b，例 ct1300-e58a-b
- 一經上線不改名、不刪除、不搬家（連結已發出去，斷了就是客戶開到 404）
- 結案物件保留頁面與路徑，只降狀態

【鐵則】
- 各分頁不得連回根 index.html，也不得連回任何索引或管理頁
- 對外導流只允許這四個：reihe-industrial（關於瑞禾）、about-mac（關於現傑）、about（睦聚現傑）、service-demo（購廠分析）
- 簡版分身不掛公開總覽

【總覽】
在售／在租案 → 在 C:\Claude\projects\properties\index.html 補一張 <a class="card">，
文案格式：分區・一句話賣點｜規模｜交流道距離。
潛銷、已結案、顧問頁、簡版分身 → 不補。

【部署】
cd C:\Claude\projects\properties
git pull --rebase origin main   （一定先 pull，這個 repo 兩台機器都會動）
git add -A
git commit -m "新增 [案名]（[PropCode]）一頁式物件頁，含簡版分身"
git push origin main
推完 curl 確認主版與簡版都回 200，且卡片數分別為 4 與 2。

【台帳】
最後到 private repo 補一列：
C:\Claude\projects\properties-admin\index.html
欄位：物件／類型／規模／開價／上架日（首次 commit 日）／狀態／有無掛總覽／有無 noindex／線上與本機連結。
完整版與簡版各佔一列。補完 commit push。
```

---

## 收頁後自我檢查（跑這段）

```bash
cd C:/Claude/projects/properties && for d in */; do d=${d%/}; printf "%-16s 卡:%s 團隊區塊:%s noindex:%s\n" "$d" "$(grep -c 'a class="kya-card"' $d/index.html)" "$(grep -c '認識專案團隊' $d/index.html)" "$(grep -c noindex $d/index.html)"; done
```

主版應為 `卡:4`，簡版 `卡:2` 且 `noindex:1`。
（`WangTian5483(+b)` 例外：使用該頁原生 `.more-card` 實作，數值為 0，屬正常。）
