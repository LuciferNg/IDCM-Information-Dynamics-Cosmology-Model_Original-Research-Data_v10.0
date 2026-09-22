# O99-v2.0 — docs/11: σ_8 首推攻堅 — 誠實判決 (scripts/11)
> **日期**: 2026-08-27
> **scripts/11**：攻 σ_8（A_φφ 最後一環）

---

## 1. 結論一句（誠實）

> **σ_8 首推攻堅 = 唔可以喺 IDCM 現有工具內純推導閉合。根本原因係「8 h⁻¹ Mpc 遠超 K_Chain 網格」的 sub-grid gap（38×），而 O86 亦無線性微擾理論（#6 明確 closed）。自相似外推只係 conjecture 唔係首推。真正路徑唔係「推」而係「校準」：BOSS ξ(s) 實測 + O83 母神對照。**

## 2. 結構性判決（scripts/11）

### 網格覆蓋
```
K_Chain: k ∈ [2.4e-4, 0.0107] Mpc⁻¹ (44-site, 用 46.9 Mpc 格距)
σ_8 需要: k_eff ~ 0.39 Mpc⁻¹ (8 h⁻¹Mpc)
→ 出格 38×  (genuine sub-grid)
```

### K_Tree 自相似外推（攻擊嘗試）
```
4^1層 k=0.20   amp 0.111
4^2層 k=0.80   amp 0.073
...→ 8 Mpc 需 2.6 個 4^層
外推 σ_8 ~ 0.29  (vs obs 0.81) —— 仍差 2.8×, 且係 conjecture
```

**關鍵**: 唔係「數值差」，係**方法論**——外推出去係假設「冪側自相似一路保持到 sub-grid」，IDCM 冇結構保證呢個假設成立。呢個係 conjecture 唔係 first-principles derivation。

## 3. 點解路線 C（O86 growth）唔夠

- O86 docs/02 剩餘開放 **#6: 「W-field 宇宙學微擾 (δg, δH, δφ) 🔴 超出當前範圍」** —— O86 本身係 homogeneous（背景）Lagrangian，**冇 linear perturbation theory**。
- 就算有 growth D(z)，σ_8 係 **P(k) 振幅**（8 Mpc 尺度嘅功率譜），唔單係 growth——需要 transfer function + 原始振幅 A_s。
- 所以「由 O86 推 D(z) 就拿到 σ_8」係**誤會**：growth 只能刻畫 redshift 演化，唔能定 z=0 嘅 8Mpc 振幅。

## 4. O91 曾迴避此路

O91 docs/04 明確「已放棄方向 C（growth equation）: 未必要——問題在於距離，非 growth」。O91 轉而用 **D_A(z) 幾何差異** 論證「S8 張力 = ΛCDM 外推 artifact」並用 Pantheon+ 驗證（34/34）。呢個迴避咗 σ_8 真值 —— **O91 冇真正閉合「σ_8=?」**，只係「解釋張力存在」。

⇒ 你嘅直覺（去馬攻 σ_8 首推）係**正確**嘅 —— 呢個係真係未閉合，唔係「無需」。

## 5. 誠實判決（A_φφ 振幅完整狀態）

```
A_φφ ∝ Ω_m × σ_8² × 幾何
        ✅      🔴      ✅
     (0.95 closed,  (genuine sub-grid gap (L~140 closed)
      scripts/10)    — 需 BOSS 校準 not 純推)
```

**A_φφ 振幅 = 未閉合**。唔係 script 失敗，係**理論機制缺口**。

## 6. 真正可行嘅下一跳（唔係過堆）

1. **路線 E（實測校準）**: 用 BOSS DR12 ξ(s) 數據做 σ_8 測量，同 O83 振幅母神對照——呢個先係目前 IDCM 能落地嘅路，因為佢唔需要 sub-grid 首推。
2. **路線 F（文獻）**: 理解 KiDS/DES S8 方法，睇 O76 D_A 差異點影響 inferred S8（方向 G 已部分）。
3. **真正 sub-grid 理論**: 需要 IDCM 自洽嘅 K_Chain→K_Tree 高 k transfer（小尺度功率密度點唔受網格限），呢個係超出當前嘅前沿工作（🔴 O72 延伸）。

## 7. 狀態

| 項目 | 狀態 |
|:--|:--|
| σ_8 純首推 | 🔴 唔可以（sub-grid 38× + O86 無微擾） |
| σ_8 自相似外推 | ⚠️ conjecture（0.29 vs 0.8） |
| 路線 E（BOSS 校準） | 🟡 唯一實證可行路 |
| A_φφ 振幅 | 🔴 未閉合（留 gap 誠實） |