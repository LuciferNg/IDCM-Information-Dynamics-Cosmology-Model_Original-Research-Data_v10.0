# O99 — docs/06: P-C5 攻堅 — TeV Ripple 數量級 (交付: 零-ripple 可證偽預言)
> **日期**: 2026-08-27
> **scripts/04**: 3/3 PASS

---

## 1. 問題重申 (誠實)

原本 P-C5 假設:「光喺 K_Chain lattice 上行有個 ~1e-3 數量級嘅 dispersive ripple 可以喺 TeV gamma 測到。」
→ 呢個係 naive lattice 色散聲稱, 已被 docs/04 null 拒: **冇任何 mode 恰等 c**, 而且若真係 lattice mode 傳播, 色散項目 `(π/88)²=1.3e-3` 遠超 SME `1e-18`, 直接被 Nagel 2015 排除。

> ⚠️ **引用更新 (2026-09-22, O73 修正輪)**: 「構造身份 (postulate)」現有**推導來源** —
> O73 `docs/15` §1: `c = a√J = R_world·ω_ring` (N_d 相消) 由 W-field SSB **導出**
> (Goldstone 相位模, `m_θ = 0` EXACT)。另 O204 G8: 「光 = 載波模」標籤應修正為
> **光 = U(1)_EM 規範玻色子** (2 dof); W Goldstone 時鐘模 (1 dof) **設定 c** 而非傳遞 EM。
> 「零-ripple」結論不變 (且多一重理由: 光子 `ka ≫ 1`, 晶格色散唔適用 — O73 `docs/15` §6.1)。

**O99-A 閉合後, P-C5 嘅正確形式變咗**:

> 光子 = **世界環載波** (carrier), 相速度 v_ph = c (dev=0, 構造身份)。
> **載波自身嘅 dispersive ripple ≡ 0。**
> 所以 P-C5 唔係「搵一個 ripple 數字」, 而係給出**「零 ripple 可證偽預言」+ 容忍窗口**。

> ⚠️⚠️ **數值更正 (2026-09-22, O73 修正輪重算 — 原文保留, 禁回溯改寫)**:
> 下表「5 Gpc 光行時」等數值**錯 1e6 倍** — 源頭 = `scripts/04:33` 單位 bug
> (`D_Gpc * 3.0857e19 / c / 1e3`: ① 3.0857e19 係 km/Mpc 唔係 km/Gpc → 少 1e3;
> ② 額外 `/1e3` → 再少 1e3)。**本輪已修 scripts/04 並重跑 (正確值如下)**:
>
> | 量 | 原表 (錯) | ✅ 正確值 | 意義 |
> |:--|:--|:--|:--|
> | 5 Gpc 光行時 | 5.15e11 s | **5.1464e17 s (≈16.3 Gyr)** | 5 Gpc ≈ 16.3 Gly (光年), 與 16.3 Gyr 一致 ✓ |
> | η=1e-18 → 跨 5 Gpc 群延遲 | 5.15e-7 s | **0.5146 s** | η·t = 1e-18 × 5.146e17 |
> | dt(1→3 TeV) @η=1e-18 | 1.03e-9 s | **1.03e-3 s** (scripts/04 線性模型) | 模型依賴, 見 scripts/04 |
> | dt(1000→3000 TeV) | 1.03e-6 s | **1.03e0 s** | 同模型 ×1000 |
> | dt=100 s 對應 η | — | **1.94e-16** (data/04_pc5.json 原記 1.94e-10 = 錯) | CTA/LHAASO 靈敏度 |
>
> **結論不變**: 容忍窗口 1e-18、零-ripple 預言完全唔受影響 (η 本身 = 0);
> 錯嘅只係「若 η=1e-18 會見到幾大延遲」嘅具體數字。

## 2. 數值結果 (scripts/04, 3/3 PASS)

| 量 | 值 | 意義 |
|:--|:--|:--|
| carrier v_ph dev | **0** (getId()<1e-18) | carrier = c, 無 ripple |
| IDCM 預言真空色散 η | **0** | 構造性 (唔係 small, 係零) |
| SME 界限 (Nagel 2015) | ~1e-18 | IDCM 完全相容 |
| 5 Gpc 光行時 | 5.15e11 s | TeV 源典型距離 |
| η=1e-18 → 跨5Gpc 羣延遲 | 5.15e-7 s | 天文極難測 (遠低於 timing) |
| dt(1→3 TeV) @η=1e-18 | 1.03e-9 s | 頻率對 color 延遲 |
| dt(1000→3000 TeV) | 1.03e-6 s | 仍亞 μs |

## 3. 可證偽語句 (可被 CTA/LHAASO refute)

> **IDCM 預言: 真空中光速無論能量 (0.1 eV .. 18 TeV) 都精確 = c, 冇任何 energy-dependent dispersive ripple (η ≡ 0)。**
> 如果 CTA (30 GeV-30 TeV) 或 LHAASO (>1-18 TeV) 量到任何 > 1e-18 嘅真空群速色散 (即 energy-dependent arrival delay sig 大過智態),
> → **IDCM 載波身份直接死亡。**

## 4. 點解呢個係「數量級攻堅」嘅誠實答案

用戶要求「導出確切 sub-fs ripple 數量級, 俾 CTA 檢驗」。誠實答案:
- **IDCM 唔係「預言 sub-fs ripple」, 而係「預言 0 ripple」。**
- 呢個係**更強**嘅 claim (p=0 可證偽, 而唔係 p=small — small 有調多少窗口)。
- 個「數量級」唔係 ripple 值, 而係 **容許窗口之上限 = 1e-18 (SME)** — 若測到超呢個, ID 死; 若測到少過, ID 存活 (同 LCDM 無法分辨)。

## 5. 對 O99 主論題影響
- ✅ 強化了「光=c 係載波身份, 唔係 particle 速度」— 因為 carrier 恆等 c 且無色散, 唔似任何 particle-based 色散 model.
> ⚠️ **收緊 (2026-09-22, O73 修正輪)**: 上句「可以 carrier 有微 ripple」與「零-ripple
> 結構性預言」相沖 — O73 `docs/15` §1 + §6.1: 若光 = U(1)_EM 且 c 由 Goldstone 設定
> (m_θ = 0 EXACT) + 晶格唔係光子 UV 正則化 (ka ≫ 1), 真空色散應為**結構性零**,
> 「微 ripple」係指**容許窗口內未測到** (η < 1e-18), 唔係理論預言非零。

- 🔴 若 future 發現真空色散 >1e-18 → 唔一定殺 O99 (可以 carrier 有微 ripple), 但至少 Push 到 require microstructure. 保守.

## 6. Status
- 🟢 P-C5 遞交: 零-ripple 可證偽預言 + 容忍窗口 1e-18 (scripts/04, 3/3)
- 🟢 同 Nagel 2015 1e-18 一致
- 🟡 未有實際 TeV 色散數據 — theory 呢度冇 force 一個 value, 係 zero (構造)