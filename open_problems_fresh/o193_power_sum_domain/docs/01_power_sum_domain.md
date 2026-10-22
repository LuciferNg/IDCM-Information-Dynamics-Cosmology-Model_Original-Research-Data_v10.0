# O193 docs/01 — 冪和閉式精確域 + Nyquist-atom 機制 + arcsine 譜定理

> 2026-09-13 · scripts/01 驗證 32/32 PASS · 零新常數 · 接 O192 冪和閉式統一定理

## 一句話本質

O192 嘅冪和閉式 Σγ^n = 88·C(2n,n) + 2^{2n−1} 唔係「全 n」: **數學精確域 n < N = 88**
(有理函數論證 + aliasing 分析), 數值域 n < 536 (cluster 修正)。佢嘅兩個副產品都係定理:
**parity-gap = γ_N^n/2 (Nyquist 原子機制, N 無關)** 同 **arcsine 譜定理 (觀察者 sector =
離散 arcsine)** — 同 O157 零偏差定理係同一對象嘅三個投影。Partition function = Bessel I₀。

## 一、精確域定理 (scripts/01 V01-V06 ✅)

```
Σγ^n = 88·C(2n,n) + 2^{2n−1},  Σγ^n_odd = 44·C(2n,n),  Σγ^n_even = 44·C(2n,n) + 2^{2n−1}
```

- **數學精確域 n < N = 88** (aliasing-free, dev < 1e-12, 實測 max 3.7e-15):
  有理函數論證 — 有限譜 MGF Σ_k 1/(1−γ_k x) 係有理函數 (44 個單極點),
  唔可能全 n 等於無理函數 44(1−4x)^{−1/2} ⟹ 必定有邊界; aliasing 分析: cos^j 展開
  嘅 m=88 頻率項喺 n ≥ 88 開始出現
- **aliasing 修正尺度**: dev ≈ 2^{n−87}·C(n,88)/C(2n,n) — n=88 時 ~1e-52,
  **峰值 ~1e-26 (n≈200)**, 之後衰減 — 永遠 float64 不可見 (V04)
  > ⚠️ **驗證修正附註 (09-14 閉合審計, scripts/05 A05)**: 峰值實測 log10(dev) = −26.04
  > **@ n=176**（9.1e-27 ≈ 1e-26 值啱, 位置 176 ≈ 200 嘅「≈」略鬆）— 對結論無影響。
- **數值閉式域 n < 536**: 首個 dev > 1e-6 喺 n = 536 — 呢個係 cluster 修正
  (離散和 vs 積分, arcsine 密度嘅 1/n 修正), **唔係 aliasing** (V05)
- **O192「全 n」claim 精化**: 數學 n<88 精確; n≥88 修正 1e-52 尺度 — O192 冇實質錯,
  但「全 n」字面上唔啱, 精確表述係「n < N = 88 精確, 其後修正指數級壓制」

## 二、Nyquist-atom gap 定理 (scripts/01 V06-V08 ✅)

```
parity-gap := Σγ^n_even − Σγ^n_odd = γ_N^n/2 = 4^n/2 = 2^{2n−1}    (n < N, 任何 N)
```

- **N 無關**: N = 22, 44, 88 三鏈全驗證 (V06) — gap 唔 depend 鏈長
- **機制**: k=N 原子 γ_N = 4sin²(Nπ/2N) = 4 (Nyquist, 任何 N 都存在, V07) 只喺 even
  sector; 其矩 4^n 嘅**一半** (½) 進入 gap — ½ 來自 pair 邊界結構 (176-cycle 喺 k=N
  自配對, sin^{2n}(π/2) = 1)
- **radion-flat 機制化 (O159/O190)**: O159「譜身份 N 無關」、O190「radion-flat」嘅
  定量形態 = Nyquist 原子嘅存在性 — 只要鏈有 Nyquist 原子, gap 就係 γ_N^n/2, 同 N 無關

## 三、arcsine 譜定理 (scripts/01 V09-V11 ✅)

```
Σγ^n_odd = (N/2)·C(2n,n)   (n < N)   ⟺   觀察者 sector = 離散 arcsine-on-[0,4]
```

- arcsine-on-[0,4] 矩 = C(2n,n) (已知); 觀察者 sector 44 個原子 (4sin²(odd·π/176))
  嘅矩 = 44·C(2n,n) — **首 N−1 = 87 個矩同 arcsine 完全一致**
- 1D 鏈 DOS = arcsine (tight-binding 已知): cos 色散 ⟹ 譜密度 1/(π√(x(4−x)))
- **O157 統一 (EXACT)**: γ_k = μ² + A_k, A_k = −μ²cos(2θ_k) (θ_k = kπ/176)
  ⟺ γ_k = 2 − 2cos(kπ/88) = 4sin²(kπ/176) — 零偏差定理、冪和閉式、arcsine 譜
  係**同一對象**嘅三個投影: 觀察者/世界 sector 就係 1D 鏈譜 μ²(1−cos)
- N→∞ 弱收斂: 離散 44 原子 → 連續 arcsine (矩相等 + 有限譜)

## 四、Σsin^{2m} 閉式 + 家族自交 (scripts/01 V12-V13 ✅)

Σ_{k=1}^{88} sin^{2m}(kπ/176) = 88·C(2m,m)/4^m + ½ (m < 88) — +½ = Nyquist 半原子
(sin^{2m}(π/2) = 1 邊界); **m=3 → 28 = L₇−1** (L−1 家族成員, O192 自交重驗)。

## 五、Partition function — Bessel (scripts/01 V14-V17 ✅)

```
Z_N(β) = Σ_k e^{−βγ_k} = e^{−2β}[1 + e^{−2β} + 2Σ_{k=1}^{43} cosh(2βcos(kπ/88))]   (精確)
       ≈ N·e^{−2β}·I₀(2β)                                                          (Bessel)
```

- Bessel 近似 dev: 0.11% (β=0.05) → 1.84% (β=1.0) — 高溫 (細 β) 準, 低溫偏離
- 內能 ⟨γ⟩ = 89/44 = **μ² + 1/N_d**; 88·⟨γ⟩ = 178 = F₁₁·μ² = **equipartition 內能 =
  總譜和預算** (O192 預算量子嘅熱力學面)
- 鏈熱力學: 全階能量矩 = 冪和閉式 ⟹ U(β), C_v(β) 全階可算 — 接 O40 virial T = 123/4

## 六、新 cutoff 登記

**Moment-domain Nyquist cutoff**: 冪和閉式精確域 n < N = 88 — IDCM 第二個 Nyquist
結構邊界 (第一個: z > 17, 記憶). 兩者同源: 離散譜嘅頻率內容撞鏈長 ⟹ 閉式斷。

## 七、判決

- 🟢 精確域定理 (數學 n<88, 數值 n<536; O192 claim 精化)
- 🟢 Nyquist-atom gap 定理 (γ_N^n/2, N 無關 — radion-flat 機制化)
- 🟢 arcsine 譜定理 (觀察者 = 離散 arcsine; O157 統一)
- 🟢 Partition function = Bessel I₀; ⟨γ⟩ = μ²+1/N_d; equipartition = 預算
- 🟡 Z(β) 低溫 (β ≳ 1) 修正結構 (Bessel 近似 1.8% — Euler-Maclaurin 級數?)
- 🟡 arcsine 譜 ↔ 宇宙學觀測面 (D6 密度漲落 arcsine, O157) — 同一測度嘅兩個出場?

## 八、開放項

1. 🟡 Z(β) 嘅 Euler-Maclaurin 修正: dev(β) ≈ ? (0.11%→1.84% — 係咪 (π/N)²β 級?)
2. 🟡 arcsine 譜 (觀察者) ↔ D6 密度漲落 arcsine (O157) 嘅統一表述 — 同一測度?
3. 🟡 精確域 n < 88 嘅物理意義: moment-domain Nyquist cutoff 有冇觀測對應
   (z > 17 有 z-cutoff; n < 88 對應?)
4. 🟡 鏈熱力學完整推導: U(β), C_v(β), 熵 S(β) — 接 O40 virial T = 123/4
