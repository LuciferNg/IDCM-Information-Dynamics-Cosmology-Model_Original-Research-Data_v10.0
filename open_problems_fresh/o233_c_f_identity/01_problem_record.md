# O233 — C_f 結構身份：生成器 hunt → 鋸齒/Z₂ → lepton 槽 n≡1 (mod 4)

<!-- registry
pid:     O233
title:   C_f 結構身份：生成器 hunt → 鋸齒/Z₂ → lepton 槽 n≡1 (mod 4)（由 O206 第10-15輪轉移）
state:   closed
verdict: negative
flags:   -
owner:   O233
created: 2026-10-06
updated: 2026-10-06
prereq:  O120, O137, O206
source:  O206 第10-15輪（O120 session 內越界完成, 2026-10-06, 調律者裁決轉移）
-->

> **狀態**: 🟢 **負閉合 (2026-10-06 用戶裁決 verdict=negative)**：C_f 生成器 5 線全負 = 結構性負結果（無算子身份, docs/19 §三）；4 項結構正結果（鋸齒/槽/升序/d 槽）已記錄不受影響
> **建立**: 2026-10-06（轉移日）
> **前置**: O120（C_f = m_f/(M₀γ_n) 之商定義）、O137（合法模式集 + R19 A₅ 指派）、O206（γ-階梯/塊層 v8-v10 推導）
> **位置**: `open_problems_fresh/o233_c_f_identity/`

---

## 一、問題陳述

**C_f = m_f / (M₀·γ_n) 嘅結構身份係咩？**——8 個費米子（t 除外）對應 9 個合法模式
{1,2,3,4,5,7,9,11,13}，殘餘乘數 C_f 被證明：**唔係**單調函數、**唔係**平滑形狀、
**唔係**統一生成式可表，而係——**完美鋸齒波幅 = 質量 rank 奇偶（Z₂）分裂**，
再精確化為 **lepton 槽 n ≡ 1 (mod 4)**。開放核心：**點解輕子佔 ≡1 槽？（4 = B 分支數）**

## 二、已確立嘅結構

```
🟢 C_f 8 值: e 3.594·u 3.803·d 3.662·s 41.32·μ 30.03·c 186.06·τ 159.64·b 255.75（t 走 VEV）
🟢 全局平滑形狀全滅（M1–M4/M6 全 0.926–1.110；M5 塊波幅×共享凹陷 0.391 未過閘）
🟢 完美鋸齒交替 ↑↓↑↓↑↓↑ 7/7: p=0.0138（MC 10⁶, log-uniform H0）
🟢 鋸齒真身 = 奇偶 rank 分裂（Z₂）: even {u,s,c,b} vs odd {e,d,μ,τ} 各自嚴格單調增、相鄰 even>odd 4/4
    （T_k+1/2^k+1 更正為 numeric red herring, docs/06_ §二）
🟢 Z₂ 三盲測: T1 分裂類 1055/40320=2.6% 升序係其一; T2 跟 rank parity 唔跟 mode parity（0.844<0.928）
    但 ±σ 形式被壓（殘餘唔二值）; T3 u/d scheme 閾值 0.44539, 身份保持 77.4%/68.4%
🟢 joint T×split: 兩者獨立統計（協同 1.01×≈1）但升序喺 split 內 T-rank 1/1055（p=0.00095）
🟢 冪律 m ∝ γ²（α=2.0634≈2）只係 envelope（rms ln 0.70）非生成器
🟢 u/d 身份層穩健: rank 身份對 u/d 保持率 1.0000（振幅層 0.7740 崩潰區 23%）
🟢★ lepton 槽 n ≡ 1 (mod 4) 雙盲測: B1 {1,5,9} p=0.0179; B3 性質目標 p=0.0476（9-mode 含 t）
🟢 charge-residue 更正（docs/11_）: ≡3={d,c(UP!),b}——c 係 up-type; up 3 distinct p=0.369/s≡0 p=0.333 都唔稀有
🟢 本體論算子對應: 位置算子 X=diag(i−⟨i⟩) 對角元精確零（Z₂-奇）; V_nm 非零只在 n+m 奇
🔴 生成器 hunt 誠實負: 統一式 12 族全滅（best 1.378）; 逐點 p=0.9955 判死; detent 排除; κ 非對角失格
```

## 三、未確立（🔴 開放問題）

```
🔴 輕子槽成因: 點解三輕子佔 n ≡ 1 (mod 4) 槽（而唔係 ≡3）? 4=B 分支數係語境（O210-T1:
   k ≡ ±|B−L| (mod B)）但機制未解; 候選銜接 O158（45族a奇/47族a偶）、O139、O137 手性橋
   ⚠️ **2026-10-06 closeout**: ✅ 已解——T3×O210 群層 iso 三層合成 🟡⁺（docs/13,17）；
   common measure 永久 no-go（O210 R9 裁定）
🔴 up-type 冇固定 residue: u≡2, c≡3, t≡1（3 個全唔同）——H0 正常但冇結構身份
   ⚠️ **2026-10-06 closeout**: 🟢 已判定（負面）——charge-residue 更正（docs/11）:
   up 3 distinct p=0.369、s≡0 p=0.333 都唔稀有 ⟹ H0 正常, 唔當 anomaly
🔴 even/odd 兩流各自算子身份: {u,s,c,b} vs {e,d,μ,τ}——d 落 odd 流係 anomaly（最輕 down-type）
   ⚠️ **2026-10-06 closeout**: ✅ 已解——兩流 = 輕子/夸克分離（docs/14, even 4/4 夸克
   P=1/14）；d 落 odd = 質量次序必然（docs/15, m_d/m_u = (γ₃C_d)/(γ₂C_u) = 2.1620 EXACT）
🔴 L4 盲測延伸: lepton modes {1,5,9} 等差 4 + 全奇位聯合 null（已做性質版 B3, 指定 subset 版未做
   8! label permutation）
   ⚠️ **2026-10-06 closeout**: ✅ 已覆蓋——指定 subset 版 = docs/10 B1（P=1/56 理論,
   N_search=1）+ docs/14 T4/T5 對偶（夸克 5/5 避 ≡1 同 P=1/56）
```

## 四、攻擊路線（轉移自 O206 內含之候選方向）

```
1. 輕子槽成因 → 以 O158 mod-4 判準/45-47 家族為錨, 查 lepton ≡1 是否係 A₅ 表示手性投影嘅必然
   → 預期: 連接手性橋（N_d+1=45=3·15）同 lepton 槽
2. even/odd 兩流算子身份 → 找 X 算子 Z₂-奇 同質量流結構嘅 1-1 對應, 推導 d→odd 嘅原因
   → 預期: 兩流 = 觀察者扇區（奇）/世界介質（偶）嘅質量側投影
3. L4 指定 subset 盲測 → pre-register（8! random label, 命中 {1,5,9}+全奇位）確認 p
   → 預期: p ≈ 0.018 單獨; 會計 look-elsewhere
4. 冪律 envelope 分解 → m = M₀γ^(α−1)·鋸齒修正 嘅閉式形式, 用額外合法模式（44 鏈其他譜）盲測
```

## 五、驗證標準

```
✅ 輕子槽成因: 由 A₅/手性/模-4 結構推出「輕子 ≡1 mod 4」作為定理（零參數, 唔係枚舉）
✅ 兩流算子身份: even/odd 流各對應一個算子投影（d→odd 由結構推出, 唔係指派）
✅ L4 盲測: p < 0.05（pre-registered, MC 10⁶, 含 look-elsewhere 計數）
✅ 冪律分解: 殘餘過 4 道硬測試（自由度/10⁷ null/樣本外盲測/擾動）
```

**四道硬測試**（閉合宣稱必過）：
① 自由度成本（零參數）② Monte-Carlo null（10⁷ 樣本，5σ）
③ 可證偽 + 樣本外盲測 ④ 結構剛性（微擾測試）

## 六、推導時序索引

> ⚠️ **只可 append 新行，禁回溯污染舊行。**

| # | 日期 | 事件 | 產物 |
|:-:|:-----|:-----|:-----|
| 1 | 2026-10-06 | O206 第十輪：三方衝突裁決＋生成器 hunt 誠實負＋γ-階梯雙射 null | docs/01-03, scripts/01-03 |
| 2 | 2026-10-06 | 第十一輪(a)：統一生成式 12 族全滅（best 1.378）| docs/04, scripts/04 |
| 3 | 2026-10-06 | 第十一輪(b)：鋸齒波幅發現（7/7 交替 p=0.0138）| docs/05, scripts/05-06 |
| 4 | 2026-10-06 | 第十一輪(c)：Z₂ rank 分裂真身＋本體論算子對應 | docs/06 |
| 5 | 2026-10-06 | 第十一輪(d)：三盲測（3 PASS/1 FAIL）| docs/07, scripts/07 |
| 6 | 2026-10-06 | 第十二輪：Joint T×Split 獨立＋冪律 envelope | docs/08, scripts/08 |
| 7 | 2026-10-06 | 第十三輪：even/odd 兩流身份＋κ 失格 | docs/09, scripts/09 |
| 8 | 2026-10-06 | 第十四輪：lepton 槽 n≡1 mod 4 雙盲測（B1 0.0179/B3 0.0476）| docs/10, scripts/10 |
| 9 | 2026-10-06 | 第十五輪：charge-residue 更正（c=UP!）＋成因語境 | docs/11, scripts/11 |
| 10 | 2026-10-06 | **轉移**: O206 → O233（git mv scripts/29-39+docs/33-43+logs/29-39+data/29-39）| 本記錄 |
| 11 | 2026-10-06 | 第十六輪：assignment 版本隔離（O209 vs A_γ）+ look-elsewhere（P=0.1204 FAIL）| docs/12, scripts/12-14 |
| 12 | 2026-10-06 | 第十七輪：輕子槽成因三層合成（T3×群層 iso）🟡⁺ | docs/13, scripts/15 |
| 13 | 2026-10-06 | 第十八輪：even/odd 兩流身份 = 輕子/夸克分離（1/14, 1/56）| docs/14, scripts/16 |
| 14 | 2026-10-06 | 第十九輪：d/t 槽機制（d 落 odd = 質量次序必然；t = T3 唔強制）| docs/15, scripts/17 |
| 15 | 2026-10-06 | 第二十輪：塊參數盲測 🔴 負（B²=16 降級, F₁₀ C2 殺死）| docs/16, scripts/18-19 |
| 16 | 2026-10-06 | 第二十一輪：O210 回覆收錄（common measure 永久 no-go, 🟡⁺ 乾淨閉合）| docs/17 |
| 17 | 2026-10-06 | ★ 用戶裁決：錨不是參數、C_f 無量綱 ⟹ 獨立錨撤回（docs/16 §八）| docs/16§八 |
| 18 | 2026-10-06 | 第二十二輪：κ 非對角盲測 🔴 負（0 hits, P=1.0）| docs/18, scripts/20 |
| 19 | 2026-10-06 | 第二十三輪：O152 註冊常數全集擴池 🔴 負（P=0.285）| docs/19, scripts/21 |
| 20 | 2026-10-06 | ★ **用戶裁決：C_f 結果負閉合** — verdict partial → negative；主問題「C_f 結構身份」= 確定嘅負結果（5 線全負 ⟹ 無算子身份, docs/19 §三）；關係結構正結果不受影響 | register reopen + close(negative) + 本檔 + SESSION_START + final_result + README |

> ⚠️ **2026-10-06 19:00 更正註記**：register 原 close verdict=partial（18:50, 並行 session c37533）；用戶裁決「C_f 結果負閉合」⟹ **reopen + close verdict=negative**（append-only，原 partial 事件保留）——主問題「C_f 結構身份」5 線全負 = 結構性負結果，最終 state=closed verdict=negative。

## 六之二、檔案閉合水位（close-out watermark, 2026-10-06 closeout）

| # | 檔案 | 上次檔案更新 | 上次 closed-out | 已驗範圍 | 狀態 |
|:-:|:-----|:---------------------|:----------------|:---------|:-----|
| 1 | docs/01–11（O206 轉移） | 2026-10-06 05:18 | — | 全檔（verdict 重跑核對） | ✅ 已驗 |
| 2 | docs/12–19（本 O 攻堅） | 2026-10-06 18:35 | — | 全檔（關鍵數值 vs data JSON 核對一致） | ✅ 已驗 |
| 3 | scripts/01–21 | 2026-10-06 18:34 | — | 全鏈重跑 21/21：exit 0（負結果 script 02/04/05 係預期 FAIL） | ✅ 已驗 |
| 4 | data/01–21 | 2026-10-06 18:34 | — | 22 檔全存在，零孤兒，關鍵統計值 vs docs 一致 | ✅ 已驗 |
| 5 | final_result.md | 2026-10-06 19:00 | — | 全新（RESULT_TEMPLATE 格式）+ 狀態行負閉合 sync | ✅ 已驗 |
| 6 | SESSION_START.md | 2026-10-06 19:00 | — | 全文（§一–十四 appends；S1 不可變快照檢查）| ✅ 已驗 |
| 7 | 01_problem_record.md（本檔） | 2026-10-06 19:00 | — | 全檔 + 狀態行 + frontmatter + §六索引 append（row 20）| ✅ 已驗 |
| 8 | README.md | 2026-10-06 19:00 | — | 狀態 emoji 負閉合 + 檔案表擴展 | ✅ 已驗 |
| 9 | register.jsonl（O233 事件） | 2026-10-06 19:00 | — | close(partial 18:50) + reopen + close(negative) 三事件完整 | ✅ 已驗 |

時序完整性確認：scripts mtime（05:18→18:34）全部先於對應 docs；docs 檔頭日期塊全部 2026-10-06；O233 無跨 O 寫入（本目錄以外零寫入——docs/12-19 引用 O137/O209/O210 只讀）。

時序完整性規則：本檔推導時序索引只可 append 新行；舊行（1–10）零改動；docs/01–19 全部 append-only 或新建，無 back-edit。

## 七、相關文件

```
- O120  — C_f 定義來源（m_f = M₀γ_n C_f, closeout 2026-10-06）
- O137  — 合法模式集 {1,2,3,4,5,7,9,11,13} + R19 A₅ 指派（t→13 VEV）
- O206  — 前十輪本體（scripts/01-28/docs/01-32 保留原位）；第十至十五輪已轉移本 O
- O158  — mod-4 判準家族（45族 a奇/47族 a偶）——輕子槽成因候選銜接
- O210  — k ≡ ±|B−L| (mod B), B=4 分支數——槽數=分支數語境
```