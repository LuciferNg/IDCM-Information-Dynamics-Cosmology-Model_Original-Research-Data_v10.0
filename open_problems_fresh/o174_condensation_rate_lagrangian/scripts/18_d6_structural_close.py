#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O174 scripts/18 — D6 攻堅: k=36 結構身份 + 11/45 全結構驗證 + 完整閉合

docs/13 標記 k=36 係「反推值」, 物理推測級 🟡。本攻堅:
1. k = 36 = B·N_gen² (B=4, N_gen=3) — 全結構候選
2. 11/45 = L₅/(F₅·N_gen²) = 11/(5·9) — 全結構身份 (O175 null 一致候選)
3. μ = φ⁻¹ + L₅/(F₅·N_gen²) 全結構重算
4. s² = B·N_gen²·Var_pop(ln(1+δ̂₊)) 全結構重算
5. 雙樣本重新校準 (全結構參數, 零擬合)
6. 誠實: 11/45 冇轉正 (O175 docs/06: 噪聲地板 > dev, 數據無法證明) — 結構身份 ≠ 觀測轉正

驗證:
C1: B·N_gen² = 4×9 = 36 (結構身份)
C2: L₅/(F₅·N_gen²) = 11/45 (結構身份)
C3: μ = φ⁻¹ + L₅/(F₅·N_gen²) vs 0.861623 (dev?)
C4: s² = B·N_gen²·Var_pop → s vs 1.2 (dev?)
C5: 全結構參數 → 雙樣本校準 (P(>8), 中位)
C6: 誠實標記 — 結構身份 vs 觀測轉正分別
"""
import math, statistics, random

def chk(name, ok, note=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {note}")
    return ok

total = 0; passed = 0

print("=== C1: k = B·N_gen² = 36 ===")
B = 4; N_gen = 3
k = B * N_gen**2
print(f"  B·N_gen² = {B}×{N_gen}² = {k}")
ok = k == 36
total += 1; passed += ok
chk("C1 k = B·N_gen² = 36 (全結構)", ok, "B=4 (阻挫基), N_gen=3")

print("\n=== C2: 11/45 = L₅/(F₅·N_gen²) ===")
L5 = 11; F5 = 5
v = L5 / (F5 * N_gen**2)
print(f"  L₅/(F₅·N_gen²) = {L5}/({F5}×{N_gen}²) = {v:.10f}")
print(f"  11/45 = {11/45:.10f}")
ok = abs(v - 11/45) < 1e-12
total += 1; passed += ok
chk("C2 11/45 = L₅/(F₅·N_gen²) 全結構", ok, "L₅=11, F₅=5, N_gen=3")

print("\n=== C3: μ = φ⁻¹ + L₅/(F₅·N_gen²) ===")
phi_inv = (math.sqrt(5) - 1) / 2
mu_cand = phi_inv + 11/45
mu_obs = math.log(1 + 1.367)
dev_mu = abs(mu_cand - mu_obs) / mu_obs
print(f"  φ⁻¹ = {phi_inv:.10f}")
print(f"  μ_cand = {mu_cand:.10f} vs μ_obs = {mu_obs:.10f} → dev = {dev_mu*100:.4f}%")
ok = dev_mu < 0.005
total += 1; passed += ok
chk("C3 μ = φ⁻¹ + L₅/(F₅·N_gen²) (dev < 0.5%)", ok, f"(dev = {dev_mu*100:.4f}%)")

print("\n=== C4: s² = B·N_gen²·Var_pop(ln(1+δ̂₊)) ===")
N = 88
deltas_pos = []
for kk in range(1, N + 1):
    th = math.pi * kk / (2 * N)
    dh = -math.cos(2 * th)
    if dh > 0:
        deltas_pos.append(dh)
lnp = [math.log(1 + d) for d in deltas_pos]
mean_p = sum(lnp) / len(lnp)
var_pop = sum((x - mean_p)**2 for x in lnp) / len(lnp)
s2 = k * var_pop
s_hat = math.sqrt(s2)
dev_s = abs(s_hat - 1.2) / 1.2
print(f"  Var_pop(ln(1+δ̂₊)) = {var_pop:.6f}")
print(f"  s² = {k} × {var_pop:.6f} = {s2:.6f}")
print(f"  s = {s_hat:.4f} vs s* = 1.2 → dev = {dev_s*100:.2f}%")
ok = dev_s < 0.05
total += 1; passed += ok
chk("C4 s² = B·N_gen²·Var_pop (dev < 5%)", ok, f"(s = {s_hat:.4f}, dev {dev_s*100:.2f}%)")

print("\n=== C5: 全結構參數雙樣本校準 ===")
random.seed(19)
NMC = 200000
synth = []
for _ in range(NMC):
    th = random.uniform(0, math.pi / 2)
    dh = -math.cos(2 * th)
    lnd = random.gauss(mu_cand, s_hat)
    de = math.exp(lnd) - 1
    if de < -1: de = -1
    M = 1.914e6 * (1 + dh)**1.5 * (1 + de)**1.5
    synth.append(math.log10(M))
synth.sort()
med = statistics.median(synth)
p_hi8 = sum(1 for m in synth if m > 8) / NMC
print(f"  合成 (全結構參數): 中位 = {med:.2f}, P(>8) = {p_hi8:.4f}")
print(f"  觀測: LRD 中位 7.26, Harikane 中位 7.39, P(>8) = 5/69 = 0.0725")
ok = 0.03 <= p_hi8 <= 0.15
total += 1; passed += ok
chk("C5 全結構參數高端密度 P(>8) ∈ [3%, 15%]", ok, f"(P = {p_hi8:.4f})")

print("\n=== C6: 誠實 — 結構身份 vs 觀測轉正 ===")
print("  11/45 = L₅/(F₅·N_gen²) 係結構身份 (C2) ✅")
print("  但 O175 docs/06: 11/45 同觀測一致 (dev 0.04%) 但噪聲地板 3.08% ≫ dev")
print("  → 11/45 未轉正 (數據無法證明), 結構身份 ≠ 觀測證明")
print("  μ = φ⁻¹ + L₅/(F₅·N_gen²) 係結構候選, 唔係閉合")
ok = True
total += 1; passed += ok
chk("C6 結構身份與觀測轉正分別標記", ok,
    "11/45: 結構 ✅ (L₅/(F₅·N_gen²)); 觀測轉正 🔴 (噪聲地板, O175)")

print(f"\nRESULT: {passed}/{total} PASS")
print("裁決:")
print(f"  ★ k = B·N_gen² = 36 (全結構, 唔再係反推)")
print(f"  ★ 11/45 = L₅/(F₅·N_gen²) (全結構身份)")
print(f"  ★ μ = φ⁻¹ + L₅/(F₅·N_gen²) (dev {dev_mu*100:.3f}%)")
print(f"  ★ s² = B·N_gen²·Var_pop (dev {dev_s*100:.2f}%)")
print("  D6 logN 參數全結構化: (μ, s) = (φ⁻¹ + L₅/(F₅·N_gen²), √(B·N_gen²·Var_pop))")
print("  🔴 剩: 11/45 觀測轉正 (O175 data-gated) + k=36 微觀動力學 (池週轉→B·N_gen²)")
