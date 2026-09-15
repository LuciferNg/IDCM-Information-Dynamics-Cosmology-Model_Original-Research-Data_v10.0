# O11 新 Session 啟動文件 — Maser H₀ 偏移

## 所需 Skills

1. `theoretical-physics-validation` (核心, 防數字遊戲)
2. `web-access-protocol` (輔助, 下載文獻)

## 前置資料

```
H₀_idcm = 72.59
TRGB = ×(1−κφ⁻¹) = 69.78 ✅ (0.03%)
Miras = ×(1+κφ⁻¹/4) = 73.29 ✅ (0.01%)
SH0ES = ×(1+φ⁻¹/100) = 73.04 ✅ (0.00%)
Maser = 73.9 = +1.80% 未鎖定
κ = 1/16, φ⁻¹ = 0.618
```

## 啟動 Prompt

```
開 O11 Maser H₀ 專案: /home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o11_maser_h0/

任務: 鎖定 Maser H₀ 偏移公式 (+1.80%)

背景: TRGB/Miras/SH0ES 已閉合 (κφ⁻¹ 家族)。Maser +1.80% 未鎖定。
Maser 係「純幾何」方法 (NGC 4258) — 同距離階梯方法唔同。

步驟:
1. 文獻: NGC 4258 幾何距離 → H₀ 最新值 (2026)
2. 1.80% 結構搜索: φ/ε/κ 組合
3. 機制: Maser 幾何投影層 = 邊個結構?
4. 閉合: 公式 → 預測

載入 skills: theoretical-physics-validation
鐵律: 禁止數字遊戲 — 公式要有結構來源
誠實: 如果 1.80% 冇結構組合 → 🟡 記錄
最後: 雙重驗證 + 更新 01_problem_record + README
```

## 常見坑

1. Maser H₀ 最新值可能更新咗 (73.9 係舊值) — 先查文獻
2. 1.80% 好細 — 要同 κφ⁻¹ 家族比較, 唔好亂撞
3. NGC 4258 幾何距離方法: 幾何投影 = IDCM 邊個層?

---

## ⚠️ O169 修正點 (2026-09-15) — 待本 O 重驗

**修正點** (上游 O169):

- 伸長定律 `E = 1 + 2φ⁻¹ℓ` **已證偽** (DESI DR2 D_M×6 排除 4.88σ) → `E(ℓ) = ℓ + 1.11911398` (= ⟨γ⟩_odd/2·ℓ + 1/⟨v_g⟩_{1..22}); `δ(ℓ) = −φ⁻³(ℓ−1/2)`, `C = 1−2φ⁻¹ = −(√5−2)`

**問題** (本 O 受影響點):

- `final_result.md:19` — Mendeleev: D_app(ℓ) = (44−44/4^ℓ)(R_H/44)(1+2φ⁻¹ℓ)
- `scripts/01_structural_search.py:58`, `scripts/10_derivation_audit.py:101,171`, `02_closure_record.md:37`

**狀態**: [ ] 未重驗
> 只加註, 未改本 O 結論檔 (01_problem_record.md / docs/ / final_result.md); 重驗後由本 O 自行寫入。
