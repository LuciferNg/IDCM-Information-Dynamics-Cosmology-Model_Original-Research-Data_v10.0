# O99 — docs/04: Null-測試 — emergent-c 假設 被 scripts/02 否定 (誠實記錄)

> **日期**: 2026-08-27
> **性質**: **Null 結果** — 我哋自己嘅框架喺自洽性檢查度 FAIL.
> **金句**: 這正是 O99「世界自洽性檢查」本身嘅操作示範 — 連我哋嘅 claim 都要過 check.

---

## 1. 事件

docs/02 我寫「emergent ray 喺 continuum 極限返回 c, 啱岩 1e-18」
→ scripts/02_R2_R3_check.py 計出:

```
v_g(n=1)  = 0.999363 c     (唔係人想嘅 0.99999)
v_g(lim)  = 0.99936283 c    (continuum 極限一樣唔到 c)
Lorentz bound 1e-18 一致性: KO   ← Null 否定
```

## 2. 點解 FAIL (結構原因)

K_Chain 嘅生 v_g = c·cos(πn/88), **n 由 1..44**, 冇 n→0 呢個 mode.
- n=44 → cos(π) = 0 (Nyquist 零速)
- n=1 → cos(π/88) = 0.999363 (最近但不等於 1)
- 所以 K_Chain **本身冇任何 mode 恰等於 c**, 而且「取 lim n→0」唔係 subset 內操作.

→ 「emergent ray = all-mode 疊加 → 返回 c」**唔係自動成立**, 佢需要一個冇俾出嚟嘅 **projection operator** 令色散互相抵消. 呢個 operator = 我 docs/02 §4 已標 🔴 未閉合嘅嘢.

**咁點解天文光學 1e-18 綁實 c?**

> ⚠️⚠️ **三選一定案 (2026-09-22, O73 修正輪 — 原文保留, 禁回溯改寫)**:
> 經 O73 `docs/15` §6/§6.3 (Goldstone 扇區 + O204 G8) 裁決, **三選一已定**:
>
> **(a) + (c) 合併之精確版成立**: K_Chain v_g = c·cos(πn/88) 係**振幅 (徑向) 扇區**之群速度
> (有質量模, m_n = M₀√γ_n ≠ 0), 唔係物理光速; 物理光 (U(1)_EM 光子) 喺**相位 (Goldstone) 扇區**
> — v = c EXACT, `m_θ = 0`。兩個 sector, 唔係「數學 vs 物理」之模糊講法。
> **(b) 投影算子路線刪除**: 唔需要「令色散喺所有頻率 cancel」嘅 projection operator —
> 相位扇區本身無質量誘發色散; 晶格色散 (sin(ka/2)) 對光子唔適用 (`ka ≫ 1`,
> a = 93.863356 Mpc, 世界環晶格唔係光子 UV 正則化)。
>
> ⇒ 「continuum 自動返回 c」唔成立**仍然正確** (唔係由 lattice 極限出嚟),
> 但缺口由「需投影算子」**降級為弱聲明**: 「光子 = 相位扇區之連續極限激發」,
> 由 c = a√J (N_d 相消, 連續極限斜率) + ka ≫ 1 支持 (O73 `docs/15` §3/§6.1)。

## 3. 誠實結論 (三選一, 尚未定)

(a) **「光學 c」同 K_Chain mode v_g 無關** — emergent input 由一套唔同嘅「continuum sector」嘅 consistency 決定, K_Chain 只係 cosmology 尺度 mode. 
(b) 需一個具體 W-field projection operator, 令色散喺所有頻率 cancel (我哋需要推 O84/O86 先有 orthant 嘅 tool)。
(c) K_Chain v_g 根本唔係物理光速 — 只係 lattice geometry 嘅數值, 同「光速」兩回事。

**而家判 (c) 最乾淨**: v_g = c·cos(πn/88) 係数学上嘅 group-velocity-of-lattice, 唔係「光線速度」。物理「光」喺另一 sector。→ 即 docs/02 嘅「兩層」拆分方向啱, 但「continuum 自動返回 c」呢步**唔成立**, 要刪。

## 4. 對 O99 主論題嘅影響 (唔係致命)

- ✅ **核心不受影**: 「光=W局地讀數」與「 lattice mode 之 v_g」獨立 — 冇一個 mode 講緊粒子穿越, 都無涉 particle transport.
> ⚠️ **更新 (2026-09-22, O73 修正輪 — 原文保留)**:
> - 「光=c 仲係要 axiom」→ **已解**: c 之**值**已由 O73 `docs/15` §3 推導
>   (`c = a√J = R_world·ω_ring`, N_d 相消 — 零自由參數); `m_γ = 0` EXACT。
>   「零色散」仍需**弱聲明** (光子 = 相位扇區連續極限 + ka ≫ 1), 唔係全盤 axiom。
> - 「O99-A: 造具體 W 投影 operator」→ **O99-A 已由 O73 docs/15 收編**: 光 = U(1)_EM;
>   c 由 Goldstone 相位模設定; 唔需 projection operator (docs/05 已更新註)。

## 5. 記錄更新

- docs/02_c_identity.md §4 ✅部分閉合 修正: 移除「continuum 返回 c」derived 聲稱, 改為 Structural (尚缺 operator).
- O99 主條目: R2 標記由「Structural 🔴」保留, 加「null test 已拒 naive emergent-c claim」。
- 呢個 null result = O99 嘅正確資產 (自洽檢查), 唔係失敗。

## 6. 一句

> ⚠️ **金句更新 (2026-09-22, O73 修正輪)**: 「要真 c, 要推 W-projector」**已達成 — 但唔係靠 projector**:
> 靠 **W Goldstone 相位扇區** (m_θ = 0 EXACT) + **連續極限** (c = a√J, N_d 相消) + **ka ≫ 1**
> (晶格色散唔適用)。原文保留作歷史。

**「光等於 c」答案未有 — 但至少知佢唔係 naive 攞K_Chain mode 攞到, 唔可以造假。 要真 c, 要推 W-projector, 唔係口吟。」**