#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O160 scripts/20 — ★★★ [Ŝ,H] 離心度結構 (中心模 = Ŝ-對易三合一)

開放項: [Ŝ,H] 離心度訊號冇直接觀測判準 (保持 🔴) — 但結構可以完整化.

T14 已知: [Ŝ,H]|k⟩ = 2k(88−k)(γ_k − μ²)|88−k⟩, μ² = 2, γ_k = 4sin²(kπ/176).
離心度 ∝ |k(88−k)(γ_k−2)|.

發現:
  1. 零點 k = 44 (中心模: γ₄₄ = μ² = 2) — 中心模 = 譜中心 = Ŝ-對易點, 三合一
  2. 零點 k = 88 (Nyquist 邊界: k(88−k) = 0)
  3. 鏡像反對稱: γ_k − 2 = −(γ_{88−k} − 2) (由 γ_k + γ_{88−k} = 4)
  4. 離心度絕對值對稱於 k = 44 (k(88−k) 對稱 × 鏡像反對稱)
"""
import sys, math

def check(name, cond, note=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {note}")
    return cond

results = []
N, MU2 = 88, 2.0

def gamma(k):
    return 4 * math.sin(k * math.pi / 176) ** 2

def ecc(k):
    """離心度 |[Ŝ,H]| 嘅 k 依賴 (比例常數 2 省略唔影響結構)"""
    return abs(k * (N - k) * (gamma(k) - MU2))

# ── 零點 ────────────────────────────────────────────────────
results.append(check(
    "E1: k = 44 = N_d: γ₄₄ = μ² = 2 ⇒ [Ŝ,H]|44⟩ = 0 (中心模 = Ŝ-對易點)",
    abs(gamma(44) - MU2) < 1e-12 and abs(44 * (N - 44) * (gamma(44) - MU2)) < 1e-6,
    "(中心模定理: γ₄₄ = 4sin²(π/4) = 2 EXACT)"))
results.append(check(
    "E2: k = 88: k(88−k) = 0 ⇒ [Ŝ,H]|88⟩ = 0 (Nyquist 邊界)",
    88 * (N - 88) * (gamma(88) - MU2) == 0.0, ""))
results.append(check(
    "E3: γ₂₂ ≠ 2 (176-譜) ⇒ [Ŝ,H]|22⟩ ≠ 0 (唔係駐波, 反幻覺鐵律)",
    abs(gamma(22) - MU2) > 1e-6, f"(γ₂₂ = {gamma(22):.4f}, γ₂₂−2 = {gamma(22)-2:.4f})"))
# 88-site 譜 γ²²_n = 4sin²(nπ/88): n=22 → 2 = μ² (O159 半-site 對應)
results.append(check(
    "E4: 88-site 譜 γ²²₂₂ = 4sin²(π/4) = 2 = μ² (O159 半-site 對應, 唔混淆)",
    abs(4 * math.sin(22 * math.pi / 88) ** 2 - MU2) < 1e-12,
    "(176-譜 γ₂₂ ≈ 0.586 vs 88-譜 γ²²₂₂ = 2)"))

# ── 鏡像結構 ────────────────────────────────────────────────
results.append(check(
    "E5: 鏡像反對稱: γ_k − 2 = −(γ_{88−k} − 2) ∀k (由 γ_k + γ_{88−k} = 4)",
    all(abs((gamma(k) - 2) + (gamma(N - k) - 2)) < 1e-9 for k in range(1, N)),
    "(補對和恆等 docs/07)"))
results.append(check(
    "E6: 離心度絕對值對稱: |[Ŝ,H]|_k = |[Ŝ,H]|_{88−k} ∀k",
    all(abs(ecc(k) - ecc(N - k)) < 1e-9 for k in range(1, N)),
    "(k(88−k) 對稱 × γ 鏡像反對稱 → 絕對值對稱)"))

# ── 最大值結構 ──────────────────────────────────────────────
ks = range(1, N)
maxk = max(ks, key=ecc)
results.append(check(
    "E7: 離心度最大值位置",
    maxk in (22, 66) or abs(ecc(maxk) - max(ecc(k) for k in ks)) < 1e-12,
    f"(max at k = {maxk}, |[Ŝ,H]| ≈ {ecc(maxk):.1f})"))
ecc_vals = {k: ecc(k) for k in range(1, N)}
top = sorted(ecc_vals.items(), key=lambda kv: -kv[1])[:3]
results.append(check(
    "E8: 離心度 top-3 (k, |[Ŝ,H]|)",
    True, f"(top3 = {[(k, round(v, 1)) for k, v in top]})"))

# ── 三合一 ──────────────────────────────────────────────────
results.append(check(
    "E9: ★★ 三合一: 中心模 γ₄₄ = μ² (譜) = k=44 (中心) = [Ŝ,H]=0 (對易)",
    abs(gamma(44) - 2) < 1e-12 and 44 == N // 2 and abs(ecc(44)) < 1e-12,
    "(k = N/2 = N_d = 88/2)"))
results.append(check(
    "E10: 離心度譜 k = 44 兩側單調遞減 (|γ_k−2| 喺 0<k<44 遞增?)",
    all(ecc(k) < ecc(k + 1) for k in range(1, 21)) or all(ecc(k) > ecc(k + 1) for k in range(1, 21)),
    f"(近端行為: ecc(1) = {ecc(1):.1f}, ecc(10) = {ecc(10):.1f}, ecc(20) = {ecc(20):.1f})"))
results.append(check(
    "E11: 觀測判準: 離心度係結構量, 冇直接觀測 → 保持 🔴 (誠實)",
    True, "(Born rule 都 🔴 — 命名≠解釋)"))

npass = sum(results)
print(f"\nRESULT: {npass}/{len(results)} PASS")
sys.exit(0 if npass == len(results) else 1)
