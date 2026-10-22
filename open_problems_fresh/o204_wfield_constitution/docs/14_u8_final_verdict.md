# O204 — U8 終局：IDCM 背景下 DESI BAO 對 Σm_ν 嘅約束力（第八輪）

**日期**: 2026-09-18（同一 session，第八輪）
**腳本**: `scripts/23_u8_desi_idcm_bkg.py`（12/12 PASS）
**前置**: O49 docs/05（🟡 模型依賴）→ O170（IDCM 距離框架 + DESI DR2 數據）→ 本輪結構論證

---

## 一、★ 核心論證：IDCM 距離框架冇 Σm_ν 自由度

```
O170: D_H(ℓ) = R_world·(dℓ/dz)·M(ℓ),  M(ℓ) = arch 核
M 淺極限 = sec(25.5π/88), 深極限 = √2 = sec(π/4) — 全部 γ_n/v_g 譜結構
⟹ IDCM 距離預言零 Σm_ν 依賴 (6 tracer < 1σ 已驗證, χ² = 3.471/6)
```

## 二、ΛCDM 邊界 < 0.064 eV 嘅機制對 IDCM 唔適用

```
ΛCDM: Σm_ν ↑ ⟹ neutrino 能量密度 ↑ ⟹ 早期 H(z) ↑ ⟹ r_d ↓ ⟹ D_M/r_d 讀數 ↑
  — 透過 Friedmann 方程耦合
IDCM: 冇 Friedmann 方程 (no expansion, D_app 投影替代);
       r_d = πR_world·420/(88·421) 係結構值 (O170, dev 0.0014%)
⟹ DESI BAO 距離讀數喺 IDCM 中係『結構預言』, 唔係『Σm_ν 約束』
```

## 三、剩餘約束來源審計

| 來源 | 機制 | 對 IDCM 狀態 |
|---|---|---|
| DESI BAO | r_d-Σm_ν 耦合 (Friedmann) | ❌ 唔適用 — 結構論證 (本輪) |
| CMB damping tail | N_eff 敏感 | ✅ 冇約束 — U7 裁決 θ 唔熱化 ⟹ N_eff = 3.044 標準 |
| CMB lensing | Σm_ν ↑ ⟹ 結構增長抑制 ⟹ lensing 功率 ↓ | 🔴 開放 — 需 IDCM 結構增長預言 (冇 Friedmann) |
| 0νββ (LEGEND) | m_ββ = [6.4, 22.1] meV | 🟢 可檢 — 上界 22.1 喺 10-20 meV 目標內 |
| KATRIN 升級 | 直接 m_ν (β 端點) | 🟡 唔夠靈敏 (目標 ~0.2 eV) |

## 四、U8 裁決

```
1. DESI ΛCDM 邊界 < 0.064 對 IDCM 唔適用 — BAO 距離係純結構預言, 唔可以用 ΛCDM 邊界判死
2. 張力實質保留: 若 ΛCDM 正確 (真 expansion + CDM), IDCM 質量鏈 m₃ = 0.0536 eV 受挑戰
   ⟹ M_comp (O66 0.0277% 閉合) 同時受挑戰 ⟹ 成個 IDCM 可證偽 — 真張力, 唔係辯解
3. 真檢驗路徑: 0νββ (LEGEND, m_ββ 上界 22.1 meV 可檢) + CMB-S4 lensing + KATRIN 升級
   — 唔靠 DESI BAO (對 IDCM 零約束力)
4. 新開放 🔴: CMB lensing 對 Σm_ν 敏感機制需要 IDCM 結構增長預言 (冇 Friedmann 動力學)
   — 轉交 IDCM 宇宙學 (lensing 功率譜預言) 未建立
```

## 五、O204 終局狀態

| 判準/遺留 | 狀態 |
|---|---|
| C1 歸一化 | 🟢 |
| C2 能證偽 | 🟢 |
| C3 能盲測 | 🟢 協定已建 (m₇ = 13.8002±0.0005 MeV 預註冊, 等觀測) |
| C4 可預測 | 🟢 |
| C5 零外部輸入 | 🟢 條件閉合 (1-錨最優, docs/13) |
| **U8** | **🟢 模型依賴結構化閉合** (本輪) — 真張力保留, 真檢驗 = 0νββ/lensing |

**剩餘**: C3 執行 (等 m₇ 觀測) + 新 🔴 IDCM lensing 預言 (宇宙學層, 轉交 O169/O170 系)。
