# O236 — 質量來源推導路線（O235 續推：R1–R7）

<!-- registry
pid:     O236
title:   質量來源推導路線 (O235 續推)
state:   partial
verdict: partial
flags:   -
owner:   O236
created: 2026-10-07
updated: 2026-10-07
prereq:  O235（T1–T5 閉合資產）
source:  O235 T5 續推（2026-10-07 調律者: 開O236, 把路線放進去, 下一session處理）
-->

> **狀態**: 🟡 **部分閉合 (2026-10-07 closeout, verdict=partial)：R1–R6 全部執行（6 script 89 checks PASS）；R5/R6 負閉合；R7 等數據（O234 觸發已註冊）。**
> **建立**: 2026-10-07（重開；同日早前 retract 已撤銷）
> **前置**: O235（tick 宇稱＋質量來源整合，partial 閉合）
> **位置**: `open_problems_fresh/o236_mass_origin_integration_n_c_f/`

---

## 一、問題陳述

承接 O235 T5（s1↔s3 相位對偶槽、輕子 = odd-flow ∩ s1 雙重篩、C_f 代際塊 3.69/35.2/196.6）
之上嘅推導方向，**已全部列出喺 `docs/01_mass_origin_routes.md`（R1–R7）**；
本 O 標準：**下一 session 先執行**，今 session 只落地路線圖同預先註冊嘅可證偽內容。

結論先行：質量來源嘅可導部分（槽位＋γ 階梯）已喺 O233/O235 閉合；C_f 值層三面負（
結構池/譜比橋/tick 判死）＋ P1 循環證明 ⟹ **唔再 hunt C_f 數值**。剩餘有效推導 =
R1（格定理）／R2（對偶 partner 空槽）／R3（t 凝結）／R4（手性橋）／R5（補填統一）／
R6（塊間比 MC 負閉合）／R7（刻唔做，等數據）。

## 二、已確立嘅結構（O235 資產，唔重推）

```txt
🟢 tick 算子: spec(H_cb) = ±2cos(πk/44); 譜半徑 = 2 = μ² EXACT; tick Δt = T_ring/88
   = λ_sync/c = (π/44)τ EXACT (T2, 21/21)
🟢 tick 相位 ℤ₄: Ŝ = S²², Ŝ|k⟩ = i^k; 四類 s0..s3 各 22 模; deficit 向量
   (Σs0−44, Σs1−44, Σs2−44, Σs3−44) = (μ², −sec, 0, +sec) EXACT (T3, 20/20)
🟢 輕子槽 ≡1: B−L 整數性 (O210 T3) × tick 相位 deficit 選取 (O235 T3) 雙機制;
   輕子 {e,μ,τ} 3/3 落 s1; 重夸克 {d,c,b} 3/3 落 s3 (T5 新: s1↔s3 對偶槽)
🟢 輕子 = odd-flow ∩ s1 雙重篩 (T5 D1); d = odd-flow − s1; t = s1 − odd-flow
🟢 C_f 代際塊: gen1 3.685 / gen2 35.226 / gen3 196.581; 塊間比 9.559/5.580 (觀察級)
⚰️ C_f 值層判死 (T4): C_f ∉ 兩步映射不動點 (R_raw=0.68 > θ=0.1)
⚰️ P1 ms/mu=42.89 = 循環 (O234 L83 C_s 校準自 FLAG ⟹ Δ=0, Z=0)
🔴 C_f 生成器 5 線全負 (O233 p=0.9955) + 譜比橋拒 (O209 RMS 0.622)
```

## 三、未確立（🔴 開放方向，詳見 docs/01）

```txt
🔴 R1 輕子格定理: (rank%2, n%4) 格 = {(1,1):4, (0,3):2, (1,3):1, (0,0):1, (0,2):1}
   —— 點解輕子³+t 係唯一全滿格？(1,1) 格結構原因
🔴 R2 對偶 partner 空槽: 9 個 88−k partner (87..75) 全空、全喺鏡像半環 > 44
   —— 角色？（反粒子？中性粒子？）s1↔s3 partner 換類機制
🔴 R3 t 嘅 VEV = 相位-1 凝結方向: s1 第 4 元素 t 最重 + VEV vs O213 主模 1 凝結
🔴 R4 s1↔s3 對偶 = 手性鏡像橋: 接 O213/O220 chirality (N_d+1=3o=45)
🔴 R5 補填原理統一: d (odd-flow 補填 rank3 + s3 內 C_f 極端 3.66 vs 186/256)
   + t (s1 補填 + VEV) = 統一「槽位補填者」機制
🔴 R6 C_f 塊間比 MC 檢定: 9.559/5.580 vs 結構池 34 原子; 氣味測試: r32 對 88/16=5.5
   dev 1.4% (觀察級) / r21 冇 obvious hit ⟹ 預期負結果閉合
⏳ R7 數據等待: P2 第三尺 (lattice 1–2% mu/md) + P3/P4 相位類守恆 (HL-LHC/FCC-ee 新粒子)
```

## 四、攻擊路線（下一 session 建議執行次序）

```txt
1. R1 (格定理形式化 + 枚舉證明) → 成本低, 即刻有新定理候選
2. R2 (對偶 partner 槽角色) → 成本低, 元素級雙射已是 T1 資產
3. R3 (t 凝結, 讀 O213 上游) → 成本中, 可能只係數值缺口 (高風險)
4. R4 (手性橋, 讀 O213/O220) → 成本中, 警惕 common-measure no-go 同構重述
5. R6 (MC 負閉合) → 成本中, 回報 = close 一個 open 項 (T5 E2 承諾)
6. R5 (補填統一) → 最後 (d anomaly 可能已由質量次序收口)
R7 全程唔推, 只等數據 (O234 kill 觸發已註冊)
```

## 五、驗證標準

```txt
✅ R1: (1,1) 格定理證明（或證偽: 存在非 (1,1) 格之輕子類填充）; 四道硬測試
✅ R2: partner 槽角色命題 + 可證偽內容（若鏡像半環有中性粒子, 必須落 partner 槽）
✅ R3: Φ_max 閉合 m_t 缺口（~121×）或明確負結果
✅ R4: 手性指標分側對應; 唔准同構重述 (O210 no-go 陰影)
✅ R6: 結構池 × 10⁷ MC null, 兩地報 (寬池/結構池), 鎖間相依性照 O208
```

**四道硬測試**（閉合宣稱必過）：
① 自由度成本（零參數）② Monte-Carlo null（10⁷ 樣本, 5σ）③ 可證偽 + 樣本外盲測
④ 結構剛性（微擾測試）

## 六、推導時序索引

> ⚠️ **只可 append 新行，禁回溯污染舊行。**

| # | 日期 | 事件 | 產物 |
|:-:|:-----|:-----|:-----|
| 1 | 2026-10-07 | 重開 O236（調律者授權: 開O236 放路線 下一 session 處理）; R1–R7 路線 + 可證偽內容落地 | docs/01 |
| 2 | 2026-10-07 | 註冊狀態: retracted(早前撤銷) → reopened → open; README row 🔴 | register events |
| 3 | 2026-10-07 | **R1 格定理閉合** 🟢: T-C 計數引理 (相位類佔據 (4,3,1,1) = F 形狀×截斷 13≡1 mod 4) ＋ T-P 奇偶保持引理 ((1,1) 全滿 4/4 兩引理合流) ＋ T-G 群論必然性 **否定** (非自由 ℤ₄×Z₂ 作用) ＋ T-R 剛性 (54/54 swap 改變模式); 格計數 assignment-invariant, 輕子類 label A_γ-specific (A_Δm τ 離場); 四硬測試過 | scripts/01 (21/21), logs/01, data/01, docs/02 |
| 4 | 2026-10-07 | **R2 對偶 partner 槽閉合** 🟢: P-1 partner 映射 = ℤ₄ reflection (88≡0 mod 4 ⟹ s1↔s3) 定理; P-2 F∩(88−F)=∅ 反射奇佔據; P-3 鏡像互補 γ 和=4; P-4 剛性 (M≡0 mod 4 家族, 半環定位平凡); C12 falsifier (鏡像中性粒子∈75..87) ＋ C13 中微子掛鉤 **refute** (O49/O57 mode 6 低半環) | scripts/02 (18/18), logs/02, data/02, docs/03 |
| 5 | 2026-10-07 | **R3 t VEV 凝結閉合** 🟢: R3-1 第4位=VEV 收口 (承接 O233 docs/15 B−L 閘: t +1/3∉ℤ; y_t=0.994≈1); R3-2 主模1↔相位-1 **負結果** (λ_max 51.56 vs γ₁₃Φ_max 51.28 dev 0.54% 觀察級, 冇推導橋, O210 陰影); R3-3 Φ_max 唔收 m_t 缺口 **明確負結果** (121× 保持; t=VEV 層); 觀察級 near-hit 88²/L₅² 記錄唔升格 | scripts/03 (14/14), logs/03, data/03, docs/04 |
| 6 | 2026-10-07 | **R4 手性橋閉合** 🟢＋⚰️: r-odd 扇區定理 (deficit (μ²,−sec,0,+sec) 分解: s1/s3=±sec 係 ℤ₄-reflection 唯一 odd sector; T5 雙重篩對象 = r-odd; partner 換類 = 粒子級 r-odd 表徵); F∩r(F)=∅ 同型 chiral 60-軌道; 幾何手性「分側對應」**否證** (冇推導橋, O210 陰影); 算術橋 45=N_d+1=3·15 計數一致機制開放 | scripts/04 (17/17), logs/04, data/04, docs/05 |
| 7 | 2026-10-07 | **R6 塊間比 MC 負閉合** ⚰️: 結構池 (O233 docs/02 凍結 57 原子; docs/01「34 原子」係筆誤) 0/0 hit (r21/r32 都係結構池避開者) ＋ 寬池 P(≥16)=0.9929 / P(≥28)=0.4838 無富集; 10⁷ log-uniform × 兩池; 氣味 88/16=5.5 dev 1.4% 窗格外; 鎖間相依 (共享 gen2) 聯合必然負 ⟹ T5 E2/P5 承諾兌現, 唔升格金; O136/mass-shape R6 項完成 | scripts/06 (8/8), logs/06, data/06, docs/06 |
| 8 | 2026-10-07 | **R5 補填統一負閉合** ⚰️ (最後推導輪): R5 可證偽預言「補填→C_f 塊極端」被現有 d (3.662 中位) 否證; d (γ階梯 L2, 2.162 EXACT) 與 t (B−L/VEV, y_t≈1) 冇共同算子; 唯一共享 = 3+1 sieve 算術 (描述性); O136 incoming ×3 整合一致 (rank-parity 否證/cs 單點/dquark H_sector FAIL) ⟹ C_f 值層無統一機制; R7 等數據 (O234 觸發已註冊) | scripts/05 (11/11), logs/05, data/05, docs/07 |
| 9 | 2026-10-07 | closeout（verdict=partial）: register 7 notes + close; 兩個 md registry block 同步 partial; README row 🟡; R7 = 數據等待（P2 第三尺 / P3/P4） | register events, README |
| 10 | 2026-10-07 | **R8/R9 越界審計**: O236 session 期間 O136 越界寫入 docs/08–09/scripts/07–08/data/07–08（R8 混標度判死 + R9 t near-hit 盲測）已歸位 O136 docs/40–42；O236 27 檔全正典、無殘餘；register 出處更正 note（12:52）正名；O236/O136 完整性 check 0 drift。**下一步方向**（docs/08）: A R7 觸發等數據 / B 45=3·15 幾何側協調（禁 chain 硬砌）/ C R2 C12 鏡像半環預言存檔 / D γ對偶和=4 operator 收編（唔開O）/ E u 特殊性放棄 / F 禁區重申 | register events, docs/08 |

## 七、相關文件

```txt
- O235 — tick 宇稱＋質量來源整合（T1–T5 + final_result; 本 O 唯一上游）
- O233 — C_f 結構身份（鋸齒/槽/生成器負; C_f 值層唔再 hunt）
- O234 — 質量比檢驗（freeze v2; P1 循環證明; P2 雙尺; P3/P4 觸發條件）
- O209 — 選擇律代數（C_f 譜比橋負結果; 塊結構）
- O213 — 世界動力學（手性橋/凝結/主模 1; R3/R4 上游）