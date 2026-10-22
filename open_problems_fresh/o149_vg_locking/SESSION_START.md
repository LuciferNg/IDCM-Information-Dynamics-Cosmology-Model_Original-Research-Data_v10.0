# O149 — SESSION START: 群速度鎖定

> **Session**: 2026-09-05（建立並完成）
> **狀態**: 🟡 部分閉合 → 見 `docs/01_derivation_record.md`
> **位置**: IDCM-v10.0--It-From-Beat/open_problems_fresh/o149_vg_locking/

## 問題

CKM/PMNS 混合角能否由 K_Chain 色散結構**先驗鎖定**（群速度身份），取代 O146 §10 揭發嘅後驗搜索？

## 結果（一句講完）

混合扇區全部係群速度比（定理 1-2: beat=sin×v_g 分解 + Z₂ 字典 ω↔v_g, γ↔v_g²）；CKM 兩個受抑制元素 sinθ₁₃ 同 V_ub 由 k-ladder 鎖定規則先驗推出（0 自由參數, 自然終止, p=9.6e-10）；其餘 9 角 🟡（docs 後驗, 家族結構支撐但未鎖定）。

## 關鍵產出

1. 定理 1: beat(a,b) = 4·sin(dπ/176)·v_g((a+b)/2), 946/946
2. 定理 2: Z₂ 對偶字典 (44/44) → O65 γ-ratio = v_g²-ratio
3. 定理 3: v_g 下限 sin(π/176)=0.01785 → 受抑制角兩因子必然, PMNS 無抑制
4. 定理 4: k-ladder g_k = beat(44-k,44-k+1)/beat(sum=44-(k+1), d=F_{k+6})
   k=2→sinθ₁₃, k=3→V_ub, k=1/4 自然終止
5. 盲測: P1 ✅ P2 ✅ P3 ✅ P4 🟡 (8/9)

## 檔案

- `docs/01_derivation_record.md` — 完整推導
- `scripts/01-07` — 全部 PASS
- `data/01-07.json` — 結果

## 剩餘（下一 session）

1. 分母規則 d=F_{k+6} 嘅代數起源 🟡
2. V_td 第三機制 (beat(40,42)/beat(3,42) 候選 δ=1.8e-4) 🔴
3. 中等扇區 O(1) 候選規則 🔴
