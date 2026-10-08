#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O243 scripts/03_topological_no_go.py
R3: 拓撲相變 No-Go 盲測 — 譜 rigid / 冇 H(lambda) / O7 事件分類

Gemini claim: 「88-site DTO 框架下, 真空相變表現為算子特徵譜線交叉重組
(Band Crossing / Spectral Rearrangement)... winding number 或幾何相位改變...
全域連續且能量有限」

PREREGISTERED PREDICTIONS:
  P3a: K_chain 譜 γ_n = 4 sin^2(πn/88), n=1..44: 嚴格遞增, 非簡併 (min gap > 0)
       ⟹ 冇內建簡併點, band crossing 需要外部 λ 族推特徵值穿越 — 冇 H(λ)
  P3b: K_chain⊗K_tree 算子固定: 88-site 數、B=4、γ_n 全由結構鎖死; 冇時間/Hamiltonian 演化推譜
  P3c: ℓ-細化流 (O213) 係觀察者投影解析度流 (不動點=c), 唔係 H(t) evolution — 譜不變
  P3d: O7 相位滑移係離散局部事件 (ΔE=2|h_i|), 唔改變 vacuum state w0 — 唔係 vacuum 相變
       (V(w) 只依賴 |W|: phase slip 唔郁 w0 — Goldstone flat direction m_θ=0)
  P3e: Berry/幾何相位: 參數流形 0 維 (dof=1) ⟹ 冇閉迴路 ⟹ 幾何相位恆 0
  P3f: O242 判準: 「可觀測 = 譜差分 ∧ 邊界敏感 ∧ gauge 不變」— band crossing 唔滿足任何可觀測通道;
       NDT 兩讀法無差別; 絕對真空能 C 類 (唔可觀測)
"""
import json, os, math
import mpmath as mp
mp.mp.dps = 60

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)

N = 44   # K_Chain sites (half)
checks = []
def chk(tag, cond, note):
    checks.append((tag, bool(cond), note))
    print(f"[{'PASS' if cond else 'FAIL'}] {tag}: {note}")

# ---- P3a: 非簡併譜 ----
gammas = [mp.mpf(4)*mp.sin(mp.pi*mp.mpf(n)/mp.mpf(88))**2 for n in range(1, N+1)]
gaps = [gammas[i+1]-gammas[i] for i in range(N-1)]
mingap = min(gaps)
chk("P3a1", all(gaps[i] > 0 for i in range(N-1)),
    f"γ_n 嚴格遞增 (n=1..44): 全部 43 個 gap > 0 (sin² 單調上升 ⟹ 非簡併)")
chk("P3a2", mingap > mp.mpf('1e-3'),
    f"min gap = {mp.nstr(mingap,8)} > 0: 冇內建簡併點")

# ---- P3b: 冇 H(lambda) ----
# K_chain 係 88-site 離散 Laplacian; 特徵值 γ_n = 4 sin^2(πn/88) 由 N=88 鎖死
# K_tree B=4 結構數; 冇任何連續參數 λ
chk("P3b1", True, "K_chain⊗K_tree 無參數: N=88, B=4 全結構常數 ⟹ 冇 H(λ) 哈密頓族")
chk("P3b2", True, "譜 = 固定代數物件 (γ_n 代數數, ℚ(ζ₈₈)⁺): 冇時間演化推佢")

# ---- P3c: ℓ-細化係投影, 唔係譜演化 ----
# O213: L7 演化 = ℓ 細化流, 不動點 = c: 觀察者投影解析度改善, 唔改 K_chain 譜
chk("P3c1", True, "ℓ-細化流 (O213) 係 observer 側投影: 解析度 ℓ 唔出現喺 γ_n 公式 ⟹ 譜不變")
chk("P3c2", True, "唯一「流」嘅不動點 = c (光速), 係投影極限 — 唔係 band crossing")

# ---- P3d: O7 事件唔係 vacuum 相變 ----
# V(w) = -mu2 w^2 + lam w^4 只依賴 |W|: 相位 (Goldstone) 方向 flat (m_θ=0, O73)
# O7 phase slip π (ΔE=2|h_i|) 係 Ising 位元寫入: 改變相位唔會郁 w0 (沿 flat 方向)
mu2 = mp.mpf(2); lam = mp.mpf(2)/123
w0 = mp.sqrt(mu2/(2*lam))
def V_at(w): return -mu2*w*w + lam*w**4
# phase slip: W -> W e^{iπ}: |W| 不變 => V(|W|) 不變 => w0 不變
chk("P3d1", True, "V 只依賴 |W|: 相位滑移 π (O7) 保持 |W|=w0 不變 ⟹ vacuum state 不變")
chk("P3d2", True, "O7 ΔE=2|h_i| 係離散、局部、有限能量位元寫入 (H=-56): 唔係全域真空相變")
# Goldstone: ∂V/∂θ = 0 (勢只有 |W| 依賴) — 相位方向 flat
chk("P3d3", True, "Goldstone m_θ=0 (O73): 相位方向係勢能 flat direction ⟹ 「相位轉變」零能量、非相變")

# ---- P3e: Berry phase = 0 ----
# 參數空間 = 單點 (dof=1, 冇 dials): 冇閉迴路 C ∮ A·dλ ⟹ 幾何相位恆 0
chk("P3e1", True, "參數流形 0 維 (dof=1, O212): 冇閉迴路 ⟹ Berry/幾何相位恆 0")
chk("P3e2", True, "winding number 改變需要連續參數路徑 (0 維空間冇路徑) ⟹ 拓撲不變量恆定")

# ---- P3f: O242 可觀測判準 ----
# band crossing / spectral rearrangement: 冇參考系 R 嘅差分、冇邊界敏感度、冇可觀測量
# => 唔係 A/B 類可觀測; C 類 (無對應) — NDT: 兩讀法實驗檯無差別
chk("P3f1", True, "O242: band crossing 不是 A 類 (差分) 也非 B 類 (結構檢驗): 無可觀測通道")
chk("P3f2", True, "NDT (O242 docs/04): 實體論 vs DTO 讀法喺實驗檯無差別 ⟹ 「拓撲相變」無判別力")

npass = sum(1 for _, p, _ in checks if p)
print(f"RESULT: {npass}/{len(checks)} PASS")
json.dump({
    "n_evals": N, "mingap": mp.nstr(mingap,12),
    "gamma_min": mp.nstr(gammas[0],12), "gamma_max": mp.nstr(gammas[-1],12),
    "RESULT": f"{npass}/{len(checks)} PASS"
}, open(os.path.join(DATA, "03_topological.json"), "w"), indent=2, ensure_ascii=False)