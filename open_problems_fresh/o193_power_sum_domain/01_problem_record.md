# O193 — 問題記錄: 冪和閉式精確域 + Nyquist-atom 機制 + arcsine 譜定理

> **日期**: 2026-09-13 (開題) · 09-14 (閉合審計)
> **狀態**: 🟢 已閉合 (scripts/01 32/32 + 02 16/16 + 03 18/18 + 04 14/14 = 80/80 PASS)
> **來源**: O192 閉合 (冪和閉式統一定理 Σγ^n = 88·C(2n,n) + 2^{2n−1}) — 精確域審計 + 機制化
> **前置**: O192 (冪和閉式), O159 (μ² = E−O, N 無關譜身份), O190 (radion-flat), O157 (零偏差定理)

## 零、問題

O192 冪和閉式統一定理宣稱「全 n 解析證明」+「N 無關」。本 O 三條線:

1. **精確域**: 有限譜嘅 MGF 係有理函數 (Σ_k 1/(1−γ_k x)), 唔可能全 n 等於無理函數
   44(1−4x)^{−1/2} — 閉式數學上必定有邊界。喺邊? (數值測試 n=1..700)
2. **N 無關機制**: parity-gap = 2^{2n−1} 點解唔 depend 喺鏈長? (Nyquist 原子假說:
   k=N 原子 γ=4 只喺 even sector, gap = ½·γ_N^n?)
3. **譜測度**: Σγ^n_odd = 44·C(2n,n) 係 arcsine-on-[0,4] 矩 — 觀察者 sector 譜測度
   係咪離散 arcsine? 同 O157 零偏差定理 (A_k = −μ²cos2θ) 點統一?

## 一、開題即閉合嘅發現 (scripts/01, 32/32 PASS)

- ★★ **精確域定理 (兩域分離)**: 閉式 Σγ^n = 88·C(2n,n) + 2^{2n−1}
  — **數學精確域 n < N = 88** (aliasing-free, 有理函數論證): n ≥ 88 有 aliasing 修正,
    尺度 dev ≈ 2^{n−87}C(n,88)/C(2n,n), n=88 時 ~1e-52, **峰值 ~1e-26 (n≈200)**, 永遠 float 不可見
  — **數值閉式域 n < 536** (dev < 1e-6): 首個可見偏差 n=536, 係 cluster 修正
    (離散和 vs 積分), 唔係 aliasing
  — O192「全 n」claim 精化: 數學 n<88 精確 (修正 1e-52 尺度), 唔係「全 n」
- ★★ **Nyquist-atom gap 定理**: parity-gap = Σγ^n_even − Σγ^n_odd = **γ_N^n/2** = 2^{2n−1}
  — **N 無關** (N=22, 44, 88 全驗證, n<N): 機制 = k=N 原子 (γ=4, Nyquist) 只喺 even
    sector, 其矩 4^n 一半 (½) 由 pair 邊界結構貢獻 — **radion-flat (O159/O190) 機制化**:
    gap 唔 depend 鏈長因為 Nyquist 原子任何 N 都存在
- ★★ **arcsine 譜定理**: Σγ^n_odd = (N/2)·C(2n,n) (n<N) — 觀察者 sector 係**離散
  arcsine-on-[0,4]** (首 N−1 矩精確); 1D 鏈 DOS = arcsine (tight-binding 已知);
  **O157 統一**: γ_k = μ² + A_k = 2 − 2cos(kπ/88) = 4sin²(kπ/176), A_k = −μ²cos(2θ_k) EXACT
  — 零偏差定理、冪和閉式、arcsine 譜係同一對象
- ★★ **partition function**: Z_N(β) = e^{−2β}[1 + e^{−2β} + 2Σ_{k=1}^{43}cosh(2βcos(kπ/88))]
  精確有限和; ≈ N·e^{−2β}·I₀(2β) (Bessel, dev 0.11% @β=0.05 → 1.84% @β=1.0);
  **⟨γ⟩ = 89/44 = μ² + 1/N_d**; 88·⟨γ⟩ = 178 = F₁₁·μ² = equipartition 內能 = 總預算
- ★ Σsin^{2m} = 88·C(2m,m)/4^m + ½ 重驗 (m=1..87); m=3 → **28 = L₇−1** (家族自交);
  +½ = Nyquist 半原子 (sin^{2m}(π/2) = 1 邊界)
- ★ **新 cutoff 登記 (moment-domain Nyquist cutoff)**: 閉式精確域 n < N = 88 —
  同 z > 17 (Nyquist cutoff) 平行 — IDCM 第二個 Nyquist 結構邊界

## 二、判準

- 零新常數: 全部由已閉合常數生成 (N, N_d, μ², F₁₁, L₇) 🟢
- 唯一性: 精確域 n < N 由 aliasing 分析唯一決定 (有理函數論證) 🟢
- 可證偽: 若閉式喺 n < 88 有偏差 > 1e-9 → 定理破; 若 gap 唔 = γ_N^n/2 → Nyquist 機制破;
  N 無關性喺 N=22/44/88 三鏈驗證 (V06/V09)
- 誠實: O192「全 n」claim 精化 (數學 n<88); 630 係我先前取樣步長偽影 (真值 536)

## 三、推導時序索引

| 時間 | 事件 |
|:---|:---|
| 09-13 | O192 閉合讀取; O193 開題 (精確域 + Nyquist 機制 + arcsine); execute_code 初步證偽測試 (冇 break 到 n=100 → log-space 掃描 → 首見偏差 n=536, 630 係取樣偽影); scripts/01 寫入 → 3 個 verifier bug 修正 (overflow branch, 取樣偽影 630→536, float 相等) → 32/32 PASS; docs/01; README 註冊 |
| 09-14 | SESSION_START 四項開放接手: ① E-M 修正 (scripts/02 16/16 PASS) — Z = e^{−2β}[N·I₀(2β)−sinh(2β)] + I_{2Nm} 階梯 (Poisson 精確; 邊界項 = Nyquist 半原子熱力學面; 矩域精確邊界精化: odd/even n<88, full n<176); ② 鏈熱力學 (scripts/03 18/18 PASS) — U/C_v/S 閉式 + 累積量 k₁..k₄ 精確結構 (K = K_arc + ln(1+sinh/(N·I₀))) + O40 virial T=123/4 接合; ③ arcsine 統一 (scripts/04 U01-U07) — δ̂ = (γ−μ²)/μ² affine 映射 → arcsine-on-[−1,1], MGF = I₀(t), D6 全階閉合; ④ moment cutoff 對應 (scripts/04 U08-U14) — 矩確定性 = 鏈長, z>17 平行, 三域 cutoff 同源; docs/02-04; README 更新 🟢 |
| 09-14 | **閉合審計** (scripts/05 55/55 PASS): 獨立重算 docs/01-04 + final_result 全部公式/數值 (由 γ_n = 4sin²(kπ/176) 第一原理, 唔 import scripts/01-04) — 全部數字確認; 捕獲 4 項文檔表述修正 (全部 ⚠️ 附註, 唔改原文): ① Z_odd 階梯公式漏 factor 2 (docs/02 §四 + final_result; 代碼 −88·I₈₈ 本身正確); ② δ = t/44 **−** t³/132 符號錯 (docs/02 §六, 原寫 +); ③ γ₁ = 0.0012743487 表記截斷 (四捨五入 0.001275); ④ docs/02-04 header 日期 09-13 → 09-14 (實際寫作日); 另: 「dev 1e-131@β≤10」精化 (β≲2 先啱), aliasing 峰值實測 n=176 (docs 記 ≈200), E-M dev@β* 2.4e-61 係 60-digit 精度地板 (180d 實測 3.7e-181) |

## 四、誠實修正記錄

- (我先前取樣偽影) 第一次 log-space 掃描用步長 100 → 「首個 dev>1e-6 喺 n=630」;
  腳本用步長 1 → 真值 **n=536** — 630 唔係結構數, 536 都唔係 — 係 cluster crossover,
  冇特別數值身份 (誠實: 唔好追 536)
- (O192 claim 精化) 「全 n 解析證明」→ 數學精確域 n < N = 88; n ≥ 88 有 aliasing 修正
  (1e-52 尺度起), 數值上 n < 536 仍 dev < 1e-6 — O192 冇實質錯, 但加咗精確域邊界
- (09-14 O193 精化) 「n < 88」正確表述: **odd/even sector** 數學精確域 n < 88
  (j=88 諧波首共振, dM = ∓88·C(2n,n−88)); **full sector** 閉式 88C+2^{2n−1} 實際
  精確到 n < 176 (j=88 族喺 odd/even 對消; 首偏差 n=176, dM = +176·C(2n,n−176),
  1e-105 尺度) — 保守結構域 (矩確定性) 仍係 n < 88, 兩者都真
- (09-14 誠實) O76 記 ℓ_max = log₄18 = 2.08 係四捨五入; 精確值 2.084962501
  (log₄18 = ln18/ln4) — O76 結論 (D_app(ℓ_nyq) ≈ πR_world, 0.9990) 不受影響
- (09-14 閉合審計, scripts/05) 文檔表述修正 — 全部以 ⚠️ 附註記錄, 原文保留:
  ① Z_odd 階梯項漏 factor 2 (docs/02 §四 + final_result): 正確 = 44e^{−2β}[I₀−2I₈₈+2I₁₇₆−...];
     scripts/02 代碼 −88·I₈₈ 本身正確 — 純文檔抄寫錯
  ② δ 展開符號: δ = sinh(2t)/(88·I₀(2t)) = t/44 **−** t³/132 + ... (docs/02 §六原寫 +)
  ③ γ₁ = 4sin²(π/176) = 0.0012743487 (docs/02 表記 0.001274 係截斷; 四捨五入 0.001275)
  ④ docs/02-04 header 日期由 09-13 更正為 09-14 (scripts/02-04 同 docs 實際寫作日)
  — 全部係表述問題, 零物理/推導錯誤; 55/55 獨立重算 PASS

## 五、跨 O 依賴

O190 → O191 → O192 → **O193**; 依賴: O192, O159, O190, O157, O140
