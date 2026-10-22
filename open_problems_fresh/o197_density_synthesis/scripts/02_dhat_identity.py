#!/usr/bin/env python3
# O197 scripts/02 — T2: δ̂ 通道閉式 + 合成統計結構
# ★關鍵身份: 1+δ̂_k = 1−cos(kπ/88) = 2sin²(kπ/176) = γ_k/2 (γ_k = 4sin²(kπ/176))
#   δ̂ = A_k/μ² = −cos(kπ/88), μ² = 2 ⟹ 1+δ̂ = γ/2
# ★Π_{k=1}^{88}(1+δ̂_k) = Π(γ_k/2) — 有冇閉式?
#   標準恆等式 Π_{k=1}^{N−1}(1−cos(kπ/N)) = N/2^{N−1}
#   加 k=88: 1−cos(π) = 2 ⟹ Π_{k=1}^{88} = (88/2^{87})·2 = 88/2^{86}
#   ⟹ Σ ln(1+δ̂_k) = ln(88) − 86·ln2 = ln(N_d) − (N_d−2)ln2
#   平均 ln(1+δ̂) = (ln N_d − (N_d−2)ln2)/N_d — 結構閉式!
# T2a: 驗證 Π 閉式 + 平均
# T2b: 合成 ln M 理論中位 (δ̂ 通道平均 + δ_env μ) vs 模擬
# T2c: 低端 arcsine 主導 / 高端 logN 主導 交叉點
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
gam = 4*np.sin(ks*np.pi/176)**2

print("== T2a: Π(1+δ̂_k) 閉式 = 88/2^86 ==")
prod = np.prod(1 + dhat)
closed = N_d / 2**(N_d-2)
print(f"  Π(1+δ̂_k) = {prod:.6e}")
print(f"  88/2^86   = {closed:.6e}")
check("T2a Π(1+δ̂_k) = N_d/2^{N_d−2}", abs(prod - closed)/closed < 1e-10, f"{prod:.6e}")
mean_ln = np.mean(np.log(1+dhat))
closed_mean = (np.log(N_d) - (N_d-2)*np.log(2))/N_d
check("T2a' ⟨ln(1+δ̂)⟩ = (ln N_d − (N_d−2)ln2)/N_d", abs(mean_ln - closed_mean) < 1e-12,
      f"{mean_ln:.6f} vs {closed_mean:.6f}")
print(f"  ⟨ln(1+δ̂)⟩ = {mean_ln:.6f} (負 — arcsine 重尾喺 δ̂→−1)")

print("\n== T2b: 1+δ̂ = γ/2 身份 ==")
check("T2b 1+δ̂_k = γ_k/2 ∀k", np.allclose(1+dhat, gam/2), "1+δ̂ = 1−cos(kπ/88) = 2sin²(kπ/176) = γ/2")

print("\n== T2c: 合成 ln M 統計 ==")
rng = np.random.default_rng(7)
N = 500000
dhat_s = rng.choice(dhat, size=N)
ln1pd_env = rng.normal(mu_env, s_env, N)
# 乘性合成 (T1 已判): ln M = ln M_base + 1.5[ln(1+δ̂) + ln(1+δ_env)]
lnM = np.log(M_base) + 1.5*(np.log(1+dhat_s) + ln1pd_env)
# 理論: E[ln M] = ln M_base + 1.5(⟨ln(1+δ̂)⟩ + μ_env)
E_lnM = np.log(M_base) + 1.5*(mean_ln + mu_env)
print(f"  E[ln M] 模擬 = {np.mean(lnM):.5f}, 理論 = {E_lnM:.5f}")
check("T2c E[ln M] = ln M_base + 1.5(⟨ln(1+δ̂)⟩+μ_env)", abs(np.mean(lnM)-E_lnM)/abs(E_lnM) < 1e-3)
# Var[ln M] = 1.5²(Var[ln(1+δ̂)] + s²)
var_dhat = np.var(np.log(1+dhat))
Var_lnM = 2.25*(var_dhat + s_env**2)
print(f"  Var[ln M] 模擬 = {np.var(lnM):.5f}, 理論 = {Var_lnM:.5f} (Var_dhat={var_dhat:.5f})")
check("T2c' Var[ln M] = 2.25(Var_dhat + s²)", abs(np.var(lnM)-Var_lnM)/Var_lnM < 1e-3)

print("\n== T2d: 通道主導交叉點 ==")
# ln(1+δ̂) 主導 (細 δ_env) vs ln(1+δ_env) 主導 (大 δ_env)
# 交叉: |ln(1+δ̂)| = |ln(1+δ_env)| — 用典型值 δ̂ ~ ⟨(1+δ̂)⟩ 中位, δ_env 中位 e^μ−1
med_dhat_ln = np.median(np.log(1+dhat))
med_env_ln = mu_env
print(f"  中位 ln(1+δ̂) = {med_dhat_ln:.4f} (δ̂ 通道), 中位 ln(1+δ_env) = {med_env_ln:.4f}")
print(f"  ⟹ 低端 δ̂ 主導 (|ln(1+δ̂)| 大, 負), 高端 δ_env 主導 (正, 無界)")
print(f"  1+δ̂ ∈ [0,2] ⟹ δ̂ 通道 M 上限 = M_base·2^{1.5} = {M_base*2**1.5:.3e}")
M_arc_hi = M_base * 2**1.5
check("T2d δ̂ 通道 M 上限 = M_base·2^{3/2} = 5.41e6 (O174 docs/09)", abs(M_arc_hi - 5.41e6)/5.41e6 < 0.01,
      f"M={M_arc_hi:.3e}")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
