# O160 docs/00 — 掃描架構 + 慣例 + 排除法管線

> 2026-09-08 | 由零開始全數字譜掃描 | scripts/03

## 1. 掃描空間

88×88×33 = 255,552 格, 三軸:

| 軸 | 譜 | 公式 | 語義 |
|:---|:---|:-----|:-----|
| a ∈ 1..88 | γ_a (chain) | 4sin²(aπ/176) | 88-site 對偶鏈 (Σ=178, even 90 世界 / odd 88 觀察者) |
| b ∈ 1..88 | ω_b (chain) | 2sin(bπ/176) | 頻率 (176-Laplacian 慣例, O155 對照表) |
| c ∈ 1..33 | λ_c (tree) | 4sin²(cπ/68) | K_Tree Dirichlet (Σ=66 = 2K_tree) |

FSR 恆等: γ_fsr(k) = csc(kπ/176) = 2/ω_k — FSR Lorentz 階梯係 ω 譜嘅倒數, 唔係獨立軸。

## 2. 不變量族 (13 族 = 每格嘅 13 條連結通道)

| family | 形式 | 維度 | 格數 |
|:-------|:-----|:----:|-----:|
| R88 | γ_a/γ_b | 88² | 7,744 |
| O88 | ω_a/ω_b | 88² | 7,744 |
| BEAT | |ω_a−ω_b| | 88² | 7,744 |
| GT_prod / GT_div | γ_a·λ_c / γ_a/λ_c | 88×33 | 2,904 |
| OT_prod / OT_div | ω_a·λ_c / ω_a/λ_c | 88×33 | 2,904 |
| FULL_wr | (ω_a/ω_b)·λ_c | 88×88×33 | 255,552 |
| FULL_gr | (γ_a/γ_b)·λ_c | 88×88×33 | 255,552 |
| FULL_gd | (γ_a/γ_b)/λ_c | 88×88×33 | 255,552 |
| FULL_bt | |ω_a−ω_b|·λ_c | 88×88×33 | 255,552 |
| SUM_plus / SUM_minus | γ_a+γ_b±λ_c | 88×88×33 | 255,552 |

恆等 (掃描內建檢查): γ 比 = ω 比² (sin² 分解); γ_fsr = 2/ω。

## 3. Target 集 (constant web)

data/constant_web.json — 68 web targets (48 整數 + 6 半整數 + 14 有理) + 22 obs targets:
- **Web**: 只收 🟢 已閉合常數 (O152 operator dictionary + O158 + O151/O153/O155/O157), 每個帶語義 (name/meaning/source)。φ-power 家族唔收 (R12 域定理, trap)。
- **Obs**: PDG 2024 / NuFIT 5.3 無量綱比 (mass ratios, mixing, J, CKM), 每個帶相對 1σ 誤差 → 3σ 窗。

## 4. 排除法管線 (反幻覺鐵律)

```
Pass 0   numpy 向量化全空間枚舉 (13 族, 總計 ~1.6M 格值, 秒級)
Pass 1   排除: |value − web| ≤ 1e-9·max(1,|web|)  → EXACT HIT (閉合網連結)
Pass 2   obs: |value − obs| ≤ 3σ·obs             → OBS HIT (觀測連結)
Pass 3   trap: 1e-5 < |value − web| ≤ 1e-3       → 🟡 候選 (φ-trap, 唔閉合)
Pass 4   novel: 近整數/半整數/web-rational/小分母有理 唔喺 web → 🔮 待解釋
Pass 5   去重: (family, value) 每值一個代表 + 多重度
Pass 6   mpmath 50dps 獨立重算存活者 (scripts/04)
Pass 7   null-control: 背景命中率 (scripts/05)
Pass 8   連結清單 + 語義 (scripts/06)
```

## 5. 語義注意 (O155 量→譜慣例)

- 掃描構造 X[i,j] = γ[j+1]/γ[i+1] ⇒ **值 = γ_b/γ_a** (b 喺分子) — scripts/04 mp_val 跟返
- 2D GT/OT family 嘅 cell_b 係樹指數 c
- 44-mode chain (γ44 = 4sin²(nπ/88)) 只做次框架對照, 唔做主掃描
- trap window 命中一律 🟡, 唔可以因為「差少少」閉合 (同 idcm-phi-power-trap)
