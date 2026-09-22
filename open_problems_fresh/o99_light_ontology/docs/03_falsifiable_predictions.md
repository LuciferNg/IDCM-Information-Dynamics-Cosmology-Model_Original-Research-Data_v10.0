# O99 — docs/03: R3 — 可證偽預言全清單 (Light-as-Wfield Discriminators)

> **日期**: 2026-08-27
> **規則**: 每條預言必須 (a) 有 IDCM unique 值, (b) 有標準天文可測路線, (c) 標明固定 filter vs 變動 discriminator (用戶對照測試要求).
> **狀態**: 全部 🔴 待測 (冇一條係已驗證嘅, 卻係「可證偽」之重點).

---

## 總表

| P# | IDCM 預言 | 值 | LCDM 對應 | 測試 | filter/disc | 狀態 |
|:--:|:-------|:----|:---------|:-----|:----|:----:|
| P-C1 | C_ℓ 純 local, 無 transfer-delay phase 散 | phase-disp = 0 | 光子行, 有 light cone delay 結構 | CMB cross-band phase corr | filter: | 🔴|
| P-C2 | D_L/D_A = (1+z)^0.857 | 0.857 | (1+z)^2 (Euler) | Pantheon+ z>0.8 | disc | O76 ✅ (樣本待加密) |
| P-C3 | 真空光恒 c (continuum) | =c 至 1e-18 | =c | 地球光腔 | — | ✅ Nagel 2015 一致 |
| P-C4 | 「距離」係投影層 | angular power 全由 C_ℓ 定 | 空間 | cross-band | — | 🔴|
| P-C5 | 喏?離散 dispersive ripple | 1e-15~1e-17 freq-dep | 無 | GRB/TeV 時延 | filter: 宇宙 | 🔴 待測 |
| P-C6 | 光源遠近嘅**因果結構** 同光錐 | 一致性即時可辨讀 | 光錐限制資訊 | Bell-type / super- | discriminator | 🔴 核心爭議 |

---

## 每條詳細

### P-C1 — C_ℓ 係 local correlator, 冇 transfer-delay 相位
- **ID**: 峰位由單一 propagator G(0) 定, 相位 constant 0, 無「光源→偵測器」light-cone delay 結構.
- **LCDM**: 每個 mode 有一個 free-flight phase ∝ k·L, 造成 cross-band phase dispersion.
- **測**: CMB/BL 高精度 phase cross-band. → 已喺 scripts/01 驗證 prel(phase=0) 3/3.

### P-C2 — 距離二重性駭然失效 (O76 閉合)
- **ID**: Etherington D_L/D_A = (1+z)^0.857 (n/p=γ₇/γ₂₀).
- **LCDM**: (1+z)².
- **測**: Pantheon+ 1701 z>0.8. → O76 🟢 但高z樣本少, 需加密.

### P-C3 — 真空光速 = c (continuum 疊加)
- **ID**: emergent consistency ray ⊕ all mode → c 精確, 唔違反 1e-18.
- **LCDM**: 同樣 c. → 呢條唔係 discriminator (兩者同), 但保 ID 唔死喺 Lorentz.

### P-C4 — 「距離」係投影層 (structuret)
- **ID**: 觀測距離 = D_APP(ℓ), 唔係實體間距.
- **LCDM**: 空間距離. → 由 angular power + cross-band 驗證.

### P-C5 — 離散 dispersive ripple (★ 唯一 ID 獨有、可證偽)
- **ID**: 1e-15~1e-17 frequency-dependent speed 殘差, 源於 K_Chain lattice 記錄.
- **LCDM**: 至 SME 1e-18 完全無色散.
- **測**: Fermi/LAT GRB multi-GeV 到達延遲, HESS/CTA TeV. **係 ID 最 sharp shot**.

### P-C6 — 一致性 vs 光錐 (核心, 最爭議)
- **ID**: 「資訊」唔係粒子攞去, 係觀察者讀取時 world self-consistency 同步. 呢個 potential 指超距 「相/IP 相關」免走光錐.
- **LCDM**: 光錐嚴禁 superrought.
- **測**: 極高紅移 cross- correlation (量子 imagery studies)/ 墚. 
- **⚠️ 誠實**: 呢條係**形而上學 → 冇直接乾淨天文實驗**仍未見. 唔好 over-claim: 記為 🟠 原理性未落地, 唔係可測 clean 預言. (可能永遠只到 P-C5 為止。)

---

## 對照測試角色標記 (照調律者要求)

- **固定 filter (baseline, 假設成立)**: photon 係實體穿越 (LCDM), 光速=c, 空間=模擬距離.
- **變動 discriminator (檢驗 target)**: D_L/D_A 冪指數 0.857 (P-C2), 相位 0 vs 轉移 (P-C1), dispersive ripple (P-C5).
- 兩者交互 (即“究竟測邊個”) 喺設計時核對: 每條只改 **一個** discriminator.

## 狀態總結
- 已閉合: P-C2 (O76), P-C3 (Nagel 2015 consistency).
- 待測 (sharp): P-C5 (TeV gamma 色散, ★★), P-C1 (CMBphase).
- 原理性開放 (唔可 clean test): P-C6.