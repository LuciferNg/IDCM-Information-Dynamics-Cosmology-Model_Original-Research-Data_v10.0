#!/usr/bin/env python3
"""
RG 流框架完整推導 (2026-09-09) — dβ/dℓ = 88/21 = 4N_d/(N_d-μ²) 嘅第一性原理
=============================================================================
Wilson/Kadanoff 離散 RG: 世界層粗粒化 → 模態計數 β-function → 線性跑動 → 觀測閉合

結構:
  A. UV 理論: 88-site 對偶鏈晶格場論 (O140 FSR, O161 Noether)
  B. 尺度: 世界層 ℓ = log₄(1+z), 每層世界分支 ×4 (t_branch 投影)
  C. Block-spin 粗粒化: 4 世界 → 1 區塊, 凝聚模截斷 (μ²=2)
  D. β-function = 每層候選模態 / 有效模態 = 4N_d/(N_d-μ²) = 176/42
  E. 積分: b(ℓ) = b₀ + (88/21)·ℓ — 線性跑動 (觀測 0.22σ)
  F. RG 不變量: 21 × (176/42) = 88 = 2N_d
  G. 凝聚統一: η = φ^{-(N_d-μ²)/2} — 同一有效模態數
"""
import math, json
import numpy as np

phi = (1+5**0.5)/2
N_d, B, mu2, N_gen = 44, 4, 2.0, 3
OUT = 'data/18_rg_flow.json'
res = {}

print("="*78)
print("A. UV 理論 — 88-site 對偶鏈晶格場論")
print("="*78)
# 88 模態, 176-Laplacian: γ_n = 4sin²(πn/176), n=1..88 (O159 88-site half-site D-D BVP)
N = 44
gamma = np.array([4*math.sin(math.pi*n/176)**2 for n in range(1, 2*N+1)])  # n=1..88
omega = np.array([2*math.sin(math.pi*n/176) for n in range(1, 2*N+1)])
print(f"  88 模態: γ_n = 4sin²(πn/176) n=1..88 (176-Laplacian, O159 D-D BVP)")
print(f"  γ 譜和 Σγ = {gamma.sum():.4f} (Σ_even={gamma[1::2].sum():.2f}, Σ_odd={gamma[0::2].sum():.2f})")
print(f"  中心模 μ² = γ₄₄ = {gamma[43]:.6f} ≈ 2 ✓ (O160 中心模定理)")
print(f"  凝聚模: n=44 (v_g=0) + 對偶 → 唔參與區塊變換 (SSB 固定背景)")

print("\n" + "="*78)
print("B. 尺度 — 世界層 ℓ 同 Hilbert 空間增長")
print("="*78)
print(f"  世界分支: N_ℓ = N·4^ℓ (t_branch, 每層 ×4)")
print(f"  深度-紅移: ℓ = log₄(1+z) (t_nz 投影)")
print(f"  dim H_ℓ = 4^ℓ · 88; 觀察者投影 P_obs: 44 世界模 (N_d)")
print(f"  每層有效動力學維度: N_d − μ² = 44 − 2 = 42 (凝聚模截斷)")
print(f"  有效比例: 42/44 = {42/44:.4f} = {21/22:.4f}")

print("\n" + "="*78)
print("C. Block-spin 粗粒化 (Kadanoff 一步 ℓ→ℓ+1)")
print("="*78)
print("  1. 4 個微觀世界副本 (分支 ×4) → 1 個區塊世界")
print("  2. 場重標度: ψ_block = (1/2)Σ_a ψ_a (√4 normalize, 動能保持)")
print("  3. 凝聚模截斷: μ² = 2 個中心模係 SSB 背景 (O160: 中心模定理)")
print("     → 區塊世界動力學維度 = N_d − μ² = 42")
print("  4. 每層候選模態 (粗粒化前): 4 世界 × N_d = 4×44 = 176")

print("\n" + "="*78)
print("D. β-function — 模態計數")
print("="*78)
dbdl = 4*N_d/(N_d-mu2)
print(f"  β(b) = (每層候選模態)/(每層有效模態) = 4N_d/(N_d−μ²)")
print(f"       = {4*N_d}/{N_d-mu2} = 176/42 = {dbdl:.6f} = 88/21 = {88/21:.6f}")
print(f"  驗證 1: 4N_d = 176 ✓; N_d−μ² = 42 ✓; 176/42 = {176/42:.6f} = 88/21 ✓")
print(f"  拆解: 4·(1 + μ²/(N_d−μ²)) = 4·(1+1/21) = 4 + 4/21 = {4+4/21:.6f}")
print(f"  → 分支 ×4 (B) + 中心模修正 (μ²/(N_d−μ²) = 1/21)")

print("\n" + "="*78)
print("E. 積分 — 光譜指數跑動")
print("="*78)
b0 = 2.3886  # script 13 naive intercept (零塵 SED 限制)
def beta(ell, b0=b0): return b0 + dbdl*ell
print(f"  db/dℓ = 176/42 (常數) → b(ℓ) = b₀ + (176/42)·ℓ")
print(f"  觀測 fit (script 13): dβ/dℓ = 4.081 ± 0.497, 0.22σ vs 176/42 ✓")
for ell in [0.0, 0.5, 1.0, 1.45, 2.08]:
    print(f"  ℓ={ell:.2f}: b = {beta(ell):.3f}")
print(f"  ℓ 範圍 [0, 2.08] (z<17 Nyquist): b ∈ [{beta(0):.3f}, {beta(2.08):.3f}]")
print(f"  線性流冇固定點 — 有限尺度窗口 (晶格冇 continuum limit 問題)")

print("\n" + "="*78)
print("F. RG 不變量 — 凝聚階梯 × 陡峭化 = 總譜")
print("="*78)
inv = 21 * dbdl
print(f"  21 × (176/42) = {inv:.6f} = 88 = 2N_d ✓ (代數: (N_d−μ²)/2 × 4N_d/(N_d−μ²) = 2N_d)")
print(f"  解讀: RG 流行 21 步 (凝聚階梯), 每步跨越 176/42 模態 → 啱好覆蓋 88 模態")
print(f"  RG 不變量: I = log_φ(1/η) × dβ/dℓ = 21 × 88/21 = 88 — 唔隨 ℓ 變")

print("\n" + "="*78)
print("G. 凝聚統一 — η 同 β-function 同源")
print("="*78)
eta_exp = (N_d-mu2)/2
eta = phi**(-eta_exp)
print(f"  η = φ^{{-{eta_exp}}} = φ⁻²¹ = {eta:.6e} (凝聚效率)")
print(f"  凝聚 = SSB 深度 ∝ 有效自由度 N_d−μ² = 42: 凝聚階梯 = 42/2 = 21")
print(f"  統一: 物質投影 (η) 同拓撲投影 (dβ/dℓ) 係同一 RG 流嘅兩個觀測面")
print(f"  — β-function: 每層候選/有效模態比 (拓撲)")
print(f"  — 凝聚: 有效模態數嘅 φ-退相干 (物質)")

print("\n" + "="*78)
print("H. 標準 Wilson 對照")
print("="*78)
print(f"  Wilson: β(g) = (d−2)/2·g + O(g²) — 維度因子 × 耦合")
print(f"  IDCM:   β(b) = ΔN/N_eff — 自由度計數 (離散無量綱)")
print(f"  類比: (d−2)/2 ↔ 4N_d/(N_d−μ²): 維度餘數角色由「候選/有效模態比」取代")
print(f"  冇圈展開 — 樹級精確 (晶格結構強迫, 非微擾)")

print("\n" + "="*78)
print("驗證總結")
print("="*78)
checks = [
    ("4N_d = 176", 4*N_d, 176),
    ("N_d−μ² = 42", N_d-mu2, 42),
    ("176/42 = 88/21", 176/42, 88/21),
    ("21 = (N_d−μ²)/2", eta_exp, 21),
    ("21×176/42 = 88", inv, 88),
    ("γ₄₄ = 2 = μ²", gamma[43], 2.0),
    ("Σγ_even/Σγ_odd = 90/88", gamma[1::2].sum()/gamma[0::2].sum(), 90/88),
]
npass = 0
for name, got, want in checks:
    ok = abs(got-want) < 1e-6*max(1, abs(want))
    npass += ok
    print(f"  {'✅' if ok else '❌'} {name:<28} {got:.6f} vs {want:.6f}")
print(f"  → {npass}/{len(checks)} PASS")

res = {'dbdl': float(dbdl), 'eta_exp': float(eta_exp), 'invariant': float(inv),
       'checks': int(npass), 'total': int(len(checks)),
       'beta_ell': {f'{e}': float(beta(e)) for e in [0, 0.5, 1.0, 1.45, 2.08]}}
json.dump(res, open(OUT, 'w'), indent=2)
print(f"\nSaved {OUT}")
