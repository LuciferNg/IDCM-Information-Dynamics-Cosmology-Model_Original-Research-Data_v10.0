#!/usr/bin/env python3
# O197 scripts/03 — T3: 合成統計結構定案
# 分歧: 乘性合成用全 δ̂ 平均 ⟨ln(1+δ̂)⟩ = −0.6265 ⟹ M 中位 2.73e6 ≠ LRD 6.97e6
# 物理: 負偏差模態 (δ̂<0) 唔會啟動種子形成 (欠密 site 唔塌縮)
# ⟹ 種子通道只用 δ̂₊ (44 正偏差模態): M_seed = M_base(1+δ̂₊)^{3/2}(1+δ_env)^{3/2}
# T3a: ⟨ln(1+δ̂₊)⟩ 值 + Π(1+δ̂₊) 閉式?
# T3b: δ̂₊-only 乘性中位 vs LRD 錨
# T3c: 混合模型 (arcsine 低端 + logN 高端) vs 乘性 — 觀測錨鑑別
# T3d: 可證偽預言 — Φ_BH 高端種子密度
import numpy as np

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

M_base = 1.914e6
mu_env, s_env = 0.862478, np.sqrt(1.4098)
N_d = 88

ks = np.arange(1, 89)
theta = ks * np.pi / 176
dhat = -np.cos(2*theta)
dhat_pos = dhat[dhat > 0]
gam = 4*np.sin(ks*np.pi/176)**2

print("== T3a: δ̂₊ 通道統計 ==")
lnp = np.log(1 + dhat_pos)
mean_p, var_p = np.mean(lnp), np.var(lnp)
print(f"  ⟨ln(1+δ̂₊)⟩ = {mean_p:.6f}   Var_pop = {var_p:.6f} (O174 0.039162)")
check("T3a δ̂₊ 44 模態, Var = 0.039162", len(dhat_pos) == 44 and abs(var_p-0.039162)/0.039162 < 0.01,
      f"n={len(dhat_pos)}, Var={var_p:.6f}")
# Π(1+δ̂₊) 閉式? δ̂₊ = k=45..88: 1−cos(kπ/88) = γ_k/2
prod_p = np.prod(1 + dhat_pos)
# 候選: 全 Π = 88/2^86, δ̂₋ (k=1..44) Π = ?  δ̂₋ 1+δ̂ = 1−cos(kπ/88), k=1..44
prod_n = np.prod(1 + dhat[dhat <= 0])
print(f"  Π(1+δ̂₊) = {prod_p:.6e}, Π(1+δ̂₋) = {prod_n:.6e}")
print(f"  Π(1+δ̂₊)·Π(1+δ̂₋) = {prod_p*prod_n:.6e} vs 88/2^86 = {N_d/2**(N_d-2):.6e}")
check("T3a' Π(δ̂₊)·Π(δ̂₋) = 88/2^86", abs(prod_p*prod_n - N_d/2**(N_d-2)) < 1e-30)
# Π(1+δ̂₊) 自身閉式: k=45..88 → 1−cos(kπ/88), 對稱 k↔88−k? cos((88−k)π/88) = cos(π−kπ/88) = −cos(kπ/88)
# k=45..88: 1−cos(kπ/88), k=44−j..? 用恆等式 Π_{k=1}^{N}(1−cos(kπ/N)) 唔直接...
# 數值: 2^{-44}·Π γ_k(k=45..88), γ_k = 4sin²(kπ/176), k=45..88
# sin²((88−j)π/176) = cos²(jπ/176) → γ_{88−j} = 4cos²(jπ/176) = 4sin²((88−j)π/176)✓ 唔幫
# 直接數值檢查: Π(1+δ̂₊) = 2^{-44}·Π_{k=45}^{88} γ_k
p2 = np.prod(gam[44:]) / 2**44
check("T3a'' Π(1+δ̂₊) = Πγ₊/2^44", abs(p2 - prod_p)/prod_p < 1e-12, f"{p2:.6e}")

print("\n== T3b: δ̂₊-only 乘性中位 vs LRD ==")
E_lnM_p = np.log(M_base) + 1.5*(mean_p + mu_env)
print(f"  E[ln M] (δ̂₊ only) = {E_lnM_p:.5f} → M = {np.exp(E_lnM_p):.3e}")
print(f"  LRD 錨 M = 6.97e6, ln = {np.log(6.97e6):.5f}")
check("T3b δ̂₊-乘性中位 ≈ LRD 6.97e6 (5% 內)", abs(np.exp(E_lnM_p) - 6.97e6)/6.97e6 < 0.05,
      f"M={np.exp(E_lnM_p):.3e}")

print("\n== T3c: 合成模型鑑別 ==")
rng = np.random.default_rng(11)
N = 500000
# 模型 A: δ̂₊-乘性 (種子必須正偏差 site + 環境)
dhatp_s = rng.choice(dhat_pos, size=N)
ln1pe = rng.normal(mu_env, s_env, N)
lnM_A = np.log(M_base) + 1.5*(np.log(1+dhatp_s) + ln1pe)
M_A = np.exp(lnM_A)
# 模型 B: 混合 (arcsine 通道 44 正模態 或 logN 通道, 各 50%)
mix = rng.random(N) < 0.5
M_arc = M_base * (1 + rng.choice(dhat_pos, size=N))**1.5
M_env = M_base * np.exp(1.5*rng.normal(mu_env, s_env, N))
M_B = np.where(mix, M_arc, M_env)
# 模型 C: logN only (冇 δ̂ 通道)
M_C = M_env
for name, M in [("A δ̂₊乘性", M_A), ("B 混合", M_B), ("C logN only", M_C)]:
    print(f"  {name}: 中位 M = {np.median(M):.3e}, P(M>1e9) = {np.mean(M>1e9):.5f}, "
          f"P(M>1.7e9) = {np.mean(M>1.7e9):.5f}, P(M<5.4e5) = {np.mean(M<5.4e5):.4f}")
print("  觀測: 中位 6.97e6 (LRD), UHz1 1.7e9 存在 (~1e-6..1e-4 尾), 低端種子存在")

print("\n== T3d: 可證偽預言 — Φ_BH 高端 ==")
# arcsine-only 高端 (δ̂₊ max = 1): M_max = M_base·2^{3/2} = 5.41e6 ⟹ P(M>1e8) = 0
print(f"  δ̂-only 通道: M_max = {M_base*2**1.5:.3e} ⟹ P(M>1e8) = 0 (arcsine 單通道預言)")
print(f"  合成: P(M>1e8) = {np.mean(M_A>1e8):.2e} (δ̂₊乘性), {np.mean(M_B>1e8):.2e} (混合)")
check("T3d 高端種子 (M>1e8) 由 δ_env 通道提供 — 可證偽: 觀測到就證明環境通道",
      np.mean(M_A > 1e8) > 0 and np.mean(M_B > 1e8) > 0,
      f"P_A={np.mean(M_A>1e8):.2e}, P_B={np.mean(M_B>1e8):.2e}")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
