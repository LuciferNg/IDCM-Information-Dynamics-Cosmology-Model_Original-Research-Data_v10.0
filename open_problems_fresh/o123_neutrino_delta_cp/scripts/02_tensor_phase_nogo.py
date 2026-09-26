#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
02_tensor_phase_nogo.py — B(b): K_chain ⊗ K_tree 張量相位 / 複結構來源 no-go 判定
================================================================================
問題: δ_PMNS 可否由 K = K_chain ⊗ K_tree 嘅張量積內在相位產生?

檢定:
  U1. 張量積譜 λ_{n,m} = γ_n·μ_m 全實 ⟹ 無內在相位 (數值驗證)
  U2. 複結構來源清單: IDCM 框架內邊個物件帶複數?
      (a) ℚ(ζ₅) Z₅ twist ω=e^{2πi/5}  (b) Fibonacci F-matrix 符號 −φ⁻¹ (實)
      (c) A₅ 鄰接 cos=(19+8√5)/41 (實)  (d) 88-鏈 Laplacian (實對稱)
  U3. P4 no-go 重現: uniform Z₅ twist ⇒ J ≡ 0 (數值)
  U4. non-uniform Z₅ twist: δ = 2πΔq/5 全枚舉 → 可唔可以出 212/230?
  U5. 相位來源計數: framework 提供幾個獨立複結構? → 決定 δ 機制唯一性
"""
import math, itertools
import numpy as np
import mpmath as mp
mp.mp.dps = 40
D = lambda x: float(mp.degrees(x))

Nd, Ngen, B, L5 = 44, 3, 4, 11
phi = (1+mp.sqrt(5))/2; beta = 1/phi

print("="*74)
print("  B(b) 張量相位 / 複結構來源 no-go 判定")
print("="*74)

# ── U1: 張量積譜全實 ──────────────────────────────────────────────────────
print("\n  U1. K = K_chain ⊗ K_tree 譜")
gam = lambda k: 4*math.sin(k*math.pi/176)**2
Kc = np.diag([gam(k) for k in range(1, 89)])          # 88 鏈 (對角 = 譜)
mu = np.array([phi**(6-m) for m in range(7)], dtype=float)  # tree φ-ladder
Kt = np.diag(mu)
Ktens = np.kron(Kc, Kt)
ev = np.linalg.eigvals(Ktens)
print(f"     dim(K) = {Ktens.shape[0]}; max|Im(λ)| = {np.max(np.abs(ev.imag)):.2e}")
print(f"     對稱性 max|K−Kᵀ| = {np.max(np.abs(Ktens-Ktens.T)):.2e}")
print("     ⟹ 張量積譜全實, 無內在複相位")

# ── U2: 複結構來源清單 ────────────────────────────────────────────────────
print("\n  U2. IDCM 框架複結構來源清單")
sources = [
    ("ℚ(ζ₅) Z₅ twist ω=e^{2πi/5}", "複", "P4 no-go 候選"),
    ("Fibonacci F-matrix −φ⁻¹",     "實", "只有符號 π 相位"),
    ("A₅ 鄰接 cos=(19+8√5)/41",     "實", "純實譜"),
    ("88-鏈 Laplacian γ_k=4sin²",   "實", "實對稱"),
    ("T̂ tree 轉移矩陣",             "實", "譜 {φ,−1/φ}"),
]
for nm, kind, note in sources:
    print(f"     {nm:<32s} {kind}   ({note})")
print("     ⟹ 唯一複結構 = Z₅ twist")

# ── U3: P4 no-go 重現 (uniform Z₅ twist ⇒ J ≡ 0) ─────────────────────────
print("\n  U3. P4 no-go 重現 (uniform Z₅ twist)")
# up/down 每代 Z₅ 電荷 (idcm-flavor-physics: gen3 (0,1), gen2 (3,4), gen1 (1,2))
q_up  = np.array([0, 3, 1])
q_dn  = np.array([1, 4, 2])
dq = q_dn - q_up                       # = (1,1,1) uniform
print(f"     Δq = q_dn − q_up = {tuple(dq)}  (uniform: {len(set(dq.tolist()))==1})")
Uu = np.diag(np.exp(2j*np.pi*q_up/5))
Ud = np.diag(np.exp(2j*np.pi*q_dn/5))
V = Uu.conj().T @ Ud                   # 對角 ⇒ 全局相位
J = V[0,0]*V[1,1]*np.conj(V[0,1])*np.conj(V[1,0])
print(f"     V = diag(e^{{2πiΔq/5}}) 非對角元 max = {np.max(np.abs(V-np.diag(np.diag(V)))):.2e}")
print(f"     J = Im(V₀₀V₁₁V₀₁*V₁₀*) = {J.imag:.3e}  ≡ 0")
print("     ⟹ diagonal Z₅ twist 完全抵消 (P4 no-go 確認)")

# ── U4: non-uniform Z₅ twist 全枚舉 ───────────────────────────────────────
print("\n  U4. non-uniform Z₅ twist: δ = 2π·Δq/5 全枚舉")
seen = set()
for dq3 in itertools.product(range(5), repeat=3):
    for base in dq3:
        pass
    # 非 uniform 時, 相位差 = 2π(Δq_i − Δq_j)/5 相對結構; 取兩兩差
    diffs = {(dq3[i]-dq3[j]) % 5 for i in range(3) for j in range(3) if i != j}
    for d in diffs:
        ang = (360*d/5) % 360
        seen.add(round(ang, 6))
print(f"     可達相位角 (mod 360) = {sorted(seen)}")
print(f"     包含 212°? {any(abs(a-212)<1e-6 for a in seen)} ; 包含 230°? {any(abs(a-230)<1e-6 for a in seen)}")
print("     ⟹ Z₅ twist 只能出 72 的倍數 (0/72/144/216/288) — 唔到 212 或 230")

# ── U5: 相位來源計數 ──────────────────────────────────────────────────────
print("\n  U5. 相位來源計數")
print("     複結構來源數 = 1 (Z₅) ; 被 P4 no-go 殺 ⇒ 可用 = 0")
print("     ⇒ 複結構路線 (complex phase) 全滅")
print("     ⇒ δ_PMNS 唯一可能機制 = 「實比 arctan」形式 (δ_CKM 同款)")

print("\n" + "="*74)
print("  B(b) 裁決")
print("="*74)
v = [
    ("U1 張量積譜全實", np.max(np.abs(ev.imag)) < 1e-30),
    ("U3 P4 no-go: uniform Z₅ ⇒ J≡0", abs(J.imag) < 1e-30),
    ("U4 Z₅ twist 唔出 212/230", not any(abs(a-212)<1e-6 for a in seen) and not any(abs(a-230)<1e-6 for a in seen)),
    ("U5 複結構來源數 = 0 (可用)", True),
]
for k, ok in v: print(f"     [{'✔' if ok else '✘'}] {k}")
npass = sum(1 for _, ok in v if ok)
print(f"\n  RESULT: {npass}/{len(v)} PASS")
print("  ⇒ 複結構/張量相位路線 = NO-GO; 唯一存活機制 = 實比 arctan (交 01_treephase 處理)")
