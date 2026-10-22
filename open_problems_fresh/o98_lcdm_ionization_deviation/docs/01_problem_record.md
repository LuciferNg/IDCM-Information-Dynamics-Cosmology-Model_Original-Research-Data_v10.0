# O98 — ΛCDM I 分歧 2.18% (reionization 距離積分幾何差異)

> **創建日期**: 2026-08-27
> **狀態**: 🟢 **已閉合 (2026-08-28) — 2.18% = 模型幾何差異, 非 IDCM 錯誤; τ 中心值修正; 概念混淆釐清**
> **來源**: O72 可疑點 #8 (★★★)
> **前置**: O73 (docs/08, docs/12), P7 reionization, Planck 2018 (1807.06209)
> **定位**: O73 發現 ΛCDM 嘅 I (距離積分 ∫dz/E(z)) 同 IDCM 有 2.18% 分歧。
> **優先度**: ★★★ (已解決)

---

## 問題

O73 發現 ΛCDM 嘅 I (距離積分, 用於 H₀ = ω_ring × 7I/24 翻譯) 同 IDCM 有 2.18% 分歧。

⚠️ 修正: 原 problem record 寫「I (ionization efficiency, reionization optical depth)」— 概念混淆。
真正嘅 reionization optical depth τ 係 P7 嘅量, 已另計閉合 (0.04σ)。
O73 嘅「I」係 ΛCDM 距離積分, 同 ionization efficiency 無關。 (見 docs/02_verdict.md §3)

無人解釋呢個分歧係:
  - 「模型幾何差異」(IDCM 同 ΛCDM 嘅幾何唔同, 自然有分歧)
  - 定係「IDCM 錯誤」(IDCM 嘅預測出錯)

## 攻擊路線

```
✅ 已完成 (2026-08-28):
  1. scripts/01_independent_audit.py — 全數值重算 (I=3.115883, I*=3.183772, dev=2.179%)
  2. scripts/02_pi144_structure_check.py — π/144 候選檢驗 (穩健性 fail, 🟡 弱候選)
  3. Planck 官方中心值修正 (τ = 0.0544 ± 0.0073)
  4. 判定: 模型幾何差異 (三層證據, 見 docs/02_verdict.md)
```

## 驗證標準

```
✅ 已達成:
  - 檢查 O73 reionization 推導 → 實為距離積分 I, 推導正確
  - 對比 Planck τ_reion → IDCM 0.054105 vs 0.0544±0.0073 → 0.04σ
  - 判定: 2.18% = 模型幾何差異, 非 IDCM 錯誤 → O73 閉合不受影響
```

## 狀態

```
🟢 已閉合 (2026-08-28)
  主判決: 2.18% 分歧 = 兩套幾何嘅本質差異
  τ 閉合: 0.04σ (P7 中心值修正 0.054 → 0.0544)
  旁支:   π/144 = π/(B·N_gen)² 弱候選 🟡 (唔升級)
```
